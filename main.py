''' ----- Imports ----- '''
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QUrl, Qt
from PyQt6.uic import loadUi
import os
import json

import sys


app = QApplication(sys.argv)

''' ----- Main Class -----'''
class JournalApp(QMainWindow):
    def __init__(self):
        super(JournalApp, self).__init__()

        # Settings

        # Variables
        self.entries = []

        

        self.show()


main = JournalApp

sys.exit(app.exec) 