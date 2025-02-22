# Pre-initialize Dash Pages callback context to avoid LookupError
import contextvars
import dash._pages as dp
dp.context_value = contextvars.ContextVar("callback_context", default={})

import os
import sys
import importlib.util
from werkzeug.serving import run_simple
from flask import Flask, request, jsonify
import dash
from dash import html, dcc
from vizro_ai import VizroAI
import vizro.plotly.express as px
from vizro import Vizro

# Create our main Flask app.
main_app = Flask(__name__)

# Global registry for storing dashboard layouts.
_dashboard_layouts = {}  # key: dashboard title, value: a Dash layout (component tree)

def get_dashboard_layout(title):
    """Return the dashboard layout for a given title."""
    return _dashboard_layouts.get(title)

def set_dashboard_layout(title, layout):
    """Store the dashboard layout in the global registry."""
    _dashboard_layouts[title] = layout

# Global registry for storing generated dashboard WSGI apps.
dashboard_apps = {}  # key: dashboard title, value: a Flask app (WSGI application)

# Directory to store dynamically generated dashboard modules.
DASH_MODULES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboards")
os.makedirs(DASH_MODULES_DIR, exist_ok=True)

@main_app.route("/generate_dashboard", methods=["POST"])
def generate_dashboard_endpoint():
    """
    Expects JSON payload:
      - title: a unique dashboard identifier (string)
      - description: (optional) a natural-language prompt (string)
    
    Uses Vizro to generate a dashboard layout, stores it in our registry,
    and writes out a new module file that creates an embedded Dash app.
    """
    req_data = request.get_json()
    title = req_data.get("title")
    description = req_data.get("description", "Sample Dashboard")
    if not title:
        return jsonify({"error": "title is required"}), 400

    # --- Generate Dashboard Layout Using Vizro ---
    # For demonstration, we load the gapminder dataset.
    df = px.data.gapminder(datetimes=True, pretty_names=True)
    dashboard_obj = VizroAI().dashboard([df], description)
    dashboard_obj.theme = "vizro_light"
    # Build the Vizro app (using main_app as the server temporarily)
    viz_instance = Vizro(server=main_app).build(dashboard_obj)
    layout_generated = viz_instance.dash.layout
    set_dashboard_layout(title, layout_generated)
    # --- End Dashboard Generation ---

    # --- Write a New Module File for This Dashboard ---
    module_filename = os.path.join(DASH_MODULES_DIR, f"dash_{title}.py")
    module_code = f'''from dash import html, dcc, register_page
from app import get_dashboard_layout
register_page(__name__, path="/dashboard/{title}", name="Dashboard: {title}")
layout = get_dashboard_layout("{title}")
'''
    with open(module_filename, "w", encoding="utf-8") as f:
        f.write(module_code)
    
    # Force import of the new module so Dash Pages picks it up.
    spec = importlib.util.spec_from_file_location(f"dash_{title}", module_filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[f"dashboards.dash_{title}"] = module
    # Initialize the dashboard's WSGI app.
    # (We'll load it on-demand in our dispatcher below.)
    dashboard_apps[title] = module
    # --- End Module Creation ---

    return jsonify({
        "message": "Dashboard created",
        "dashboard_url": f"/dashboard/{title}/"
    }), 200

# --- Define a Home Page ---
@main_app.route("/")
def home():
    links = ""
    if dashboard_apps:
        for title in dashboard_apps:
            links += f'<p><a href="/dashboard/{title}/">Dashboard: {title}</a></p>'
    else:
        links = "<p>No dashboards generated yet.</p>"
    return f"""
    <html>
        <head><title>Multi-Page Dashboard App</title></head>
        <body>
            <h1>Welcome to the Multi-Page Dashboard App</h1>
            {links}
            <p>To generate a new dashboard, POST JSON to /generate_dashboard</p>
        </body>
    </html>
    """

# --- Custom WSGI Dispatcher ---
class DashboardDispatcher:
    """
    A WSGI application that dispatches requests based on URL path.
    If the PATH_INFO starts with '/dashboard/<title>/', delegate to the corresponding dashboard module.
    Otherwise, pass the request to the main Flask app.
    """
    def __init__(self, default_app, dashboards_dir, dashboard_apps):
        self.default_app = default_app
        self.dashboards_dir = dashboards_dir
        self.dashboard_apps = dashboard_apps  # This dict maps title -> module

    def load_dashboard_app(self, title):
        # For simplicity, we assume the module file is already written.
        # You could also re-import if needed.
        if title in self.dashboard_apps:
            module = self.dashboard_apps[title]
            # Call the module's init function if defined.
            # In our case, our module simply sets layout via register_page.
            # We return the main_app (Dash Pages will handle rendering).
            return self.default_app
        return None

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        if path.startswith("/dashboard/"):
            parts = path.split("/")
            if len(parts) > 2:
                title = parts[2]
                dash_app = self.load_dashboard_app(title)
                if dash_app:
                    return dash_app(environ, start_response)
        return self.default_app(environ, start_response)

# Create our composite WSGI application.
dispatcher = DashboardDispatcher(main_app, DASH_MODULES_DIR, dashboard_apps)

if __name__ == "__main__":
    # Use run_simple to serve our composite WSGI app.
    run_simple("0.0.0.0", 8050, dispatcher, use_reloader=True, use_debugger=True)
