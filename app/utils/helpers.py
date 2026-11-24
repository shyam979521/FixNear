"""
Small, pure display-helper functions with no database access — safe to
call directly from Jinja templates via `app.jinja_env.globals`.
"""

from datetime import datetime

DEFAULT_CATEGORIES = [
    ("Electrician", "30–60 min"),
    ("Plumber", "45–90 min"),
    ("Carpenter", "1–3 hrs"),
    ("Painter", "3–6 hrs"),
    ("Furniture Repair", "1–2 hrs"),
    ("Bike Repair", "30–45 min"),
    ("Car Repair", "1–2 hrs"),
    ("Cleaning", "2–4 hrs"),
    ("AC Repair", "45–90 min"),
    ("Home Appliance Repair", "45–90 min"),
]

BUDGET_RANGES = ["₹200 – ₹500", "₹500 – ₹1000", "₹1000 – ₹2500", "₹2500+"]


def is_urgent_date(date_str):
    """Flags jobs whose preferred date is within 2 days (display only)."""
    if not date_str:
        return False
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        delta = (d - datetime.now().date()).days
        return 0 <= delta <= 2
    except (ValueError, TypeError):
        return False


def duration_estimate_for(category):
    for name, duration in DEFAULT_CATEGORIES:
        if name == category:
            return duration
    return "1–2 hrs"
