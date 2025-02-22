import flask
import docker
import json
import os
import socket
import shutil
from flask import request, jsonify, redirect

app = flask.Flask(__name__)
client = docker.from_env()

###############################################################################
# Directory paths inside the core server container
###############################################################################
CONTAINER_CONFIGS_DIR = "/app/configs"  # The container sees your host's configs here
CONTAINER_ENV_DIR = "/app/env"

###############################################################################
# Actual host paths (so Docker can find them)
###############################################################################
# These are passed in via environment variables in docker-compose.yml
HOST_CONFIGS_DIR = os.environ.get("HOST_CONFIGS_DIR", "/app/configs")
HOST_ENV_DIR = os.environ.get("HOST_ENV_DIR", "/app/env")

# Track running dashboard containers by a "user_id:dashboard_id" key
dashboard_containers = {}

def is_port_in_use(port):
    """Check if the given port is in use on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_free_port():
    """Return the first free port in the range 8051-8100."""
    for port in range(8051, 8101):
        if is_port_in_use(port):
            continue
        if port in [info['port'] for info in dashboard_containers.values()]:
            continue
        return port
    raise Exception("No free ports available")

@app.route("/create_dashboard", methods=["POST"])
def create_dashboard():
    data = request.get_json()
    dashboard_id = data.get("dashboard_id")
    user_id = data.get("user_id")
    description = data.get("description")
    csv_path = data.get("csv_path")  # optional

    if not all([dashboard_id, user_id, description]):
        return jsonify({"error": "dashboard_id, user_id, and description are required"}), 400

    dashboard_key = f"{user_id}:{dashboard_id}"

    # If dashboard already exists, remove it first
    if dashboard_key in dashboard_containers:
        existing_info = dashboard_containers.pop(dashboard_key)
        try:
            existing_info['container'].stop()
            existing_info['container'].remove()
        except Exception as e:
            app.logger.error(f"Error stopping existing container: {e}")

    try:
        # Build the config dictionary
        config = {
            "dashboard_id": dashboard_id,
            "user_id": user_id,
            "description": description,
            "csv_path": csv_path
        }

        # Generate a filename like "john_smith_my_dashboard.json"
        config_filename = f"{dashboard_key.replace(':', '_')}.json"

        #######################################################################
        # 1. Write the config INSIDE this container at /app/configs
        #######################################################################
        container_config_path = os.path.join(CONTAINER_CONFIGS_DIR, config_filename)
        if os.path.exists(container_config_path) and os.path.isdir(container_config_path):
            shutil.rmtree(container_config_path)

        with open(container_config_path, "w", encoding="utf-8") as f:
            json.dump(config, f)

        if not os.path.isfile(container_config_path):
            raise Exception(f"Failed to create config file: {container_config_path}")

        #######################################################################
        # 2. Determine the REAL HOST path so Docker can mount the file
        #######################################################################
        host_config_path = os.path.join(HOST_CONFIGS_DIR, config_filename)
        if os.path.exists(host_config_path) and os.path.isdir(host_config_path):
            shutil.rmtree(host_config_path)

        # Prepare extra.env (for your API keys, etc.)
        container_env_path = os.path.join(CONTAINER_ENV_DIR, "extra.env")
        host_env_path = os.path.join(HOST_ENV_DIR, "extra.env")
        if not os.path.exists(container_env_path):
            with open(container_env_path, "w", encoding="utf-8") as f:
                f.write("OPENAI_API_KEY=your_api_key_here\n")

        port = get_free_port()

        app.logger.info(f"Container config path: {container_config_path}")
        app.logger.info(f"Host config path: {host_config_path}")

        #######################################################################
        # 3. Spawn the dashboard container, using the HOST path for volumes
        #######################################################################
        container = client.containers.run(
            "vizro-dashboard",  # Make sure this image is built/pulled
            detach=True,
            ports={"8050/tcp": port},
            volumes={
                host_config_path: {"bind": "/config/dashboard_config.json", "mode": "ro"},
                os.path.join(HOST_ENV_DIR, "extra.env"): {"bind": "/config/extra.env", "mode": "ro"}
            }
        )

        # Record the container info
        dashboard_containers[dashboard_key] = {
            "port": port,
            "container": container,
            "user_id": user_id,
            "dashboard_id": dashboard_id
        }

        dashboard_url = f"http://localhost:{port}/"
        return jsonify({
            "message": "Dashboard created",
            "dashboard_url": dashboard_url,
            "dashboard_key": dashboard_key
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/remove_dashboard", methods=["POST"])
def remove_dashboard():
    data = request.get_json()
    dashboard_id = data.get("dashboard_id")
    user_id = data.get("user_id")
    if not dashboard_id or not user_id:
        return jsonify({"error": "dashboard_id and user_id are required"}), 400

    dashboard_key = f"{user_id}:{dashboard_id}"
    if dashboard_key not in dashboard_containers:
        return jsonify({"error": "Dashboard not found"}), 404

    info = dashboard_containers.pop(dashboard_key)
    try:
        info['container'].stop()
        info['container'].remove()
    except Exception as e:
        return jsonify({"error": f"Failed to stop container: {str(e)}"}), 500

    # Remove the config file on the HOST side
    config_file = os.path.join(HOST_CONFIGS_DIR, f"{dashboard_key.replace(':', '_')}.json")
    if os.path.exists(config_file):
        os.remove(config_file)

    return jsonify({"message": f"Dashboard '{dashboard_id}' removed for user '{user_id}'"}), 200

@app.route("/list_dashboards", methods=["GET"])
def list_dashboards():
    """List all dashboards for a given user."""
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id query parameter is required"}), 400

    dashboards = {
        key.split(":")[1]: info['port']
        for key, info in dashboard_containers.items()
        if info['user_id'] == user_id
    }
    return jsonify({"dashboards": dashboards}), 200

@app.route("/dashboard/<user_id>/<dashboard_id>")
def route_dashboard(user_id, dashboard_id):
    """Redirect to the requested dashboard's URL."""
    dashboard_key = f"{user_id}:{dashboard_id}"
    if dashboard_key not in dashboard_containers:
        return jsonify({"error": "Dashboard not found"}), 404
    port = dashboard_containers[dashboard_key]['port']
    return redirect(f"http://localhost:{port}/", code=302)

@app.route("/")
def index():
    """Return all running dashboards (for debugging)."""
    all_dashboards = {key: info['port'] for key, info in dashboard_containers.items()}
    return jsonify({"running_dashboards": all_dashboards}), 200

if __name__ == "__main__":
    # For production, you may want to bind to 0.0.0.0 and run behind a reverse proxy.
    app.run(debug=False, host="0.0.0.0", port=8000)
