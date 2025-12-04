# src/ui/file_management.py
import sys, os, csv
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton, QHBoxLayout,
                             QVBoxLayout, QFrame, QFileDialog, QLineEdit, QMessageBox, QDialog,
                             QTableWidget, QTableWidgetItem, QHeaderView, QListWidget, QDialogButtonBox,
                             QSizePolicy, QGridLayout, QScrollArea)

from PyQt6.QtCore import Qt
from .styles import DARK_THEME_STYLESHEET, LIGHT_THEME_STYLESHEET
from .widgets import ClockWidget
import constants
from ..card_types import CardType

class PreviewWindow(QDialog):
    def __init__(self, expected_cards, card_type, parent=None):
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
            # Determine number of columns based on card type
            qr_labels = CardType.get_qr_labels(card_type)
            num_columns = 1 + len(qr_labels)  # Card Number + QR codes
            
            table = QTableWidget(len(expected_cards), num_columns)
            headers = ["Card Number"] + qr_labels
            table.setHorizontalHeaderLabels(headers)
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            for i in range(1, num_columns):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

            for row, card in enumerate(expected_cards):
                numcard = card[0]
                qr_codes = card[1:]
                table.setItem(row, 0, QTableWidgetItem(str(numcard)))
                for col, qr_code in enumerate(qr_codes, start=1):
                    table.setItem(row, col, QTableWidgetItem(str(qr_code)))
            
            layout.addWidget(table)

        self.setMinimumSize(600, 400)

