# src/ui/card_type_selector.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QRadioButton, QButtonGroup, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class CardTypeSelector(QDialog):
    """Dialog for selecting the card type at application startup"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Card Type Selection")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.selected_card_type = None
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Select Card Type")
        title.setObjectName("h1")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Choose the type of cards you will be validating in this session.")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        
        layout.addSpacing(10)
        
        # Radio button group
        self.button_group = QButtonGroup(self)
        
        # Single Card Option
        self.single_card_option = self.create_card_option(
            "Single Card",
            "One ICCID per card",
            "single"
        )
        layout.addWidget(self.single_card_option)
        
        # Half Card Option (Default)
        self.half_card_option = self.create_card_option(
            "Half Card (Default)",
            "Two ICCIDs per card: Left and Right positions",
            "half"
        )
        layout.addWidget(self.half_card_option)
        
        # Quarter Card Option
        self.quarter_card_option = self.create_card_option(
            "Quarter Card",
            "Four ICCIDs per card: Bottom-Left, Top-Left, Top-Right, Bottom-Right",
            "quarter"
        )
        layout.addWidget(self.quarter_card_option)
        
        # Set default selection
        self.half_card_option.findChild(QRadioButton).setChecked(True)
        
        layout.addSpacing(10)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.confirm_button = QPushButton("Continue")
        self.confirm_button.setObjectName("primary")
        self.confirm_button.setMinimumWidth(120)
        self.confirm_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.confirm_button)
        layout.addLayout(button_layout)
        
    def create_card_option(self, title, description, card_type):
        """Create a card option frame with radio button"""
        frame = QFrame()
        frame.setObjectName("panel")
        frame.setCursor(Qt.CursorShape.PointingHandCursor)
        
        frame_layout = QHBoxLayout(frame)
        frame_layout.setContentsMargins(20, 15, 20, 15)
        
        # Radio button
        radio = QRadioButton()
        radio.setProperty("card_type", card_type)
        self.button_group.addButton(radio)
        frame_layout.addWidget(radio)
        
        # Text content
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setObjectName("h2")
        
        desc_label = QLabel(description)
        desc_label.setObjectName("subtitle")
        desc_label.setWordWrap(True)
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)
        
        frame_layout.addLayout(text_layout, 1)
        
        # Make frame clickable
        frame.mousePressEvent = lambda event: radio.setChecked(True)
        
        return frame
    
    def accept(self):
        """Store the selected card type and close dialog"""
        checked_button = self.button_group.checkedButton()
        if checked_button:
            self.selected_card_type = checked_button.property("card_type")
        super().accept()
    
    def get_selected_card_type(self):
        """Return the selected card type"""
        return self.selected_card_type
