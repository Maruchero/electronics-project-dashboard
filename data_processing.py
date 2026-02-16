import time
from sensor_manager import SensorManager
from sensor_fusion import SensorFusion
from app_constants import AppConstants
from PyQt5.QtCore import QThread, pyqtSignal


class DataProcessingWorker(QThread):
    def __init__(self, shared_state):
        super().__init__()
        self.shared_state = shared_state
        self.sensor_manager = SensorManager(AppConstants.SERIAL_PORT, AppConstants.BAUD_RATE, AppConstants.SIMULATION_MODE)
        self.sensor_fusion = SensorFusion(damping=AppConstants.ENABLE_POSITION_DAMPING, deadzone=AppConstants.ACCELERATION_DEADZONE)
        self.last_update_time = time.time()
        self.running = True
        print(f"[DEBUG] DataProcessingWorker initialized {AppConstants.PHYSICS_UPDATE_INTERVAL / 1000.0}ms")

    def run(self):
        try:
            print("[DEBUG] DataProcessingWorker thread started")
            while self.running:
                new_data = self.sensor_manager.get_next_sample()

                if new_data is None:
                    return

                ax, ay, az = new_data[0], new_data[1], new_data[2]
                gx, gy, gz = new_data[3], new_data[4], new_data[5]

                current_time = time.time()
                dt = current_time - self.last_update_time
                self.last_update_time = current_time

                pitch, roll, yaw, px, py, pz = self.sensor_fusion.update(ax, ay, az, gx, gy, gz, dt)
                
                self.shared_state.update((px, py, pz, roll, pitch, yaw))
                time.sleep(AppConstants.PHYSICS_UPDATE_INTERVAL / 1000.0)

            self.sensor_manager.ser.close()
            print("[DEBUG] DataProcessingWorker thread exiting")
        except Exception as e:
            print(f"WORKER CRASHED: {e}")
