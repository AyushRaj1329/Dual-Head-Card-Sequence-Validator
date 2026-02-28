# src/ui/file_management_dual.py
"""
Dual Head Job Management Window - Split view for Head A and Head B
Left side: Head B job operations
Right side: Head A job operations
"""

import sys, os, csv
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QHBoxLayout,
    QVBoxLayout, QFrame, QFileDialog, QLineEdit, QMessageBox, QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QGridLayout, QScrollArea, QComboBox
)
from PyQt6.QtCore import Qt
from .styles import DARK_THEME_STYLESHEET, LIGHT_THEME_STYLESHEET
from .widgets import ClockWidget
from .card_type_selector import CardTypeSelector
import constants
from ..card_types import CardType

class PreviewWindow(QDialog):
    """Preview window for sequence data"""
    def __init__(self, expected_cards, card_type, scan_direction="top_to_bottom", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preview Sequence Data")
        if parent and hasattr(parent, 'styleSheet'):
            try:
                self.setStyleSheet(parent.styleSheet())
            except: pass

        layout = QVBoxLayout(self)
        if not expected_cards:
            layout.addWidget(QLabel("No expected cards loaded."))
        else:
            # Add scan direction indicator
            direction_label = QLabel()
            if scan_direction == "bottom_to_top":
                direction_label.setText("📋 Scan Direction: Bottom → Top (Reversed Order)")
                direction_label.setStyleSheet("color: #2196F3; font-weight: bold; padding: 5px;")
            else:
                direction_label.setText("📋 Scan Direction: Top → Bottom (Normal Order)")
                direction_label.setStyleSheet("color: #4CAF50; font-weight: bold; padding: 5px;")
            layout.addWidget(direction_label)
            
            qr_labels = CardType.get_qr_labels(card_type)
            num_columns = 1 + len(qr_labels)
            
            # Reverse the cards if scan direction is bottom_to_top
            display_cards = list(reversed(expected_cards)) if scan_direction == "bottom_to_top" else expected_cards
            
            table = QTableWidget(len(display_cards), num_columns)
            headers = ["Card Number"] + qr_labels
            table.setHorizontalHeaderLabels(headers)
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            for i in range(1, num_columns):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

            for row, card in enumerate(display_cards):
                numcard = card[0]
                qr_codes = card[1:]
                table.setItem(row, 0, QTableWidgetItem(str(numcard)))
                for col, qr_code in enumerate(qr_codes, start=1):
                    table.setItem(row, col, QTableWidgetItem(str(qr_code)))
            
            layout.addWidget(table)
        self.setMinimumSize(600, 400)


class FileManagementWindow(QMainWindow):
    """Dual-head job management window with split view"""
    def __init__(self, dual_head_manager, open_scanner_callback=None):
        super().__init__()
        self.dual_head_manager = dual_head_manager
        self.head_a = dual_head_manager.head_a
        self.head_b = dual_head_manager.head_b
        self.open_scanner_callback = open_scanner_callback
        self.setWindowTitle("Job Management - Dual Head")
        self.setMinimumSize(1400, 800)
        
        self.update_theme(self.head_a.current_theme)
        self.head_a.theme_changed.connect(self.update_theme)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        central_widget = QWidget()
        scroll_area.setWidget(central_widget)
        self.setCentralWidget(scroll_area)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)

        self.create_header(main_layout)
        self.create_split_panels(main_layout)
        
        # Add Start Validation button at bottom
        self.create_start_validation_section(main_layout)
        
        main_layout.addStretch()

        # Connect signals from both heads
        self.head_a.state_changed.connect(lambda: self.update_ui('A'))
        self.head_b.state_changed.connect(lambda: self.update_ui('B'))
        self.head_a.start_card_scan_complete.connect(lambda msg, success: self.handle_start_card_scan_complete('A', msg, success))
        self.head_b.start_card_scan_complete.connect(lambda msg, success: self.handle_start_card_scan_complete('B', msg, success))
        self.head_a.card_count_update.connect(lambda type, msg: self.handle_card_count_update('A', type, msg))
        self.head_b.card_count_update.connect(lambda type, msg: self.handle_card_count_update('B', type, msg))
        self.head_a.ondemand_scan_status_update.connect(lambda status, msg: self.handle_ondemand_scan_status('A', status, msg))
        self.head_b.ondemand_scan_status_update.connect(lambda status, msg: self.handle_ondemand_scan_status('B', status, msg))
        self.head_a.card_type_changed.connect(lambda ct: self.rebuild_card_details_fields('A', ct))
        self.head_b.card_type_changed.connect(lambda ct: self.rebuild_card_details_fields('B', ct))
        
        self.update_ui('A')
        self.update_ui('B')

    def create_header(self, parent_layout):
        title = QLabel("Job Management - Dual Head")
        title.setObjectName("h1")
        subtitle = QLabel("Manage job files for Head A (Right) and Head B (Left)")
        subtitle.setObjectName("subtitle")
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        header_layout = QHBoxLayout()
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(ClockWidget())
        parent_layout.addLayout(header_layout)

    def create_split_panels(self, parent_layout):
        """Create split view with Head B on left and Head A on right"""
        split_container = QFrame()
        split_container.setObjectName("panel")
        split_layout = QHBoxLayout(split_container)
        split_layout.setContentsMargins(0, 0, 0, 0)
        split_layout.setSpacing(2)
        
        # Head B (Left Side)
        head_b_panel = self.create_head_panel('B', "Head B (Left)")
        split_layout.addWidget(head_b_panel, 1)
        
        # Vertical separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet("background-color: #444; max-width: 2px;")
        split_layout.addWidget(separator)
        
        # Head A (Right Side)
        head_a_panel = self.create_head_panel('A', "Head A (Right)")
        split_layout.addWidget(head_a_panel, 1)
        
        parent_layout.addWidget(split_container)

    def create_start_validation_section(self, parent_layout):
        """Create start validation button section at bottom"""
        button_container = QFrame()
        button_container.setObjectName("accentPanel")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(20, 15, 20, 15)
        
        # Info label
        info_label = QLabel("Ready to start validation? Click below to begin scanning.")
        info_label.setObjectName("subtitle")
        button_layout.addWidget(info_label)
        
        button_layout.addStretch()
        
        # Start Validation buttons for both heads
        start_head_b_btn = QPushButton("▶ Start Validation - Head B")
        start_head_b_btn.setObjectName("primary")
        start_head_b_btn.setMinimumWidth(220)
        start_head_b_btn.clicked.connect(lambda: self.start_validation_and_switch('B'))
        button_layout.addWidget(start_head_b_btn)
        self.start_validation_btn_B = start_head_b_btn
        
        start_head_a_btn = QPushButton("▶ Start Validation - Head A")
        start_head_a_btn.setObjectName("primary")
        start_head_a_btn.setMinimumWidth(220)
        start_head_a_btn.clicked.connect(lambda: self.start_validation_and_switch('A'))
        button_layout.addWidget(start_head_a_btn)
        self.start_validation_btn_A = start_head_a_btn
        
        parent_layout.addWidget(button_container)

    def create_head_panel(self, head_id, title):
        """Create job management panel for one head"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header with color coding
        header = QLabel(title)
        header.setObjectName("h1")
        if head_id == 'A':
            header.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 20px;")
        else:
            header.setStyleSheet("color: #2196F3; font-weight: bold; font-size: 20px;")
        layout.addWidget(header)
        
        # File Operations Section
        file_ops = self.create_file_operations_section(head_id)
        layout.addWidget(file_ops)
        
        # Checksum Configuration Section
        checksum_section = self.create_checksum_section(head_id)
        layout.addWidget(checksum_section)
        
        # Sequence Control Tools Section
        seq_tools = self.create_sequence_tools_section(head_id)
        layout.addWidget(seq_tools)
        
        # Log Management Section
        log_mgmt = self.create_log_management_section(head_id)
        layout.addWidget(log_mgmt)
        
        layout.addStretch()
        
        return panel

    def create_file_operations_section(self, head_id):
        """Create file operations section for specified head"""
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        title = QLabel("Job File Operations")
        title.setObjectName("h2")
        layout.addWidget(title)
        
        # Load file button
        load_btn = QPushButton("📁 Load Job File")
        load_btn.setObjectName("primary")
        load_btn.clicked.connect(lambda: self.select_file(head_id))
        layout.addWidget(load_btn)
        
        # File status
        file_status = QLabel("No job file loaded.")
        file_status.setObjectName("subtitle")
        setattr(self, f'file_status_{head_id}', file_status)
        layout.addWidget(file_status)
        
        # Scan direction toggle
        direction_layout = QHBoxLayout()
        direction_label = QLabel("Scan Direction:")
        direction_label.setObjectName("subtitle")
        
        direction_toggle = QPushButton("🔄 Top → Bottom")
        direction_toggle.setObjectName("secondary")
        direction_toggle.setCheckable(True)
        direction_toggle.clicked.connect(lambda: self.toggle_scan_direction(head_id))
        setattr(self, f'scan_direction_toggle_{head_id}', direction_toggle)
        
        direction_layout.addWidget(direction_label)
        direction_layout.addWidget(direction_toggle)
        direction_layout.addStretch()
        layout.addLayout(direction_layout)
        
        # Preview and Clear buttons
        button_layout = QHBoxLayout()
        preview_btn = QPushButton("👁 Preview")
        preview_btn.setObjectName("secondary")
        preview_btn.clicked.connect(lambda: self.preview_file(head_id))
        setattr(self, f'preview_btn_{head_id}', preview_btn)
        
        clear_btn = QPushButton("🗑 Clear")
        clear_btn.setObjectName("secondary")
        clear_btn.clicked.connect(lambda: self.clear_file(head_id))
        setattr(self, f'clear_btn_{head_id}', clear_btn)
        
        button_layout.addWidget(preview_btn)
        button_layout.addWidget(clear_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return frame

    def create_checksum_section(self, head_id):
        """Create checksum configuration section for specified head"""
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        title = QLabel("Checksum Configuration")
        title.setObjectName("h2")
        layout.addWidget(title)
        
        description = QLabel("Strip checksum digits from the end of scanned codes before validation.")
        description.setObjectName("subtitle")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Checksum digits selector
        checksum_layout = QHBoxLayout()
        checksum_label = QLabel("Checksum Digits:")
        checksum_label.setObjectName("subtitle")
        
        checksum_combo = QComboBox()
        checksum_combo.addItems([
            "0 (None)", 
            "1 (Last digit)", 
            "2 (Last 2 digits)", 
            "3 (Last 3 digits)",
            "4 (Last 4 digits)",
            "5 (Last 5 digits)"
        ])
        checksum_combo.setObjectName("secondary")
        checksum_combo.currentIndexChanged.connect(lambda idx: self.update_checksum_digits(head_id, idx))
        # Disable scroll wheel to prevent accidental changes
        checksum_combo.wheelEvent = lambda event: None
        setattr(self, f'checksum_combo_{head_id}', checksum_combo)
        
        checksum_layout.addWidget(checksum_label)
        checksum_layout.addWidget(checksum_combo)
        checksum_layout.addStretch()
        layout.addLayout(checksum_layout)
        
        # Example display
        example_frame = QFrame()
        example_frame.setObjectName("accentPanel")
        example_layout = QVBoxLayout(example_frame)
        example_layout.setSpacing(5)
        
        example_title = QLabel("Example:")
        example_title.setStyleSheet("font-weight: bold;")
        example_layout.addWidget(example_title)
        
        example_text = QLabel("Scanned: 123456789\nValidated: 123456789")
        example_text.setObjectName("subtitle")
        setattr(self, f'checksum_example_{head_id}', example_text)
        example_layout.addWidget(example_text)
        
        layout.addWidget(example_frame)
        
        return frame

    def create_sequence_tools_section(self, head_id):
        """Create sequence control tools section for specified head"""
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        title = QLabel("Sequence Control Tools")
        title.setObjectName("h2")
        layout.addWidget(title)
        
        # Card Details Subsection
        details_frame = QFrame()
        details_frame.setObjectName("accentPanel")
        details_layout = QVBoxLayout(details_frame)
        details_layout.setSpacing(10)
        
        details_title = QLabel("Scan Card Details")
        details_title.setStyleSheet("font-weight: bold;")
        details_layout.addWidget(details_title)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        scan_btn = QPushButton("Scan Card")
        scan_btn.setObjectName("primary")
        scan_btn.clicked.connect(lambda: self.scan_card_details(head_id))
        setattr(self, f'scan_card_details_btn_{head_id}', scan_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(lambda: self.cancel_card_details(head_id))
        cancel_btn.setVisible(False)
        setattr(self, f'cancel_card_details_btn_{head_id}', cancel_btn)
        
        actions_layout.addWidget(scan_btn)
        actions_layout.addWidget(cancel_btn)
        actions_layout.addStretch()
        details_layout.addLayout(actions_layout)
        
        # Status label
        status_label = QLabel("Click 'Scan Card' to view card information.")
        status_label.setObjectName("subtitle")
        setattr(self, f'card_details_status_{head_id}', status_label)
        details_layout.addWidget(status_label)
        
        # Fields grid
        fields_grid = QGridLayout()
        fields_grid.setSpacing(8)
        
        # Card Number
        fields_grid.addWidget(QLabel("Card Number:"), 0, 0, Qt.AlignmentFlag.AlignLeft)
        card_num_field = QLineEdit()
        card_num_field.setReadOnly(True)
        setattr(self, f'card_number_field_{head_id}', card_num_field)
        fields_grid.addWidget(card_num_field, 0, 1)
        
        # Dynamic QR fields
        head = self.head_a if head_id == 'A' else self.head_b
        qr_labels = CardType.get_qr_labels(head.card_type)
        qr_fields = []
        for i, label in enumerate(qr_labels, start=1):
            fields_grid.addWidget(QLabel(f"{label}:"), i, 0, Qt.AlignmentFlag.AlignLeft)
            qr_field = QLineEdit()
            qr_field.setReadOnly(True)
            fields_grid.addWidget(qr_field, i, 1)
            qr_fields.append(qr_field)
        setattr(self, f'qr_fields_{head_id}', qr_fields)
        
        # Position
        position_row = len(qr_labels) + 1
        fields_grid.addWidget(QLabel("Position:"), position_row, 0, Qt.AlignmentFlag.AlignLeft)
        position_field = QLineEdit()
        position_field.setReadOnly(True)
        setattr(self, f'position_field_{head_id}', position_field)
        fields_grid.addWidget(position_field, position_row, 1)
        
        # Store grid for rebuilding
        setattr(self, f'details_fields_grid_{head_id}', fields_grid)
        
        details_layout.addLayout(fields_grid)
        layout.addWidget(details_frame)
        
        # Card Count Subsection
        count_frame = QFrame()
        count_frame.setObjectName("accentPanel")
        count_layout = QVBoxLayout(count_frame)
        count_layout.setSpacing(10)
        
        count_title = QLabel("Count Card Range")
        count_title.setStyleSheet("font-weight: bold;")
        count_layout.addWidget(count_title)
        
        # Action buttons
        count_actions_layout = QHBoxLayout()
        count_btn = QPushButton("Count Range")
        count_btn.setObjectName("primary")
        count_btn.clicked.connect(lambda: self.start_card_counting(head_id))
        setattr(self, f'count_cards_btn_{head_id}', count_btn)
        
        cancel_count_btn = QPushButton("Cancel")
        cancel_count_btn.setObjectName("secondary")
        cancel_count_btn.clicked.connect(lambda: self.cancel_count_cards(head_id))
        cancel_count_btn.setVisible(False)
        setattr(self, f'cancel_count_cards_btn_{head_id}', cancel_count_btn)
        
        count_actions_layout.addWidget(count_btn)
        count_actions_layout.addWidget(cancel_count_btn)
        count_actions_layout.addStretch()
        count_layout.addLayout(count_actions_layout)
        
        # Status label
        count_status_label = QLabel("Click 'Count Range' to begin.")
        count_status_label.setObjectName("subtitle")
        setattr(self, f'card_count_status_{head_id}', count_status_label)
        count_layout.addWidget(count_status_label)
        
        # Count fields
        count_fields = QGridLayout()
        count_fields.setSpacing(8)
        
        count_fields.addWidget(QLabel("First Card:"), 0, 0, Qt.AlignmentFlag.AlignLeft)
        first_card_field = QLineEdit()
        first_card_field.setReadOnly(True)
        setattr(self, f'first_card_field_{head_id}', first_card_field)
        count_fields.addWidget(first_card_field, 0, 1)
        
        count_fields.addWidget(QLabel("Last Card:"), 1, 0, Qt.AlignmentFlag.AlignLeft)
        last_card_field = QLineEdit()
        last_card_field.setReadOnly(True)
        setattr(self, f'last_card_field_{head_id}', last_card_field)
        count_fields.addWidget(last_card_field, 1, 1)
        
        count_fields.addWidget(QLabel("Total:"), 2, 0, Qt.AlignmentFlag.AlignLeft)
        total_count_field = QLineEdit()
        total_count_field.setReadOnly(True)
        setattr(self, f'total_count_field_{head_id}', total_count_field)
        count_fields.addWidget(total_count_field, 2, 1)
        
        count_layout.addLayout(count_fields)
        layout.addWidget(count_frame)
        
        return frame


    def create_log_management_section(self, head_id):
        """Create log management section for specified head"""
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        title = QLabel("Validation Log Management")
        title.setObjectName("h2")
        layout.addWidget(title)
        
        # Buttons
        button_layout = QHBoxLayout()
        export_btn = QPushButton("📥 Export Logs")
        export_btn.setObjectName("primary")
        export_btn.clicked.connect(lambda: self.download_logs(head_id))
        setattr(self, f'download_btn_{head_id}', export_btn)
        
        clear_logs_btn = QPushButton("💾 Download & Clear Logs")
        clear_logs_btn.setObjectName("secondary")
        clear_logs_btn.clicked.connect(lambda: self.clear_logs(head_id))
        setattr(self, f'clear_logs_btn_{head_id}', clear_logs_btn)
        
        button_layout.addWidget(export_btn)
        button_layout.addWidget(clear_logs_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Statistics
        stats_frame = QFrame()
        stats_frame.setObjectName("accentPanel")
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setContentsMargins(15, 15, 15, 15)
        
        total_label = QLabel("0")
        total_label.setObjectName("accent")
        setattr(self, f'total_scanned_label_{head_id}', total_label)
        
        ok_label = QLabel("0")
        ok_label.setObjectName("accent")
        setattr(self, f'scanned_ok_label_{head_id}', ok_label)
        
        error_label = QLabel("0")
        error_label.setObjectName("accent")
        setattr(self, f'error_not_ok_label_{head_id}', error_label)
        
        skipped_label = QLabel("0")
        skipped_label.setObjectName("accent")
        setattr(self, f'skipped_label_{head_id}', skipped_label)
        
        stats_layout.addWidget(self.create_stat("Total Scans:", total_label), 0, 0)
        stats_layout.addWidget(self.create_stat("Successful:", ok_label), 0, 1)
        stats_layout.addWidget(self.create_stat("Failed:", error_label), 1, 0)
        stats_layout.addWidget(self.create_stat("Skipped:", skipped_label), 1, 1)
        
        layout.addWidget(stats_frame)
        
        return frame

    def create_stat(self, text, value_label):
        """Create a stat widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel(text)
        label.setObjectName("subtitle")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(value_label)
        return widget

    # File operation methods
    def update_checksum_digits(self, head_id, index):
        """Update checksum digits configuration for specified head"""
        head = self.head_a if head_id == 'A' else self.head_b
        head.checksum_digits = index
        head.save_cache()
        
        # Update example text
        example_label = getattr(self, f'checksum_example_{head_id}')
        if index == 0:
            example_label.setText("Scanned: 123456789\nValidated: 123456789")
        elif index == 1:
            example_label.setText("Scanned: 123456789\nValidated: 12345678")
        elif index == 2:
            example_label.setText("Scanned: 123456789\nValidated: 1234567")
        elif index == 3:
            example_label.setText("Scanned: 123456789\nValidated: 123456")
        elif index == 4:
            example_label.setText("Scanned: 123456789\nValidated: 12345")
        elif index == 5:
            example_label.setText("Scanned: 123456789\nValidated: 1234")
        
        head.state_changed.emit()
    
    def select_file(self, head_id):
        """Load job file for specified head"""
        head = self.head_a if head_id == 'A' else self.head_b
        head.stop_scanning()
        
        # Check if there's an unloaded file path from previous session
        has_unloaded_file = head.selected_file_path and not head.expected_cards
        is_reloading_previous = False
        
        if has_unloaded_file:
            # Ask user if they want to load the previous file or select a new one
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(f"Load Previous File - Head {head_id}")
            msg_box.setText(f"Previous file detected:\n{os.path.basename(head.selected_file_path)}\n\nDo you want to load this file or select a different one?")
            load_prev_btn = msg_box.addButton("Load Previous", QMessageBox.ButtonRole.AcceptRole)
            select_new_btn = msg_box.addButton("Select New File", QMessageBox.ButtonRole.ActionRole)
            cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            msg_box.exec()
            
            clicked_button = msg_box.clickedButton()
            if clicked_button == cancel_btn:
                return
            elif clicked_button == load_prev_btn:
                # Load the previous file with card type selection
                file_path = head.selected_file_path
                is_reloading_previous = True
            else:
                # User wants to select a new file
                file_path, _ = QFileDialog.getOpenFileName(self, f"Select File for Head {head_id}", "", constants.FILE_FILTER)
                if not file_path:
                    return
        else:
            # Normal file selection
            file_path, _ = QFileDialog.getOpenFileName(self, f"Select File for Head {head_id}", "", constants.FILE_FILTER)
            if not file_path:
                return
        
        # Show card type selector
        card_type_dialog = CardTypeSelector(self)
        if hasattr(self, 'current_theme'):
            stylesheet = DARK_THEME_STYLESHEET if self.current_theme == "dark" else LIGHT_THEME_STYLESHEET
            card_type_dialog.setStyleSheet(stylesheet)
        
        if card_type_dialog.exec() == QDialog.DialogCode.Accepted:
            selected_type_str = card_type_dialog.get_selected_card_type()
            if selected_type_str:
                card_type_map = {
                    "single": CardType.SINGLE,
                    "half": CardType.HALF,
                    "quarter": CardType.QUARTER
                }
                selected_card_type = card_type_map.get(selected_type_str, CardType.HALF)
                
                # Handle logs differently based on whether reloading previous file
                should_restore_state = False  # Track if we should restore scan state
                
                if head.log_data:
                    if is_reloading_previous:
                        # Reloading previous file - ask fresh start or continue
                        msg_box = QMessageBox(self)
                        msg_box.setWindowTitle(f"Resume Session - Head {head_id}")
                        msg_box.setText(f"Previous session logs found ({len(head.log_data)} entries).\n\nDo you want to continue from where you left off or start fresh?")
                        continue_btn = msg_box.addButton("Continue from Last Use", QMessageBox.ButtonRole.AcceptRole)
                        fresh_btn = msg_box.addButton("Fresh Start (Download & Clear)", QMessageBox.ButtonRole.DestructiveRole)
                        cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
                        msg_box.exec()

                        clicked_button = msg_box.clickedButton()
                        if clicked_button == fresh_btn:
                            # Download logs first, then clear
                            if self.download_logs(head_id):
                                head.clear_logs()
                            else:
                                # Download cancelled, don't proceed
                                return
                        elif clicked_button == cancel_btn:
                            return
                        elif clicked_button == continue_btn:
                            should_restore_state = True  # User wants to continue from last position
                    else:
                        # Loading a different file - show export option
                        msg_box = QMessageBox(self)
                        msg_box.setWindowTitle(f"Unsaved Log Data - Head {head_id}")
                        msg_box.setText("Unsaved log data detected. Export before proceeding?")
                        export_btn = msg_box.addButton("Export and Clear", QMessageBox.ButtonRole.AcceptRole)
                        clear_btn = msg_box.addButton("Clear and Continue", QMessageBox.ButtonRole.DestructiveRole)
                        cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
                        msg_box.exec()

                        clicked_button = msg_box.clickedButton()
                        if clicked_button == export_btn:
                            if not self.download_logs(head_id): 
                                return
                            head.clear_logs()
                        elif clicked_button == clear_btn:
                            head.clear_logs()
                        else: 
                            return

                success, message = head.load_file(file_path, selected_card_type)
                if success:
                    # If user chose to continue from last use, restore scan state
                    if should_restore_state:
                        head.restore_scan_state_from_logs()
                        QMessageBox.information(self, "Success", f"Head {head_id}: {message}\n\nResumed from card index {head.current_card_index + 1}.")
                    else:
                        QMessageBox.information(self, "Success", f"Head {head_id}: {message}")
                else:
                    QMessageBox.critical(self, "Error", f"Head {head_id}: {message}")

    def clear_file(self, head_id):
        """Clear loaded file for specified head"""
        head = self.head_a if head_id == 'A' else self.head_b
        head.stop_scanning()
        head.clear_file()
        QMessageBox.information(self, "Cleared", f"Head {head_id}: File cleared.")

    def preview_file(self, head_id):
        """Preview loaded file for specified head"""
        head = self.head_a if head_id == 'A' else self.head_b
        if not head.expected_cards:
            QMessageBox.warning(self, "Warning", f"Head {head_id}: No file loaded to preview.")
            return
        dialog = PreviewWindow(head.expected_cards, head.card_type, head.scan_direction, self)
        dialog.setWindowTitle(f"Preview - Head {head_id}")
        dialog.exec()

    def toggle_scan_direction(self, head_id):
        """Toggle scan direction for specified head"""
        head = self.head_a if head_id == 'A' else self.head_b
        toggle_btn = getattr(self, f'scan_direction_toggle_{head_id}')
        
        if head.start_card_has_been_scanned and head.current_card_index > 0:
            QMessageBox.warning(
                self, "Cannot Toggle",
                f"Head {head_id}: Direction cannot be changed after scanning has started."
            )
            return
        
        if head.scan_direction == "top_to_bottom":
            head.scan_direction = "bottom_to_top"
            toggle_btn.setText("🔄 Bottom → Top")
            toggle_btn.setChecked(True)
        else:
            head.scan_direction = "top_to_bottom"
            toggle_btn.setText("🔄 Top → Bottom")
            toggle_btn.setChecked(False)
        
        head.current_card_index = 0
        head.start_card_has_been_scanned = False
        head.first_scan_received = True
        head.save_cache()
        head.state_changed.emit()
        
        direction_desc = head.get_scan_direction_description()
        QMessageBox.information(
            self, "Direction Changed",
            f"Head {head_id}: Scan direction changed to {direction_desc}"
        )


    # On-demand scanner methods
    def scan_card_details(self, head_id):
        """Start scanning card details for specified head"""
        head = self.head_a if head_id == 'A' else self.head_b
        head.scan_and_get_card_details()

    def cancel_card_details(self, head_id):
        """Cancel card details scan for specified head"""
        head = self.head_a if head_id == 'A' else self.head_b
        head.cancel_card_details_scan()

    def start_card_counting(self, head_id):
        """Start card counting for specified head"""
        head = self.head_a if head_id == 'A' else self.head_b
        head.start_card_counting()

    def cancel_count_cards(self, head_id):
        """Cancel card counting for specified head"""
        head = self.head_a if head_id == 'A' else self.head_b
        head.cancel_count_card_range_scan()

    # Log management methods
    def download_logs(self, head_id):
        """Export logs for specified head"""
        head = self.head_a if head_id == 'A' else self.head_b
        if not head.log_data:
            QMessageBox.information(self, "Info", f"Head {head_id}: No log data to export.")
            return False
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Save Logs - Head {head_id}",
            f"logs_head_{head_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    if head.card_type == CardType.SINGLE:
                        fieldnames = ['index', 'timestamp', 'scanned_code', 'expected_code', 'status']
                    else:
                        fieldnames = ['index', 'timestamp', 'scanned_code', 'expected_code', 'status', 'scanned_side']
                    
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for log_entry in head.log_data:
                        indexed_entry = {}
                        expected_code = log_entry.get("expected_code", "N/A")
                        display_numcard = "---"
                        
                        for numcard, qr_codes in head.numcard_to_qrs.items():
                            if expected_code in qr_codes:
                                display_numcard = str(numcard)
                                break
                        
                        if display_numcard == "---":
                            if expected_code == "N/A": 
                                display_numcard = "N/A"
                            elif expected_code == "End of Sequence": 
                                display_numcard = "End"

                        indexed_entry['index'] = display_numcard
                        indexed_entry['timestamp'] = "'" + str(log_entry.get('timestamp', ''))
                        indexed_entry['scanned_code'] = "'" + str(log_entry.get('scanned_code', ''))
                        indexed_entry['expected_code'] = "'" + str(log_entry.get('expected_code', ''))
                        indexed_entry['status'] = log_entry.get('status', '')
                        
                        if head.card_type != CardType.SINGLE:
                            indexed_entry['scanned_side'] = log_entry.get('scanned_side', 'N/A')
                        
                        writer.writerow(indexed_entry)

                QMessageBox.information(self, "Success", f"Head {head_id}: Logs saved to {file_path}")
                head.clear_logs()
                return True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Head {head_id}: Error saving file: {e}")
                return False
        return False

    def clear_logs(self, head_id):
        """Download logs and clear for specified head"""
        head = self.head_a if head_id == 'A' else self.head_b
        
        if not head.log_data:
            QMessageBox.information(self, "No Logs", f"Head {head_id}: No logs to clear.")
            return
        
        reply = QMessageBox.question(
            self, 
            "Download and Clear Logs", 
            f"Head {head_id}: This will download the logs and then clear them.\n\nDo you want to continue?"
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Download logs first
            if self.download_logs(head_id):
                # Only clear if download was successful
                head.clear_logs()
                QMessageBox.information(self, "Success", f"Head {head_id}: Logs downloaded and cleared.")
            else:
                # Download was cancelled or failed
                QMessageBox.warning(self, "Cancelled", f"Head {head_id}: Logs were not cleared because download was cancelled.")


    def start_validation_and_switch(self, head_id):
        """Start validation for specified head and switch to scanner logging page"""
        head = self.head_a if head_id == 'A' else self.head_b
        
        # Check if file is loaded
        if not head.expected_cards:
            QMessageBox.warning(self, "No File Loaded", f"Head {head_id}: Please load a job file before starting validation.")
            return
        
        # Check if already scanning
        if head.is_scanning:
            QMessageBox.information(self, "Already Scanning", f"Head {head_id}: Validation is already in progress.")
            # Still switch to scanner logging page
            if self.open_scanner_callback:
                self.open_scanner_callback()
            return
        
        # Check for existing logs (same logic as scanner logging window)
        if head.log_data:
            msg_box = QMessageBox(self)
            head_name = "Head A (Right)" if head_id == 'A' else "Head B (Left)"
            msg_box.setWindowTitle(f"Existing Logs Found - {head_name}")
            msg_box.setText("There are existing logs in the table.")
            msg_box.setInformativeText("Do you want to download and clear the logs before starting a new scan?")
            clear_button = msg_box.addButton("Download, Clear & Start", QMessageBox.ButtonRole.AcceptRole)
            continue_button = msg_box.addButton("Continue with Existing Logs", QMessageBox.ButtonRole.DestructiveRole)
            cancel_button = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            msg_box.exec()

            clicked_button = msg_box.clickedButton()

            if clicked_button == clear_button:
                # Download logs first, then clear and start
                if self.download_logs(head_id):
                    head.clear_logs()
                    head.start_scanning()
                else:
                    # Download cancelled, don't proceed
                    return
            elif clicked_button == continue_button:
                head.start_scanning()
            else:
                # User cancelled
                return
        else:
            # No existing logs, just start scanning
            head.start_scanning()
        
        # Switch to scanner logging page
        if self.open_scanner_callback:
            self.open_scanner_callback()

    # Signal handlers
    def handle_start_card_scan_complete(self, head_id, message, success):
        """Handle card details scan completion"""
        card_num_field = getattr(self, f'card_number_field_{head_id}')
        qr_fields = getattr(self, f'qr_fields_{head_id}')
        position_field = getattr(self, f'position_field_{head_id}')
        status_label = getattr(self, f'card_details_status_{head_id}')
        
        if success:
            lines = message.split('\n')
            head = self.head_a if head_id == 'A' else self.head_b
            qr_labels = CardType.get_qr_labels(head.card_type)
            qr_field_index = 0
            
            for line in lines:
                if line.startswith("Card Number:"):
                    card_num_field.setText(line.split(":", 1)[1].strip())
                elif line.startswith("Position:"):
                    position_field.setText(line.split(":", 1)[1].strip())
                else:
                    for label in qr_labels:
                        if line.startswith(f"{label}:"):
                            if qr_field_index < len(qr_fields):
                                qr_fields[qr_field_index].setText(line.split(":", 1)[1].strip())
                                qr_field_index += 1
                            break
            
            status_label.setText("Card details loaded successfully.")
        else:
            card_num_field.clear()
            for qr_field in qr_fields:
                qr_field.clear()
            position_field.clear()
            status_label.setText(message)
        
        self.update_ui(head_id)

    def handle_card_count_update(self, head_id, type, message):
        """Handle card count updates"""
        if type == 'first_card':
            getattr(self, f'first_card_field_{head_id}').setText(message)
        elif type == 'last_card':
            getattr(self, f'last_card_field_{head_id}').setText(message)
        elif type == 'total':
            getattr(self, f'total_count_field_{head_id}').setText(message)
        elif type == 'error':
            QMessageBox.warning(self, "Error", f"Head {head_id}: {message}")
        elif type == 'clear':
            getattr(self, f'first_card_field_{head_id}').clear()
            getattr(self, f'last_card_field_{head_id}').clear()
            getattr(self, f'total_count_field_{head_id}').clear()
            getattr(self, f'card_count_status_{head_id}').setText("Click 'Count Range' to begin.")

    def handle_ondemand_scan_status(self, head_id, status, message):
        """Handle on-demand scan status updates"""
        head = self.head_a if head_id == 'A' else self.head_b
        
        if status == 'active':
            if head.is_waiting_for_start_card:
                getattr(self, f'card_details_status_{head_id}').setText(message)
                getattr(self, f'scan_card_details_btn_{head_id}').setEnabled(False)
                getattr(self, f'count_cards_btn_{head_id}').setEnabled(False)
                getattr(self, f'cancel_card_details_btn_{head_id}').setVisible(True)
                getattr(self, f'cancel_count_cards_btn_{head_id}').setVisible(False)
            elif head.is_waiting_for_count_card_1 or head.is_waiting_for_count_card_2:
                getattr(self, f'card_count_status_{head_id}').setText(message)
                getattr(self, f'scan_card_details_btn_{head_id}').setEnabled(False)
                getattr(self, f'count_cards_btn_{head_id}').setEnabled(False)
                getattr(self, f'cancel_card_details_btn_{head_id}').setVisible(False)
                getattr(self, f'cancel_count_cards_btn_{head_id}').setVisible(True)
        else:
            getattr(self, f'card_details_status_{head_id}').setText("Click 'Scan Card' to view card information.")
            getattr(self, f'card_count_status_{head_id}').setText("Click 'Count Range' to begin.")
            getattr(self, f'cancel_card_details_btn_{head_id}').setVisible(False)
            getattr(self, f'cancel_count_cards_btn_{head_id}').setVisible(False)
            self.update_ui(head_id)

    def rebuild_card_details_fields(self, head_id, card_type):
        """Rebuild card details fields when card type changes"""
        grid = getattr(self, f'details_fields_grid_{head_id}')
        
        # Clear grid
        while grid.count():
            item = grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Rebuild fields
        grid.addWidget(QLabel("Card Number:"), 0, 0, Qt.AlignmentFlag.AlignLeft)
        card_num_field = QLineEdit()
        card_num_field.setReadOnly(True)
        setattr(self, f'card_number_field_{head_id}', card_num_field)
        grid.addWidget(card_num_field, 0, 1)
        
        qr_labels = CardType.get_qr_labels(card_type)
        qr_fields = []
        for i, label in enumerate(qr_labels, start=1):
            grid.addWidget(QLabel(f"{label}:"), i, 0, Qt.AlignmentFlag.AlignLeft)
            qr_field = QLineEdit()
            qr_field.setReadOnly(True)
            grid.addWidget(qr_field, i, 1)
            qr_fields.append(qr_field)
        setattr(self, f'qr_fields_{head_id}', qr_fields)
        
        position_row = len(qr_labels) + 1
        grid.addWidget(QLabel("Position:"), position_row, 0, Qt.AlignmentFlag.AlignLeft)
        position_field = QLineEdit()
        position_field.setReadOnly(True)
        setattr(self, f'position_field_{head_id}', position_field)
        grid.addWidget(position_field, position_row, 1)

    def update_ui(self, head_id):
        """Update UI for specified head"""
        head = self.head_a if head_id == 'A' else self.head_b
        
        has_file = bool(head.expected_cards)
        has_file_path = bool(head.selected_file_path)  # File path exists but may not be loaded
        has_logs = bool(head.log_data)
        has_ondemand = bool(head.ondemand_port_reader)
        is_waiting = head.is_waiting_for_start_card or head.is_waiting_for_count_card_1 or head.is_waiting_for_count_card_2
        is_scanning = head.is_scanning
        
        getattr(self, f'preview_btn_{head_id}').setEnabled(has_file)
        getattr(self, f'clear_btn_{head_id}').setEnabled(has_file or has_file_path)
        getattr(self, f'scan_card_details_btn_{head_id}').setEnabled(has_file and has_ondemand and not is_waiting and not is_scanning)
        getattr(self, f'count_cards_btn_{head_id}').setEnabled(has_file and has_ondemand and not is_waiting)
        getattr(self, f'download_btn_{head_id}').setEnabled(has_logs)
        getattr(self, f'clear_logs_btn_{head_id}').setEnabled(has_logs)
        
        # Update start validation button
        start_btn = getattr(self, f'start_validation_btn_{head_id}')
        start_btn.setEnabled(has_file)
        if is_scanning:
            start_btn.setText(f"▶ Validation Running - Head {head_id}")
        else:
            start_btn.setText(f"▶ Start Validation - Head {head_id}")
        
        # Update checksum combo box
        checksum_combo = getattr(self, f'checksum_combo_{head_id}')
        checksum_combo.setCurrentIndex(head.checksum_digits)
        
        # Update file status
        file_status = getattr(self, f'file_status_{head_id}')
        if has_file:
            file_status.setText(f"Active: {os.path.basename(head.selected_file_path)}")
        elif has_file_path:
            # File path exists but not loaded (e.g., after crash/restart)
            file_status.setText(f"Not loaded: {os.path.basename(head.selected_file_path)} (Click 'Load File' to continue)")
        else:
            file_status.setText("No job file loaded.")
        
        # Update statistics
        total = len(head.log_data)
        
        # Count successful scans: "OK" or "OK (JUMPED)"
        ok = len([log for log in head.log_data if log["status"] in ("OK", "OK (JUMPED)")])
        
        # Count skipped cards: status is exactly "SKIPPED"
        skipped = len([log for log in head.log_data if log["status"] == "SKIPPED"])
        
        # Count failed scans: "NOT OK" and other error statuses (NO FILE, EXTRA SCAN, NOT IN SEQUENCE)
        error = len([log for log in head.log_data if log["status"] in ("NOT OK", "NO FILE", "EXTRA SCAN", "NOT IN SEQUENCE")])
        
        getattr(self, f'total_scanned_label_{head_id}').setText(str(total))
        getattr(self, f'scanned_ok_label_{head_id}').setText(str(ok))
        getattr(self, f'error_not_ok_label_{head_id}').setText(str(error))
        getattr(self, f'skipped_label_{head_id}').setText(str(skipped))
        
        # Update scan direction toggle
        toggle = getattr(self, f'scan_direction_toggle_{head_id}')
        if head.scan_direction == "bottom_to_top":
            toggle.setText("🔄 Bottom → Top")
            toggle.setChecked(True)
        else:
            toggle.setText("🔄 Top → Bottom")
            toggle.setChecked(False)

    def update_theme(self, theme_name):
        """Update theme for window"""
        self.current_theme = theme_name
        stylesheet = DARK_THEME_STYLESHEET if theme_name == "dark" else LIGHT_THEME_STYLESHEET
        self.setStyleSheet(stylesheet)
        for widget in self.findChildren(QWidget):
            widget.style().unpolish(widget)
            widget.style().polish(widget)
