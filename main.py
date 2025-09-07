''' ----- Imports ----- '''
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QUrl, Qt
from PyQt6.uic import loadUi
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QTextCharFormat, QBrush, QColor
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

THEMES = {
    "Light": {
        "window_bg": "#ffffff",
        "text_color": "#000000",
        "button_bg": "#f0f0f0",
        "button_text": "#000000",
        "highlight": "#add8e6"
    },
    "Dark": {
        "window_bg": "#2e2e2e",
        "text_color": "#ffffff",
        "button_bg": "#3a3a3a",
        "button_text": "#ffffff",
        "highlight": "#4a90e2"
    },
    "Dracula": {
        "window_bg": "#282a36",
        "text_color": "#f8f8f2",
        "button_bg": "#44475a",
        "button_text": "#f8f8f2",
        "highlight": "#bd93f9"
    },
    "Solarized Dark": {
        "window_bg": "#002b36",
        "text_color": "#839496",
        "button_bg": "#073642",
        "button_text": "#93a1a1",
        "highlight": "#268bd2"
    },
    "Monokai": {
        "window_bg": "#272822",
        "text_color": "#f8f8f2",
        "button_bg": "#3e3d32",
        "button_text": "#f8f8f2",
        "highlight": "#f92672"
    },
    "Ocean": {
        "window_bg": "#1a2b4c",
        "text_color": "#d6eaff",
        "button_bg": "#264d73",
        "button_text": "#d6eaff",
        "highlight": "#4da6ff"
    },
    "Forest": {
        "window_bg": "#1b2e1b",
        "text_color": "#e0f5e0",
        "button_bg": "#2a442a",
        "button_text": "#e0f5e0",
        "highlight": "#66cc66"
    },
    "Cyberpunk": {
        "window_bg": "#0f0f1c",
        "text_color": "#ff00ff",
        "button_bg": "#1a1a2e",
        "button_text": "#00ffff",
        "highlight": "#00ffff"
    },
    "Matrix": {
        "window_bg": "#000000",
        "text_color": "#00ff00",
        "button_bg": "#0a0a0a",
        "button_text": "#00ff00",
        "highlight": "#007700"
    },
    "Paper": {
        "window_bg": "#fafafa",
        "text_color": "#333333",
        "button_bg": "#e0e0e0",
        "button_text": "#333333",
        "highlight": "#007acc"
    }
}


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

        self.entry_page = QWidget()
        entry_layout = QVBoxLayout(self.entry_page)

        self.entry_title_label = QLabel("No entry loaded")
        entry_layout.addWidget(self.entry_title_label)

        self.text_edit = QTextEdit()
        entry_layout.addWidget(self.text_edit)

        self.save_btn = QPushButton("Save Entry")
        entry_layout.addWidget(self.save_btn)


        self.stacked.addWidget(self.entry_page)

        self.theme_selector = QComboBox()
        self.theme_selector.addItems(THEMES.keys())
        sidebar_layout.addWidget(self.theme_selector)

        self.theme_selector.currentTextChanged.connect(self.apply_theme)

        # Signals
        self.to_calendar_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.calendar_page))
        self.to_entry_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.entry_page))
        self.save_btn.clicked.connect(self.save_entry)
        self.calendar.selectionChanged.connect(self.load_entry_for_date)
        self.entry_list.itemClicked.connect(self.load_entry_from_list)

        # Data
        self.entries = []
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)

        self.load_settings()
        
        self.apply_theme(self.current_theme)

        self.load_entries()
        
        self.refresh_entry_list()

        self.show()

    ''' ----- Load and Save Functions ----- '''

    def save_settings(self):
        settings_path = os.path.join(self.data_dir, "settings.json")
        settings = {
            "theme": self.current_theme
        }
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=4)

    def load_settings(self):
        settings_path = os.path.join(self.data_dir, "settings.json")
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                settings = json.load(f)
                self.apply_theme(settings.get("theme"))
        else:
            self.apply_theme("Dark")
            self.save_settings()

    def load_entries(self):
        entries_path = os.path.join(self.data_dir, "entries.json")
        if os.path.exists(entries_path):
            with open(entries_path, "r") as f:
                self.entries = json.load(f)
        else:
            self.entries = []
            self.save_entries()
        self.highlight_entries()

    def save_entries(self):
        entries_path = os.path.join(self.data_dir, "entries.json")
        with open(entries_path, "w") as f:
            json.dump(self.entries, f, indent=4)

    ''' ----- Theme Application ----- '''
    def apply_theme(self, theme_name):
        theme = THEMES.get(theme_name, THEMES["Dark"])
        self.current_theme = theme_name

        # Apply to main window
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {theme['window_bg']};
                color: {theme['text_color']};
            }}
            QPushButton {{
                background-color: {theme['button_bg']};
                color: {theme['button_text']};
                border-radius: 5px;
                padding: 4px;
            }}
            QPushButton:hover {{
                background-color: {theme['highlight']};
            }}
            QTextEdit {{
                background-color: {theme['window_bg']};
                color: {theme['text_color']};
                border: 1px solid {theme['highlight']};
            }}
            QListWidget {{
                background-color: {theme['window_bg']};
                color: {theme['text_color']};
                border: 1px solid {theme['highlight']};
            }}
        """)

        # Re-highlight calendar entries with theme color
        self.highlight_entries()
        self.save_settings()

    def save_entry(self):
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        content = self.text_edit.toPlainText()

        # Check if entry already exists
        existing = next((e for e in self.entries if e["date"] == date), None)

        if existing:
            existing["content"] = content
        else:
            # Ask for a title if new entry
            title, ok = QInputDialog.getText(self, "Entry Title", "Enter a title for this entry:")
            if not ok or not title.strip():
                title = "Untitled"
            self.entries.append({"date": date, "title": title.strip(), "content": content})

        self.save_entries()
        self.refresh_entry_list()
        self.highlight_entries()
        
    def refresh_entry_list(self):
        self.entry_list.clear()
        for entry in sorted(self.entries, key=lambda x: x["date"]):
            preview = entry["content"][:30].replace("\n", " ")
            self.entry_list.addItem(f"{entry['date']} - {preview}")

    def load_entry_from_list(self, item):
        date = item.text().split(" - ")[0]
        entry = next((e for e in self.entries if e["date"] == date), None)
        if entry:
            self.text_edit.setText(entry["content"])
            # Update calendar selection too
            self.calendar.setSelectedDate(QDate.fromString(date, "yyyy-MM-dd"))
            self.stacked.setCurrentWidget(self.entry_page)

    def load_entry_for_date(self):
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        entry = next((e for e in self.entries if e["date"] == date), None)

        if entry:
            self.text_edit.setText(entry["content"])
            self.entry_title_label.setText(f"{entry['title']} - {date}")
        else:
            self.text_edit.clear()
            self.entry_title_label.setText(f"New Entry - {date}")

    def highlight_entries(self):
        # Clear old formatting
        self.calendar.setDateTextFormat(self.calendar.minimumDate(), QTextCharFormat())

        # Use theme highlight
        theme = THEMES.get(self.current_theme, THEMES["Dark"])
        has_entry_format = QTextCharFormat()
        has_entry_format.setBackground(QBrush(QColor(theme["highlight"])))

        for entry in self.entries:
            date = QDate.fromString(entry["date"], "yyyy-MM-dd")
            self.calendar.setDateTextFormat(date, has_entry_format)


main = JournalApp() 

print("Hello, World!") #Hello World for good luck

sys.exit(app.exec()) 