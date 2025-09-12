# src/ui/file_management.py
import sys, os, csv
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton, QHBoxLayout, 
                             QVBoxLayout, QFrame, QFileDialog, QLineEdit, QMessageBox, QDialog,
                             QTableWidget, QTableWidgetItem, QHeaderView, QListWidget, QDialogButtonBox)

from PyQt6.QtCore import Qt
from .styles import DARK_THEME_STYLESHEET, LIGHT_THEME_STYLESHEET
from .widgets import ClockWidget
import constants

class PreviewWindow(QDialog):
    def __init__(self, expected_cards, parent=None):
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
            table = QTableWidget(len(expected_cards), 3)
            table.setHorizontalHeaderLabels(["Card Number", "Left QR (ICCID)", "Right QR (IMSI)"])
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

            for row, (numcard, left_qr, right_qr) in enumerate(expected_cards):
                table.setItem(row, 0, QTableWidgetItem(str(numcard)))
                table.setItem(row, 1, QTableWidgetItem(str(left_qr)))
                table.setItem(row, 2, QTableWidgetItem(str(right_qr)))
            
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
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(25)

        self.create_header(main_layout)
        self.create_file_operations(main_layout)
        self.create_card_selection(main_layout)
        self.create_log_management(main_layout)
        main_layout.addStretch()

        self.app_state.state_changed.connect(self.update_ui)
        self.app_state.start_card_scan_complete.connect(self.handle_start_card_scan_complete)
        self.app_state.card_count_update.connect(self.handle_card_count_update)
        self.app_state.ondemand_scan_status_update.connect(self.handle_ondemand_scan_status)
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

        scan_layout = QHBoxLayout()
        scan_layout.setSpacing(15)
        self.scan_start_card_btn = QPushButton("Scan Start Card")
        self.scan_start_card_btn.setObjectName("primary")
        self.scan_start_card_btn.clicked.connect(self.app_state.scan_and_set_start_card)
        scan_layout.addWidget(self.scan_start_card_btn)

        scan_layout.addWidget(QLabel("Current Start Card:"))
        self.start_card_display = QLineEdit()
        self.start_card_display.setReadOnly(True)
        scan_layout.addWidget(self.start_card_display, 1)

        count_frame = QFrame()
        count_frame.setObjectName("accentPanel")
        count_layout = QVBoxLayout(count_frame)
        count_layout.setSpacing(10)

        count_actions_layout = QHBoxLayout()
        self.count_cards_btn = QPushButton("Count Card Range")
        self.count_cards_btn.setObjectName("primary")
        self.count_cards_btn.clicked.connect(self.app_state.start_card_counting)
        self.cancel_scan_btn = QPushButton("Cancel Scan")
        self.cancel_scan_btn.setObjectName("secondary")
        self.cancel_scan_btn.clicked.connect(self.app_state.cancel_ondemand_scan)
        self.cancel_scan_btn.setVisible(False)
        count_actions_layout.addWidget(self.count_cards_btn)
        count_actions_layout.addWidget(self.cancel_scan_btn)
        count_actions_layout.addStretch()

        self.card_count_status_label = QLabel("Click a button to start an on-demand scan.")
        self.card_count_status_label.setObjectName("subtitle")

        fields_layout = QHBoxLayout()
        fields_layout.addWidget(QLabel("First Card:"))
        self.first_card_field = QLineEdit()
        self.first_card_field.setReadOnly(True)
        fields_layout.addWidget(self.first_card_field)
        fields_layout.addWidget(QLabel("Last Card:"))
        self.last_card_field = QLineEdit()
        self.last_card_field.setReadOnly(True)
        fields_layout.addWidget(self.last_card_field)
        fields_layout.addWidget(QLabel("Total:"))
        self.total_count_field = QLineEdit()
        self.total_count_field.setReadOnly(True)
        self.total_count_field.setFixedWidth(80)
        fields_layout.addWidget(self.total_count_field)

        count_layout.addLayout(count_actions_layout)
        count_layout.addWidget(self.card_count_status_label)
        count_layout.addLayout(fields_layout)

        layout.addLayout(scan_layout)
        layout.addWidget(count_frame)
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
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(20,20,20,20)
        self.total_scanned_label = QLabel("0")
        self.scanned_ok_label = QLabel("0")
        self.error_not_ok_label = QLabel("0")
        self.skipped_label = QLabel("0")
        stats_layout.addWidget(self.create_stat("Total Scans:", self.total_scanned_label))
        stats_layout.addWidget(self.create_stat("Successful Scans:", self.scanned_ok_label))
        stats_layout.addWidget(self.create_stat("Failed Scans:", self.error_not_ok_label))
        stats_layout.addWidget(self.create_stat("Skipped Entries:", self.skipped_label))
        
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

        self.preview_btn.setEnabled(has_file)
        self.clear_btn.setEnabled(has_file)
        self.scan_start_card_btn.setEnabled(has_file and has_start_card_port and not is_waiting_for_scan)
        self.count_cards_btn.setEnabled(has_file and has_start_card_port and not is_waiting_for_scan)
        self.download_btn.setEnabled(has_logs)
        self.clear_logs_btn.setEnabled(has_logs)
        
        if has_file:
            self.file_status.setText(f"Active Sequence: {os.path.basename(self.app_state.selected_file_path)}")
        else:
            self.file_status.setText("No sequence file loaded.")

        self.start_card_display.setText(self.app_state.start_card_code or "None")

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
        dialog = PreviewWindow(self.app_state.expected_cards, self)
        dialog.exec()

    def handle_start_card_scan_complete(self, message, success):
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Scan Failed", message)
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
        self.card_count_status_label.setText(message)
        if status == 'active':
            self.scan_start_card_btn.setEnabled(False)
            self.count_cards_btn.setEnabled(False)
            self.cancel_scan_btn.setVisible(True)
        else: # idle, complete, or error
            self.cancel_scan_btn.setVisible(False)
            self.update_ui()

    def download_logs(self):
        if not self.app_state.log_data:
            QMessageBox.information(self, "Info", "No log data to download.")
            return False
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Logs", f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "CSV Files (*.csv)")
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['index', 'timestamp', 'scanned_code', 'expected_code', 'status', 'scanned_side'])
                    writer.writeheader()
                    
                    indexed_log_data = []
                    for log_entry in self.app_state.log_data:
                        indexed_entry = log_entry.copy()
                        expected_code = log_entry.get("expected_code", "N/A")
                        display_numcard = "---"
                        found_num = False
                        for numcard, (left_qr, right_qr) in self.app_state.numcard_to_qrs.items():
                            if expected_code == left_qr or expected_code == right_qr:
                                display_numcard = str(numcard)
                                found_num = True
                                break
                        if not found_num:
                            if expected_code == "N/A": display_numcard = "N/A"
                            elif expected_code == "End of Sequence": display_numcard = "End"

                        indexed_entry['index'] = display_numcard
                        indexed_entry['timestamp'] = "'" + str(indexed_entry.get('timestamp', ''))
                        indexed_entry['scanned_code'] = "'" + str(indexed_entry.get('scanned_code', ''))
                        indexed_entry['expected_code'] = "'" + str(indexed_entry.get('expected_code', ''))
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

    def update_theme(self, theme_name):
        if theme_name == "dark":
            self.setStyleSheet(DARK_THEME_STYLESHEET)
        else:
            self.setStyleSheet(LIGHT_THEME_STYLESHEET)
        for widget in self.findChildren(QWidget):
            widget.style().unpolish(widget)
            widget.style().polish(widget)