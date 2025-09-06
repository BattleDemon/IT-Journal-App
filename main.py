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
        self.setWindowTitle("Journal App")
        self.setGeometry(200, 100, 1000, 600)

        # Main central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)

        # ----- Sidebar -----
        self.sidebar = QWidget()
        sidebar_layout = QVBoxLayout(self.sidebar)

        # Toggle buttons
        self.to_calendar_btn = QPushButton("Calendar View")
        self.to_entry_btn = QPushButton("Entry View")
        sidebar_layout.addWidget(self.to_calendar_btn)
        sidebar_layout.addWidget(self.to_entry_btn)

        # Entry list
        self.entry_list = QListWidget()
        sidebar_layout.addWidget(self.entry_list)

        # Add sidebar to main layout
        main_layout.addWidget(self.sidebar, 1)  # Sidebar smaller
        

        # ----- Stacked Widget (Main Content) -----
        self.stacked = QStackedWidget()
        main_layout.addWidget(self.stacked, 3)  # Main content bigger

        # Calendar page
        self.calendar_page = QWidget()
        cal_layout = QVBoxLayout(self.calendar_page)
        self.calendar = QCalendarWidget()
        cal_layout.addWidget(self.calendar)
        self.stacked.addWidget(self.calendar_page)

        # Entry page
        self.entry_page = QWidget()
        entry_layout = QVBoxLayout(self.entry_page)
        self.text_edit = QTextEdit()
        self.save_btn = QPushButton("Save Entry")
        entry_layout.addWidget(self.text_edit)
        entry_layout.addWidget(self.save_btn)
        self.stacked.addWidget(self.entry_page)

        # Signals
        self.to_calendar_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.calendar_page))
        self.to_entry_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.entry_page))
        self.save_btn.clicked.connect(self.save_entries)
        #self.calendar.selectionChanged.connect(self.load_entry_for_date)
        #self.entry_list.itemClicked.connect(self.load_entry_from_list)

        # Data
        self.entries = []
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.load_entries()
        #self.refresh_entry_list()

        self.show()

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