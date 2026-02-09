#!/usr/bin/env python
"""
Quick test script to verify the application starts without errors
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Import the main components
from src.app_state import AppState
from src.ui.main_application import HomePage
from src.card_types import CardType

def test_application():
    """Test that the application initializes correctly"""
    print("Testing Card Sequence Validator...")
    
    app = QApplication(sys.argv)
    
    try:
        # Create AppState
        print("✓ Creating AppState...")
        app_state = AppState(card_type=CardType.HALF)
        print(f"  - Main scanner config: {app_state.main_scanner_config}")
        print(f"  - On-demand scanner config: {app_state.ondemand_scanner_config}")
        print(f"  - Output config: {app_state.output_config}")
        
        # Create main window
        print("✓ Creating HomePage...")
        window = HomePage(app_state)
        
        # Show window
        print("✓ Showing window...")
        window.show()
        
        # Test opening Network Setup
        print("✓ Testing Network Setup window...")
        window.open_com_port_setup()
        if window.com_port_window:
            print("  - Network Setup window created successfully")
            window.com_port_window.close()
        
        # Test opening File Management
        print("✓ Testing File Management window...")
        window.open_file_management()
        if window.file_management_window:
            print("  - File Management window created successfully")
            window.file_management_window.close()
        
        # Test opening Scanner Logging
        print("✓ Testing Scanner Logging window...")
        window.open_scanner()
        if window.scanner_logging_window:
            print("  - Scanner Logging window created successfully")
            window.scanner_logging_window.close()
        
        print("\n✅ All tests passed! Application is working correctly.")
        
        # Close after 2 seconds
        QTimer.singleShot(2000, app.quit)
        
        return app.exec()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_application())
