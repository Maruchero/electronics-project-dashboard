# This file contains configuration variables for the application.

class AppConstants:
    SIMULATION_MODE = False  # Set to False to use real Serial
    SERIAL_PORT = '/dev/ttyACM0' 
    BAUD_RATE = 115200
    ENABLE_POSITION_DAMPING = False # Set to True to prevent position drift (resets velocity)
    ACCELERATION_DEADZONE = 1.5 # Set a threshold for linear acceleration to reduce drift. 0.0 to disable.
    G = 9.81  # Gravity constant in mm/s²
    UPDATE_INTERVAL_MS = 1  # Update interval in milliseconds (1000 Hz)