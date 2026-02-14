# Stirling PDF Docker Manager GUI

This is a simple Python Tkinter GUI application designed to manage the Stirling PDF Docker container. It provides a convenient graphical interface to start, stop, and access your Stirling PDF instance, along with a visual status indicator.

## Features

*   **Run Stirling PDF:** Starts the `stirling-pdf` Docker container. If the container doesn't exist, it will create and run a new one, exposing it on port `8080`.
*   **Stop Stirling PDF:** Stops the running `stirling-pdf` Docker container.
*   **Open in Browser:** Opens `http://localhost:8080` in your default web browser, allowing quick access to the Stirling PDF web interface.
*   **Status Indicator:** A visual circle indicates the current status of the `stirling-pdf` Docker container:
    *   **Green:** Running
    *   **Red:** Stopped (container exists but is not running)
    *   **Gray:** Unknown or container not found
*   **Dynamic Button States:** Buttons are enabled or disabled based on the container's status to prevent invalid operations.
*   **Automatic Status Refresh:** The status indicator updates automatically every 5 seconds.

## Requirements

*   **Python 3:** The GUI is written in Python 3.
*   **Tkinter:** Typically included with Python, but might need to be installed separately on some Linux distributions (e.g., `sudo apt install python3-tk` or `sudo dnf install python3-tkinter`).
*   **Docker:** The Docker daemon must be running and accessible to your user (i.e., your user should be in the `docker` group, or you should be able to run `docker` commands without `sudo`).
*   **`stirlingtools/stirling-pdf:latest` Docker Image:** The application expects this image to be available (it will pull it if not found when running the container for the first time).

## Installation and Usage

1.  **Clone the repository (or download the files):**
    ```bash
    git clone https://github.com/intmain-voidmain/stirling-pdf-manager.git
    cd stirling-pdf-manager
    ```

2.  **Ensure `stirling-data` directory exists:**
    The application mounts a local directory named `stirling-data` to `/configs` inside the Docker container for persistent configuration. Make sure this directory exists in the same location as your `stirling_pdf_gui.py` script.
    ```bash
    mkdir -p stirling-data
    ```

3.  **Run the GUI:**
    ```bash
    python3 stirling_pdf_gui.py
    ```

## Creating a Desktop Shortcut (Linux)

To integrate the application into your desktop environment and application menu:

1.  **Ensure the `.desktop` file is in place:**
    The `stirling-pdf-manager.desktop` file is included in this repository. You can place it in your applications directory:
    ```bash
    cp stirling-pdf-manager.desktop ~/.local/share/applications/
    ```

2.  **For a Desktop Icon:**
    Copy the `.desktop` file to your Desktop directory:
    ```bash
    cp stirling-pdf-manager.desktop ~/Desktop/
    ```
    You may need to right-click the icon on your desktop and select "Allow Launching" or "Mark as Executable" to make it directly clickable, depending on your desktop environment.

## Docker Container Details

The GUI manages a Docker container named `stirling-pdf`. It maps port `8080` from your host to `8080` in the container and uses a local `stirling-data` directory for persistent configuration.
