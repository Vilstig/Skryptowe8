import sys
from datetime import datetime

import PyQt5.QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette, QFont, QTextCursor

from http_log import HttpLog


class DatePickerDialog(PyQt5.QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wybierz datę")
        self.calendar = PyQt5.QtWidgets.QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.ok_button = PyQt5.QtWidgets.QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)

        layout = PyQt5.QtWidgets.QVBoxLayout()
        layout.addWidget(self.calendar)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

    def get_date(self):
        return self.calendar.selectedDate()


class LogViewer(PyQt5.QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Log browser")
        self.logs = []
        self.filtered_logs = []
        self.current_index = -1
        self.init_ui()

    def init_ui(self):
        main_layout = PyQt5.QtWidgets.QVBoxLayout()
        main_widget = PyQt5.QtWidgets.QWidget()

        self.dummy_focus = PyQt5.QtWidgets.QLabel(self)
        self.dummy_focus.setFixedSize(0, 0)  # Invisible
        self.dummy_focus.setFocusPolicy(Qt.StrongFocus)

        # Top file entry
        file_layout = PyQt5.QtWidgets.QHBoxLayout()
        self.file_entry = PyQt5.QtWidgets.QLineEdit("")
        open_button = PyQt5.QtWidgets.QPushButton("Open")
        open_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_entry)
        file_layout.addWidget(open_button)
        main_layout.addLayout(file_layout)

        # Split below into left and right
        split_layout = PyQt5.QtWidgets.QHBoxLayout()

        # LEFT PANE
        left_layout = PyQt5.QtWidgets.QVBoxLayout()

        # Horizontal date filter layout
        date_filter_layout = PyQt5.QtWidgets.QHBoxLayout()
        date_filter_layout.setSpacing(10)

        date_filter_layout.addWidget(PyQt5.QtWidgets.QLabel("From"))
        self.start_date_entry = PyQt5.QtWidgets.QLineEdit()
        date_filter_layout.addWidget(self.start_date_entry)

        start_button = PyQt5.QtWidgets.QPushButton("📅")
        start_button.clicked.connect(lambda: self.pick_date(self.start_date_entry))
        date_filter_layout.addWidget(start_button)

        date_filter_layout.addSpacing(10)

        date_filter_layout.addWidget(PyQt5.QtWidgets.QLabel("To"))
        self.end_date_entry = PyQt5.QtWidgets.QLineEdit()
        date_filter_layout.addWidget(self.end_date_entry)

        end_button = PyQt5.QtWidgets.QPushButton("📅")
        end_button.clicked.connect(lambda: self.pick_date(self.end_date_entry))
        date_filter_layout.addWidget(end_button)

        date_filter_layout.addSpacing(10)

        filter_button = PyQt5.QtWidgets.QPushButton("Filter")
        filter_button.clicked.connect(self.filter_dates)
        date_filter_layout.addWidget(filter_button)

        # Add horizontal date filter layout to left pane
        left_layout.addLayout(date_filter_layout)

        # Log list
        self.log_list = PyQt5.QtWidgets.QListWidget()
        self.log_list.currentRowChanged.connect(self.show_details)
        self.log_list.setSpacing(2)
        self.log_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.log_list.setTextElideMode(Qt.ElideRight)

        left_layout.addWidget(self.log_list)

        # Navigation buttons
        nav_layout = PyQt5.QtWidgets.QHBoxLayout()
        self.prev_button = PyQt5.QtWidgets.QPushButton("Previous")
        self.prev_button.clicked.connect(self.show_previous)
        self.next_button = PyQt5.QtWidgets.QPushButton("Next")
        self.next_button.clicked.connect(self.show_next)
        nav_layout.addWidget(self.prev_button)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_button)
        left_layout.addLayout(nav_layout)


        # RIGHT PANE (centered vertically)
        right_container = PyQt5.QtWidgets.QWidget()
        right_container_layout = PyQt5.QtWidgets.QVBoxLayout(right_container)
        right_container_layout.addStretch()

        self.fields = {}

        for label in ["Remote host", "Date"]:
            hlayout = PyQt5.QtWidgets.QVBoxLayout()
            title = PyQt5.QtWidgets.QLabel(label + ":")
            title.setFont(QFont("Arial", 12, QFont.Bold))

            field = PyQt5.QtWidgets.QLineEdit()
            field.setReadOnly(True)

            field.setFixedWidth(300)

            self.fields[label] = field

            hlayout.addWidget(title)
            hlayout.addWidget(field)
            hlayout.addSpacing(15)
            right_container_layout.addLayout(hlayout)

        # Status code + Method w jednej linii
        hlayout = PyQt5.QtWidgets.QHBoxLayout()

        # Status code
        status_title = PyQt5.QtWidgets.QLabel("Status code:")
        status_field = PyQt5.QtWidgets.QLabel()
        status_field.setTextInteractionFlags(Qt.TextSelectableByMouse)
        status_field.setStyleSheet("color: lime; font-weight: bold;")
        status_field.setAlignment(Qt.AlignCenter)
        self.fields["Status code"] = status_field

        # Method
        method_title = PyQt5.QtWidgets.QLabel("Method:")
        method_field = PyQt5.QtWidgets.QLabel()
        method_field.setTextInteractionFlags(Qt.TextSelectableByMouse)
        method_field.setStyleSheet("font-weight: bold;")
        method_field.setAlignment(Qt.AlignCenter)
        self.fields["Method"] = method_field

        # Ułóż w poziomie z odstępem
        col1 = PyQt5.QtWidgets.QVBoxLayout()
        col1.addWidget(status_title)
        col1.addWidget(status_field)

        col2 = PyQt5.QtWidgets.QVBoxLayout()
        col2.addWidget(method_title)
        col2.addWidget(method_field)

        hlayout.addLayout(col1)
        hlayout.addSpacing(80)
        hlayout.addLayout(col2)
        hlayout.addStretch()
        right_container_layout.addLayout(hlayout)

        # Resource (duże pole z zawijaniem tekstu)
        hlayout = PyQt5.QtWidgets.QVBoxLayout()
        title = PyQt5.QtWidgets.QLabel("Resource:")
        title.setFont(QFont("Arial", 12, QFont.Bold))

        resource_field = PyQt5.QtWidgets.QTextEdit()
        resource_field.setReadOnly(True)
        resource_field.setFixedHeight(100)
        self.fields["Resource"] = resource_field

        hlayout.addWidget(title)
        hlayout.addWidget(resource_field)
        hlayout.addSpacing(20)
        right_container_layout.addLayout(hlayout)

        # Size – osobno
        hlayout = PyQt5.QtWidgets.QVBoxLayout()
        title = PyQt5.QtWidgets.QLabel("Size:")
        field = PyQt5.QtWidgets.QLabel()
        field.setTextInteractionFlags(Qt.TextSelectableByMouse)
        field.setStyleSheet("font-weight: bold;")
        self.fields["Size"] = field
        hlayout.addWidget(title)
        hlayout.addWidget(field)
        hlayout.addSpacing(80)
        right_container_layout.addLayout(hlayout)

        # Add both panes
        split_layout.addLayout(left_layout, 3)

        # Separator line
        separator = PyQt5.QtWidgets.QFrame()
        separator.setFrameShape(PyQt5.QtWidgets.QFrame.VLine)
        separator.setFrameShadow(PyQt5.QtWidgets.QFrame.Sunken)
        split_layout.addWidget(separator)

        split_layout.addWidget(right_container, 2)

        main_layout.addLayout(split_layout)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.setFixedSize(1200, 800)

    def pick_date(self, target_entry):
        dialog = DatePickerDialog(self)
        if dialog.exec_() == PyQt5.QtWidgets.QDialog.Accepted:
            date = dialog.get_date()
            target_entry.setText(date.toString("yyyy-MM-dd"))

    def browse_file(self):
        file_path, _ = PyQt5.QtWidgets.QFileDialog.getOpenFileName(self, "Select Log File", "",
                                                                   "Log Files (*.log);;All Files (*)")
        if file_path:
            self.file_entry.setText(file_path)
            self.load_file(file_path)

    def load_file(self, file_path):
        try:
            log = HttpLog(file_path)
            self.logs = log.entries
            self.filtered_logs = log.entries
            self.update_list()
        except Exception as e:
            print("Error loading file:", e)

    def filter_dates(self):
        try:
            start = datetime.strptime(self.start_date_entry.text(), "%Y-%m-%d")
            end = datetime.strptime(self.end_date_entry.text(), "%Y-%m-%d")
            self.filtered_logs = [e for e in self.logs if start.date() <= e.timestamp.date() <= end.date()]
            self.update_list()
        except Exception as e:
            print("Filter error:", e)

    def update_list(self):
        self.log_list.clear()

        for entry in self.filtered_logs:
            self.log_list.addItem(str(entry))

    def show_details(self, index):
        if 0 <= index < len(self.filtered_logs):
            entry = self.filtered_logs[index]
            data = entry.to_dict()
            self.fields["Remote host"].setText(data.get("host", ""))
            timestamp = data.get("ts", None)
            self.fields["Date"].setText(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
            self.fields["Status code"].setText(str(data.get("stat_code", "")))
            self.fields["Method"].setText(data.get("method", ""))
            self.fields["Resource"].setPlainText(data.get("uri", ""))
            self.fields["Size"].setText(str(data.get("response_body_len", "")))
            self.current_index = index
            self.update_nav_buttons()
            self.dummy_focus.setFocus()

    def update_nav_buttons(self):
        self.prev_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(self.current_index < len(self.filtered_logs) - 1)

    def show_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.log_list.setCurrentRow(self.current_index)

    def show_next(self):
        if self.current_index < len(self.filtered_logs) - 1:
            self.current_index += 1
            self.log_list.setCurrentRow(self.current_index)


def set_dark_palette(app):
    dark_palette = QPalette()

    # Kolory ogólne
    background_color = QColor(30, 30, 30)
    text_color = QColor(220, 220, 220)
    button_color = QColor("#002147")  # Ciemnoniebieski
    button_text_color = QColor(240, 240, 240)

    # Ustawienia palety
    dark_palette.setColor(QPalette.Window, background_color)
    dark_palette.setColor(QPalette.WindowText, text_color)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.ToolTipBase, text_color)
    dark_palette.setColor(QPalette.ToolTipText, text_color)
    dark_palette.setColor(QPalette.Text, text_color)
    dark_palette.setColor(QPalette.Button, button_color)
    dark_palette.setColor(QPalette.ButtonText, button_text_color)
    dark_palette.setColor(QPalette.BrightText, QColor("red"))
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))

    # Dla elementów nieaktywnych
    dark_palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))

    app.setPalette(dark_palette)

    app.setStyleSheet("""
        QMainWindow {
            background-color: #121212;
        }

        QPushButton {
            background-color: #002147;
            color: #f0f0f0;
            border: 1px solid #003366;
            padding: 6px 12px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #003366;
        }
        QPushButton:pressed {
            background-color: #001a33;
        }
        QPushButton:disabled {
            background-color: #333;
            color: #888;
        }

        QLineEdit, QTextEdit {
            background-color: #1e1e1e;
            color: #f0f0f0;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 6px;
        }

        QListWidget {
            background-color: #1e1e1e;
            color: #f0f0f0;
            border: 1px solid #555;
            font-family: "Segoe UI";
            font-size: 20px;  
        }
        QListWidget::item {
            padding: 8px 16px;
        }
        QListWidget::item:selected {
            background-color: #005a9e;  /* Darker blue */
            color: white;
            font-weight: bold;
            border-radius: 4px;
        }

        QLabel {
            color: #e0e0e0;
        }

        QCalendarWidget QToolButton {
            background-color: #002147;
            color: #f0f0f0;
            border: none;
        }

        QCalendarWidget QAbstractItemView {
            background-color: #1e1e1e;
            color: #f0f0f0;
            selection-background-color: #003366;
        }

        QScrollBar:vertical, QScrollBar:horizontal {
            background-color: #121212;
            border: none;
            width: 10px;
            margin: 0px;
        }

        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
            background-color: #444;
            min-height: 20px;
            border-radius: 5px;
        }

        QScrollBar::add-line, QScrollBar::sub-line {
            background: none;
        }

        QScrollBar::add-page, QScrollBar::sub-page {
            background: none;
        }
    """)


if __name__ == "__main__":
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    font = QFont("Arial", 14)
    app.setFont(font)

    set_dark_palette(app)

    viewer = LogViewer()
    viewer.show()
    sys.exit(app.exec_())
