from PyQt5.QtWidgets import (QLineEdit, QWidget, QPushButton, QLabel,
                             QFormLayout)
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QThread, QEvent
import os
import json


class SettingsUI(QWidget) :
    def __init__(self, parent=None, settings_file_path="settings.json"):
        super(SettingsUI, self).__init__(parent)

        self.parent = parent
        self.setStyleSheet(open('app/style.css').read())
        self.settings_file = settings_file_path

        self.init_ui()


    def init_ui(self):
        settings = self.parent.settings_dict

        # Populate settings form with settings
        self.fbox = QFormLayout()
        for key in settings :
            self.fbox.addRow(QLabel(key), QLineEdit(str(settings[key])))

        # Add save and cancel buttongs
        b1, b2 = QPushButton("Save"), QPushButton("Cancel")
        b1.setObjectName("login"), b2.setObjectName("login")
        b1.clicked.connect(self._on_save_click)
        b2.clicked.connect(self._on_cancel_click)
        self.fbox.addRow(b1, b2)
        self.setLayout(self.fbox)


    def _on_save_click(self) :
        settings_dict = {}
        # Read all text fields and save in settings.json
        for i in range(self.fbox.count()) :
            w = self.fbox.itemAt(i).widget()
            if type(w) is QLabel  :      # This is a settings key
                k = w.text()
            elif type(w) is QLineEdit  : # This is a settings value
                settings_dict[k] = w.text()
            else :                       # This is a button
                continue
        # Update the settings dict shared by all widgets
        self.parent.settings_dict = settings_dict
        # Save the settings in a JSON file
        with open(self.settings_file, 'w') as outfile:
            json.dump(settings_dict, outfile, indent=4)

        # Go back to previously active widget
        self.parent._on_close_settings()



    def _on_cancel_click(self) :
        # Do nothing and go back to previously active widget
        self.parent._on_close_settings()
