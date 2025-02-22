import os
import subprocess
import yaml

def modify_docker_compose_yaml(script_dir):
    """Modifies docker-compose.yaml to use absolute paths."""
    absolute_configs_dir = os.path.join(script_dir, "app", "configs")
    absolute_env_dir = os.path.join(script_dir, "app", "env")

    print("\nStep 1: Setting absolute paths in docker-compose.yaml...")
    print(f"Using absolute path for CONFIGS directory: {absolute_configs_dir}")
    print(f"Using absolute path for ENV directory: {absolute_env_dir}\n")

    try:
        with open("docker-compose.yaml", "r") as f:
            yaml_content = yaml.safe_load(f)
    except FileNotFoundError:
        print("Error: docker-compose.yaml not found in the current directory.")
        return False

    # Modify volume mounts - DIRECTLY REPLACE RELATIVE PATHS WITH ABSOLUTE PATHS
    if yaml_content and 'services' in yaml_content and 'core_server' in yaml_content['services'] and 'volumes' in yaml_content['services']['core_server']:
        volumes = yaml_content['services']['core_server']['volumes']
        volumes[0] = f"{absolute_configs_dir}:/app/configs"  # Assuming configs volume is the first one
        volumes[1] = f"{absolute_env_dir}:/app/env"      # Assuming env volume is the second one


        # Modify env_file path (keep environment variable in environment section)
        if 'env_file' in yaml_content['services']['core_server']:
            yaml_content['services']['core_server']['env_file'] = f"{absolute_env_dir}/extra.env"

        # Modify environment variables (keep environment variables in environment section - these are for inside the container!)
        if 'environment' in yaml_content['services']['core_server']:
            environment = yaml_content['services']['core_server']['environment']
            for i, env_var in enumerate(environment):
                if env_var.startswith("HOST_CONFIGS_DIR="):
                    environment[i] = f"HOST_CONFIGS_DIR={absolute_configs_dir}" # Keep as absolute path for clarity inside container env
                elif env_var.startswith("HOST_ENV_DIR="):
                    environment[i] = f"HOST_ENV_DIR={absolute_env_dir}"     # Keep as absolute path for clarity inside container env


        try:
            with open("docker-compose.yaml", "w") as f:
                yaml.dump(yaml_content, f, indent=2)
        except Exception as e:
            print(f"Error writing to docker-compose.yaml: {e}")
            return False
    else:
        print("Error: Could not find 'core_server' service or 'volumes' definition in docker-compose.yaml.")
        return False
    return True

def create_env_file(env_dir):
    """Creates the .env file and prompts user for OpenAI API key."""
    env_file_path = os.path.join(env_dir, "extra.env")
    if not os.path.exists(env_file_path):
        print("\nCreating 'extra.env' file in '{}' directory...".format(env_dir))
        try:
            api_key = input("Please enter your OpenAI API Key: ")
            with open(env_file_path, "w") as f:
                f.write(f"OPENAI_API_KEY={api_key.strip()}\n")
            print("'extra.env' file created and OpenAI API Key saved.\n")
        except Exception as e:
            print(f"Error creating or writing to 'extra.env' file: {e}")
            return False
    else:
        print(f"\n'extra.env' file already exists in '{env_dir}' directory. Skipping creation.\n")
    return True


def build_docker_images():
    """Builds the Docker images."""
    print("\nStep 2: Building Docker images...\n")
    try:
        subprocess.check_call(["docker", "build", "-t", "vizro-dashboard", ".", "--no-cache"], stderr=subprocess.STDOUT, shell=True)
        subprocess.check_call(["docker", "build", "-t", "core-server", "-f", "CoreDockerfile", ".", "--no-cache"], stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Docker image build failed. Please check the output above.\n")
        print(f"Make sure Docker Desktop (or Docker Engine) is running.")
        return False
    return True

def start_docker_containers():
    """Starts the Docker containers using docker-compose."""
    print("\nStep 3: Starting Docker containers using docker-compose...\n")
    try:
        subprocess.check_call(["docker-compose", "up", "-d"], stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Docker Compose failed to start. Please check the output above.\n")
        print(f"Make sure Docker Compose is installed and Docker Desktop (or Docker Engine) is running.")
        return False
    return True

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    absolute_env_dir = os.path.join(script_dir, "app", "env")

    if not modify_docker_compose_yaml(script_dir):
        exit(1)

    if not create_env_file(absolute_env_dir): # Call function to create .env
        exit(1)

    if not build_docker_images():
        exit(1)

    if not start_docker_containers():
        exit(1)


    print("\nInstallation complete!\n")
    print("**IMPORTANT: Your OpenAI API Key is now saved in the '.env' file.**") # Updated message
    print(f"The '.env' file is located in the '{absolute_env_dir}' directory.\n") # More specific message
    print("Access the Core Server UI at http://localhost:8000")
    print("\nTo generate dashboards, you can use the n8n workflow provided.")
    print("Import the workflow into n8n and configure it.\n")
    print("Make sure Docker Desktop (or Docker Engine) is running.")
    print("\nTo stop the demo, run: docker-compose down\n")

    exit(0)