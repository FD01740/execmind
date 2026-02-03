from app.llm.client import call_llm
import json
from app.storage.database import SessionLocal, Idea
from app.utils.parsing import parse_json_safely
from app.context.provider import get_context

from app.llm.client import call_llm
from app.storage.database import SessionLocal, Idea
from app.utils.parsing import parse_json_safely
from app.context.provider import get_context
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

# 1. Framing Prompt
FRAMING_SYSTEM_PROMPT = """
You are a perceptive product analyst. 
The user will provide a raw idea. 
Your goal is to restate it clearly to confirm understanding.
Output VALID JSON with:
- "restatement": "A clean, professional summary of the idea"
- "confirmation_question": "A question asking if this logic is correct"
"""

# 2. Research Prompt
RESEARCH_SYSTEM_PROMPT = """
You are a Deep Research Agent. 
You will be given:
1. A Product Idea
2. Internal History (matches found in internal DB)
3. External Web Search Results

Your task:
Analyze if this idea has been implemented before.
- If it exists (internally or externally), cite WHO and WHEN.
- If it is novel, say so.

Output valid text (not JSON) summarizing your findings.
Structure it as:
**Internal History:** ...
**External Market:** ...
**Verdict:** (Novel / Derivative / Exact Duplicate)
"""

# 3. Structuring Prompt (Original)
STRUCTURING_SYSTEM_PROMPT = """
You are an expert product manager.
Take the confirmed idea and structure it.
Output VALID JSON only:
- "problem_statement"
- "proposed_solution"
- "target_users"
- "assumptions"
"""

def frame_idea(raw_input: str) -> dict:
    """
    Step 1: Frame the idea for user confirmation.
    """
    llm_output = call_llm(FRAMING_SYSTEM_PROMPT, raw_input)
    return parse_json_safely(llm_output)

def conduct_research(framed_text: str) -> str:
    """
    Step 2: Check internal history and web.
    """
    # A. Internal Search (Simple Linear Scan via LLM for now - lean)
    db = SessionLocal()
    history_context = "No internal duplicates found."
    try:
        # Get last 20 ideas to check against - lean method
        recent_ideas = db.query(Idea).order_by(Idea.id.desc()).limit(20).all()
        if recent_ideas:
            history_list = "\n".join([f"- ID {i.id}: {i.proposed_solution}" for i in recent_ideas])
            # Ask LLM if any match
            # For speed, we just dump this into the final prompt
            history_context = f"Recent Internal Ideas:\n{history_list}"
    finally:
        db.close()

    # B. External Search
    web_context = "No web results found."
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(framed_text, max_results=5))
            if results:
                web_context = "\n".join([f"- {r['title']}: {r['body']} ({r['href']})" for r in results])
    except Exception as e:
        web_context = f"Web search failed: {e}"

    # C. Analyze
    research_prompt = f"""
    Idea: {framed_text}
    
    {history_context}
    
    Web Search Results:
    {web_context}
    """
    
    return call_llm(RESEARCH_SYSTEM_PROMPT, research_prompt)

def save_structured_idea(raw_input: str, source: str) -> Idea:
    """
    Step 3: Final save after confirmation.
    """
    context = get_context(raw_input) 
    user_prompt = f"Raw Idea: {raw_input}\n\nContext: {context}"
    llm_output = call_llm(STRUCTURING_SYSTEM_PROMPT, user_prompt)
    
    parsed_data = parse_json_safely(llm_output)
    
    db = SessionLocal()
    try:
        assumptions = parsed_data.get("assumptions")
        if isinstance(assumptions, list):
            assumptions = json.dumps(assumptions)
            
        target_users = parsed_data.get("target_users")
        if isinstance(target_users, list):
            target_users = json.dumps(target_users)

        new_idea = Idea(
            raw_input=raw_input,
            problem_statement=parsed_data.get("problem_statement"),
            proposed_solution=parsed_data.get("proposed_solution"),
            target_users=target_users,
            assumptions=assumptions,
            source=source
        )
        db.add(new_idea)
        db.commit()
        db.refresh(new_idea)
        return new_idea
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
