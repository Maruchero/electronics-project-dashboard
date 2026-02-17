import sys
import numpy as np
import pyqtgraph.opengl as gl
from pyqtgraph.dockarea import DockArea, Dock
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColorConstants as QColors, QColor, QPalette
from data_processing import DataProcessingWorker, DataProcessingWorkerState
from views.acc_gyro_view import AccGyroView
from views.magnetometer_view import MagnetometerView
from app_constants import AppConstants
from dataclasses import dataclass


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


class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("6-Axis Sensor Dashboard")
        self.resize(1200, 800)
        
        self.shared_state = DataProcessingWorkerState()
        self.worker_thread = DataProcessingWorker(self.shared_state)
        self.worker_thread.start()
        
        self.debug_stats = DebugStats()

        self.area = DockArea()
        self.setCentralWidget(self.area)

        self.d_3d = Dock("3D Representation", size=(400, 400))
        self.d_controls = Dock("Controls", size=(400, 200))
        self.d_acc_gyro = Dock("Acc & Gyro", size=(800, 600))
        self.d_magnetometer = Dock("Magnetometer", size=(800, 600))

        self.area.addDock(self.d_acc_gyro, 'right') 
        self.area.addDock(self.d_magnetometer, 'above', self.d_acc_gyro)
        self.area.addDock(self.d_3d, 'left', self.d_acc_gyro) 
        self.area.addDock(self.d_controls, 'bottom', self.d_3d)

        self.w_3d = gl.GLViewWidget()
        self.w_3d.setCameraPosition(distance=20)

        grid = gl.GLGridItem()
        grid.setSize(x=20, y=20, z=20)
        grid.setSpacing(x=1, y=1, z=1)
        self.w_3d.addItem(grid)

        line_thickness = 3
        axis_length = 1

        self.axes_items = []

        self.x_axis = gl.GLLinePlotItem(pos=np.array([[0,0,0], [axis_length,0,0]]), color=(1,0,0,1), width=line_thickness)
        self.w_3d.addItem(self.x_axis)
        self.axes_items.append(self.x_axis)

        self.y_axis = gl.GLLinePlotItem(pos=np.array([[0,0,0], [0,axis_length,0]]), color=(0,1,0,1), width=line_thickness)
        self.w_3d.addItem(self.y_axis)
        self.axes_items.append(self.y_axis)

        self.z_axis = gl.GLLinePlotItem(pos=np.array([[0,0,0], [0,0,axis_length]]), color=(0,0,1,1), width=line_thickness)
        self.w_3d.addItem(self.z_axis)
        self.axes_items.append(self.z_axis)

        self.d_3d.addWidget(self.w_3d)

        self.w_controls = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Controls"))
        self.btn_reset_orient = QPushButton("Reset Orientation")
        self.btn_reset_orient.clicked.connect(self.reset_orientation)
        layout.addWidget(self.btn_reset_orient)
        self.debug_stats_label = QLabel("*debug stats will appear here*")
        layout.addWidget(self.debug_stats_label)
        layout.addStretch()
        self.w_controls.setLayout(layout)
        self.d_controls.addWidget(self.w_controls)

        self.acc_gyro_view = AccGyroView(self)
        self.d_acc_gyro.addWidget(self.acc_gyro_view)

        self.magnetometer_view = MagnetometerView(self)
        self.d_magnetometer.addWidget(self.magnetometer_view)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(AppConstants.DASHBOARD_UPDATE_INTERVAL)

    def reset_orientation(self):
        self.worker_thread.reset()

    def update_debug_stats(self):
        self.debug_stats.miss_rate = sum(self.sensor_manager.misses) / len(
            self.sensor_manager.misses
        )
        self.debug_stats.update_frequency = 1000.0 / AppConstants.DASHBOARD_UPDATE_INTERVAL
        self.debug_stats_label.setText(str(self.debug_stats))

    def update(self) -> None:
        snapshot = self.shared_state.get_snapshot()
        pitch, roll, yaw, px, py, pz = snapshot
        self.acc_gyro_view.update_view(snapshot)

        for axis_item in self.axes_items:
            axis_item.resetTransform()
            axis_item.translate(px, py, pz)
            axis_item.rotate(yaw,   0, 0, 1)
            axis_item.rotate(pitch, 0, 1, 0)
            axis_item.rotate(roll,  1, 0, 0)

        # self.update_debug_stats()
        
    def closeEvent(self, event):
        self.worker_thread.stop()
        self.worker_thread.quit()
        self.worker_thread.wait()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, QColors.White)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, QColors.White)
    palette.setColor(QPalette.ToolTipText, QColors.White)
    palette.setColor(QPalette.Text, QColors.White)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, QColors.White)
    palette.setColor(QPalette.BrightText, QColors.Red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColors.Black)
    app.setPalette(palette)

    dash = Dashboard()
    dash.show()
    sys.exit(app.exec_())
