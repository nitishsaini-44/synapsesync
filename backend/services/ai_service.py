"""
services/ai_service.py
───────────────────────
All Groq AI interactions via the OpenAI-compatible SDK.

Fixes applied:
- H6:  Uses logging instead of print()
- M4:  classify_lead() now returns 'urgency' (not 'priority') — key naming unified
- LLM client is a module-level singleton to avoid recreating it per call
- Configurable timeout (30 s) on all API calls
"""
import os
import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

# ── Groq model ───────────────────────────────────────────────────────────────
MODEL_NAME = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")

# ── Singleton LLM client (created once at module import time) ─────────────────
_llm_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _llm_client
    if _llm_client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            logger.warning("GROQ_API_KEY is not set — AI calls will fail.")
        _llm_client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key,
            timeout=30.0,       # prevents indefinite blocking if Groq is slow
        )
    return _llm_client


# ── Internal helper ───────────────────────────────────────────────────────────

def _call_ai(system_prompt: str, user_message: str, fallback: dict) -> dict:
    """
    Shared wrapper around every Groq completion call.
    Handles timeout, JSON parsing, and structured error logging.
    """
    try:
        response = _get_client().chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        logger.exception("Groq AI call failed")
        return fallback


# ── Public AI functions ───────────────────────────────────────────────────────

def summarize_message(message: str) -> dict:
    """
    Summarises a message and extracts urgency and category.
    Returns: { summary, category, urgency }
    """
    system_prompt = (
        "You are an AI email triage assistant for a business operations team. "
        "Analyse the user's message and respond in JSON format with exactly these keys: "
        "'summary' (a concise 1-2 sentence summary), "
        "'category' (exactly one of: 'urgent', 'sales', 'support', 'spam'), "
        "'urgency' (exactly one of: 'high', 'medium', 'low'). "
        "If the message contains time-sensitive requests or critical issues, "
        "classify as 'urgent' with 'high' urgency."
    )
    return _call_ai(
        system_prompt,
        message,
        fallback={"summary": "Error processing message.", "category": "support", "urgency": "low"},
    )


def classify_lead(message: str) -> dict:
    """
    Classifies a lead into category and urgency.
    Returns: { summary, category, urgency }   ← 'urgency' (was 'priority', now unified — M4)
    """
    system_prompt = (
        "You are an expert AI lead classification system for a business. "
        "Classify incoming emails/messages into exactly ONE category and ONE priority level.\n\n"

        "## CATEGORIES (pick exactly one):\n"
        "1. **urgent** — Requires IMMEDIATE action. Indicators:\n"
        "   - System outages, downtime, critical bugs affecting production\n"
        "   - Security breaches, data loss, or compliance violations\n"
        "   - Deadlines within 24 hours or explicit words like 'ASAP', 'emergency', 'critical'\n"
        "   - Legal threats, account suspension, or escalation notices\n"
        "   - Payment failures or billing disputes with deadlines\n\n"

        "2. **sales** — Purchasing, pricing, partnerships, or business development. Indicators:\n"
        "   - Asking about pricing, plans, quotes, or demos\n"
        "   - Interest in buying, upgrading, or expanding services\n"
        "   - Partnership proposals, RFP/RFQ submissions, or contract negotiations\n\n"

        "3. **support** — Customer seeking help, asking questions, or reporting non-critical issues:\n"
        "   - How-to questions, feature requests, or general inquiries\n"
        "   - Non-production bug reports, account setup, onboarding\n"
        "   - Feedback, complaints, or suggestions\n\n"

        "4. **spam** — Unsolicited, irrelevant, or not actionable:\n"
        "   - Marketing emails, newsletters, phishing, no-reply notifications\n"
        "   - Mass cold outreach, SEO/link-building offers\n\n"

        "## URGENCY LEVELS (pick exactly one):\n"
        "- **high** — Response within hours. Revenue/legal risk or major customer affected.\n"
        "- **medium** — Response within 1-2 business days. Important but not time-critical.\n"
        "- **low** — Handle when convenient. Informational, no urgency, or spam.\n\n"

        "## CONFLICT RESOLUTION:\n"
        "- urgent + sales → 'urgent' / 'high'\n"
        "- support + sales → 'sales' / 'medium'\n"
        "- spam → always 'low'\n"
        "- Hackathon/event notifications → 'support' / 'medium'\n\n"

        "## RESPONSE FORMAT:\n"
        "Respond in JSON with exactly these keys:\n"
        "- 'summary': 1-2 sentence summary of what the sender wants.\n"
        "- 'category': one of 'urgent', 'sales', 'support', 'spam'.\n"
        "- 'urgency': one of 'high', 'medium', 'low'."   # ← unified key name (M4)
    )
    return _call_ai(
        system_prompt,
        message,
        fallback={"summary": "Error classifying lead.", "category": "support", "urgency": "low"},
    )


def generate_reply(message: str, category: str | None = None) -> dict:
    """
    Generates a professional reply.
    Returns: { reply }
    """
    context = (
        f"The message was categorised as '{category}'."
        if category
        else "Determine the best approach based on the message content."
    )
    system_prompt = (
        "You are a professional customer support assistant. "
        "Draft a polite, professional, and concise reply to the user's message. "
        "Keep the reply short and to the point (maximum 3 sentences). "
        f"{context} "
        "Respond in JSON format with exactly one key: 'reply' containing the response text."
    )
    return _call_ai(
        system_prompt,
        message,
        fallback={"reply": "We are currently experiencing issues. Please try again later."},
    )
