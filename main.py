from PyQt6.QtWidgets import *
from PyQt6.QtCore import QUrl, Qt
from PyQt6.uic import loadUi
import os

import sys

app = QApplication(sys.argv)

class JournalApp(QMainWindow):
    def __init__(self):
        super(JournalApp, self).__init__()



        self.show()



main = JournalApp

sys.exit(app.exec) 