import serial
import numpy as np

class SensorManager:
    MG_TO_MS2 = 9.80665 / 1000.0
    MDPS_TO_DPS = 1.0 / 1000.0

    def __init__(self, port='/dev/ttyACM0', baud=115200, simulation_mode=True):
        self.port = port
        self.baud = baud
        self.simulation_mode = simulation_mode
        self.ser = None
        self.sim_t = 0
        self.buffer = ""

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
        Returns a numpy array of 9 floats in SI units:
        [ax (m/s^2), ay (m/s^2), az (m/s^2),
         gx (deg/s), gy (deg/s), gz (deg/s),
         mx (Gauss), my (Gauss), mz (Gauss)]
        
        Input data (Sim or Real) is assumed to be in mg, mdps, Gauss.
        """
        if self.simulation_mode:
            self.sim_t += 0.02
            new_data = np.zeros(9)
            
            noise_acc_mg = 10.0
            new_data[0] = np.random.normal(0, noise_acc_mg)
            new_data[1] = np.random.normal(0, noise_acc_mg)
            new_data[2] = 1000.0 + np.random.normal(0, noise_acc_mg)
            
            noise_gyro_mdps = 50.0
            new_data[3] = np.random.normal(0, noise_gyro_mdps)
            new_data[4] = np.random.normal(0, noise_gyro_mdps)
            new_data[5] = np.random.normal(0, noise_gyro_mdps)
            
            noise_mag = 0.01
            new_data[6] = 0.5 + np.random.normal(0, noise_mag)
            new_data[7] = np.random.normal(0, noise_mag)
            new_data[8] = -0.5 + np.random.normal(0, noise_mag)
            
            new_data[0:3] *= self.MG_TO_MS2
            new_data[3:6] *= self.MDPS_TO_DPS
            
            return new_data
        
        else:
            if self.ser and self.ser.in_waiting:
                try:
                    raw_bytes = self.ser.readline()
                    line = raw_bytes.decode('utf-8', errors='ignore').replace('\x00', '').strip()
                    
                    if not line:
                        return None

                    parts = line.split(',')
                    
                    if len(parts) == 6:
                        raw_data = [float(x) for x in parts]
                        si_data = np.zeros(9)
                        
                        si_data[0] = raw_data[0] * self.MG_TO_MS2
                        si_data[1] = raw_data[1] * self.MG_TO_MS2
                        si_data[2] = raw_data[2] * self.MG_TO_MS2
                        
                        si_data[3] = raw_data[3] * self.MDPS_TO_DPS
                        si_data[4] = raw_data[4] * self.MDPS_TO_DPS
                        si_data[5] = raw_data[5] * self.MDPS_TO_DPS
                        
                        return si_data
                    else:
                        return None
                except Exception as e:
                    print(f"Serial Parse Error: {e}")
                    return None
            else:
                return None
