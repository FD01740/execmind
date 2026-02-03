from app.llm.client import call_llm
from app.storage.database import SessionLocal, Idea, Evaluation
from app.utils.parsing import parse_json_safely

EVALUATION_SYSTEM_PROMPT = """
You are a ruthless VC investor and technical auditor.
Evaluate the following product idea.
Output VALID JSON only with these exact keys:
- "feasibility": integer 1-10 (technical feasibility)
- "market_value": integer 1-10 (business potential)
- "complexity": integer 1-10 (implementation difficulty)
- "risk": integer 1-10 (failure risk)
- "innovation": integer 1-10 (novelty)
- "verdict": "pursue" or "refine" or "drop"
- "summary": "1-2 sentence justification"

Do not include conversational text.
"""

def evaluate_idea(idea: Idea) -> Evaluation:
    """
    Evaluates an existing Idea object and saves the evaluation.
    """
    # 1. Construct Prompt
    idea_description = f"""
    Problem: {idea.problem_statement}
    Solution: {idea.proposed_solution}
    Target Users: {idea.target_users}
    Assumptions: {idea.assumptions}
    """
    
    # 2. Call LLM
    llm_output = call_llm(EVALUATION_SYSTEM_PROMPT, idea_description)
    
    # 3. Parse
    data = parse_json_safely(llm_output)
    
    # 4. Calculate Final Score (Simple Average for now)
    scores = [
        data.get("feasibility", 0),
        data.get("market_value", 0),
        data.get("complexity", 0), # High complexity might be bad, but storing raw 1-10
        data.get("risk", 0),       # High risk might be bad
        data.get("innovation", 0)
    ]
    # Naive scoring: (Feasibility + Market + Innovation) - (Risk + Complexity)/2 ... 
    # Let's just do a simple weighted score or just average of positives. 
    # For simplicity, let's just Avg(Feasibility, Market, Innovation).
    # NOTE: The user didn't specify the formula, just "Compute final score".
    # I'll use a balanced weighted sum logic.
    score_val = (
        data.get("feasibility", 0) * 0.2 + 
        data.get("market_value", 0) * 0.3 + 
        data.get("innovation", 0) * 0.2 +
        (10 - data.get("complexity", 10)) * 0.15 + # Lower complexity is better
        (10 - data.get("risk", 10)) * 0.15         # Lower risk is better
    )
    final_score = round(score_val, 2)

    # 5. Save
    db = SessionLocal()
    try:
        evaluation = Evaluation(
            idea_id=idea.id,
            feasibility=data.get("feasibility"),
            market_value=data.get("market_value"),
            complexity=data.get("complexity"),
            risk=data.get("risk"),
            innovation=data.get("innovation"),
            final_score=final_score,
            verdict=data.get("verdict"),
            summary=data.get("summary")
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        return evaluation
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
