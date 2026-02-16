# src/dual_head_manager.py
"""
Dual Head Manager - Manages two independent validation heads (Head A and Head B)
Each head operates independently with its own configuration, files, and logs.
"""

from PyQt6.QtCore import QObject, pyqtSignal
from .app_state import AppState
from .card_types import CardType

class DualHeadManager(QObject):
    """
    Manages two independent AppState instances for Head A and Head B.
    Provides unified interface for dual-head operation.
    """
    
    # Signals for UI updates
    head_a_state_changed = pyqtSignal()
    head_b_state_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        print("[DEBUG] DualHeadManager: Initializing...")
        
        # Create two independent AppState instances
        # Head A = Instance 1 (Right side)
        # Head B = Instance 2 (Left side)
        
        # Set instance 1 for Head A
        from .app_state import set_current_instance
        print("[DEBUG] DualHeadManager: Creating Head A (Instance 1)...")
        set_current_instance(1)
        self.head_a = AppState(card_type=CardType.HALF)
        self.head_a.current_instance = 1
        print(f"[DEBUG] DualHeadManager: Head A created with instance={self.head_a.current_instance}")
        
        # Set instance 2 for Head B
        print("[DEBUG] DualHeadManager: Creating Head B (Instance 2)...")
        set_current_instance(2)
        self.head_b = AppState(card_type=CardType.HALF)
        self.head_b.current_instance = 2
        print(f"[DEBUG] DualHeadManager: Head B created with instance={self.head_b.current_instance}")
        
        # Connect signals to forward them with head identification
        self.head_a.state_changed.connect(self.head_a_state_changed.emit)
        self.head_b.state_changed.connect(self.head_b_state_changed.emit)
        
        # Store head names for UI display
        self.head_a_name = "Head A"
        self.head_b_name = "Head B"
        
        print("[DEBUG] DualHeadManager: Initialization complete")
    
    def get_head(self, head_id):
        """Get AppState for specified head ('A' or 'B')"""
        if head_id == 'A':
            return self.head_a
        elif head_id == 'B':
            return self.head_b
        else:
            raise ValueError(f"Invalid head_id: {head_id}. Must be 'A' or 'B'")
    
    def get_head_name(self, head_id):
        """Get display name for specified head"""
        if head_id == 'A':
            return self.head_a_name
        elif head_id == 'B':
            return self.head_b_name
        else:
            return "Unknown"
    
    def save_all(self):
        """Save cache for both heads"""
        self.head_a.save_cache()
        self.head_b.save_cache()
    
    def stop_all_scanning(self):
        """Stop scanning on both heads"""
        self.head_a.stop_scanning()
        self.head_b.stop_scanning()
    
    def disconnect_all(self):
        """Disconnect all ports on both heads"""
        self.head_a.disconnect_all_ports()
        self.head_b.disconnect_all_ports()
