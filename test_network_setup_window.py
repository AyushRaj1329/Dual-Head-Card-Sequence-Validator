#!/usr/bin/env python
"""
Test script to verify Network Setup Window opens without crashing
"""

import sys
from PyQt6.QtWidgets import QApplication
from src.app_state import AppState
from src.ui.network_setup import NetworkSetupWindow
from src.card_types import CardType

def test_network_setup_window():
    """Test that the Network Setup Window can be opened"""
    print("Testing Network Setup Window initialization...")
    
    try:
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Create AppState
        print("Creating AppState...")
        app_state = AppState(card_type=CardType.HALF)
        
        # Create Network Setup Window
        print("Creating Network Setup Window...")
        window = NetworkSetupWindow(app_state)
        
        # Show window
        print("Showing window...")
        window.show()
        
        print("\n✅ SUCCESS! Network Setup Window opened without crashing.")
        print("\nWindow is now visible. Close it to exit the test.")
        
        # Run event loop
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"\n❌ FAILED! Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_network_setup_window()
