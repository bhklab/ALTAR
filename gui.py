from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QWidget, QPushButton, QHBoxLayout, QDialog, QVBoxLayout, QGridLayout, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os

import numpy as np
from paramiko import SSHClient
from getpass import getpass


class MainWindow(QWidget):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Define the distance from top left of screen
        # (first two ints), x,y size of windows (last two ints)
        self.setGeometry(300, 400, 700, 500)
        self.setStyleSheet(open('style.css').read())

        # Open remote connection to H4H
        # If this is successful,
        self.init_authentiation()

        # Initialize the user interface
        # self.initUI()

        # Plot Initial image
        # self.load_img("/cluster/home/carrowsm/temp_data/trg_data/1.npy")

    def initUI(self) :
        # --- WINDOW --- #
        self.setWindowTitle("Image Labelling")

        hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        # --- ###### --- #

        # --- BUTTONS --- #
        s_button = QPushButton("Strong")
        w_button = QPushButton("Weak")
        n_button = QPushButton("None")
        s_button.setToolTip('Label this patient as having a strong artifact.')
        w_button.setToolTip('Label this patient as having a weak artifact.')
        n_button.setToolTip('Label this patient as having no artifacts.')
        s_button.setObjectName("label-slice")
        w_button.setObjectName("label-slice-center")
        n_button.setObjectName("label-slice")
        s_button.clicked.connect(lambda: self.on_click(result="Strong"))
        w_button.clicked.connect(lambda: self.on_click(result="Weak"))
        n_button.clicked.connect(lambda: self.on_click(result="None"))

        hbox.addStretch()
        hbox.addWidget(s_button)
        hbox.addWidget(w_button)
        hbox.addWidget(n_button)
        hbox.setSpacing(0)
        hbox.addStretch()
        # --- ###### --- #

        # ---  TEXT   --- #
        self.text_header = QLabel("Press [ENTER] to begin.")
        self.text_header.setAlignment(Qt.AlignCenter)
        vbox.addWidget(self.text_header)
        # --- ####### --- #


        # --- IMAGE --- #
        self.imageWidget = pg.ImageView()
        vbox.addWidget(self.imageWidget)
        # --- ----- --- #

        vbox.addLayout(hbox)
        self.setLayout(vbox)


    def on_click(self, result=None) :
        print(result)

    def init_authentiation(self) :
        # We are currently in "authentication mode"
        self.mode = "auth"

        # Set GUI title
        self.setWindowTitle("H4H Login")

        # Create a widget with username and password fields
        vbox = QVBoxLayout()
        user = QLineEdit()
        pw = QLineEdit()
        submit_button = QPushButton("Login")
        submit_button.setObjectName("login")
        submit_button.clicked.connect(lambda: self.authenticate(user.text(), pw.text(), vbox))
        pw.setEchoMode(QLineEdit.Password)
        user.setPlaceholderText("Username")
        pw.setPlaceholderText("Password")

        # Prompt user for their h4h cridentials
        vbox.addStretch()
        vbox.addWidget(user)
        vbox.addWidget(pw)
        vbox.addWidget(submit_button)
        vbox.addStretch()
        self.setLayout(vbox)

    def authenticate(self, username, password, auth_widget) :
        # Remove the authentication widget
        QWidget().setLayout(auth_widget.layout())
        try :
            self.sftp = self.setup_remote(username, password)
            print("Authentication Successful")
            self.initUI()
        except :
            self.init_authentiation()
            print("Authentication Unsuccessful")


    def setup_remote(self, username, password) :
        host = "172.27.23.173"
        port = 22

        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(host, port=port,
                    username=username, password=password)
        sftp_client = ssh.open_sftp()
        return sftp_client

    def load_img(self, path) :
        remote_file = self.sftp_client.open(path)
        X = np.load(remote_file)
        print(X.shape)
        self.imageWidget.setImage(X)

    def keyPressEvent(self, e):
        """ Handle key press events"""
        if e.key == "16777220" :
            # Enter key was hit
            if self.mode == "auth" :
                print("Authenticating")
            if self.mode == "label" :
                print("")



def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
