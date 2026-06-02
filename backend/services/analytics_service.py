from backend.database.db import get_analytics

def get_dashboard_stats(user_id):
    """Fetches dashboard statistics from the database for a specific user."""
    try:
        stats = get_analytics(user_id)
        # Ensure we always return expected keys even if DB returns none
        if not stats:
            return {
                "total_processed": 0,
                "urgent_count": 0,
                "sales_count": 0,
                "support_count": 0,
                "spam_count": 0,
                "recent_summaries": []
            }
        
        # Convert datetime objects to string for JSON serialization
        for summary in stats.get("recent_summaries", []):
            if 'created_at' in summary and summary['created_at']:
                summary['created_at'] = summary['created_at'].isoformat()
                
        return stats
    except Exception as e:
        print(f"Analytics Service Error: {e}")
        return {
            "total_processed": 0,
            "urgent_count": 0,
            "sales_count": 0,
            "support_count": 0,
            "spam_count": 0,
            "recent_summaries": []
        }
