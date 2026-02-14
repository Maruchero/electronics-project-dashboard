import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout

class MagnetometerView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.w_charts = pg.GraphicsLayoutWidget()
        self.layout.addWidget(self.w_charts)

        self.plots = []
        self.curves = []
        
        titles = ["Mag X (North)", "Mag Y (East)", "Mag Z (Down)"]
        
        for row in range(3):
            title = titles[row]
            p = self.w_charts.addPlot(row=row, col=0, title=title)
            p.showGrid(x=True, y=True)
            p.setLabel('left', 'Field', units='Gauss')
            
            c = p.plot(pen='c') 
            
            self.plots.append(p)
            self.curves.append(c)
            
        self.history_length = 200
        self.data_buffer = np.zeros((3, self.history_length))

    def update_view(self, mag_data):
        """
        Updates the 3 plots with new magnetometer data.
        mag_data: A numpy array of 3 floats (mx, my, mz).
        """
        self.data_buffer = np.roll(self.data_buffer, -1, axis=1)
        self.data_buffer[:, -1] = mag_data

        for i, curve in enumerate(self.curves):
            curve.setData(self.data_buffer[i])
