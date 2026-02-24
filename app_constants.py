# This file contains configuration variables for the application.


class AppConstants:
    ## Serial communication ##
    SIMULATION_MODE = False  # If True, the app will simulate sensor data instead of reading from serial port
    SERIAL_PORT = "/dev/ttyACM0"
    BAUD_RATE = 115200

    ## Performance ##
    DASHBOARD_UPDATE_INTERVAL = 50  # Update interval in milliseconds (30 Hz)
    PHYSICS_UPDATE_INTERVAL = 3  # Physics update interval in milliseconds (333 Hz)

    ## Sensor fusion ##
    DAMPING_FACTOR = 0.95  # Slows down velocity over time to prevent drift
    ACCELERATION_DEADZONE = 1  # Deadzone for linear accelerations
    ROTATION_DEADZONE = 0.1  # Deadzone for rotation speed
    ACC_BIAS = [0, 0.05, -0.4]  # Bias correction for ax,ay,az (tuned experimentally)
    GYRO_BIAS = [1.68, 1.61, 0.14]  # Bias correction for gx,gy,gz (tuned experimentally)
    G = 9.81  # Gravity constant in mm/s²

# BIAS
# z = 10.28
# z = -9.47
# x = 9.87
# y = 9.72
# rx = -1.68
# ry = -1.6
# rz = -0.14