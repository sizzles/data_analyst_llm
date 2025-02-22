# store.py
dashboards = {}

def get_dashboard(title: str):
    """Retrieve the dashboard layout by title."""
    return dashboards.get(title)

def set_dashboard(title: str, layout):
    """Store the dashboard layout by title."""
    dashboards[title] = layout
