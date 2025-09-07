import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import os

# Only import the necessary components to start the application
from src.app_state import AppState
from src.ui.main_application import HomePage

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import os

# Only import the necessary components to start the application
from src.app_state import AppState
from src.ui.main_application import HomePage

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("assets/Icon.png")))

    # Create the single instance of the app's brain (AppState)
    app_state = AppState()

    # Create and show the main window, passing the AppState to it
    # The HomePage itself will be responsible for creating the other windows.
    window = HomePage(app_state)
    window.showMaximized()

    sys.exit(app.exec())