from dataclasses import dataclass
import time
from sensor_manager import SensorManager
from sensor_fusion import SensorFusion
from app_constants import AppConstants
from PyQt5.QtCore import QThread, QTimer, QMutex


@dataclass
class DebugStats:
    miss_rate: float = 0.0
    update_frequency: float = 0.0

    def __repr__(self):
        return "\n".join(
            [
                f"{name.replace('_', ' ').title()}: {value:.2f}"
                for name, value in self.__dict__.items()
            ]
        )


class DataProcessingWorkerState:
    def __init__(self):
        self.x, self.y, self.z = 0.0, 0.0, 0.0
        self.roll, self.pitch, self.yaw = 0.0, 0.0, 0.0
        self.debug_stats = DebugStats()
        self.mutex = QMutex()

    def update(self, new_coords):
        self.mutex.lock()
        self.x, self.y, self.z, self.roll, self.pitch, self.yaw = new_coords
        self.mutex.unlock()

    def update_stats(self, stats):
        self.mutex.lock()
        self.debug_stats = stats
        self.mutex.unlock()

    def get_snapshot(self):
        self.mutex.lock()
        snapshot = (self.x, self.y, self.z, self.roll, self.pitch, self.yaw)
        self.mutex.unlock()
        return snapshot

    def get_stats(self):
        self.mutex.lock()
        stats = self.debug_stats
        self.mutex.unlock()
        return stats


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
        print(f"[DEBUG] {self.__class__.__name__} thread started")
        while self.running:
            self.update()
            self.update_debug_stats()
            time.sleep(AppConstants.PHYSICS_UPDATE_INTERVAL / 1000.0)
            
        if self.sensor_manager.ser is not None:
            self.sensor_manager.ser.close()
        print(f"[DEBUG] {self.__class__.__name__} thread exiting")
            
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
            
    def update_debug_stats(self):
        stats = DebugStats()
        if len(self.sensor_manager.misses) > 0:
            stats.miss_rate = sum(self.sensor_manager.misses) / len(
                self.sensor_manager.misses
            )
        stats.update_frequency = 1.0 / AppConstants.PHYSICS_UPDATE_INTERVAL * 1000.0
        self.shared_state.update_stats(stats)
            
    def reset(self):
        self.sensor_fusion.reset()
        
    def stop(self):
        self.running = False
