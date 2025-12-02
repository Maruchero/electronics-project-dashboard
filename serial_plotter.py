import sys
import serial
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# --- CONFIGURATION ---
USE_REAL_SERIAL = True # Set to True when your STM32 is plugged in
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200
# ---------------------

app = QApplication(sys.argv)

# Create the Window
win = pg.GraphicsLayoutWidget(show=True, title="STM32 Real-Time Data")
p1 = win.addPlot(title="Sensor Data")
curve = p1.plot(pen='y') # Yellow line

# Data buffer (store last 100 points)
data_buffer = np.zeros(100)
ptr = 0

if USE_REAL_SERIAL:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

def update():
    global data_buffer, ptr
    
    val = 0
    if USE_REAL_SERIAL:
        if ser.in_waiting:
            try:
                line = ser.readline().decode().strip()
                val = float(line.split(',')[0]) # Assume format: "123.45\n"
            except:
                return
    else:
        # Simulation: Generate a sine wave
        val = np.sin(ptr / 10) 

    # Shift data and add new value
    data_buffer[:-1] = data_buffer[1:]
    data_buffer[-1] = val
    
    # Update plot
    curve.setData(data_buffer)
    ptr += 1

timer = QTimer()
timer.timeout.connect(update)
timer.start(10) # Update every 10ms

if __name__ == '__main__':
    sys.exit(app.exec_())