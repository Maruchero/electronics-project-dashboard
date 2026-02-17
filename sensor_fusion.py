import math
import numpy as np
from scipy.spatial.transform import Rotation as R

from app_constants import AppConstants

class SensorFusion:
    def __init__(self):
        self.rpy = np.zeros(3)  # world frame
        self.pos = np.zeros(3)  # world frame
        self.vel = np.zeros(3)  # world frame

    def update(self, data: np.ndarray, dt):
        """
        Update orientation and position based on sensor data.
        This version uses purely gyroscope integration for orientation.
        Position (X,Y,Z) is fixed to 0.
        
        Args:
            ax, ay, az: Accelerometer data in m/s^2 (unused in this version)
            gx, gy, gz: Gyroscope data in deg/s
            dt: Time delta in seconds
            
        Returns:
            tuple: (pitch, roll, yaw, px, py, pz)
        """
        if len(data) < 6:
            raise ValueError("Data array must contain at least 6 elements: [ax, ay, az, gx, gy, gz]")
        
        rpy = data[3:6] * dt
        for i in range(3):
            if abs(rpy[i]) < AppConstants.ROTATION_DEADZONE:
                rpy[i] = 0.0
        rotation = R.from_euler("XYZ", rpy, degrees=True)
        
        acc_world = rotation.apply(data[0:3])
        acc_world[2] -= AppConstants.G
        for i in range(3):
            if abs(acc_world[i]) < AppConstants.ACCELERATION_DEADZONE:
                acc_world[i] = 0.0
        
        self.vel = acc_world * dt + self.vel * AppConstants.DAMPING_FACTOR

        self.pos = self.vel * dt + self.pos
        
        self.rpy = self.rpy + rotation.as_euler("XYZ", degrees=True)
        return self.rpy[1], self.rpy[0], self.rpy[2], self.pos[0], self.pos[1], self.pos[2]

    def reset(self):
        """
        Reset all state variables (orientation, position, velocity) to zero.
        """
        self.rpy = np.zeros(3)
        self.pos = np.zeros(3)
        self.vel = np.zeros(3)
