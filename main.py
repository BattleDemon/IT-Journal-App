''' ----- Imports ----- '''
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QUrl, Qt
from PyQt6.uic import loadUi
import os
import tkinter as tk
import json

import sys


app = QApplication(sys.argv)

''' ----- Get Screen Size ----- '''
# Create a Tkinter root window (it won't be displayed)
root = tk.Tk()

# Get the screen width and height in pixels
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Destroy the root window after getting the information
root.destroy()


''' ----- Main Class -----'''
class JournalApp(QMainWindow):
    def __init__(self):
        super(JournalApp, self).__init__()

        # Window Settings
        self.window_pos_x = int((screen_width / 2) - 600)
        self.window_pos_y = int((screen_height / 2) + 300)

        self.setWindowTitle("Journal App")
        self.setGeometry(self.window_pos_x, 100, 800, 600)

        # Variables
        self.entries = []

        self.show() # Allows the user to actually see the window
         
        # Load Settings and Entries
        self.load_settings()
        self.load_entries()
        self.apply_theme()  

    ''' ----- Load and Save Functions ----- '''

    def load_settings(self):
        if os.path.exists("data/settings.json"):
            with open("data/settings.json", "r") as f:
                settings = json.load(f)
                self.theme = settings.get("theme")
        else:
            self.save_settings()
    
    def save_settings(self):
        settings = {
            "theme": self.theme
        }
        with open("data/settings.json", "w") as f:
            json.dump(settings, f, indent=4)  

    def load_entries(self):
        if os.path.exists("data/entries.json"):
            with open("data/entries.json", "r") as f:
                self.entries = json.load(f)
        else:
            self.entries = []
            self.save_entries()

    def save_entries(self):
        with open("data/entries.json", "w") as f:
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
print("Hello, World!")

sys.exit(app.exec()) 