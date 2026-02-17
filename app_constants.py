# This file contains configuration variables for the application.


class AppConstants:
    ## Serial communication ##
    SIMULATION_MODE = False  # If True, the app will simulate sensor data instead of reading from serial port
    SERIAL_PORT = "/dev/ttyACM0"
    BAUD_RATE = 115200

    ## Performance ##
    DASHBOARD_UPDATE_INTERVAL = 50  # Update interval in milliseconds (30 Hz)
    PHYSICS_UPDATE_INTERVAL = 50  # Physics update interval in milliseconds (100 Hz)

    ## Sensor fusion ##
    DAMPING_FACTOR = 0.95  # Slows down velocity over time to prevent drift
    ACCELERATION_DEADZONE = 1.5  # Deadzone for linear accelerations
    ROTATION_DEADZONE = 0.05  # Deadzone for rotation rate
    G = 9.81  # Gravity constant in mm/s²
