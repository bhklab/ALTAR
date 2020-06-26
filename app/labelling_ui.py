from PyQt5.QtWidgets import (QLineEdit, QWidget, QPushButton, QHBoxLayout,
                             QVBoxLayout, QLabel, QProgressBar)
from PyQt5.QtCore import pyqtSignal, QThread
import pyqtgraph as pg
import os
import re

import numpy as np
import paramiko

from app.label import LabelImageApp





class DownloadThread(QThread):
    """A Thread dedicated to a progress bar widget to show
       image download progress."""
    def __init__(self, sftp, path_to_remote_img, buffer):
        self.path_to_remote_img = path_to_remote_img
        self.sftp = sftp
        self.buffer = buffer
        super().__init__()
    # Send a pyqtSignal with :
    # list = [number of bits transferred, number of bits to transfer]
    notifyProgress = pyqtSignal(list)

    def run(self) :
        # Download the Image
        self.sftp.get(self.path_to_remote_img, "tmp.npy", callback=self.status_bar)
        self.buffer.append((np.load("tmp.npy"), re.search( "([0-9]+)_img.npy",self.path_to_remote_img).group(1)))
        os.remove("tmp.npy")

    def status_bar(self, packets_sent, packets_to_send) :
        l = [packets_sent, packets_to_send]

        # Notify the progress bar widget of download progress
        self.notifyProgress.emit(l)



class LabelUI(QWidget):
    def __init__(self, parent=None):
        super(LabelUI, self).__init__(parent)
        self.parent = parent
        self.sftp = parent.sftp

        # Define the distance from top left of screen
        # (first two ints), x,y size of windows (last two ints)
        # self.setGeometry(300, 400, 1000, 700)
        self.setStyleSheet(open('app/style.css').read())

        # Enable pressing enter key to do stuff
        self.keyPressed.connect(self.on_key_press)


    def initUI(self) :
        """ The main Application UI """
        self.mode = "label"

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
        s_button.clicked.connect(lambda: self.on_click(result="s"))
        w_button.clicked.connect(lambda: self.on_click(result="w"))
        n_button.clicked.connect(lambda: self.on_click(result="n"))

        hbox.addStretch()
        hbox.addWidget(s_button)
        hbox.addWidget(w_button)
        hbox.addWidget(n_button)
        hbox.setSpacing(0)
        hbox.addStretch()
        # --- ###### --- #

        # --- Plot specific patient --- #
        self.plt_patient_box = QHBoxLayout()
        patient_input = QLineEdit()
        patient_input.setPlaceholderText("Type Specific Patient ID")
        patient_button = QPushButton("Plot Patient")
        patient_button.setObjectName("input")
        patient_button.clicked.connect(lambda:
                     self.plt_specific_patient(patient_input.text()))
        self.plt_patient_box.addWidget(patient_button)
        self.plt_patient_box.addWidget(patient_input)
        # self.plt_patient_box.setSpacing(4)
        # --- ################### --- #

        # ---  TEXT   --- #
        self.text_header = QLabel("")
        self.text_header.setAlignment(Qt.AlignCenter)
        vbox.addWidget(self.text_header)
        # --- ####### --- #

        # --- IMAGE --- #
        self.imageWidget = pg.ImageView()
        vbox.addWidget(self.imageWidget)
        # --- ----- --- #

        # Progress Bar #
        self.progressBar = QProgressBar(self)
        self.progressBar.setTextVisible(True)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)

        vbox.addLayout(hbox)
        vbox.addLayout(self.plt_patient_box)
        vbox.addWidget(self.progressBar)
        self.setLayout(vbox)


    def initLoading(self):
        self.buffer = []

        # Initialize the data
        print("Initializing data")
        self.app_functions = LabelImageApp(saving=True,
                                           img_widget=self.imageWidget,
                                           sftp_client=self.sftp)
        self.current_patient = self.app_functions.index
        self.patient_id = self.app_functions.label_df.loc[self.current_patient, "patient_id"]
        self.text_header.setText(f"Current Patient: {self.current_patient}/{self.patient_id}")

        # Load the first patient in the GUI
        self.loadImage(patientIndex = self.current_patient)
        self.update_display()


    def getPath(self, patientIndex = None, patientId = None):
        if(patientIndex != None):
            patientId = self.app_functions.label_df.loc[patientIndex, "patient_id"]
        file_name = str(patientId) + "_img.npy"
        return os.path.join(self.app_functions.img_path, file_name)


    def getNextImage(self):
        if(len(self.buffer) == 0 or self.patient_id != self.buffer[0][1]):
            self.buffer = []
            self.loadImage(patientId = self.patient_id)
        if(len(self.buffer) == 0):
           self.load.wait()
        image = self.buffer[0][0]
        self.buffer = self.buffer[1:]
        return image


    def loadImage(self, patientIndex = None, patientId = None):
        path = self.getPath(patientId = patientId, patientIndex = patientIndex)
        self.load = DownloadThread(self.sftp, path, self.buffer)
        self.load.notifyProgress.connect(self.onProgress)
        self.load.start()

        self.load.finished.connect(self.clear_progressBar)


    def clear_progressBar(self) :
        self.progressBar.setValue(0)
        self.progressBar.setFormat("")


    def plt_specific_patient(self, patient_id) :
        df = self.app_functions.label_df.copy()
        try :
            self.patient_id = patient_id
            self.current_patient = df[df["patient_id"] == patient_id].index[0]

            # Valid patient. Update display
            self.buffer = []
            self.loadImage(patientId = self.patient_id)
            self.update_display()
        except ValueError :
            # Invalid patient. Do nothing.
            return


    def on_click(self, result=None) :
        slice_index = self.imageWidget.currentIndex
        # Processes the result and updates the label DF
        self.app_functions.process_result(result,
                                          index=self.current_patient,
                                          slice=slice_index)
        # Move to next patient
        self.current_patient = self.current_patient + 1
        self.patient_id = self.app_functions.label_df.loc[self.current_patient, "patient_id"]

        # Plot the new patient in the GUI
        self.update_display()


    def update_display(self) :
        # Update Image widget
        print("Loading Image")
        self.display_img()
        print("Image transferred")
        # self.current_patient = self.current_patient + 1
        # self.patient_id = self.app_functions.label_df.loc[self.current_patient, "patient_id"]
        if (len(self.buffer) == 0):
            self.loadImage(patientIndex = self.current_patient+1)


    def display_img(self) :
        # Remove progress bar
        self.progressBar.setValue(0)
        self.progressBar.setFormat("")

        if(len(self.buffer) == 0):
           self.load.wait()
        image = self.getNextImage()
        image = image[:, 50:-175, 75:-75]

        # Convert the image to 16-bit integer
        image = image.astype(np.int16)
        # Normalize the image
        image = self.app_functions.normalize(image)

        self.imageWidget.setImage(image)

        # Update text header
        self.text_header.setText(f"Current patient: {self.current_patient}/{self.patient_id}")


    def onProgress(self, l) :
        percent_done = (l[0] / (l[0] + l[1])) * 100
        self.progressBar.setFormat("Loading Next Image (%d %%)" % (2 * percent_done))
        self.progressBar.setValue(2*percent_done)
