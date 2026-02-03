from openai import AzureOpenAI
from app.config.settings import (
    AZURE_OPENAI_API_KEY, 
    AZURE_OPENAI_ENDPOINT, 
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT_NAME
)

client = None
if AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT:
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )

def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Calls Azure OpenAI with the given system and user prompts.
    Returns the content of the response message.
    """
    if not client:
        raise ValueError("Azure OpenAI Client is not initialized. Check your credentials.")

    try:
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # In a real app we might retry or log more specifically
        raise RuntimeError(f"LLM Call Failed: {str(e)}")
