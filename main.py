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

# Load themes from JSON file
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

        # Navigation buttons
        self.to_calendar_btn = QPushButton("Calendar View")
        self.to_entry_btn = QPushButton("Entry View")
        self.to_todo_btn = QPushButton("Todo List")
        self.to_gym_btn = QPushButton("Gym Tracking")

        # Add buttons to sidebar layout
        sidebar_layout.addWidget(self.to_calendar_btn)
        sidebar_layout.addWidget(self.to_entry_btn)
        sidebar_layout.addWidget(self.to_todo_btn)
        sidebar_layout.addWidget(self.to_gym_btn)

        # Entry list
        self.entry_list = QListWidget()
        sidebar_layout.addWidget(self.entry_list)

        # Delete button under entry list
        self.delete_btn = QPushButton("Delete Entry")
        self.delete_btn.clicked.connect(self.delete_entry)
        sidebar_layout.addWidget(self.delete_btn)

        # Add sidebar to main layout with smaller stretch
        main_layout.addWidget(self.sidebar, 1)

        # Staked widget for main content area
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

        # Pin button
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

        # Italic button
        self.italic_btn = QPushButton("I")
        self.italic_btn.setCheckable(True)
        self.italic_btn.setFixedSize(24, 24)
        self.italic_btn.clicked.connect(self.toggle_italic)
        header_layout.addWidget(self.italic_btn)

        # Font size selector
        self.font_size_box = QSpinBox()
        self.font_size_box.setRange(8, 48) # Limit font size range
        self.font_size_box.setValue(12) # Default font size
        self.font_size_box.setMaximumWidth(60) 
        self.font_size_box.valueChanged.connect(self.change_font_size)
        header_layout.addWidget(self.font_size_box)

        entry_layout.addLayout(header_layout)

        # Rich text edit
        self.text_edit = QTextEdit()
        entry_layout.addWidget(self.text_edit)

        # Action buttons row (Save + Categories)
        actions_layout = QHBoxLayout()

        # Save button
        self.save_btn = QPushButton("Save Entry")
        actions_layout.addWidget(self.save_btn)

        # Categories button
        self.categories_btn = QPushButton("🏷")
        self.categories_btn.setFixedSize(24, 24) 
        self.categories_btn.clicked.connect(self.edit_categories)
        actions_layout.addWidget(self.categories_btn)

        entry_layout.addLayout(actions_layout)

        # Add entry page to stacked widget
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

        # Add todo
        todo_form_layout = QHBoxLayout()
        self.todo_input = QLineEdit()
        self.todo_input.setPlaceholderText("Enter new todo...")
        todo_form_layout.addWidget(self.todo_input)

        # Date and time pickers
        self.todo_date = QDateEdit()
        self.todo_date.setDate(QDate.currentDate())
        self.todo_date.setCalendarPopup(True)
        todo_form_layout.addWidget(self.todo_date)

        # Time picker
        self.todo_time = QTimeEdit()
        self.todo_time.setTime(QTime(9, 0))
        todo_form_layout.addWidget(self.todo_time)

        # Add button
        self.add_todo_btn = QPushButton("Add Todo")
        self.add_todo_btn.clicked.connect(self.add_todo)
        todo_form_layout.addWidget(self.add_todo_btn)

        todo_layout.addLayout(todo_form_layout)

        # Todo actions
        todo_actions_layout = QHBoxLayout()
        self.complete_todo_btn = QPushButton("Complete")
        self.complete_todo_btn.clicked.connect(self.complete_todo)
        todo_actions_layout.addWidget(self.complete_todo_btn)

        # Edit button
        self.edit_todo_btn = QPushButton("Edit")
        self.edit_todo_btn.clicked.connect(self.edit_todo)
        todo_actions_layout.addWidget(self.edit_todo_btn)

        # Delete button
        self.delete_todo_btn = QPushButton("Delete")
        self.delete_todo_btn.clicked.connect(self.delete_todo)
        todo_actions_layout.addWidget(self.delete_todo_btn)

        todo_layout.addLayout(todo_actions_layout)

        # Add todo page to stacked widget
        self.stacked.addWidget(self.todo_page)

        # Gym Tracking page setup
        self.gym_page = QWidget()
        gym_layout = QVBoxLayout(self.gym_page)

        # Workout session selection
        session_layout = QHBoxLayout()
        self.session_date = QDateEdit()
        self.session_date.setDate(QDate.currentDate())
        self.session_date.setCalendarPopup(True)
        session_layout.addWidget(QLabel("Workout Date:"))
        session_layout.addWidget(self.session_date)

        # Load session buttons
        self.load_session_btn = QPushButton("Load Session")
        self.load_session_btn.clicked.connect(self.load_workout_session)
        session_layout.addWidget(self.load_session_btn)

        # New session button
        self.new_session_btn = QPushButton("New Session")
        self.new_session_btn.clicked.connect(self.create_new_session)
        session_layout.addWidget(self.new_session_btn)

        # Add session layout to main gym layout
        gym_layout.addLayout(session_layout)

        # Exercise input form
        exercise_form_layout = QHBoxLayout()
        self.exercise_input = QLineEdit()
        self.exercise_input.setPlaceholderText("Exercise name...")
        exercise_form_layout.addWidget(self.exercise_input)

        # Sets input
        self.sets_input = QSpinBox()
        self.sets_input.setRange(1, 10)
        self.sets_input.setValue(3)
        exercise_form_layout.addWidget(QLabel("Sets:"))
        exercise_form_layout.addWidget(self.sets_input)

        # Add exercise button
        self.add_exercise_btn = QPushButton("Add Exercise")
        self.add_exercise_btn.clicked.connect(self.add_exercise)
        exercise_form_layout.addWidget(self.add_exercise_btn)

        # Add exercise layout to gym layout
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

        # Delete session button
        self.delete_session_btn = QPushButton("Delete Session")
        self.delete_session_btn.clicked.connect(self.delete_workout_session)
        session_actions_layout.addWidget(self.delete_session_btn)

        gym_layout.addLayout(session_actions_layout)

        # Add gym page to stacked widget
        self.stacked.addWidget(self.gym_page)


        # Theme selector in sidebar
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(THEMES.keys())
        sidebar_layout.addWidget(self.theme_selector)
        self.theme_selector.currentTextChanged.connect(self.apply_theme)

        # Connect navigation buttons
        self.to_calendar_btn.clicked.connect(
            lambda: self.stacked.setCurrentWidget(self.calendar_page)
        )
        self.to_entry_btn.clicked.connect(
            lambda: self.stacked.setCurrentWidget(self.entry_page)
        )
        self.to_todo_btn.clicked.connect(
            lambda: self.stacked.setCurrentWidget(self.todo_page)
        )
        self.to_gym_btn.clicked.connect(
            lambda: self.stacked.setCurrentWidget(self.gym_page)
        )

        # Action buttons
        self.save_btn.clicked.connect(self.save_entry)
        self.calendar.selectionChanged.connect(self.load_entry_for_date)
        self.entry_list.itemClicked.connect(self.load_entry_from_list)

        # Data and storage setup
        self.entries = []
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)

        # Todo list data
        self.todos = []
        self.load_todos()
        self.refresh_todo_lists()

        # Gym tracking data
        self.workout_sessions = []
        self.current_session = None
        self.load_workout_sessions()

        # Load last used settings and entries
        self.load_settings()

        # apply_theme will set current_theme and also save the settings
        self.apply_theme(self.current_theme)
        
        # Load entries after theme to ensure highlights use correct color
        self.load_entries()
        self.refresh_entry_list()

        # Actually display the window
        self.show()

    # Save current settings to file
    def save_settings(self):
        settings_path = os.path.join(self.data_dir, "settings.json") # Path to settings file
        settings = {"theme": self.current_theme} 
        with open(settings_path, "w", encoding="utf-8") as f: 
            json.dump(settings, f, indent=4) # Save settings as JSON

    # Load settings from file
    def load_settings(self):
        settings_path = os.path.join(self.data_dir, "settings.json") # Path to settings file
        if os.path.exists(settings_path): # If settings file exists
            with open(settings_path, "r") as f: # Open and read settings
                settings = json.load(f) # Load JSON data
                theme_name = settings.get("theme", "Dark") # Default to Dark theme
                self.apply_theme(theme_name) # Apply loaded theme
                # Set theme selector to match loaded theme
                index = self.theme_selector.findText(theme_name)
                if index >= 0:
                    self.theme_selector.setCurrentIndex(index)
        else:
            self.apply_theme("Dark") # Default to Dark theme if no settings file
            self.save_settings() # Save default settings
            # Default select Dark
            index = self.theme_selector.findText("Dark") # Set selector to Dark
            if index >= 0:
                self.theme_selector.setCurrentIndex(index)

    # Load journal entries from file
    def load_entries(self):
        entries_path = os.path.join(self.data_dir, "entries.json") # Path to entries file
        if os.path.exists(entries_path): # If entries file exists
            with open(entries_path, "r", encoding="utf-8") as f: 
                self.entries = json.load(f) # Load entries as JSON
        else: # If no entries file, start with empty list
            self.entries = [] 
            self.save_entries()
        # Highlight dates with entries
        self.highlight_entries()

    # Save journal entries to file
    def save_entries(self):
        entries_path = os.path.join(self.data_dir, "entries.json") # Path to entries file
        with open(entries_path, "w", encoding="utf-8") as f: 
            json.dump(self.entries, f, indent=4) # Save entries as JSON

    # Apply selected theme across the app
    def apply_theme(self, theme_name):
        theme = THEMES.get(theme_name, THEMES["Dark"]) # Default to Dark theme if not found
        self.current_theme = theme_name # Store current theme

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

    # Save or update current entry
    def save_entry(self):
        date = self.calendar.selectedDate().toString("yyyy-MM-dd") # Get selected date
        content = self.text_edit.toHtml() # Get rich text content

        # find existing entry for date
        existing = next((e for e in self.entries if e["date"] == date), None)

        if existing: # Update existing entry
            existing["content"] = content
        else:
            # Prompt for a title when creating a new entry
            title, ok = QInputDialog.getText(self, "Entry Title", "Enter a title for this entry:")
            if not ok or not title.strip():
                title = "Untitled"
            self.entries.append({"date": date, "title": title.strip(), "content": content}) # Add new entry

        # Save entries and refresh UI
        self.save_entries()
        self.refresh_entry_list()
        self.highlight_entries()

    # Refresh the entry list in the sidebar
    def refresh_entry_list(self):
        self.entry_list.clear() # Clear existing items

        # Sort entries: pinned first, then by date
        pinned = [e for e in self.entries if e.get("pinned")]
        others = [e for e in self.entries if not e.get("pinned")]

        # Sort both lists by date
        pinned = sorted(pinned, key=lambda x: x["date"])
        others = sorted(others, key=lambda x: x["date"])

        # Helper to create list item with pin icon and categories
        def make_item(entry, pinned=False):
            cats = ", ".join(entry.get("categories", [])) # Join categories
            label = f"{'📌 ' if pinned else ''}{entry['date']} - {entry['title']} " 
            if cats: # Append categories if any
                label += f" [{cats}]"
            item = QListWidgetItem(label) # Create list item
            item.setData(Qt.ItemDataRole.UserRole, entry["date"]) # Store date for lookup
            return item 

        # Add pinned entries first
        for entry in pinned:
            self.entry_list.addItem(make_item(entry, pinned=True))

        # Then add other entries
        for entry in others:
            self.entry_list.addItem(make_item(entry))

    # Load entry when selected from list
    def load_entry_from_list(self, item):
        date = item.data(Qt.ItemDataRole.UserRole)
        entry = next((e for e in self.entries if e["date"] == date), None)
        if entry:
            self.text_edit.setHtml(entry["content"])
            self.calendar.setSelectedDate(QDate.fromString(date, "yyyy-MM-dd"))
            self.stacked.setCurrentWidget(self.entry_page)

    # Load entry for selected date in calendar
    def load_entry_for_date(self):
        date = self.calendar.selectedDate().toString("yyyy-MM-dd") # Get selected date
        entry = next((e for e in self.entries if e["date"] == date), None) # Find entry by date
        
        if entry:
            self.text_edit.setHtml(entry["content"])
            self.entry_title_label.setText(f"{entry['title']} - {date}")
        else:
            self.text_edit.clear()
            self.entry_title_label.setText(f"New Entry - {date}")

    # Highlight dates in calendar with entries
    def highlight_entries(self):
        # Clear only previously highlighted dates
        if not hasattr(self, "_highlighted_dates"):
            self._highlighted_dates = set()

        # Reset previous highlights
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



    # Text formatting functions
    def toggle_bold(self):
        # Toggle bold formatting
        fmt = self.text_edit.currentCharFormat()
        fmt.setFontWeight(QFont.Weight.Bold if self.bold_btn.isChecked() else QFont.Weight.Normal)
        self.text_edit.setCurrentCharFormat(fmt)

    def toggle_italic(self):
        # Toggle italic formatting
        fmt = self.text_edit.currentCharFormat()
        fmt.setFontItalic(self.italic_btn.isChecked())
        self.text_edit.setCurrentCharFormat(fmt)

    def change_font_size(self, size):
        # Change font size
        fmt = self.text_edit.currentCharFormat()
        fmt.setFontPointSize(size)
        self.text_edit.setCurrentCharFormat(fmt)

    def toggle_pin(self, checked):
        # Toggle pin status of current entry
        date = self.calendar.selectedDate().toString("yyyy-MM-dd") #
        entry = next((e for e in self.entries if e["date"] == date), None)
        if entry: 
            entry["pinned"] = checked
            self.save_entries()
            self.refresh_entry_list()
            self.highlight_entries()

    # Edit categories for current entry
    def edit_categories(self):
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        entry = next((e for e in self.entries if e["date"] == date), None)
        if entry:
            current = ", ".join(entry.get("categories", [])) # Current categories
            text, ok = QInputDialog.getText(self, "Edit Categories", "Enter categories (seperate with comma):", text=current)
            if ok:
                cats = [c.strip() for c in text.split(",") if c.strip()]
                entry["categories"] = cats
                # Update title in sidebar
                self.save_entries()
                self.refresh_entry_list()

    # Delete entry for selected date
    def delete_entry(self):
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        entry = next((e for e in self.entries if e["date"] == date), None) 

        # Confirm deletion
        if not entry:
            QMessageBox.information(self, "No Entry", "There is no entry for this date to delete.")
            return

        reply = QMessageBox.question(
            self,
            "Delete Entry",
            f"Are you sure you want to delete the entry for {date}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        # If confirmed, delete entry
        if reply == QMessageBox.StandardButton.Yes:
            self.entries = [e for e in self.entries if e["date"] != date]
            self.save_entries()
            self.refresh_entry_list()
            self.highlight_entries()
            self.text_edit.clear()
            self.entry_title_label.setText(f"Deleted Entry - {date}")

    # ----- Todo List Functions -----

    # Load todos from file
    def load_todos(self):
        todos_path = os.path.join(self.data_dir, "todos.json")
        if os.path.exists(todos_path):
            with open(todos_path, "r", encoding="utf-8") as f:
                self.todos = json.load(f) # Load todos as JSON
        else:
            # If no todos file, start with empty list
            self.todos = []
            self.save_todos()

    # Save todos to file
    def save_todos(self):
        todos_path = os.path.join(self.data_dir, "todos.json")
        with open(todos_path, "w", encoding="utf-8") as f:
            json.dump(self.todos, f, indent=4) # Save todos as JSON

    # Add new todo
    def add_todo(self):
        text = self.todo_input.text().strip() # Get and trim input text
        if not text:
            return

        # Combine date and time into single datetime string
        date = self.todo_date.date().toString("yyyy-MM-dd")
        time = self.todo_time.time().toString("HH:mm")
        datetime_str = f"{date} {time}"

        # Create new todo item
        todo = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "text": text,
            "datetime": datetime_str,
            "completed": False,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        # Add to list and save
        self.todos.append(todo)
        self.save_todos()
        self.refresh_todo_lists()
        self.todo_input.clear()

    # Refresh all todo list views
    def refresh_todo_lists(self):
        # Clear existing items
        self.todo_list.clear()
        self.today_todo_list.clear()
        self.overdue_todo_list.clear()

        # Current date and time for comparisons
        now = datetime.now()
        today = QDate.currentDate().toString("yyyy-MM-dd")

        # Add todos to appropriate lists
        for todo in self.todos:
            todo_datetime = datetime.strptime(todo["datetime"], "%Y-%m-%d %H:%M")

            todo_date = todo["datetime"].split(" ")[0]

            # Format item text with status
            status = "✅" if todo["completed"] else "❌"
            item_text = f"{status} {todo['text']} (Due: {todo['datetime']})"

            # Create list item and store ID for reference
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, todo["id"])

            # Add to all todos list
            self.todo_list.addItem(item)

            # Add to today's todos if due today
            if todo_date == today:
                self.today_todo_list.addItem(QListWidgetItem(item_text))

            # Add to overdue if past due and not completed
            if not todo["completed"] and todo_datetime < now:
                self.overdue_todo_list.addItem(QListWidgetItem(item_text))
            
    # Mark selected todo as complete/incomplete
    def complete_todo(self):
        current_item = self.todo_list.currentItem()
        if not current_item:
            return
        # Toggle completed status
        todo_id = current_item.data(Qt.ItemDataRole.UserRole)
        for todo in self.todos:
            if todo["id"] == todo_id:
                # Toggle between completed status
                todo["completed"] = not todo["completed"]

                break

        # Save changes and refresh lists
        self.save_todos()
        self.refresh_todo_lists()

    # Edit selected todo
    def edit_todo(self):
        # Get currently selected item
        current_item = self.todo_list.currentItem()
        if not current_item:
            return
        
        # Find corresponding todo
        todo_id = current_item.data(Qt.ItemDataRole.UserRole)
        todo = next((t for t in self.todos if t["id"] == todo_id), None)
        if not todo:
            return
        
        # Prompt for new text
        text, ok = QInputDialog.getText(self, "Edit Todo", "Update todo text:", text=todo["text"])
        if ok and text.strip():
            todo["text"] = text.strip()
            
            # Prompt for new date/time
            current_datetime = datetime.strptime(todo["datetime"], "%Y-%m-%d %H:%M")
            new_datetime, ok = QInputDialog.getText(self, "Edit Todo", "Update due date and time (YYYY-MM-DD HH:MM):", text=todo["datetime"])
            if ok and new_datetime.strip():
                try:
                    datetime.strptime(new_datetime.strip(), "%Y-%m-%d %H:%M")
                    todo["datetime"] = new_datetime.strip()
                except ValueError:
                    QMessageBox.warning(self, "Invalid DateTime", "The date and time format is invalid. Keeping the old value.")
            
        # Save changes and refresh lists
        self.save_todos()
        self.refresh_todo_lists()

    # Delete selected todo
    def delete_todo(self):
        current_item = self.todo_list.currentItem()
        if not current_item:
            return
        
        # Confirm deletion
        todo_id = current_item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self,
            "Delete Todo",
            "Are you sure you want to delete this todo?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        # If confirmed, delete todo
        if reply == QMessageBox.StandardButton.Yes:
            self.todos = [t for t in self.todos if t["id"] != todo_id]
            self.save_todos()
            self.refresh_todo_lists()

    # ----- Gym Tracking Functions -----

    # Load workout sessions from file
    def load_workout_sessions(self):
        workouts_path = os.path.join(self.data_dir, "workouts.json") # Path to workouts file
        if os.path.exists(workouts_path):
            with open(workouts_path, "r", encoding="utf-8") as f:
                self.workout_sessions = json.load(f) # Load sessions as JSON
        else:
            # If no workouts file, start with empty list
            self.workout_sessions = [] 
            self.save_workout_sessions_to_file()

    # Save workout sessions to file
    def save_workout_session(self):
        workouts_path = os.path.join(self.data_dir, "workouts.json")
        with open(workouts_path, "w", encoding="utf-8") as f:
            json.dump(self.workout_sessions, f, indent=4) # Save sessions as JSON

    # Delete workout session for selected date
    def create_new_session(self):
        date = self.session_date.date().toString("yyyy-MM-dd") 

        # Check if session already exists for date
        existing = next((s for s in self.workout_sessions if s["date"] == date), None)
        if existing:
            # Prompt to load existing session
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
        
        # Create new session
        self.current_session = {
            "date": date,
            "exercises": [],
            "id": datetime.now().strftime("%Y%m%d%H%M%S")
        }

        # Clear table for new session
        self.clear_exercises_table()
        QMessageBox.information(self, "New Session", f"Created new session for {date}.")
           
    # Load workout session for selected date
    def load_workout_session(self):
        date = self.session_date.date().toString("yyyy-MM-dd")
        self.current_session = next((s for s in self.workout_sessions if s["date"] == date), None)

        # If found, load data into table
        if self.current_session:
            self.load_session_data()
        else:
            return

    # Load current session data into exercises table
    def load_session_data(self):
        self.clear_exercises_table()
        if not self.current_session:
            return
        
        # Populate table with exercises
        self.exercises_table.setRowCount(len(self.current_session["exercises"]))

        # Add each exercise to the table
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

    # Clear all rows from exercises table
    def clear_exercises_table(self):
        self.exercises_table.setRowCount(0)

    # Add new exercise to current session
    def add_exercise(self):
        if not self.current_session:
            QMessageBox.warning(self, "No Session", "Please create or load a workout session first.")
            return

        # Get exercise details from input fields
        name = self.exercise_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter an exercise name.")
            return

        sets = self.sets_input.value()

        # Create new exercise entry
        exercise = {
            "name": name,
            "sets": sets,
            "reps": "",
            "weight": ""
        }

        # Add to current session
        self.current_session["exercises"].append(exercise)

        # Add to table
        row = self.exercises_table.rowCount()
        self.exercises_table.insertRow(row)

        # Populate row with exercise data
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

        self.exercise_input.clear()

    # Delete exercise from current session
    def delete_exercise(self, row):
        if not self.current_session:
            return
        
        # Remove from session data and table
        if 0 <= row < len(self.current_session["exercises"]):
            self.current_session["exercises"].pop(row)
            self.exercises_table.removeRow(row)

    # Save current workout session to file
    def save_workout_session(self):
        if not self.current_session:
            QMessageBox.warning(self, "No Session", "No workout session to save.")
            return
        
        # Update exercise data from table
        for row in range(self.exercises_table.rowCount()):
            if row < len(self.current_session["exercises"]):
                exercise = self.current_session["exercises"][row]
                exercise["reps"] = self.exercises_table.item(row, 2).text() if self.exercises_table.item(row, 2) else ""
                exercise["weight"] = self.exercises_table.item(row, 3).text() if self.exercises_table.item(row, 3) else ""
        
        # Add or update in sessions list
        existing_index = next((i for i, s in enumerate(self.workout_sessions) if s["id"] == self.current_session["id"]), -1)
        if existing_index >= 0:
            self.workout_sessions[existing_index] = self.current_session
        else:
            self.workout_sessions.append(self.current_session)
        
        self.save_workout_sessions_to_file()  
        QMessageBox.information(self, "Saved", "Workout session saved successfully.")

    # Save all workout sessions to file
    def save_workout_sessions_to_file(self):  
        workouts_path = os.path.join(self.data_dir, "workouts.json")
        with open(workouts_path, "w", encoding="utf-8") as f:
            json.dump(self.workout_sessions, f, indent=4) # Save sessions as JSON

    # Delete current workout session
    def delete_workout_session(self):
        if not self.current_session:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Session",
            f"Are you sure you want to delete the session for {self.current_session['date']}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No 
        )

        # If confirmed, delete session
        if reply == QMessageBox.StandardButton.Yes:
            self.workout_sessions = [s for s in self.workout_sessions if s["id"] != self.current_session["id"]]
            self.save_workout_sessions_to_file()
            self.current_session = None
            self.clear_excercises_table()
            QMessageBox.information(self, "Deleted", "Workout session deleted.")
        else:
            return

# /* ----- App entry point ----- */
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = JournalApp()
    print("Hello, World!")
    sys.exit(app.exec())