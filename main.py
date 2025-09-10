# /* ------ Import Used Libraries ------ */
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QListWidget,
    QStackedWidget,
    QCalendarWidget,
    QLabel,
    QSpinBox,
    QTextEdit,
    QInputDialog,
    QComboBox,
    QListWidgetItem
)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QTextCharFormat, QBrush, QColor, QFont
import json
import os
import sys

# /* ------ Screen and Theme Defaults ------ */
screen_width = 1920
screen_height = 1080

THEMES = {
    "Light": {
        "window_bg": "#ffffff",
        "text_color": "#000000",
        "button_bg": "#f0f0f0",
        "button_text": "#000000",
        "highlight": "#add8e6",
    },
    "Dark": {
        "window_bg": "#2e2e2e",
        "text_color": "#ffffff",
        "button_bg": "#3a3a3a",
        "button_text": "#ffffff",
        "highlight": "#4a90e2",
    },
    "Dracula": {
        "window_bg": "#282a36",
        "text_color": "#f8f8f2",
        "button_bg": "#44475a",
        "button_text": "#f8f8f2",
        "highlight": "#bd93f9",
    },
    # A few more themes for variety
    "Monokai": {
        "window_bg": "#272822",
        "text_color": "#f8f8f2",
        "button_bg": "#3e3d32",
        "button_text": "#f8f8f2",
        "highlight": "#f92672",
    },
    "Paper": {
        "window_bg": "#fafafa",
        "text_color": "#333333",
        "button_bg": "#e0e0e0",
        "button_text": "#333333",
        "highlight": "#007acc",
    },
    "Solarized": {
        "window_bg": "#fdf6e3",
        "text_color": "#657b83",
        "button_bg": "#eee8d5",
        "button_text": "#657b83",
        "highlight": "#268bd2",
    },
    "Nord": {
        "window_bg": "#2e3440",
        "text_color": "#d8dee9",
        "button_bg": "#4c566a",
        "button_text": "#d8dee9",
        "highlight": "#88c0d0",
    },
    "Gruvbox": {
        "window_bg": "#282828",
        "text_color": "#ebdbb2",
        "button_bg": "#3c3836",
        "button_text": "#ebdbb2",
        "highlight": "#fe8019",
    },
    "Ocean Breeze" : {
        "window_bg" : "#e0f7fa",
        "text_color" : "#004d40",
        "button_bg" : "#80deea",
        "button_text" : "#ffffff",
        "highlight" : "#00bed4",
    },
    "Midnight Obsidian" : {
        "window_bg" : "#0a0a0a",
        "text_color" : "#e6e6e6",
        "button_bg" : "#1a1a1a",
        "button_text" : "#ffffff",
        "highlight" : "#00ffff",
    },
    "Vampire" : {
        "window_bg" : "#33001a",
        "text_color" : "#f0e68c",
        "button_bg" : "#8b0000",
        "button_text" : "#f5f5dc",
        "highlight" : "#dc143c",
    },
    "Crimson Shadow" : {
        "window_bg" : "#3b0000",
        "text_color" : "#ffe0e0",
        "button_bg" : "#800000",
        "button_text" : "#f5f5dc",
        "highlight" : "#dc143c",
    },
    "Emerald Dream" : {
        "window_bg" : "#002b00",
        "text_color" : "#d0f0c0",
        "button_bg" : "#004d00",
        "button_text" : "#f0fff0",
        "highlight" : "#00ff00",
    },
    "Royal Purple" : {
        "window_bg" : "#2e003e",
        "text_color" : "#e6ccff",
        "button_bg" : "#5e005e",
        "button_text" : "#f5f5dc",
        "highlight" : "#bf40bf",
    }
}


