import sys
import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.dockarea import DockArea, Dock
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
import serial
import math # Added for atan2, degrees, pi
import time # Added for time.time()

# --- CONFIGURATION ---
SIMULATION_MODE = True  # Set to False to use real Serial
SERIAL_PORT = '/dev/ttyACM0' 
BAUD_RATE = 115200
ENABLE_POSITION_DAMPING = False # Set to True to prevent position drift (resets velocity)
# ---------------------

class Dashboard(QMainWindow):
    def __init__(self):
        global SIMULATION_MODE
        super().__init__()
        self.setWindowTitle("6-Axis Sensor Dashboard")
        self.resize(1200, 800)

        # Initialize sensor fusion variables
        self.current_yaw = 0.0
        self.last_update_time = time.time()
        
        # Physics State (Velocity and Position)
        self.vx, self.vy, self.vz = 0.0, 0.0, 0.0
        self.px, self.py, self.pz = 0.0, 0.0, 0.0

        # 1. Setup DockArea
        self.area = DockArea()
        self.setCentralWidget(self.area)

        # 2. Define Docks
        # Left side (approx 1/3 width implied by size ratio vs right dock)
        self.d_3d = Dock("3D Representation", size=(400, 400))
        self.d_controls = Dock("Controls", size=(400, 200))
        
        # Right side (approx 2/3 width)
        self.d_charts = Dock("Sensor Data (Acc & Gyro)", size=(800, 600))

        # 3. Layout Docks
        # Strategy: Place the main right-side content first, then carve out the left side.
        self.area.addDock(self.d_charts, 'right')     # Occupy full screen initially
        self.area.addDock(self.d_3d, 'left', self.d_charts) # Split: Left(3D) | Right(Charts)
        self.area.addDock(self.d_controls, 'bottom', self.d_3d) # Split Left: Top(3D) / Bottom(Controls)

        # --- LEFT PANEL CONTENT ---
        
        # 3D View
        self.w_3d = gl.GLViewWidget()
        self.w_3d.setCameraPosition(distance=20)
        
        # Add a grid
        grid = gl.GLGridItem()
        grid.setSize(x=20, y=20, z=20)
        grid.setSpacing(x=1, y=1, z=1)
        self.w_3d.addItem(grid)
        
        # OPTION 2: Coordinate Axes (using GLLinePlotItem for custom thickness)
        line_thickness = 3 # Adjust as needed
        axis_length = 5    # Same length as before

        self.axes_items = []

        # X-axis (Red)
        self.x_axis = gl.GLLinePlotItem(pos=np.array([[0,0,0], [axis_length,0,0]]), color=(1,0,0,1), width=line_thickness)
        self.w_3d.addItem(self.x_axis)
        self.axes_items.append(self.x_axis)

        # Y-axis (Green)
        self.y_axis = gl.GLLinePlotItem(pos=np.array([[0,0,0], [0,axis_length,0]]), color=(0,1,0,1), width=line_thickness)
        self.w_3d.addItem(self.y_axis)
        self.axes_items.append(self.y_axis)

        # Z-axis (Blue)
        self.z_axis = gl.GLLinePlotItem(pos=np.array([[0,0,0], [0,0,axis_length]]), color=(0,0,1,1), width=line_thickness)
        self.w_3d.addItem(self.z_axis)
        self.axes_items.append(self.z_axis)
        
        self.d_3d.addWidget(self.w_3d)

        # Controls (Empty for now)
        self.w_controls = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Controls Section (Placeholder)"))
        layout.addStretch()
        self.w_controls.setLayout(layout)
        self.d_controls.addWidget(self.w_controls)

        # --- RIGHT PANEL CONTENT (6 CHARTS) ---
        self.w_charts = pg.GraphicsLayoutWidget()
        self.d_charts.addWidget(self.w_charts)

        # Create 6 plots in a 2-column x 3-row grid
        # Col 1: Accelerometer, Col 2: Gyroscope
        self.plots = []
        self.curves = []
        
        # Titles
        titles = [
            ("Acc X", "Acc Y", "Acc Z"),
            ("Gyro X", "Gyro Y", "Gyro Z")
        ]
        
        # We want:
        # Acc X | Gyro X
        # Acc Y | Gyro Y
        # Acc Z | Gyro Z
        
        for row in range(3):
            row_plots = []
            for col in range(2):
                title = titles[col][row]
                # Add plot to layout
                p = self.w_charts.addPlot(row=row, col=col, title=title)
                p.showGrid(x=True, y=True)
                # Create a curve
                c = p.plot(pen=(col+1, 3)) # Different color for Acc vs Gyro
                
                self.plots.append(p)
                self.curves.append(c)
            
        # Data buffers for 6 channels
        self.history_length = 200
        self.data_buffer = np.zeros((6, self.history_length))

        # --- DATA STREAM SETUP ---
        if not SIMULATION_MODE:
            try:
                self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
                print(f"Connected to {SERIAL_PORT}")
            except Exception as e:
                print(f"Serial Error: {e}")
                print("Switching to SIMULATION_MODE")
                SIMULATION_MODE = True

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(20) # 50 Hz update rate
        
        self.sim_t = 0

    def update(self):
        new_data = np.zeros(6)
        px, py, pz = 0, 0, 0 # Initialize position variables

        if SIMULATION_MODE:
            self.sim_t += 0.1
            # Simulate Acc (X, Y, Z) - sinusoidal
            new_data[0] = np.sin(self.sim_t) * 9.81  # Acc X (simulating +/- 1g)
            new_data[1] = np.cos(self.sim_t) * 9.81  # Acc Y
            new_data[2] = -9.81 + np.sin(self.sim_t * 0.5) * 2  # Acc Z (gravity -9.81)
            
            # Simulate Gyro (X, Y, Z) - noisy, in deg/s
            new_data[3] = np.random.normal(0, 5) # Gyro X
            new_data[4] = np.random.normal(0, 5) # Gyro Y
            new_data[5] = 20 + np.random.normal(0, 2) # Gyro Z (constant rotation + noise)
            
            # Simulate Movement in Space (Figure-8 pattern)
            px = np.sin(self.sim_t * 0.5) * 10
            py = np.cos(self.sim_t * 0.5) * 10
            pz = np.sin(self.sim_t) * 2
            
        else:
            if self.ser.in_waiting:
                try:
                    # Expecting CSV: "ax,ay,az,gx,gy,gz\n"
                    line = self.ser.readline().decode().strip()
                    parts = line.split(',')
                    if len(parts) == 6:
                        new_data = np.array([float(x) for x in parts])
                    else:
                        # Malformed line
                        return 
                except Exception as e:
                    print(f"Parse Error: {e}")
                    return
            else:
                return # No new data

        # Update Buffers
        # Roll buffer back
        self.data_buffer = np.roll(self.data_buffer, -1, axis=1)
        # Insert new data at the end
        self.data_buffer[:, -1] = new_data

        # Update Curves
        # We stored curves in a flattened list: 
        # [AccX, GyroX, AccY, GyroY, AccZ, GyroZ] due to the loop order?
        # Wait, loop was:
        # for row:
        #   for col:
        #     append
        # So list is: [Row0Col0, Row0Col1, Row1Col0, Row1Col1, Row2Col0, Row2Col1]
        # Which corresponds to: [AccX, GyroX, AccY, GyroY, AccZ, GyroZ]
        
        # Our data buffer is 0..5. 
        # Let's map them correctly:
        # Buffer Indices: 0=AccX, 1=AccY, 2=AccZ, 3=GyroX, 4=GyroY, 5=GyroZ
        
        # Curve List Indices:
        # 0: AccX (Row0, Col0) -> Data 0
        # 1: GyroX (Row0, Col1) -> Data 3
        # 2: AccY (Row1, Col0) -> Data 1
        # 3: GyroY (Row1, Col1) -> Data 4
        # 4: AccZ (Row2, Col0) -> Data 2
        # 5: GyroZ (Row2, Col1) -> Data 5
        
        mapping = [0, 3, 1, 4, 2, 5]
        
        for i, curve in enumerate(self.curves):
            data_index = mapping[i]
            curve.setData(self.data_buffer[data_index])

        # --- 3. CALCULATE ORIENTATION (Pitch, Roll, Yaw) ---
        ax, ay, az = new_data[0], new_data[1], new_data[2]
        gx, gy, gz = new_data[3], new_data[4], new_data[5]

        # Calculate dt for integration
        current_time = time.time()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time

        # --- Pitch & Roll (Accelerometer) ---
        # Calculate magnitude of acceleration in YZ plane
        acc_magnitude_yz = math.sqrt(ay*ay + az*az)
        
        pitch_rad = math.atan2(-ax, acc_magnitude_yz) if acc_magnitude_yz != 0 else 0
        roll_rad  = math.atan2(ay, az) if az != 0 else 0
        
        pitch = math.degrees(pitch_rad)
        roll  = math.degrees(roll_rad)

        # --- Yaw (Gyro Integration) ---
        self.current_yaw += gz * dt
        yaw = self.current_yaw
        yaw_rad = math.radians(yaw)

        # --- 4. POSITION PHYSICS (Double Integration) ---
        # Rotation Matrix construction (Yaw-Pitch-Roll sequence)
        
        # Precompute sines and cosines
        c_y, s_y = math.cos(yaw_rad), math.sin(yaw_rad)
        c_p, s_p = math.cos(pitch_rad), math.sin(pitch_rad)
        c_r, s_r = math.cos(roll_rad), math.sin(roll_rad)
        
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
               
        # Remove Gravity (assuming World Z is Up, and Gravity is -9.81 relative to that)
        az_w_linear = az_w - 9.81
        
        # Deadzone (Noise Reduction)
        if abs(ax_w) < 0.5: ax_w = 0
        if abs(ay_w) < 0.5: ay_w = 0
        if abs(az_w_linear) < 0.5: az_w_linear = 0

        # Integrate Acceleration -> Velocity
        self.vx += ax_w * dt
        self.vy += ay_w * dt
        self.vz += az_w_linear * dt
        
        # Damping/Friction (CRITICAL to stop it flying away infinitely due to noise)
        if ENABLE_POSITION_DAMPING:
            damping_factor = 0.95
            self.vx *= damping_factor
            self.vy *= damping_factor
            self.vz *= damping_factor
        
        # Integrate Velocity -> Position
        self.px += self.vx * dt
        self.py += self.vy * dt
        self.pz += self.vz * dt
        
        # If in simulation mode, we OVERRIDE this physics position with the figure-8 for demo purposes
        # unless we want to test the physics engine with simulated data (which is static/boring).
        # Let's use the calculated px, py, pz for REAL mode, but keep the override for SIM mode
        # if desired. 
        
        # Logic: If px, py, pz were set by SIMULATION block (Figure-8), use them.
        # But wait, we initialized them to 0 at the top.
        # Let's check: 
        if SIMULATION_MODE:
            # Re-apply the figure-8 logic if we want the "demo" look, 
            # OR comment this out to test the double-integration on simulated data (which will drift).
            # Given the user wants "Double Integration", let's use the PHYSICS calculated values 
            # BUT the simulated input (sine wave) doesn't have linear acceleration, only gravity rotation.
            # So the physics engine will result in 0 movement.
            # To keep the visual interesting, let's revert to the Figure-8 for SIMULATION.
            px = np.sin(self.sim_t * 0.5) * 10
            py = np.cos(self.sim_t * 0.5) * 10
            pz = np.sin(self.sim_t) * 2
        else:
            # Real Mode: Use the Physics Integrated values
            px, py, pz = self.px, self.py, self.pz

        for axis_item in self.axes_items:
            axis_item.resetTransform()
            axis_item.translate(px, py, pz) # Move the object
            axis_item.rotate(yaw,   0, 0, 1) # Rotate around Z
            axis_item.rotate(pitch, 0, 1, 0) # Rotate around Y
            axis_item.rotate(roll,  1, 0, 0) # Rotate around X

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # --- DARK PALETTE SETUP ---
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
    # --------------------------

    dash = Dashboard()
    dash.show()
    sys.exit(app.exec_())
