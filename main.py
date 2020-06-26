import sys
from app.gui import MainWindow
from PyQt5.QtWidgets import QApplication


# Initialize an app window and the app itself
app = QApplication(sys.argv)
main = MainWindow()
main.show()


# Start the event loop
sys.exit(app.exec_())
