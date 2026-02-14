import sys
import serial
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

USE_REAL_SERIAL = True
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200

app = QApplication(sys.argv)

win = pg.GraphicsLayoutWidget(show=True, title="STM32 Real-Time Data")
p1 = win.addPlot(title="Sensor Data")
curve = p1.plot(pen='y')

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
                val = float(line.split(',')[0])
            except:
                return
    else:
        val = np.sin(ptr / 10) 

    data_buffer[:-1] = data_buffer[1:]
    data_buffer[-1] = val
    
    curve.setData(data_buffer)
    ptr += 1

timer = QTimer()
timer.timeout.connect(update)
timer.start(10)

if __name__ == '__main__':
    sys.exit(app.exec_())
