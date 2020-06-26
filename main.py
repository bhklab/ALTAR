import sys
from app.gui import MainWindow as mw
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QProgressBar, QMenu)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QThread, QEvent

from app.authentication_ui import AuthenticationUI
from app.labelling_ui import LabelUI
from app.settings_ui import SettingsUI



class MainWindow(QMainWindow):
    """docstring for MainWindow."""

    def __init__(self, parent=None):
        super(MainWindow, self).__init__()

        # Define the distance from top left of screen
        # (first two ints), x,y size of windows (last two ints)
        self.setGeometry(300, 400, 1000, 700)
        self.setStyleSheet(open('app/style.css').read())

        # Initialize the authentication window
        self.auth_widget = AuthenticationUI(parent=self)

        # Set the current widget to the authentication window
        # When the user sucessfully authenticates, auth_widget will call
        # _on_successful_login
        self.setCentralWidget(self.auth_widget)



    def _on_successful_login(self, sftp_client) :
        """ This function is called by the AuthenticationUI widget when
            the user successfully logs on to the remote machine.
        Parameters :
            sftp_client :
                The SFTP client returned by paramiko after successfully
                authenticating the user.
        Opens the labelling interface and loads the first image.
        """
        self.sftp = sftp_client

        # Remove the authentication widget
        QWidget().setLayout(self.auth_widget.layout())

        # Initialize the labelling widget
        self.label_widget = LabelUI(parent=self)
        self.setCentralWidget(self.label_widget)
        self.label_widget.initUI()
        self.label_widget.initLoading()


    def closeEvent(self, event) :
        """ This function is called when the app closes.
        Close sftp connections and exit cleanly
        """
        try :
            # Save results
            self.app_functions.exit_app()
            # Close sftp
            self.sftp.close()
        except : # Application is still on login window
            pass


# Initialize an app window and the app itself
app = QApplication(sys.argv)
main = MainWindow()
# main = mw()
main.show()


# Start the event loop
sys.exit(app.exec_())
