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

from label import LabelImageApp


class MainWindow(QWidget):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Define the distance from top left of screen
        # (first two ints), x,y size of windows (last two ints)
        self.setGeometry(300, 400, 700, 500)
        self.setStyleSheet(open('style.css').read())

        # Open remote connection to H4H
        # If this is successful, initUI will be called
        self.init_authentiation()



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
        self.text_header = QLabel("")
        self.text_header.setAlignment(Qt.AlignCenter)
        vbox.addWidget(self.text_header)
        # --- ####### --- #


        # --- IMAGE --- #
        self.imageWidget = pg.ImageView()
        vbox.addWidget(self.imageWidget)
        # --- ----- --- #

        vbox.addLayout(hbox)
        self.setLayout(vbox)

        # Initialize the data
        print("Initializing data")
        self.app_functions = LabelImageApp(saving=True,
                                           img_widget=self.imageWidget,
                                           sftp_client=self.sftp)
        self.current_patient = self.app_functions.index
        self.text_header.setText(f"Current Patient: {self.current_patient}")

        # Load the first patient in the GUI
        self.update_display()



    def on_click(self, result=None) :
        slice_index = self.imageWidget.currentIndex
        # Processes the result and updates the label DF
        self.app_functions.process_result(result,
                                          index=self.current_patient,
                                          slice=slice_index)

        # Update current patient index
        self.current_patient = self.current_patient + 1

        # Plot the new patient in the GUI
        self.update_display()



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

        except :
            # self.initUI() # Dev mode only
            print("Authentication Unsuccessful")
            self.init_authentiation()
        self.initUI()


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
        # Load the new image and send to the graphing GUI
        remote_file = self.sftp.open(path)
        image = np.load(remote_file)
        image = image[:, 50:-175, 75:-75]

        # Convert the image to 16-bit integer
        image = image.astype(np.int16)
        # Normalize the image
        image = self.app_functions.normalize(image)

        self.imageWidget.setImage(image)

    def keyPressEvent(self, e):
        """ Handle key press events"""
        if e.key == 16777220 :
            # [Enter] key was hit
            if self.mode == "auth" :
                print("Authenticating")
            if self.mode == "label" :
                print("")

    def update_display(self) :
        patient_id = self.app_functions.label_df.loc[self.current_patient, "patient_id"]
        file_name = str(patient_id) + "_img.npy"
        img_path = os.path.join(self.app_functions.img_path, file_name)

        # Update Image widget
        self.load_img(img_path)

        # Update text header
        self.text_header.setText(f"Current patient: {self.current_patient}")

def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()

    try :
        sys.exit(app.exec_())
    except :
        # Save progress
        main.app_functions.exit_app()

        # Close GUI
        self.app.close()

        # Close python interpreter
        exit()

if __name__ == '__main__':
    main()
