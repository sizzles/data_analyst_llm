## Installation

1.  **Download the Demo Files:** Download or clone the repository containing the demo files (e.g., from GitHub).

2.  **Navigate to the Demo Directory:** Open a terminal or command prompt and navigate to the directory where you downloaded the demo files.

3.  **Run the Installation Script:**
    *   **Windows/Mac/Linux:** Open a terminal or command prompt in the demo directory and run: `python install.py`

    The installation script will guide you through the following steps:

    *   **Step 1: Setting Absolute Paths in `docker-compose.yaml`:** The script will automatically modify the `docker-compose.yaml` file to use absolute paths for the `app/configs` and `app/env` directories, ensuring that Docker volumes correctly point to these folders within your downloaded demo repository.

    *   **Step 2: Create and Configure `.env` File:**
        *   The script will check if an `.env` file exists in the `app/env` directory.
        *   If it does not exist, the script will create it.
        *   **You will be prompted to enter your OpenAI API Key.** The script will then save this API key into the `.env` file.

    *   **Step 3: Build Docker Images:** The script will build the Docker images for the core server and the dashboard application.

    *   **Step 4: Start Docker Containers:** The script will start the Docker containers using `docker-compose`.

4.  **Wait for Containers to Start:** It might take a few moments for the Docker containers to start up for the first time. You can check the progress in the Docker Desktop application or by running `docker-compose logs` in your terminal.

## Configuration

**Configuration is now handled automatically during the installation process!**

During installation (Step 2), you will be prompted to enter your OpenAI API Key. This API key will be saved in the `.env` file located in the `app/env` directory.

**Verification (Optional):**

If you want to verify the configuration, you can:

1.  **Verify `app/env` Directory:** Ensure that you have an `app/env` directory within your demo directory. This directory should now contain the `.env` file.

2.  **Check `.env` File Content:** Open the `.env` file in the `app/env` directory in a text editor. You should see a line that looks like: `OPENAI_API_KEY=YOUR_API_KEY_YOU_ENTERED`.  Make sure your API key is correctly saved there.

    **Security Note:** The `.env` file is used to store sensitive information like API keys outside of your code.  **Do not commit your `.env` file to public version control repositories (like GitHub) if it contains your actual API key.**  It's generally good practice to add `.env` to your `.gitignore` file to prevent accidental commits.  For this demo, we are including it in the package for simplicity of setup, but users should be aware of the security implications.


[Rest of the README.md remains the same]