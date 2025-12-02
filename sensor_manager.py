import serial
import numpy as np

class SensorManager:
    def __init__(self, port='/dev/ttyACM0', baud=115200, simulation_mode=True):
        self.port = port
        self.baud = baud
        self.simulation_mode = simulation_mode
        self.ser = None
        self.sim_t = 0

        if not self.simulation_mode:
            try:
                self.ser = serial.Serial(self.port, self.baud, timeout=0.1)
                print(f"Connected to {self.port}")
            except Exception as e:
                print(f"Serial Error: {e}")
                print("Switching to SIMULATION_MODE")
                self.simulation_mode = True

    def get_next_sample(self):
        """
        Returns a numpy array of 6 floats [ax, ay, az, gx, gy, gz]
        or None if no data is available (waiting for serial).
        """
        if self.simulation_mode:
            self.sim_t += 0.1
            new_data = np.zeros(6)
            # Simulate Acc (X, Y, Z) - sinusoidal
            new_data[0] = np.sin(self.sim_t) * 9.81  # Acc X (simulating +/- 1g)
            new_data[1] = np.cos(self.sim_t) * 9.81  # Acc Y
            new_data[2] = -9.81 + np.sin(self.sim_t * 0.5) * 2  # Acc Z (gravity -9.81)
            
            # Simulate Gyro (X, Y, Z) - noisy, in deg/s
            new_data[3] = np.random.normal(0, 5) # Gyro X
            new_data[4] = np.random.normal(0, 5) # Gyro Y
            new_data[5] = 20 + np.random.normal(0, 2) # Gyro Z (constant rotation + noise)
            
            return new_data
        
        else:
            if self.ser and self.ser.in_waiting:
                try:
                    # Expecting CSV: "ax,ay,az,gx,gy,gz\n"
                    line = self.ser.readline().decode().strip()
                    parts = line.split(',')
                    if len(parts) == 6:
                        return np.array([float(x) for x in parts])
                    else:
                        # Malformed line
                        return None
                except Exception as e:
                    print(f"Serial Parse Error: {e}")
                    return None
            else:
                return None
