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
    QMessageBox,
    QCheckBox,
    QTimeEdit,
    QLineEdit,
    QTabWidget,
    QDateTimeEdit,
    QDateEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView
) # Import PyQt6 widgets i will use
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QTextCharFormat, QBrush, QColor, QFont
from PyQt6.QtCore import QTime, QDateTime
from datetime import datetime, timedelta 
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
        self.to_todo_btn = QPushButton("Todo List")
        sidebar_layout.addWidget(self.to_todo_btn)
        self.to_gym_btn = QPushButton("Gym Tracking")
        sidebar_layout.addWidget(self.to_gym_btn)

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

        # Todo List page setup
        self.todo_page = QWidget()
        todo_layout = QVBoxLayout(self.todo_page)

        # Todo list tabs
        self.todo_tabs = QTabWidget()
        todo_layout.addWidget(self.todo_tabs)

        # All Todos tab
        self.all_todos_tab = QWidget()
        all_todos_layout = QVBoxLayout(self.all_todos_tab)
        self.todo_list = QListWidget()
        all_todos_layout.addWidget(self.todo_list)
        self.todo_tabs.addTab(self.all_todos_tab, "All Todos")

        # Today's Todos tab
        self.today_todos_tab = QWidget()
        today_todos_layout = QVBoxLayout(self.today_todos_tab)
        self.today_todo_list = QListWidget()
        today_todos_layout.addWidget(self.today_todo_list)
        self.todo_tabs.addTab(self.today_todos_tab, "Today")

        # Overdue Todos tab
        self.overdue_todos_tab = QWidget()
        overdue_todos_layout = QVBoxLayout(self.overdue_todos_tab)
        self.overdue_todo_list = QListWidget()
        overdue_todos_layout.addWidget(self.overdue_todo_list)
        self.todo_tabs.addTab(self.overdue_todos_tab, "Overdue")

        # Add todo form
        todo_form_layout = QHBoxLayout()
        self.todo_input = QLineEdit()
        self.todo_input.setPlaceholderText("Enter new todo...")
        todo_form_layout.addWidget(self.todo_input)

        self.todo_date = QDateEdit()
        self.todo_date.setDate(QDate.currentDate())
        self.todo_date.setCalendarPopup(True)
        todo_form_layout.addWidget(self.todo_date)

        self.todo_time = QTimeEdit()
        self.todo_time.setTime(QTime(9, 0))
        todo_form_layout.addWidget(self.todo_time)

        self.add_todo_btn = QPushButton("Add Todo")
        self.add_todo_btn.clicked.connect(self.add_todo)
        todo_form_layout.addWidget(self.add_todo_btn)

        todo_layout.addLayout(todo_form_layout)

        # Todo actions
        todo_actions_layout = QHBoxLayout()
        self.complete_todo_btn = QPushButton("Complete")
        self.complete_todo_btn.clicked.connect(self.complete_todo)
        todo_actions_layout.addWidget(self.complete_todo_btn)

        self.edit_todo_btn = QPushButton("Edit")
        self.edit_todo_btn.clicked.connect(self.edit_todo)
        todo_actions_layout.addWidget(self.edit_todo_btn)

        self.delete_todo_btn = QPushButton("Delete")
        self.delete_todo_btn.clicked.connect(self.delete_todo)
        todo_actions_layout.addWidget(self.delete_todo_btn)

        todo_layout.addLayout(todo_actions_layout)

        self.stacked.addWidget(self.todo_page)

        self.gym_page = QWidget()
        gym_layout = QVBoxLayout(self.gym_page)

        # Workout session selection
        session_layout = QHBoxLayout()
        self.session_date = QDateEdit()
        self.session_date.setDate(QDate.currentDate())
        self.session_date.setCalendarPopup(True)
        session_layout.addWidget(QLabel("Workout Date:"))
        session_layout.addWidget(self.session_date)

        self.load_session_btn = QPushButton("Load Session")
        self.load_session_btn.clicked.connect(self.load_workout_sessions)
        session_layout.addWidget(self.load_session_btn)

        self.new_session_btn = QPushButton("New Session")
        self.new_session_btn.clicked.connect(self.create_new_session)
        session_layout.addWidget(self.new_session_btn)

        gym_layout.addLayout(session_layout)

        # Exercise input form
        exercise_form_layout = QHBoxLayout()
        self.exercise_input = QLineEdit()
        self.exercise_input.setPlaceholderText("Exercise name...")
        exercise_form_layout.addWidget(self.exercise_input)

        self.sets_input = QSpinBox()
        self.sets_input.setRange(1, 10)
        self.sets_input.setValue(3)
        exercise_form_layout.addWidget(QLabel("Sets:"))
        exercise_form_layout.addWidget(self.sets_input)

        self.add_exercise_btn = QPushButton("Add Exercise")
        self.add_exercise_btn.clicked.connect(self.add_exercise)
        exercise_form_layout.addWidget(self.add_exercise_btn)

        gym_layout.addLayout(exercise_form_layout)

        # Exercises table
        self.exercises_table = QTableWidget()
        self.exercises_table.setColumnCount(5)
        self.exercises_table.setHorizontalHeaderLabels(["Exercise", "Sets", "Reps", "Weight", "Actions"])
        self.exercises_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        gym_layout.addWidget(self.exercises_table)

        # Session actions
        session_actions_layout = QHBoxLayout()
        self.save_session_btn = QPushButton("Save Session")
        self.save_session_btn.clicked.connect(self.save_workout_session)
        session_actions_layout.addWidget(self.save_session_btn)

        self.delete_session_btn = QPushButton("Delete Session")
        self.delete_session_btn.clicked.connect(self.delete_workout_session)
        session_actions_layout.addWidget(self.delete_session_btn)

        gym_layout.addLayout(session_actions_layout)

        self.stacked.addWidget(self.gym_page)


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
        self.to_todo_btn.clicked.connect(
            lambda: self.stacked.setCurrentWidget(self.todo_page)
        )
        self.to_gym_btn.clicked.connect(
            lambda: self.stacked.setCurrentWidget(self.gym_page)
        )

        # Data and storage setup
        self.entries = []
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)

        self.todos = []
        self.load_todos()
        self.refresh_todo_lists()

        self.workout_sessions = []
        self.current_session = None
        self.load_workout_sessions()

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
            QLineEdit {{
                background-color: {theme['window_bg']};
                color: {theme['text_color']};
                border: 1px solid {theme['highlight']};
            }}
            QDateEdit, QTimeEdit {{
                background-color: {theme['window_bg']};
                color: {theme['text_color']};
                border: 1px solid {theme['highlight']};
            }}
            QTabWidget::pane {{
                border: 1px solid {theme['highlight']};
            }}
            QTabBar::tab {{
                background: {theme['button_bg']};
                color: {theme['button_text']};
                padding: 5px;
            }}
            QTabBar::tab:selected {{
                background: {theme['highlight']};
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
            text, ok = QInputDialog.getText(self, "Edit Categories", "Enter categories (seperate with comma):", text=current)
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

    def load_todos(self):
        todos_path = os.path.join(self.data_dir, "todos.json")
        if os.path.exists(todos_path):
            with open(todos_path, "r", encoding="utf-8") as f:
                self.todos = json.load(f)
        else:
            self.todos = []
            self.save_todos()

    def save_todos(self):
        todos_path = os.path.join(self.data_dir, "todos.json")
        with open(todos_path, "w", encoding="utf-8") as f:
            json.dump(self.todos, f, indent=4)

    def add_todo(self):
        text = self.todo_input.text().strip()
        if not text:
            return

        date = self.todo_date.date().toString("yyyy-MM-dd")
        time = self.todo_time.time().toString("HH:mm")
        datetime_str = f"{date} {time}"

        todo = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "text": text,
            "datetime": datetime_str,
            "completed": False,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        self.todos.append(todo)
        self.save_todos()
        self.refresh_todo_lists()
        self.todo_input.clear()

    def refresh_todo_lists(self):
        # Clear existing items
        self.todo_list.clear()
        self.today_todo_list.clear()
        self.overdue_todo_list.clear()

        now = datetime.now()
        today = QDate.currentDate().toString("yyyy-MM-dd")

        for todo in self.todos:
            todo_datetime = datetime.strptime(todo["datetime"], "%Y-%m-%d %H:%M")

            todo_date = todo["datetime"].split(" ")[0]

            status = "✅" if todo["completed"] else "❌"
            item_text = f"{status} {todo['text']} (Due: {todo['datetime']})"

            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, todo["id"])

            self.todo_list.addItem(item)

            if todo_date == today:
                self.today_todo_list.addItem(QListWidgetItem(item_text))

            if not todo["completed"] and todo_datetime < now:
                self.overdue_todo_list.addItem(QListWidgetItem(item_text))
            
    def complete_todo(self):
        current_item = self.todo_list.currentItem()
        if not current_item:
            return
        
        todo_id = current_item.data(Qt.ItemDataRole.UserRole)
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["completed"] = not todo["completed"]

                break

        self.save_todos()
        self.refresh_todo_lists()

    def edit_todo(self):
        current_item = self.todo_list.currentItem()
        if not current_item:
            return
        
        todo_id = current_item.data(Qt.ItemDataRole.UserRole)
        todo = next((t for t in self.todos if t["id"] == todo_id), None)
        if not todo:
            return
        
        text, ok = QInputDialog.getText(self, "Edit Todo", "Update todo text:", text=todo["text"])
        if ok and text.strip():
            todo["text"] = text.strip()
            
            current_datetime = datetime.strptime(todo["datetime"], "%Y-%m-%d %H:%M")
            new_datetime, ok = QInputDialog.getText(self, "Edit Todo", "Update due date and time (YYYY-MM-DD HH:MM):", text=todo["datetime"])
            if ok and new_datetime.strip():
                try:
                    datetime.strptime(new_datetime.strip(), "%Y-%m-%d %H:%M")
                    todo["datetime"] = new_datetime.strip()
                except ValueError:
                    QMessageBox.warning(self, "Invalid DateTime", "The date and time format is invalid. Keeping the old value.")
            
        self.save_todos()
        self.refresh_todo_lists()

    def delete_todo(self):
        current_item = self.todo_list.currentItem()
        if not current_item:
            return
        
        todo_id = current_item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self,
            "Delete Todo",
            "Are you sure you want to delete this todo?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.todos = [t for t in self.todos if t["id"] != todo_id]
            self.save_todos()
            self.refresh_todo_lists()

    def load_workout_sessions(self):
        workouts_path = os.path.join(self.data_dir, "workouts.json")
        if os.path.exists(workouts_path):
            with open(workouts_path, "r", encoding="utf-8") as f:
                self.workout_sessions = json.load(f)
        else:
            self.workout_sessions = []
            self.save_workout_sessions()

    def save_workout_session(self):
        workouts_path = os.path.join(self.data_dir, "workouts.json")
        with open(workouts_path, "w", encoding="utf-8") as f:
            json.dump(self.workout_sessions, f, indent=4)

    def create_new_session(self):
        date = self.session_date.date().toString("yyyy-MM-dd")

        existing = next((s for s in self.workout_sessions if s["date"] == date), None)
        if existing:
            reply = QMessageBox.question(
                self,
                "Session Exists",
                f"A session for {date} already exists. Do you want to load it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.current_session = existing
                self.load_session_data()
            return
        
        self.current_session = {
            "date": date,
            "exercises": [],
            "id": datetime.now().strftime("%Y%m%d%H%M%S")
        }

        self.clear_excercises_table()
        QMessageBox.information(self, "New Session", f"Created new session for {date}.")
           
    def load_workout_session(self):
        date = self.session_date.date().toString("yyyy-MM-dd")
        self.current_session = next((s for s in self.workout_sessions if s["date"] == date), None)

        if self.current_session:
            self.load_session_data()
        else:
            QMessageBox.information(self, "No Session", f"No session found for {date}. You can create a new one.")


    def load_session_date(self):
        self.clear_excercises_table()
        if not self.current_session:
            return
        
        self.exercises_table.setRowCount(len(self.current_session["exercises"]))

        for row, exercise in enumerate(self.current_session["exercises"]):
            self.exercises_table.setItem(row, 0, QTableWidgetItem(exercise["name"]))
            sets_item = QTableWidgetItem(str(exercise["sets"]))
            sets_item.setFlags(sets_item.flags() & ~Qt.ItemFlag.ItemIsEditable )
            self.exercises_table.setItem(row, 1, sets_item)

            reps_item = QTableWidgetItem(str(exercise.get("reps", "")))
            self.exercises_table.setItem(row, 2, reps_item)

            weight_item = QTableWidgetItem(str(exercise.get("weight", "")))
            self.exercises_table.setItem(row, 3, weight_item)

            del_btn = QPushButton("Delete")
            del_btn.clicked.connect(lambda _, r=row: self.delete_exercise(r))
            self.exercises_table.setCellWidget(row, 4, del_btn)

    def clear_excercises_table(self):
        self.exercises_table.setRowCount(0)

    def add_exercise(self):
        pass

    def delete_exercise(self, row):
        pass

    def save_workout_session(self):
        pass

    def delete_workout_session(self):
        pass



# /* ----- App entry point ----- */
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = JournalApp()
    print("Hello, World!")
    sys.exit(app.exec())