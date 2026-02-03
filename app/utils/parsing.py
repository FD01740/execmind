import json
import re

def parse_json_safely(text: str) -> dict:
    """
    Attempts to parse JSON from a string, handling markdown code blocks
    and potentially malformed JSON.
    """
    try:
        # 1. Try direct parse
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Extract from markdown code blocks ```json ... ```
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        clean_text = match.group(1)
        try:
            return json.loads(clean_text)
        except json.JSONDecodeError:
            pass
            
    # 3. Last ditch: try to find start and end braces
    try:
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            possible_json = text[start:end+1]
            return json.loads(possible_json)
    except json.JSONDecodeError:
        pass

    # Fail gracefully
    raise ValueError(f"Could not parse JSON from text: {text[:100]}...")
