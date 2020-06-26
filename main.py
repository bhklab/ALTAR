import sys
from app.gui import MainWindow
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)
main = MainWindow()
main.show()

try :
    sys.exit(app.exec_())
except :
    # Save progress
    main.app_functions.exit_app()

    # Close remote connections
    main.sftp.close()

    # Close GUI
    app.quit()

    # Close python interpreter
    sys.exit()
