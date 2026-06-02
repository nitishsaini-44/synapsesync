import os
import json
from openai import OpenAI

def get_openai_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("WARNING: GROQ_API_KEY is not set.")
    
    # Use OpenAI client but point it to Groq's API
    return OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )

# Use a Groq model optimized for instruction following and JSON
MODEL_NAME = "llama-3.1-8b-instant"

def summarize_message(message: str) -> dict:
    """Summarizes a message and extracts urgency and category."""
    client = get_openai_client()
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI email triage assistant for a business operations team. "
                        "Analyze the user's message and respond in JSON format with exactly these keys: "
                        "'summary' (a concise 1-2 sentence summary), "
                        "'category' (exactly one of: 'urgent', 'sales', 'support', 'spam'), "
                        "'urgency' (exactly one of: 'high', 'medium', 'low'). "
                        "If the message contains time-sensitive requests or critical issues, classify as 'urgent' with 'high' urgency."
                    )
                },
                {"role": "user", "content": message}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"OpenAI Summarize Error: {e}")
        return {"summary": "Error processing message", "category": "support", "urgency": "low"}

def classify_lead(message: str) -> dict:
    """Classifies a lead into categories and priority."""
    client = get_openai_client()
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI lead classification system. "
                        "Analyze the user's message and respond in JSON format with exactly these keys: "
                        "'summary' (a very short summary), "
                        "'category' (exactly one of: 'urgent', 'sales', 'support', 'spam'), "
                        "'priority' (exactly one of: 'high', 'medium', 'low')."
                    )
                },
                {"role": "user", "content": message}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"OpenAI Classify Error: {e}")
        return {"summary": "Error classifying lead", "category": "support", "priority": "low"}

def generate_reply(message: str, category: str = None) -> dict:
    """Generates a professional reply based on the message and optional category."""
    client = get_openai_client()
    context = f"The message was categorized as '{category}'." if category else "Determine the best approach based on the message."
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional customer support assistant. "
                        "Draft a polite, professional reply to the user's message. "
                        f"{context} "
                        "Respond in JSON format with exactly one key: 'reply' containing the response text."
                    )
                },
                {"role": "user", "content": message}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"OpenAI Reply Error: {e}")
        return {"reply": "We are currently experiencing issues generating a reply. Please try again later."}
