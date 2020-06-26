from PyQt5.QtWidgets import (QApplication, QMainWindow, QLineEdit, QWidget,
                             QPushButton, QHBoxLayout, QVBoxLayout, QLabel,
                             QProgressBar, QMenu)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QThread, QEvent
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
import io
import re


import time


class SettingsUI(QWidget) :
    def __init__(self, parent=None):
        super(AuthenticationUI, self).__init__(parent)

        self.parent = parent

        # Define the distance from top left of screen
        # (first two ints), x,y size of windows (last two ints)
        # self.setGeometry(300, 400, 1000, 700)
        self.setStyleSheet(open('app/style.css').read())


        # Enable pressing enter key to do stuff
        # self.keyPressed.connect(self.on_key_press)

        # Open remote connection to H4H
        # If this is successful, initUI will be called
        # self.init_authentiation()
