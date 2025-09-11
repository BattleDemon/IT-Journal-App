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
    QListWidgetItem,
    QMessageBox
) # Import PyQt6 widgets i will use
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QTextCharFormat, QBrush, QColor, QFont
import json
import os
import sys

# /* ------ Screen and Theme Defaults ------ */
screen_width = 1920
screen_height = 1080

THEMES = json.load(open("themes.json", "r", encoding="utf-8"))

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

        # Entry list
        self.entry_list = QListWidget()
        sidebar_layout.addWidget(self.entry_list)

        # Delete button under entry list
        self.delete_btn = QPushButton("Delete Entry")
        self.delete_btn.clicked.connect(self.delete_entry)
        sidebar_layout.addWidget(self.delete_btn)

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

        # Rich text edit
        self.text_edit = QTextEdit()
        entry_layout.addWidget(self.text_edit)

        # Action buttons row (Save + Categories)
        actions_layout = QHBoxLayout()

        self.save_btn = QPushButton("Save Entry")
        actions_layout.addWidget(self.save_btn)

        self.categories_btn = QPushButton("🏷")
        self.categories_btn.setFixedSize(24, 24)
        self.categories_btn.clicked.connect(self.edit_categories)
        actions_layout.addWidget(self.categories_btn)

        entry_layout.addLayout(actions_layout)

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

        pinned = [e for e in self.entries if e.get("pinned")]
        others = [e for e in self.entries if not e.get("pinned")]

        pinned = sorted(pinned, key=lambda x: x["date"])
        others = sorted(others, key=lambda x: x["date"])

        def make_item(entry, pinned=False):
            cats = ", ".join(entry.get("categories", []))
            label = f"{'📌 ' if pinned else ''}{entry['date']} - {entry['title']} "
            if cats:
                label += f" [{cats}]"
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, entry["date"])
            return item

        for entry in pinned:
            self.entry_list.addItem(make_item(entry, pinned=True))

        for entry in others:
            self.entry_list.addItem(make_item(entry))


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
        # Clear only previously highlighted dates
        if not hasattr(self, "_highlighted_dates"):
            self._highlighted_dates = set()

        default_format = QTextCharFormat()
        for d in self._highlighted_dates:
            self.calendar.setDateTextFormat(d, default_format)
        self._highlighted_dates.clear()

        # Use theme highlight for normal entries
        theme = THEMES.get(self.current_theme, THEMES["Dark"])
        has_entry_format = QTextCharFormat()
        has_entry_format.setBackground(QBrush(QColor(theme["highlight"])))

        # Different color for pinned entries
        pinned_format = QTextCharFormat()
        pinned_format.setBackground(QBrush(QColor("#ffcc00")))

        # Reapply new highlights
        for entry in self.entries:
            date = QDate.fromString(entry["date"], "yyyy-MM-dd")
            if entry.get("pinned"):
                self.calendar.setDateTextFormat(date, pinned_format)
            else:
                self.calendar.setDateTextFormat(date, has_entry_format)
            self._highlighted_dates.add(date)



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

    def edit_categories(self):
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        entry = next((e for e in self.entries if e["date"] == date), None)
        if entry:
            current = ", ".join(entry.get("categories", []))
            text, ok = QInputDialog.getText(self, "Edit Categories", "Enter categories (comma-separated):", text=current)
            if ok:
                cats = [c.strip() for c in text.split(",") if c.strip()]
                entry["categories"] = cats
                self.save_entries()
                self.refresh_entry_list()

    def delete_entry(self):
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        entry = next((e for e in self.entries if e["date"] == date), None)

        if not entry:
            QMessageBox.information(self, "No Entry", "There is no entry for this date to delete.")
            return

        reply = QMessageBox.question(
            self,
            "Delete Entry",
            f"Are you sure you want to delete the entry for {date}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.entries = [e for e in self.entries if e["date"] != date]
            self.save_entries()
            self.refresh_entry_list()
            self.highlight_entries()
            self.text_edit.clear()
            self.entry_title_label.setText(f"Deleted Entry - {date}")


# /* ----- App entry point ----- */
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = JournalApp()
    print("Hello, World!")
    sys.exit(app.exec())