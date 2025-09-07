# src/ui/widgets.py
from PyQt6.QtWidgets import QLabel, QDialog, QVBoxLayout, QDialogButtonBox
from PyQt6.QtCore import QTimer, QTime
from datetime import datetime

class ClockWidget(QLabel):
    """A QLabel widget that displays the current date and time, updated continuously."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("clock_display") # Use a specific style for the clock

        # Set up a timer to update the clock every 100 milliseconds
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(100)

        # Initial call to display time immediately
        self.update_time()

    def update_time(self):
        """Fetches the current time and updates the label's text."""
        now = datetime.now()
        # Format: YYYY-MM-DD | HH:MM:SS.ms TZ
        # Slicing microseconds to get 3-digit milliseconds
        formatted_time = now.strftime("%Y-%m-%d | %H:%M:%S.%f")[:-3] + now.strftime(" %Z")
        self.setText(formatted_time)

# --- NEW DIALOG CLASS ---
class ApprovalDialog(QDialog):
    """A simple dialog to ask for user approval."""
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)

        # Safely inherit styles from parent if available
        if parent and hasattr(parent, 'styleSheet'):
            try:
                self.setStyleSheet(parent.styleSheet())
            except:
                pass  # Ignore style errors

        layout = QVBoxLayout(self)

        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setObjectName("subtitle")

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(message_label)
        layout.addWidget(button_box)

        # Set minimum size for better readability
        self.setMinimumWidth(400)
        self.setMinimumHeight(150)