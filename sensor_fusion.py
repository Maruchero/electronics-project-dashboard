import math

class SensorFusion:
    def __init__(self, damping=False, deadzone=0.0):
        # Orientation State (Degrees)
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0
        
        # Physics State (Position in meters, Velocity in m/s)
        self.px, self.py, self.pz = 0.0, 0.0, 0.0
        self.vx, self.vy, self.vz = 0.0, 0.0, 0.0
        
        # Configuration
        self.enable_damping = damping
        self.deadzone = deadzone
        self.gravity = 9.81 # m/s^2

    def update(self, ax, ay, az, gx, gy, gz, dt):
        """
        Update orientation and position based on sensor data.
        
        Args:
            ax, ay, az: Accelerometer data in m/s^2
            gx, gy, gz: Gyroscope data in deg/s
            dt: Time delta in seconds
            
        Returns:
            tuple: (pitch, roll, yaw, px, py, pz)
        """
        # --- 1. Orientation (Pitch/Roll from Acc, Yaw from Gyro) ---
        
        # Pitch & Roll using Accelerometer (Trigonometry)
        acc_magnitude_yz = math.sqrt(ay*ay + az*az)
        
        pitch_rad = math.atan2(-ax, acc_magnitude_yz) if acc_magnitude_yz != 0 else 0
        roll_rad  = math.atan2(ay, az) if az != 0 else 0
        
        self.pitch = math.degrees(pitch_rad)
        self.roll  = math.degrees(roll_rad)
        
        # Yaw Integration (Gyro Z)
        self.yaw += gz * dt
        
        # --- 2. Position Physics (Double Integration) ---
        
        # Convert Euler angles to Radians for the rotation matrix
        yaw_rad = math.radians(self.yaw)
        
        # Precompute sines and cosines
        c_y, s_y = math.cos(yaw_rad), math.sin(yaw_rad)
        c_p, s_p = math.cos(pitch_rad), math.sin(pitch_rad)
        c_r, s_r = math.cos(roll_rad), math.sin(roll_rad)
        
        # Rotate Local Acceleration to World Frame
        # X_World
        ax_w = (c_y*c_p) * ax + \
               (c_y*s_p*s_r - s_y*c_r) * ay + \
               (c_y*s_p*c_r + s_y*s_r) * az

        # Y_World
        ay_w = (s_y*c_p) * ax + \
               (s_y*s_p*s_r + c_y*c_r) * ay + \
               (s_y*s_p*c_r - c_y*s_r) * az
               
        # Z_World
        az_w = (-s_p) * ax + \
               (c_p*s_r) * ay + \
               (c_p*c_r) * az
               
        # Remove Gravity
        az_w_linear = az_w - self.gravity
        
        # Apply Deadzone
        if abs(ax_w) < self.deadzone: ax_w = 0
        if abs(ay_w) < self.deadzone: ay_w = 0
        if abs(az_w_linear) < self.deadzone: az_w_linear = 0
        
        # Integrate Acceleration -> Velocity
        self.vx += ax_w * dt
        self.vy += ay_w * dt
        self.vz += az_w_linear * dt
        
        # Apply Damping
        if self.enable_damping:
            damping_factor = 0.95
            self.vx *= damping_factor
            self.vy *= damping_factor
            self.vz *= damping_factor
            
        # Integrate Velocity -> Position
        self.px += self.vx * dt
        self.py += self.vy * dt
        self.pz += self.vz * dt
        
        return self.pitch, self.roll, self.yaw, self.px, self.py, self.pz
