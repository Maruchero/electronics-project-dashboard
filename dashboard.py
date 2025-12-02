import sys
import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.dockarea import DockArea, Dock
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt
import serial

# --- CONFIGURATION ---
SIMULATION_MODE = True  # Set to False to use real STM32 Serial
SERIAL_PORT = '/dev/ttyACM0' 
BAUD_RATE = 115200
# ---------------------

class Dashboard(QMainWindow):
    def __init__(self):
        global SIMULATION_MODE
        super().__init__()
        self.setWindowTitle("STM32 Real-Time Dashboard")
        self.resize(1000, 600)

        # 1. Setup the Docking Area (The Layout Manager)
        self.area = DockArea()
        self.setCentralWidget(self.area)

        # 2. Create Docks (Draggable Windows)
        self.d_control = Dock("Controls", size=(200, 200)) # Top Left
        self.d_plot    = Dock("Live Data (2D)", size=(500, 400)) # Bottom
        self.d_3d      = Dock("Orientation (3D)", size=(500, 200)) # Top Right

        # Arrange Docks
        self.area.addDock(self.d_control, 'left')
        self.area.addDock(self.d_3d, 'right', self.d_control)
        self.area.addDock(self.d_plot, 'bottom', self.d_3d)

        # --- WIDGET 1: CONTROL PANEL ---
        self.w_control = QWidget()
        layout = QVBoxLayout()
        
        # Digital Readout
        self.lbl_value = QLabel("0.00 V")
        self.lbl_value.setStyleSheet("font-size: 30px; color: cyan; font-weight: bold;")
        self.lbl_value.setAlignment(Qt.AlignCenter)
        
        # Buttons
        self.btn_reset = QPushButton("Reset Graphs")
        self.btn_log   = QPushButton("Start Logging")
        self.btn_reset.clicked.connect(self.reset_data)

        layout.addWidget(QLabel("Current Voltage:"))
        layout.addWidget(self.lbl_value)
        layout.addStretch()
        layout.addWidget(self.btn_reset)
        layout.addWidget(self.btn_log)
        self.w_control.setLayout(layout)
        self.d_control.addWidget(self.w_control)

        # --- WIDGET 2: 2D PLOT ---
        self.w_plot = pg.PlotWidget(title="Sensor History")
        self.w_plot.showGrid(x=True, y=True)
        self.w_plot.setLabel('left', 'Voltage', units='V')
        self.curve = self.w_plot.plot(pen='y')
        self.data_buffer = np.zeros(200)
        self.d_plot.addWidget(self.w_plot)

        # --- WIDGET 3: 3D VIEW ---
        self.w_3d = gl.GLViewWidget()
        self.w_3d.setCameraPosition(distance=20)
        grid = gl.GLGridItem()
        self.w_3d.addItem(grid)
        
        # A simple 3D vector (Line) representing orientation
        self.vector_item = gl.GLLinePlotItem(pos=np.array([[0,0,0], [0,0,5]]), color=(1,0,0,1), width=3)
        self.w_3d.addItem(self.vector_item)
        self.d_3d.addWidget(self.w_3d)

        # --- SETUP DATA STREAM ---
        if not SIMULATION_MODE:
            try:
                self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
            except:
                print("Could not open Serial Port!")
                SIMULATION_MODE = True
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(20) # 50 FPS
        
        self.t = 0

    def update(self):
        val = 0
        x, y, z = 0, 0, 5

        # A. GET DATA
        if SIMULATION_MODE:
            self.t += 0.1
            val = np.sin(self.t) * 5 + np.random.normal(0, 0.2)
            # Simulate 3D rotation
            x = np.sin(self.t) * 5
            y = np.cos(self.t) * 5
        else:
            if self.ser.in_waiting:
                try:
                    # Expecting CSV: "voltage,x,y,z\n"
                    line = self.ser.readline().decode().strip()
                    parts = line.split(',')
                    val = float(parts[0])
                    # If you have 3D data, parse it here:
                    # x = float(parts[1])
                    # y = float(parts[2])
                except:
                    pass

        # B. UPDATE 2D PLOT
        self.data_buffer[:-1] = self.data_buffer[1:]
        self.data_buffer[-1] = val
        self.curve.setData(self.data_buffer)

        # C. UPDATE TEXT
        self.lbl_value.setText(f"{val:.2f} V")

        # D. UPDATE 3D VIEW
        # Move the tip of the red line
        new_pos = np.array([[0,0,0], [x, y, z]])
        self.vector_item.setData(pos=new_pos)

    def reset_data(self):
        self.data_buffer = np.zeros(200)
        self.curve.setData(self.data_buffer)

# Run the App
app = QApplication(sys.argv)
# Dark Theme for cool "Dashboard" look
app.setStyle("Fusion") 
dashboard = Dashboard()
dashboard.show()
sys.exit(app.exec_())