from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QHBoxLayout, QDialog, QVBoxLayout, QGridLayout, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os

class MainWindow(QWidget):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # self.imageWidget = pg.ImageView()
        # self.setCentralWidget(self.imageWidget)

        self.initUI()

    def initUI(self) :
        # --- WINDOW --- #
        self.setWindowTitle("Image Labelling")
        # Define the distance from top left of screen
        # (first two ints), x,y size of windows (last two ints)
        self.setGeometry(300, 400, 700, 500)

        hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        # --- ###### --- #

        # --- BUTTONS --- #
        s_button = QPushButton("Strong")
        w_button = QPushButton("Weak")
        n_button = QPushButton("None")
        s_button.setToolTip('Label this patient as having a strong artifact.')
        w_button.setToolTip('Label this patient as having a weak artifact.')
        n_button .setToolTip('Label this patient as having no artifacts.')
        hbox.addStretch()
        hbox.addWidget(s_button)
        hbox.addWidget(w_button)
        hbox.addWidget(n_button)
        hbox.addStretch()
        # --- ###### --- #

        # --- TEXT   --- #
        self.text_header = QLabel("Press [ENTER] to begin.")
        self.text_header.setAlignment(Qt.AlignCenter)
        vbox.addWidget(self.text_header)


        # --- IMAGE --- #
        self.imageWidget = pg.ImageView()
        vbox.addWidget(self.imageWidget)
        # --- ----- --- #


        vbox.addLayout(hbox)
        self.setLayout(vbox)



def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
