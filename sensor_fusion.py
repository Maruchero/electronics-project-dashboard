import math
import numpy as np
from scipy.spatial.transform import Rotation as R

class SensorFusion:
    def __init__(self, damping=False, deadzone=0.0):
        self.rpy = np.zeros(3)  # board frame
        self.pos = np.zeros(3)  # world frame
        self.vel = np.zeros(3)  # world frame
        
        self.enable_damping = damping
        self.deadzone = deadzone
        self.gravity = 9.81

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
        
        rotation = R.from_euler("XYZ", data[3:6] * dt, degrees=True)
        acc_world = rotation.apply(data[0:3])
        acc_world[2] -= self.gravity
        
        # Apply deadzone to accelerations
        
        self.vel = acc_world * dt + self.vel
        
        # if self.enable_damping:
        #     damping_factor = 0.95
        #     self.vx *= damping_factor
        #     self.vy *= damping_factor
        #     self.vz *= damping_factor

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
