"""
utils/serializers.py
─────────────────────
Shared serialisation helpers.
Centralises datetime→ISO-string conversion so it is not duplicated across
five route/service files.
"""
from __future__ import annotations
import datetime


def serialize_lead(lead: dict) -> dict:
    """
    Returns a JSON-safe copy of a lead row dict.
    Converts any datetime fields to ISO-8601 strings.
    """
    result = dict(lead)
    if result.get("created_at") and isinstance(result["created_at"], datetime.datetime):
        dt = result["created_at"]
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        result["created_at"] = dt.isoformat()
    return result


def serialize_leads(leads: list[dict]) -> list[dict]:
    """Applies serialize_lead to a list of lead rows."""
    return [serialize_lead(lead) for lead in leads]
