# Electronic Project Dashboard

## Overview
This project contains Python scripts for visualizing real-time data from an external electronics board (specifically designed for STM32, but adaptable). It features a 2D plotter and a comprehensive dashboard with 3D orientation visualization.

## Key Files
*   **`dashboard.py`**: The main application. A `PyQt5` based dashboard featuring:
    *   **Controls**: Reset graphs, start logging.
    *   **Live Data (2D)**: A rolling plot of sensor values (e.g., voltage).
    *   **Orientation (3D)**: A 3D visualization using `pyqtgraph.opengl` to show device orientation.
    *   **Simulation Mode**: Can run without hardware by simulating data (sine waves).
*   **`serial_plotter.py`**: A lightweight, standalone script for simple 2D real-time plotting of serial data.
*   **`deps`**: A text file containing the command to install necessary Python packages.

## Setup & Installation
1.  **Environment**: Ensure you are in the python virtual environment (`.venv`).
    ```bash
    source .venv/bin/activate
    ```
2.  **Dependencies**: Install the required libraries (`pyqtgraph`, `PyQt5`, `pyserial`, `numpy`).
    ```bash
    pip install pyqtgraph PyQt5 pyserial numpy
    ```
    *(Note: The `deps` file suggests a command, but `numpy` is also imported in the scripts)*

## Usage

### Running the Dashboard
To launch the main dashboard:
```bash
python dashboard.py
```
*   **Configuration**: Edit the top of `dashboard.py` to toggle `SIMULATION_MODE` (default is `True` if serial fails) or change `SERIAL_PORT` (default `/dev/ttyACM0`).

### Running the Simple Plotter
For a quick view of the data stream:
```bash
python serial_plotter.py
```
*   **Configuration**: Edit `USE_REAL_SERIAL` and `SERIAL_PORT` at the top of the file.

## Hardware Connection
*   The scripts expect a device connected to a serial port (e.g., `/dev/ttyACM0` on Linux).
*   **Baud Rate**: 115200.
*   **Data Format**: Expects CSV-like strings ending in newline (e.g., `value,x,y,z\n`).
