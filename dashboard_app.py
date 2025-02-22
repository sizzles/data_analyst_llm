import os
import json
import pandas as pd
from dotenv import load_dotenv
from vizro_ai import VizroAI
import vizro.plotly.express as px
from vizro import Vizro

# Load extra environment variables from the mounted extra.env file.
load_dotenv("/config/extra.env")

# Read dashboard configuration from the JSON file.
config_path = os.getenv("CONFIG_PATH", "/config/dashboard_config.json")
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

dashboard_id = config.get("dashboard_id", "default_dashboard")
description = config.get("description", "Default dashboard description")
csv_path = config.get("csv_path", None)

# Load data: if csv_path is provided, use it; otherwise, default to Gapminder dataset.
if csv_path:
    df = pd.read_csv(csv_path)
else:
    df = px.data.gapminder(datetimes=True, pretty_names=True)

# Reset Vizro's internal state.
Vizro._reset()

# Generate the dashboard using the description.
dashboard = VizroAI(model="gpt-4o").dashboard([df], description)
#dashboard.dashboard_id = dashboard_id  # Set required dashboard_id.
dashboard.theme = "vizro_light"         # Use a known theme.

# Build and run the dashboard on port 8050.
Vizro().build(dashboard).run(host="0.0.0.0", port=8050)