# /* ----- Main App Class ----- */
class JournalApp(QMainWindow):
    def __init__(self):
        # Initialise base QMainWindow
        super(JournalApp, self).__init__()
        self.setWindowTitle("Journal App")
        # Place window, keep size modest for testing
        self.setGeometry(200, 100, 1000, 600)

        # Central widget and main horizontal layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)

        # /* ----- Sidebar ----- */
        self.sidebar = QWidget()
        sidebar_layout = QVBoxLayout(self.sidebar)

        # Navigation toggles for calendar and entry views
        self.to_calendar_btn = QPushButton("Calendar View")
        self.to_entry_btn = QPushButton("Entry View")
        sidebar_layout.addWidget(self.to_calendar_btn)
        sidebar_layout.addWidget(self.to_entry_btn)

        # Entry list shown in sidebar
        self.entry_list = QListWidget()
        sidebar_layout.addWidget(self.entry_list)

        # Add sidebar to main layout, give it a smaller stretch
        main_layout.addWidget(self.sidebar, 1)

        # /* ----- Main content stack ----- */
        self.stacked = QStackedWidget()
        main_layout.addWidget(self.stacked, 3)

        # Calendar page setup
        self.calendar_page = QWidget()
        cal_layout = QVBoxLayout(self.calendar_page)
        self.calendar = QCalendarWidget()
        cal_layout.addWidget(self.calendar)
        self.stacked.addWidget(self.calendar_page)

        # Entry page setup
        self.entry_page = QWidget()
        entry_layout = QVBoxLayout(self.entry_page)

        # Header row: title at left, formatting on right
        header_layout = QHBoxLayout()
        self.entry_title_label = QLabel("No entry loaded")
        header_layout.addWidget(self.entry_title_label)
        header_layout.addStretch()

        self.pin_btn = QPushButton("📌")
        self.pin_btn.setCheckable(True)
        self.pin_btn.setFixedSize(24, 24)
        self.pin_btn.toggled.connect(self.toggle_pin)
        header_layout.addWidget(self.pin_btn)

        # Simple formatting controls
        self.bold_btn = QPushButton("B")
        self.bold_btn.setCheckable(True)
        self.bold_btn.setFixedSize(24, 24)
        self.bold_btn.clicked.connect(self.toggle_bold)
        header_layout.addWidget(self.bold_btn)

        self.italic_btn = QPushButton("I")
        self.italic_btn.setCheckable(True)
        self.italic_btn.setFixedSize(24, 24)
        self.italic_btn.clicked.connect(self.toggle_italic)
        header_layout.addWidget(self.italic_btn)

        self.font_size_box = QSpinBox()
        self.font_size_box.setRange(8, 48)
        self.font_size_box.setValue(12)
        self.font_size_box.setMaximumWidth(60)
        self.font_size_box.valueChanged.connect(self.change_font_size)
        header_layout.addWidget(self.font_size_box)

        entry_layout.addLayout(header_layout)

        # Rich text editor for entry bodies
        self.text_edit = QTextEdit()
        entry_layout.addWidget(self.text_edit)

        # Save button
        self.save_btn = QPushButton("Save Entry")
        entry_layout.addWidget(self.save_btn)

        self.stacked.addWidget(self.entry_page)

        # Theme selector in sidebar
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(THEMES.keys())
        sidebar_layout.addWidget(self.theme_selector)
        self.theme_selector.currentTextChanged.connect(self.apply_theme)

        # Wire up navigation and actions
        self.to_calendar_btn.clicked.connect(
            lambda: self.stacked.setCurrentWidget(self.calendar_page)
        )
        self.to_entry_btn.clicked.connect(
            lambda: self.stacked.setCurrentWidget(self.entry_page)
        )
        self.save_btn.clicked.connect(self.save_entry)
        self.calendar.selectionChanged.connect(self.load_entry_for_date)
        self.entry_list.itemClicked.connect(self.load_entry_from_list)

        # Data and storage setup
        self.entries = []
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)

        # Load last used settings and entries
        self.load_settings()
        # apply_theme will set current_theme and also save the settings
        self.apply_theme(self.current_theme)
        self.load_entries()
        self.refresh_entry_list()
        self.show()

    # /* ----- Settings IO ----- */
    def save_settings(self):
        settings_path = os.path.join(self.data_dir, "settings.json")
        settings = {"theme": self.current_theme}
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)

    def load_settings(self):
        settings_path = os.path.join(self.data_dir, "settings.json")
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                settings = json.load(f)
                theme_name = settings.get("theme", "Dark")
                self.apply_theme(theme_name)
                # Update combobox to match
                index = self.theme_selector.findText(theme_name)
                if index >= 0:
                    self.theme_selector.setCurrentIndex(index)
        else:
            self.apply_theme("Dark")
            self.save_settings()
            # Default select Dark
            index = self.theme_selector.findText("Dark")
            if index >= 0:
                self.theme_selector.setCurrentIndex(index)

    # /* ----- Entries IO ----- */
    def load_entries(self):
        entries_path = os.path.join(self.data_dir, "entries.json")
        if os.path.exists(entries_path):
            with open(entries_path, "r", encoding="utf-8") as f:
                self.entries = json.load(f)
        else:
            self.entries = []
            self.save_entries()
        # After loading ensure calendar highlights are up to date
        self.highlight_entries()

    def save_entries(self):
        entries_path = os.path.join(self.data_dir, "entries.json")
        with open(entries_path, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=4)

    # /* ----- Theme application ----- */
    def apply_theme(self, theme_name):
        theme = THEMES.get(theme_name, THEMES["Dark"])
        self.current_theme = theme_name

        # Set stylesheet across app using theme values
        self.setStyleSheet(
            f"""
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
        """
        )

        # Repaint calendar highlights to use new highlight colour
        self.highlight_entries()
        self.save_settings()

    # /* ----- Entry operations ----- */
    def save_entry(self):
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        content = self.text_edit.toHtml()

        # find existing entry for date
        existing = next((e for e in self.entries if e["date"] == date), None)

        if existing:
            existing["content"] = content
        else:
            # Prompt for a title when creating a new entry
            title, ok = QInputDialog.getText(self, "Entry Title", "Enter a title for this entry:")
            if not ok or not title.strip():
                title = "Untitled"
            self.entries.append({"date": date, "title": title.strip(), "content": content})

        self.save_entries()
        self.refresh_entry_list()
        self.highlight_entries()

    def refresh_entry_list(self):
        self.entry_list.clear()

        # Pinned entries first
        pinned = [e for e in self.entries if e.get("pinned")]
        others = [e for e in self.entries if not e.get("pinned")]

        # Sort both groups by date for now
        pinned = sorted(pinned, key=lambda x: x["date"])
        others = sorted(others, key=lambda x: x["date"])

        # Add pinned with marker
        for entry in pinned:
            item = QListWidgetItem(f"📌 {entry['date']} - {entry['title']} ")
            item.setData(Qt.ItemDataRole.UserRole, entry["date"])
            self.entry_list.addItem(item)

        # Add non-pinned
        for entry in others:
            item = QListWidgetItem(f"{entry['date']} - {entry['title']}")
            item.setData(Qt.ItemDataRole.UserRole, entry["date"])
            self.entry_list.addItem(item)

    def load_entry_from_list(self, item):
        date = item.text().split(" - ")[0]
        entry = next((e for e in self.entries if e["date"] == date), None)
        if entry:
            self.text_edit.setHtml(entry["content"])
            # keep calendar selection in sync
            self.calendar.setSelectedDate(QDate.fromString(date, "yyyy-MM-dd"))
            self.stacked.setCurrentWidget(self.entry_page)

    def load_entry_for_date(self):
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        entry = next((e for e in self.entries if e["date"] == date), None)

        if entry:
            self.text_edit.setHtml(entry["content"])
            self.entry_title_label.setText(f"{entry['title']} - {date}")
        else:
            self.text_edit.clear()
            self.entry_title_label.setText(f"New Entry - {date}")

    def highlight_entries(self):
        self.calendar.setDateTextFormat(self.calendar.minimumDate(), QTextCharFormat())

        theme = THEMES.get(self.current_theme, THEMES["Dark"])

        # Normal entry highlight
        normal_format = QTextCharFormat()
        normal_format.setBackground(QBrush(QColor(theme["highlight"])))

        # Pinned entry highlight (different color)
        pinned_format = QTextCharFormat()
        pinned_format.setBackground(QBrush(QColor("#FFD700")))  # Gold for pinned

        for entry in self.entries:
            date = QDate.fromString(entry["date"], "yyyy-MM-dd")
            if entry.get("pinned"):
                self.calendar.setDateTextFormat(date, pinned_format)
            else:
                self.calendar.setDateTextFormat(date, normal_format)

    # /* ----- Simple rich text helpers ----- */
    def toggle_bold(self):
        fmt = self.text_edit.currentCharFormat()
        fmt.setFontWeight(QFont.Weight.Bold if self.bold_btn.isChecked() else QFont.Weight.Normal)
        self.text_edit.setCurrentCharFormat(fmt)

    def toggle_italic(self):
        fmt = self.text_edit.currentCharFormat()
        fmt.setFontItalic(self.italic_btn.isChecked())
        self.text_edit.setCurrentCharFormat(fmt)

    def change_font_size(self, size):
        fmt = self.text_edit.currentCharFormat()
        fmt.setFontPointSize(size)
        self.text_edit.setCurrentCharFormat(fmt)

    def toggle_pin(self, checked):
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        entry = next((e for e in self.entries if e["date"] == date), None)
        if entry:
            entry["pinned"] = checked
            self.save_entries()
            self.refresh_entry_list()
            self.highlight_entries()


# /* ----- App entry point ----- */
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = JournalApp()
    print("Hello, World!")
    sys.exit(app.exec())