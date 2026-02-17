import time
from sensor_manager import SensorManager
from sensor_fusion import SensorFusion
from app_constants import AppConstants
from PyQt5.QtCore import QThread, QTimer, QMutex


class DataProcessingWorkerState:
    def __init__(self):
        self.x, self.y, self.z = 0.0, 0.0, 0.0
        self.roll, self.pitch, self.yaw = 0.0, 0.0, 0.0
        self.mutex = QMutex()

    def update(self, new_coords):
        self.mutex.lock()
        self.x, self.y, self.z, self.roll, self.pitch, self.yaw = new_coords
        self.mutex.unlock()

    def get_snapshot(self):
        self.mutex.lock()
        snapshot = (self.x, self.y, self.z, self.roll, self.pitch, self.yaw)
        self.mutex.unlock()
        return snapshot


class DataProcessingWorker(QThread):
    def __init__(self, shared_state):
        super().__init__()
        self.shared_state = shared_state
        self.sensor_manager = SensorManager(AppConstants.SERIAL_PORT, AppConstants.BAUD_RATE, AppConstants.SIMULATION_MODE)
        self.sensor_fusion = SensorFusion(damping=AppConstants.ENABLE_POSITION_DAMPING, deadzone=AppConstants.ACCELERATION_DEADZONE)
        self.last_update_time = time.time()
        self.running = True
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)

    def run(self):
        print("[DEBUG] DataProcessingWorker thread started")
        while self.running:
            self.update()
            time.sleep(AppConstants.PHYSICS_UPDATE_INTERVAL / 1000.0)
            
        if self.sensor_manager.ser is not None:
            self.sensor_manager.ser.close()
        print("[DEBUG] DataProcessingWorker thread exiting")
            
    def update(self):
        try:
            new_data = self.sensor_manager.get_next_sample()
            if new_data is None:
                return

            ax, ay, az, gx, gy, gz = new_data[0:6]
            current_time = time.time()
            dt = current_time - self.last_update_time
            self.last_update_time = current_time

            pitch, roll, yaw, px, py, pz = self.sensor_fusion.update(ax, ay, az, gx, gy, gz, dt)
            
            self.shared_state.update((px, py, pz, roll, pitch, yaw))
        except Exception as e:
            print(f"WORKER CRASHED: {e}")
            self.stop()
            
    def reset(self):
        self.sensor_fusion.reset()
        
    def stop(self):
        self.running = False
