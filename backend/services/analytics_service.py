"""
services/analytics_service.py
───────────────────────────────
Analytics data retrieval service.

Fixes:
- M2:  uses serialize_leads() for datetime conversion — no inline isoformat()
- H6:  logging replaces print()
"""
import logging
from backend.database.db import get_analytics
from backend.utils.serializers import serialize_leads

logger = logging.getLogger(__name__)

_EMPTY_STATS = {
    "total_processed":  0,
    "urgent_count":     0,
    "sales_count":      0,
    "support_count":    0,
    "spam_count":       0,
    "recent_summaries": [],
}


def get_dashboard_stats(user_id: int) -> dict:
    """Fetches dashboard statistics from the database for a specific user."""
    try:
        stats = get_analytics(user_id)
        if not stats:
            return dict(_EMPTY_STATS)

        # Use shared serialiser — no inline datetime conversion (M2)
        stats["recent_summaries"] = serialize_leads(stats.get("recent_summaries", []))
        return stats

    except Exception:
        logger.exception("Analytics service error for user %s", user_id)
        return dict(_EMPTY_STATS)
