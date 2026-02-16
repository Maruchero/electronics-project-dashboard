import math

class SensorFusion:
    def __init__(self, damping=False, deadzone=0.0):
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0
        
        self.px, self.py, self.pz = 0.0, 0.0, 0.0
        self.vx, self.vy, self.vz = 0.0, 0.0, 0.0
        
        self.enable_damping = damping
        self.deadzone = deadzone
        self.gravity = 9.81

    def update(self, ax, ay, az, gx, gy, gz, dt):
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
        self.pitch += gx * dt
        self.roll  += gy * dt
        self.yaw   += gz * dt
        
        self.pitch %= 360
        if self.pitch > 180: self.pitch -= 360
        if self.pitch < -180: self.pitch += 360

        self.roll %= 360
        if self.roll > 180: self.roll -= 360
        if self.roll < -180: self.roll += 360

        self.yaw %= 360
        if self.yaw > 180: self.yaw -= 360
        if self.yaw < -180: self.yaw += 360
        
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)
        roll_rad = math.radians(self.roll)
        
        c_y, s_y = math.cos(yaw_rad), math.sin(yaw_rad)
        c_p, s_p = math.cos(pitch_rad), math.sin(pitch_rad)
        c_r, s_r = math.cos(roll_rad), math.sin(roll_rad)
        
        # Rotate Local Acceleration to World Frame
        ax_w = (c_y*c_p) * ax + \
               (c_y*s_p*s_r - s_y*c_r) * ay + \
               (c_y*s_p*c_r + s_y*s_r) * az

        ay_w = (s_y*c_p) * ax + \
               (s_y*s_p*s_r + c_y*c_r) * ay + \
               (s_y*s_p*c_r - c_y*s_r) * az
               
        az_w = (-s_p) * ax + \
               (c_p*s_r) * ay + \
               (c_p*c_r) * az
               
        az_w_linear = az_w - self.gravity
        
        if abs(ax_w) < self.deadzone: ax_w = 0
        if abs(ay_w) < self.deadzone: ay_w = 0
        if abs(az_w_linear) < self.deadzone: az_w_linear = 0
        
        self.vx += ax_w * dt
        self.vy += ay_w * dt
        self.vz += az_w_linear * dt
        
        if self.enable_damping:
            damping_factor = 0.95
            self.vx *= damping_factor
            self.vy *= damping_factor
            self.vz *= damping_factor
            
        self.px += self.vx * dt
        self.py += self.vy * dt
        self.pz += self.vz * dt
        
        return self.pitch, self.roll, self.yaw, self.px, self.py, self.pz

    def reset(self):
        """
        Reset all state variables (orientation, position, velocity) to zero.
        """
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0
        self.px, self.py, self.pz = 0.0, 0.0, 0.0
        self.vx, self.vy, self.vz = 0.0, 0.0, 0.0
