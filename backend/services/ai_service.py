import os
import json
from openai import OpenAI

def get_llm_client():
    """Returns a Groq-compatible LLM client using the OpenAI SDK."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("WARNING: GROQ_API_KEY is not set.")
    
    return OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )

# Groq model optimized for instruction following and JSON
MODEL_NAME = "llama-3.1-8b-instant"

def summarize_message(message: str) -> dict:
    """Summarizes a message and extracts urgency and category."""
    client = get_llm_client()
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
        print(f"AI Summarize Error: {e}")
        return {"summary": "Error processing message", "category": "support", "urgency": "low"}

def classify_lead(message: str) -> dict:
    """Classifies a lead into categories and priority."""
    client = get_llm_client()
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert AI lead classification system for a business. "
                        "Your job is to accurately classify incoming emails/messages into exactly ONE category and ONE priority level.\n\n"

                        "## CATEGORIES (pick exactly one):\n"
                        "1. **urgent** — The message requires IMMEDIATE action or response. Indicators:\n"
                        "   - System outages, downtime, or critical bugs affecting production\n"
                        "   - Security breaches, data loss, or compliance violations\n"
                        "   - Deadlines within 24 hours or explicit words like 'ASAP', 'emergency', 'critical', 'immediately'\n"
                        "   - Legal threats, account suspension, or escalation notices\n"
                        "   - Payment failures or billing disputes with deadlines\n\n"

                        "2. **sales** — The message is related to purchasing, pricing, partnerships, or business development. Indicators:\n"
                        "   - Asking about pricing, plans, quotes, or demos\n"
                        "   - Interest in buying, upgrading, or expanding services\n"
                        "   - Partnership proposals, collaboration requests, or investment inquiries\n"
                        "   - RFP/RFQ submissions or contract negotiations\n"
                        "   - Referrals or introductions for potential business\n\n"

                        "3. **support** — The message is a customer seeking help, asking questions, or reporting non-critical issues. Indicators:\n"
                        "   - How-to questions, feature requests, or general inquiries\n"
                        "   - Bug reports that are NOT production-critical\n"
                        "   - Account setup, configuration, or onboarding help\n"
                        "   - Feedback, complaints, or suggestions\n"
                        "   - Documentation or training requests\n\n"

                        "4. **spam** — The message is unsolicited, irrelevant, or not actionable. Indicators:\n"
                        "   - Marketing emails, newsletters, or promotional content from third parties\n"
                        "   - Phishing attempts, scam messages, or suspicious links\n"
                        "   - Auto-generated notifications with no action required (e.g., 'your receipt', 'no-reply')\n"
                        "   - Completely irrelevant messages unrelated to business operations\n"
                        "   - Mass-sent cold outreach or SEO/link-building offers\n\n"

                        "## PRIORITY LEVELS (pick exactly one):\n"
                        "- **high** — Requires response within hours. Revenue impact, legal risk, or major customer affected.\n"
                        "- **medium** — Requires response within 1-2 business days. Important but not time-critical.\n"
                        "- **low** — Can be handled when convenient. Informational, no urgency, or spam.\n\n"

                        "## CONFLICT RESOLUTION RULES:\n"
                        "- If a message could be both 'urgent' and 'sales' (e.g., 'We need pricing ASAP for a deal closing today'), classify as 'urgent' with 'high' priority.\n"
                        "- If a message could be both 'support' and 'sales' (e.g., 'I love your product, how do I upgrade?'), classify as 'sales' with 'medium' priority.\n"
                        "- If a message looks like spam but mentions a real business concern, classify as 'support' with 'low' priority.\n"
                        "- Always classify 'spam' with 'low' priority.\n"
                        "- Hackathon notifications, competition updates, and event registrations are 'support' with 'medium' priority.\n\n"

                        "## RESPONSE FORMAT:\n"
                        "Respond in JSON with exactly these keys:\n"
                        "- 'summary': A concise 1-2 sentence summary of what the sender wants or needs.\n"
                        "- 'category': Exactly one of 'urgent', 'sales', 'support', 'spam'.\n"
                        "- 'priority': Exactly one of 'high', 'medium', 'low'."
                    )
                },
                {"role": "user", "content": message}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"AI Classify Error: {e}")
        return {"summary": "Error classifying lead", "category": "support", "priority": "low"}

def generate_reply(message: str, category: str = None) -> dict:
    """Generates a professional reply based on the message and optional category."""
    client = get_llm_client()
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
        print(f"AI Reply Error: {e}")
        return {"reply": "We are currently experiencing issues generating a reply. Please try again later."}
