from PyQt5.QtWidgets import (QApplication, QMainWindow, QLineEdit, QWidget,
                             QPushButton, QHBoxLayout, QVBoxLayout, QLabel,
                             QProgressBar, QMenu)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QThread, QEvent

import paramiko
from getpass import getpass





class AuthenticateThread(QThread) :
    notifyProgress = pyqtSignal(list)

    def run(self) :
        pass



class AuthenticationUI(QWidget) :
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
        self.init_authentiation()



    ## -- AUTHENTICATION -- ##
    def init_authentiation(self) :
        """ The authentication window UI """
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
        submit_button.clicked.connect(lambda: self.authenticate(user, pw))
        pw.setEchoMode(QLineEdit.Password)
        user.setPlaceholderText("Username")
        pw.setPlaceholderText("Password")

        progress = QHBoxLayout()
        self.message = QLabel("Enter your H4H username and password")
        self.icon = QLabel("")
        progress.addWidget(self.message)
        progress.addWidget(self.icon)
        progress.addStretch()

        # Progress bar
        # self.progressBar = QProgressBar(self)
        # self.progressBar.setText("Loading Images")

        # Prompt user for their h4h cridentials
        vbox.addStretch()
        vbox.addLayout(progress)
        vbox.addWidget(user)
        vbox.addWidget(pw)
        vbox.addWidget(submit_button)
        # vbox.addWidget(self.progressBar)
        vbox.addStretch()
        self.setLayout(vbox)


    def setup_remote(self, username, password) :
        # Get the remote host and port from settings
        host = str(self.parent.settings_dict["Host"])
        port = int(self.parent.settings_dict["Port"])
        client = paramiko.SSHClient()     # Create SFTP client
        client.load_system_host_keys()
        client.connect(host, port=port,   # Authenticate
                       username=username, password=password)
        sftp_client = client.open_sftp()  # Open connection to remote

        return sftp_client



    def authenticate(self, user_widget, pass_widget) :
        try :
            sftp = self.setup_remote(user_widget.text(), pass_widget.text())
            # Call the MainWindow's function to proceed to next widget
            self.parent._on_successful_login(sftp)
        except paramiko.ssh_exception.AuthenticationException :
            # Clear fields and add message
            user_widget.clear()
            pass_widget.clear()
            self.message.setText("Enter your H4H username and password\n" +
                                 "Authentication unsuccessful.")
    ## -- ################ -- ##
