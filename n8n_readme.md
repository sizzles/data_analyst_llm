# Local n8n Installation Guide (Optional)

To fully utilize the AI-Powered Dashboard Demo and generate dashboards using the provided n8n workflow, it's recommended to install n8n locally on your machine.

Follow the steps below for your operating system:

## Windows

1.  **Install nvm-windows (Node Version Manager for Windows):**
    *   Go to: [https://github.com/coreybutler/nvm-windows](https://github.com/coreybutler/nvm-windows)
    *   Download and run the latest installer from the "Download Now!" link.
    *   Follow the installation instructions provided by the installer.

2.  **Open a new Administrator PowerShell or Command Prompt.**

3.  **Install Node.js 20 or later using nvm-windows: **
    *   Run the following command:
        ```bash
        nvm install 20
        ```
        (or use `nvm install latest` for the latest version of Node.js)
    *   Then, use the installed Node.js version:
        ```bash
        nvm use 20
        ```

4.  **Install n8n globally using npm (Node Package Manager):**
    *   Run the following command:
        ```bash
        npm install -g n8n
        ```

5.  **Start n8n:**
    *   Run the following command:
        ```bash
        n8n
        ```
        or
        ```bash
        n8n start
        ```
    *   **Important for Windows users:** Before running `n8n start`, navigate to your n8n configuration directory:
        ```bash
        cd ~/.n8n
        ```

6.  **Access n8n in your web browser:**
    *   Open your browser and go to: `http://localhost:5678`

## Mac/Linux

1.  **Ensure Node.js (version 18 or later) and npm are installed on your system.**
    *   If Node.js and npm are not already installed, follow the official Node.js installation instructions for your operating system. You can find instructions on the [Node.js website](https://nodejs.org/).

2.  **Install n8n globally using npm (Node Package Manager):**
    *   Run the following command in your terminal:
        ```bash
        npm install -g n8n
        ```

3.  **Start n8n:**
    *   Run the following command:
        ```bash
        n8n
        ```
        or
        ```bash
        n8n start
        ```

4.  **Access n8n in your web browser:**
    *   Open your browser and go to: `http://localhost:5678`

## Further Information

For more detailed installation and setup instructions, please refer to the official n8n documentation:

[https://docs.n8n.io/self-hosting/installation/](https://docs.n8n.io/self-hosting/installation/)