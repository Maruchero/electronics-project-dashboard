import sys
import numpy as np
import pyqtgraph.opengl as gl
from pyqtgraph.dockarea import DockArea, Dock
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer, Qt
from sensor_manager import SensorManager
from sensor_fusion import SensorFusion
from views.acc_gyro_view import AccGyroView
from views.magnetometer_view import MagnetometerView
from app_constants import AppConstants
import time

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("6-Axis Sensor Dashboard")
        self.resize(1200, 800)

        self.sensor_fusion = SensorFusion(damping=AppConstants.ENABLE_POSITION_DAMPING, deadzone=AppConstants.ACCELERATION_DEADZONE)
        self.last_update_time = time.time()
        
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
        
        layout.addStretch()
        self.w_controls.setLayout(layout)
        self.d_controls.addWidget(self.w_controls)

        self.acc_gyro_view = AccGyroView(self)
        self.d_acc_gyro.addWidget(self.acc_gyro_view)
        
        self.magnetometer_view = MagnetometerView(self)
        self.d_magnetometer.addWidget(self.magnetometer_view)

        self.sensor_manager = SensorManager(AppConstants.SERIAL_PORT, AppConstants.BAUD_RATE, AppConstants.SIMULATION_MODE)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(20)
        
        self.sim_t = 0

    def reset_orientation(self):
        self.sensor_fusion.reset()

    def update(self):
        new_data = self.sensor_manager.get_next_sample()
        
        if new_data is None:
            return
            
        self.acc_gyro_view.update_view(new_data[:6])
        
        if len(new_data) >= 9:
            self.magnetometer_view.update_view(new_data[6:9])

        ax, ay, az = new_data[0], new_data[1], new_data[2]
        gx, gy, gz = new_data[3], new_data[4], new_data[5]

        current_time = time.time()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time

        pitch, roll, yaw, px, py, pz = self.sensor_fusion.update(ax, ay, az, gx, gy, gz, dt)
        
        for axis_item in self.axes_items:
            axis_item.resetTransform()
            axis_item.translate(px, py, pz)
            axis_item.rotate(yaw,   0, 0, 1)
            axis_item.rotate(pitch, 0, 1, 0)
            axis_item.rotate(roll,  1, 0, 0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    from PyQt5.QtGui import QPalette, QColor
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    dash = Dashboard()
    dash.show()
    sys.exit(app.exec_())