class FileManagementWindow(QMainWindow):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.setWindowTitle("Sequence File Management")
        
        self.update_theme(self.app_state.current_theme)
        self.app_state.theme_changed.connect(self.update_theme)

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(25)

        self.create_header(main_layout)
        self.create_file_operations(main_layout)
        self.create_card_selection(main_layout)
        self.create_log_management(main_layout)
        main_layout.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(central_widget)
        self.setCentralWidget(scroll_area)

        self.app_state.state_changed.connect(self.update_ui)
        self.app_state.start_card_scan_complete.connect(self.handle_start_card_scan_complete)
        self.app_state.card_count_update.connect(self.handle_card_count_update)
        self.app_state.ondemand_scan_status_update.connect(self.handle_ondemand_scan_status)
        self.app_state.card_type_changed.connect(self.rebuild_card_details_fields)
        self.update_ui()

    def create_header(self, parent_layout):
        title = QLabel("File Management")
        title.setObjectName("h1")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0,0,0,10)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(ClockWidget())
        parent_layout.addLayout(header_layout)
        
    def create_file_operations(self, parent_layout):
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)
        title = QLabel("Sequence File Operations")
        title.setObjectName("h2")
        
        file_button = QPushButton("📁 Load Sequence File")
        file_button.setObjectName("primary")
        file_button.clicked.connect(self.select_file)
        
        self.file_status = QLabel()
        self.file_status.setObjectName("subtitle")

        button_layout = QHBoxLayout()
        self.preview_btn = QPushButton("👁 Preview Sequence")
        self.preview_btn.setObjectName("secondary")
        self.preview_btn.clicked.connect(self.preview_file)
        self.clear_btn = QPushButton("🗑 Clear Sequence")
        self.clear_btn.setObjectName("secondary")
        self.clear_btn.clicked.connect(self.clear_file)
        
        button_layout.addWidget(self.preview_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(file_button)
        layout.addWidget(self.file_status)
        layout.addLayout(button_layout)
        parent_layout.addWidget(frame)

    def create_card_selection(self, parent_layout):
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        title = QLabel("Sequence Control Tools")
        title.setObjectName("h2")
        layout.addWidget(title)

        # Card Details Section
        details_frame = QFrame()
        details_frame.setObjectName("accentPanel")
        details_layout = QVBoxLayout(details_frame)
        details_layout.setSpacing(10)

        details_actions_layout = QHBoxLayout()
        self.scan_card_details_btn = QPushButton("Scan Card Details")
        self.scan_card_details_btn.setObjectName("primary")
        self.scan_card_details_btn.clicked.connect(self.app_state.scan_and_get_card_details)
        self.scan_card_details_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.scan_card_details_btn.setMinimumWidth(120)
        
        self.cancel_card_details_btn = QPushButton("Cancel Scan")
        self.cancel_card_details_btn.setObjectName("secondary")
        self.cancel_card_details_btn.clicked.connect(self.app_state.cancel_card_details_scan)
        self.cancel_card_details_btn.setVisible(False)
        self.cancel_card_details_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.cancel_card_details_btn.setMinimumWidth(120)

        details_actions_layout.addWidget(self.scan_card_details_btn)
        details_actions_layout.addWidget(self.cancel_card_details_btn)
        details_actions_layout.addStretch(1)

        self.card_details_status_label = QLabel("Click 'Scan Card Details' to view card information.")
        self.card_details_status_label.setObjectName("subtitle")

        details_fields_layout = QGridLayout()
        details_fields_layout.setSpacing(10)
        
        # Card Number field
        details_fields_layout.addWidget(QLabel("Card Number:"), 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.card_number_field = QLineEdit()
        self.card_number_field.setReadOnly(True)
        details_fields_layout.addWidget(self.card_number_field, 0, 1)
        
        # Dynamic QR fields based on card type
        qr_labels = CardType.get_qr_labels(self.app_state.card_type)
        self.qr_fields = []
        for i, label in enumerate(qr_labels, start=1):
            details_fields_layout.addWidget(QLabel(f"{label}:"), i, 0, alignment=Qt.AlignmentFlag.AlignLeft)
            qr_field = QLineEdit()
            qr_field.setReadOnly(True)
            details_fields_layout.addWidget(qr_field, i, 1)
            self.qr_fields.append(qr_field)
        
        # Position field
        position_row = len(qr_labels) + 1
        details_fields_layout.addWidget(QLabel("Position:"), position_row, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.position_field = QLineEdit()
        self.position_field.setReadOnly(True)
        details_fields_layout.addWidget(self.position_field, position_row, 1)

        # Store references for rebuilding
        self.details_layout = details_layout
        self.details_fields_layout = details_fields_layout
        self.qr_field_labels = []  # Store label widgets for cleanup
        
        details_layout.addLayout(details_actions_layout)
        details_layout.addWidget(self.card_details_status_label)
        details_layout.addLayout(details_fields_layout)
        details_layout.addStretch(1)

        count_frame = QFrame()
        count_frame.setObjectName("accentPanel")
        count_layout = QVBoxLayout(count_frame)
        count_layout.setSpacing(10)

        count_actions_layout = QHBoxLayout()
        self.count_cards_btn = QPushButton("Count Card Range")
        self.count_cards_btn.setObjectName("primary")
        self.count_cards_btn.clicked.connect(self.app_state.start_card_counting)
        self.count_cards_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.count_cards_btn.setMinimumWidth(120)
        
        self.cancel_count_cards_btn = QPushButton("Cancel Scan")
        self.cancel_count_cards_btn.setObjectName("secondary")
        self.cancel_count_cards_btn.clicked.connect(self.app_state.cancel_count_card_range_scan)
        self.cancel_count_cards_btn.setVisible(False)
        self.cancel_count_cards_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.cancel_count_cards_btn.setMinimumWidth(120)

        count_actions_layout.addWidget(self.count_cards_btn)
        count_actions_layout.addWidget(self.cancel_count_cards_btn)
        count_actions_layout.addStretch(1)

        self.card_count_status_label = QLabel("Click a button to start an on-demand scan.")
        self.card_count_status_label.setObjectName("subtitle")

        fields_layout = QGridLayout()
        fields_layout.setSpacing(10)
        
        fields_layout.addWidget(QLabel("First Card:"), 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.first_card_field = QLineEdit()
        self.first_card_field.setReadOnly(True)
        fields_layout.addWidget(self.first_card_field, 0, 1)
        
        fields_layout.addWidget(QLabel("Last Card:"), 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.last_card_field = QLineEdit()
        self.last_card_field.setReadOnly(True)
        fields_layout.addWidget(self.last_card_field, 1, 1)
        
        fields_layout.addWidget(QLabel("Total:"), 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.total_count_field = QLineEdit()
        self.total_count_field.setReadOnly(True)
        fields_layout.addWidget(self.total_count_field, 2, 1)

        count_layout.addLayout(count_actions_layout)
        count_layout.addWidget(self.card_count_status_label)
        count_layout.addLayout(fields_layout)
        count_layout.addStretch(1)

        layout.addWidget(details_frame)
        layout.addWidget(count_frame)
        layout.addStretch(1)
        parent_layout.addWidget(frame)

    def create_log_management(self, parent_layout):
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(25, 20, 25, 20)
        title = QLabel("Validation Log Management")
        title.setObjectName("h2")
        
        button_layout = QHBoxLayout()
        self.download_btn = QPushButton("📥 Export Logs")
        self.download_btn.setObjectName("primary")
        self.download_btn.clicked.connect(self.download_logs)
        self.clear_logs_btn = QPushButton("🗑 Clear Validation Logs")
        self.clear_logs_btn.setObjectName("secondary")
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        button_layout.addWidget(self.download_btn)
        button_layout.addWidget(self.clear_logs_btn)
        button_layout.addStretch()
        
        stats_frame = QFrame()
        stats_frame.setObjectName("accentPanel")
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setContentsMargins(20,20,20,20)
        self.total_scanned_label = QLabel("0")
        self.scanned_ok_label = QLabel("0")
        self.error_not_ok_label = QLabel("0")
        self.skipped_label = QLabel("0")
        stats_layout.addWidget(self.create_stat("Total Scans:", self.total_scanned_label), 0, 0)
        stats_layout.addWidget(self.create_stat("Successful Scans:", self.scanned_ok_label), 0, 1)
        stats_layout.addWidget(self.create_stat("Failed Scans:", self.error_not_ok_label), 1, 0)
        stats_layout.addWidget(self.create_stat("Skipped Entries:", self.skipped_label), 1, 1)
        
        layout.addWidget(title)
        layout.addLayout(button_layout)
        layout.addWidget(stats_frame)
        parent_layout.addWidget(frame)

    def create_stat(self, text, value_label):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel(text)
        label.setObjectName("subtitle")
        value_label.setObjectName("accent")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(value_label)
        return widget
        
    def update_ui(self):
        has_file = bool(self.app_state.expected_cards)
        has_logs = bool(self.app_state.log_data)
        has_start_card_port = bool(self.app_state.start_card_scan_port)

        is_waiting_for_scan = self.app_state.is_waiting_for_start_card or \
                              self.app_state.is_waiting_for_count_card_1 or \
                              self.app_state.is_waiting_for_count_card_2

        is_scanning = self.app_state.is_scanning

        self.preview_btn.setEnabled(has_file)
        self.clear_btn.setEnabled(has_file)
        self.scan_card_details_btn.setEnabled(has_file and has_start_card_port and not is_waiting_for_scan and not is_scanning)
        self.count_cards_btn.setEnabled(has_file and has_start_card_port and not is_waiting_for_scan)
        self.download_btn.setEnabled(has_logs)
        self.clear_logs_btn.setEnabled(has_logs)
        
        if has_file:
            self.file_status.setText(f"Active Sequence: {os.path.basename(self.app_state.selected_file_path)}")
        else:
            self.file_status.setText("No sequence file loaded.")

        total = len(self.app_state.log_data)
        ok = len([log for log in self.app_state.log_data if log["status"] == "OK" or log["status"] == "OK (JUMPED)"])
        skipped = len([log for log in self.app_state.log_data if "SKIPPED" in log["status"]])
        error = len([log for log in self.app_state.log_data if "NOT OK" in log["status"]])

        self.total_scanned_label.setText(str(total))
        self.scanned_ok_label.setText(str(ok))
        self.error_not_ok_label.setText(str(error))
        self.skipped_label.setText(str(skipped))

    def select_file(self):
        self.app_state.stop_scanning()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", constants.FILE_FILTER)
        if file_path:
            if self.app_state.log_data:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Unsaved Log Data Detected")
                msg_box.setText("Unsaved log data from a previous session was detected. Would you like to export it before proceeding, or clear it and continue?")
                download_button = msg_box.addButton("Export and Clear Logs", QMessageBox.ButtonRole.AcceptRole)
                clear_button = msg_box.addButton("Clear Logs and Continue", QMessageBox.ButtonRole.DestructiveRole)
                cancel_button = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
                msg_box.exec()

                clicked_button = msg_box.clickedButton()

                if clicked_button == download_button:
                    if not self.download_logs(): return
                    self.app_state.clear_logs()
                elif clicked_button == clear_button:
                    self.app_state.clear_logs()
                else: return

            success, message = self.app_state.load_file(file_path)
            if success:
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.critical(self, "Error", message)

    def clear_file(self):
        self.app_state.stop_scanning()
        self.app_state.clear_file()
        QMessageBox.information(self, "Cleared", "Loaded file has been cleared.")

    def preview_file(self):
        if not self.app_state.expected_cards:
            QMessageBox.warning(self, "Warning", "No file loaded to preview.")
            return
        dialog = PreviewWindow(self.app_state.expected_cards, self.app_state.card_type, self)
        dialog.exec()

    def handle_start_card_scan_complete(self, message, success):
        if success:
            # Parse the message and populate fields
            lines = message.split('\n')
            qr_labels = CardType.get_qr_labels(self.app_state.card_type)
            qr_field_index = 0
            
            for line in lines:
                if line.startswith("Card Number:"):
                    self.card_number_field.setText(line.split(":", 1)[1].strip())
                elif line.startswith("Position:"):
                    self.position_field.setText(line.split(":", 1)[1].strip())
                else:
                    # Check if this line matches any QR label
                    for label in qr_labels:
                        if line.startswith(f"{label}:"):
                            if qr_field_index < len(self.qr_fields):
                                self.qr_fields[qr_field_index].setText(line.split(":", 1)[1].strip())
                                qr_field_index += 1
                            break
            
            self.card_details_status_label.setText("Card details loaded successfully.")
        else:
            # Clear fields and show error
            self.card_number_field.clear()
            for qr_field in self.qr_fields:
                qr_field.clear()
            self.position_field.clear()
            self.card_details_status_label.setText(message)
        self.update_ui() # Re-enable buttons

    def handle_card_count_update(self, type, message):
        if type == 'first_card':
            self.first_card_field.setText(message)
        elif type == 'last_card':
            self.last_card_field.setText(message)
        elif type == 'total':
            self.total_count_field.setText(message)
        elif type == 'error':
            QMessageBox.warning(self, "Card Count Error", message)
        elif type == 'clear':
            self.first_card_field.clear()
            self.last_card_field.clear()
            self.total_count_field.clear()
            self.card_count_status_label.setText("Click 'Count Card Range' to begin.")

    def handle_ondemand_scan_status(self, status, message):
        if status == 'active':
            # Determine which operation is active and update the appropriate status label
            if self.app_state.is_waiting_for_start_card:
                self.card_details_status_label.setText(message)
                self.scan_card_details_btn.setEnabled(False)
                self.count_cards_btn.setEnabled(False)
                self.cancel_card_details_btn.setVisible(True)
                self.cancel_count_cards_btn.setVisible(False)
            elif self.app_state.is_waiting_for_count_card_1 or self.app_state.is_waiting_for_count_card_2:
                self.card_count_status_label.setText(message)
                self.scan_card_details_btn.setEnabled(False)
                self.count_cards_btn.setEnabled(False)
                self.cancel_card_details_btn.setVisible(False)
                self.cancel_count_cards_btn.setVisible(True)
        else: # idle, complete, or error
            if message:
                # Update the appropriate status label based on which was last active
                if hasattr(self, 'card_details_status_label'):
                    self.card_details_status_label.setText("Click 'Scan Card Details' to view card information.")
                if hasattr(self, 'card_count_status_label'):
                    self.card_count_status_label.setText("Click 'Count Card Range' to begin.")
            self.cancel_card_details_btn.setVisible(False)
            self.cancel_count_cards_btn.setVisible(False)
            self.update_ui()

    def download_logs(self):
        if not self.app_state.log_data:
            QMessageBox.information(self, "Info", "No log data to download.")
            return False
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Logs", f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "CSV Files (*.csv)")
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    # Include scan_side for Half and Quarter cards only
                    if self.app_state.card_type == CardType.SINGLE:
                        fieldnames = ['index', 'timestamp', 'scanned_code', 'expected_code', 'status']
                    else:
                        fieldnames = ['index', 'timestamp', 'scanned_code', 'expected_code', 'status', 'scanned_side']
                    
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    indexed_log_data = []
                    for log_entry in self.app_state.log_data:
                        indexed_entry = {}
                        expected_code = log_entry.get("expected_code", "N/A")
                        display_numcard = "---"
                        found_num = False
                        
                        # Find numcard by searching all QR codes
                        for numcard, qr_codes in self.app_state.numcard_to_qrs.items():
                            if expected_code in qr_codes:
                                display_numcard = str(numcard)
                                found_num = True
                                break
                        
                        if not found_num:
                            if expected_code == "N/A": 
                                display_numcard = "N/A"
                            elif expected_code == "End of Sequence": 
                                display_numcard = "End"

                        indexed_entry['index'] = display_numcard
                        indexed_entry['timestamp'] = "'" + str(log_entry.get('timestamp', ''))
                        indexed_entry['scanned_code'] = "'" + str(log_entry.get('scanned_code', ''))
                        indexed_entry['expected_code'] = "'" + str(log_entry.get('expected_code', ''))
                        indexed_entry['status'] = log_entry.get('status', '')
                        
                        # Add scan_side for Half and Quarter cards
                        if self.app_state.card_type != CardType.SINGLE:
                            indexed_entry['scanned_side'] = log_entry.get('scanned_side', 'N/A')
                        
                        indexed_log_data.append(indexed_entry)

                    writer.writerows(indexed_log_data)
                QMessageBox.information(self, "Success", f"Logs saved to {file_path}")
                self.app_state.clear_logs()
                return True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving file: {e}")
                return False
        return False

    def clear_logs(self):
        reply = QMessageBox.question(self, "Confirm", "Are you sure you want to clear all logs?")
        if reply == QMessageBox.StandardButton.Yes:
            self.app_state.clear_logs()
            QMessageBox.information(self, "Success", "Logs have been cleared.")

    def rebuild_card_details_fields(self, card_type):
        """Rebuild the card details fields when card type changes"""
        # Clear all items from the grid layout
        while self.details_fields_layout.count():
            item = self.details_fields_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Reset lists
        self.qr_fields = []
        self.qr_field_labels = []
        
        # Rebuild the entire grid layout
        # Row 0: Card Number
        card_num_label = QLabel("Card Number:")
        self.details_fields_layout.addWidget(card_num_label, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.card_number_field = QLineEdit()
        self.card_number_field.setReadOnly(True)
        self.details_fields_layout.addWidget(self.card_number_field, 0, 1)
        
        # Rows 1+: Dynamic QR fields based on card type
        qr_labels = CardType.get_qr_labels(card_type)
        for i, label_text in enumerate(qr_labels, start=1):
            label = QLabel(f"{label_text}:")
            self.details_fields_layout.addWidget(label, i, 0, alignment=Qt.AlignmentFlag.AlignLeft)
            self.qr_field_labels.append(label)
            
            qr_field = QLineEdit()
            qr_field.setReadOnly(True)
            self.details_fields_layout.addWidget(qr_field, i, 1)
            self.qr_fields.append(qr_field)
        
        # Last row: Position field
        position_row = len(qr_labels) + 1
        position_label = QLabel("Position:")
        self.details_fields_layout.addWidget(position_label, position_row, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.position_field = QLineEdit()
        self.position_field.setReadOnly(True)
        self.details_fields_layout.addWidget(self.position_field, position_row, 1)
        
        # Update status label
        card_type_names = {
            CardType.SINGLE: "Single Card",
            CardType.HALF: "Half Card",
            CardType.QUARTER: "Quarter Card"
        }
        card_type_name = card_type_names.get(card_type, "Unknown")
        self.card_details_status_label.setText(f"Card type changed to: {card_type_name}. Click 'Scan Card Details' to view card information.")

    def update_theme(self, theme_name):
        if theme_name == "dark":
            self.setStyleSheet(DARK_THEME_STYLESHEET)
        else:
            self.setStyleSheet(LIGHT_THEME_STYLESHEET)
        for widget in self.findChildren(QWidget):
            widget.style().unpolish(widget)
            widget.style().polish(widget)