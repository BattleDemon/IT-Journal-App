''' ----- Imports ----- '''
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QUrl, Qt
from PyQt6.uic import loadUi
import os
#import tkinter as tk
import json

import sys


app = QApplication(sys.argv)

''' ----- Get Screen Size ----- '''
# Create a Tkinter window (it won't be displayed)
#root = tk.Tk()

# Get the screen width and height in pixels
#screen_width = root.winfo_screenwidth()
#screen_height = root.winfo_screenheight()

# Destroy the root window after getting the information
#root.destroy()

screen_width = 1920
screen_height = 1080


''' ----- Main Class -----'''
class JournalApp(QMainWindow):
    def __init__(self):
        super(JournalApp, self).__init__()

        # Window Settings
        self.window_pos_x = int((screen_width / 2) - 600)
        self.window_pos_y = int((screen_height / 2) + 300)

        self.setWindowTitle("Journal App")
        self.setGeometry(self.window_pos_x, 100, 800, 600)

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(self.date_picker.calendarWidget().selectedDate())
        self.layout.addWidget(self.date_picker)

        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)

        # Variables
        self.entries = []

        self.show() # Allows the user to actually see the window
         
        # Load Settings and Entries
        #self.load_settings()
        self.load_entries()
        self.apply_theme()  

    ''' ----- Load and Save Functions ----- '''

    def load_settings(self):
        settings_path = os.path.join(self.data_dir, "settings.json")
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                settings = json.load(f)
                self.theme = settings.get("theme")
        else:
            self.save_settings()
    
    def save_settings(self):
        settings_path = os.path.join(self.data_dir, "settings.json")
        settings = {
            "theme": self.theme
        }
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=4)  

    def load_entries(self):
        entries_path = os.path.join(self.data_dir, "entries.json")
        if os.path.exists(entries_path):
            with open(entries_path, "r") as f:
                self.entries = json.load(f)
        else:
            self.entries = []
            self.save_entries()

    def save_entries(self):
        entries_path = os.path.join(self.data_dir, "entries.json")
        with open(entries_path, "w") as f:
            json.dump(self.entries, f, indent=4)

    ''' ----- Theme Application ----- '''
    def apply_theme(self):
        pass


    
''' ----- Journal Entry Class ----- '''
class JournalEntry(QWidget):
    def __init__(self, title, content, date):
        super(JournalEntry, self).__init__()
        self.title = title
        self.content = content
        self.date = date

main = JournalApp() 

print("Hello, World!") #Hello World for good luck

sys.exit(app.exec()) 