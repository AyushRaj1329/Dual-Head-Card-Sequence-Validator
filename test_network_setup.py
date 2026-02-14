"""
Standalone test script for Network Setup Window
Run this from the project root directory
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from src.app_state import AppState
from src.ui.network_setup import NetworkSetupWindow

def main():
    """Run Network Setup Window standalone for testing"""
    app = QApplication(sys.argv)
    
    # Create app state
    app_state = AppState()
    
    # Create and show network setup window
    window = NetworkSetupWindow(app_state)
    window.show()
    
    print("Network Setup Window opened successfully!")
    print("Close the window to exit.")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
