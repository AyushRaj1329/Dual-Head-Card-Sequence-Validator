# src/ui/scanner_logging.py
import sys
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QAbstractItemView, QStackedLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QApplication, QGraphicsRotation, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor, QMovie, QTransform
from .styles import DARK_THEME_STYLESHEET, LIGHT_THEME_STYLESHEET

from .widgets import ClockWidget, ApprovalDialog

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class ScannerLoggingWindow(QMainWindow):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.setWindowTitle("Live Scanner Feed & Validation Log")
        
        self.update_theme(self.app_state.current_theme) # Set initial theme
        self.app_state.theme_changed.connect(self.update_theme) # Connect to theme changes

        # Pagination variables - Initialized first
        self.current_page = 0
        self.items_per_page = 100
        self.total_log_entries = []
        self.filtered_log_entries = []
        self.is_searching = False

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(25)

        self.create_header(main_layout)
        self.create_scanner_section(main_layout)
        self.create_validation_log(main_layout) # This creates self.log_table and pagination buttons

        # Connect pagination buttons - after they are created
        self.first_page_button.clicked.connect(self.go_to_first_page)
        self.prev_page_button.clicked.connect(self.go_to_previous_page)
        self.next_page_button.clicked.connect(self.go_to_next_page)
        self.last_page_button.clicked.connect(self.go_to_last_page)

        self.app_state.log_updated.connect(self.on_log_updated)
        self.app_state.log_cleared.connect(self.on_log_cleared)
        self.app_state.state_changed.connect(self.update_displays)
        self.app_state.card_type_changed.connect(self.rebuild_log_table)

        # --- MODIFIED: Connection for the "not found" alert is removed ---
        self.app_state.mismatch_found_in_sequence.connect(self.show_approval_dialog)

        # Manually populate logs if they exist from cache
        if self.app_state.log_data:
            self.on_log_updated(self.app_state.log_data)

        self.update_displays()

    def on_log_updated(self, new_entries):
        self.total_log_entries.extend(new_entries)
        self.filtered_log_entries.extend(new_entries) # For now, filtered is all
        self.update_pagination_controls()
        self.display_current_page()

    def on_log_cleared(self):
        self.total_log_entries = []
        self.filtered_log_entries = []
        self.current_page = 0
        self.update_pagination_controls()
        self.display_current_page()

    def show_approval_dialog(self, scanned_code, num_skipped, future_index):
        dialog = ApprovalDialog(
            "Sequence Mismatch",
            f"The scanned card ({scanned_code}) was found {num_skipped} position(s) ahead of the expected sequence. Would you like to advance the sequence to this card?",
            parent=self
        )
        approved = dialog.exec()

        if approved:
            self.stacked_layout.setCurrentIndex(1) # Show loading indicator
            QApplication.processEvents() # Ensure UI updates

        # Call the async resolve_mismatch.
        # If not approved, it will still run in a thread, but will be very fast.
        self.app_state.resolve_mismatch(scanned_code, approved, future_index)

    def start_scanning_clicked(self):
        if self.app_state.log_data:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Existing Logs Found")
            msg_box.setText("There are existing logs in the table.")
            msg_box.setInformativeText("There are existing logs in the table.\nDo you want to clear the logs before starting a new scan?\n\nYou can save the logs from the File & Log Management window.")
            clear_button = msg_box.addButton("Clear Logs and Start", QMessageBox.ButtonRole.AcceptRole)
            continue_button = msg_box.addButton("Continue with Existing Logs", QMessageBox.ButtonRole.DestructiveRole)
            cancel_button = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            msg_box.exec()

            clicked_button = msg_box.clickedButton()

            if clicked_button == clear_button:
                self.app_state.clear_logs()
                self.app_state.start_scanning()
            elif clicked_button == continue_button:
                self.app_state.start_scanning()
            else: # Cancel
                return
        else:
            self.app_state.start_scanning()

    def create_header(self, parent_layout):
        layout = QHBoxLayout()
        title = QLabel("Live Scanner Feed & Validation Log")
        title.setObjectName("h1")

        self.start_btn = QPushButton("Start Validation")
        self.start_btn.setObjectName("primary")
        self.start_btn.clicked.connect(self.start_scanning_clicked)

        self.stop_btn = QPushButton("Stop Validation")
        self.stop_btn.setObjectName("secondary")
        self.stop_btn.clicked.connect(self.app_state.stop_scanning)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(ClockWidget())
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        parent_layout.addLayout(layout)

    def create_scanner_section(self, parent_layout):
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(25,20,25,25)

        columns_layout = QGridLayout()
        columns_layout.setSpacing(25)
        self.scanner_input_label = QLabel()
        self.current_card_label = QLabel()
        self.next_card_label = QLabel()

        columns_layout.addWidget(self.create_display_column("Last Scanned ID", self.scanner_input_label), 0, 0)
        columns_layout.addWidget(self.create_display_column("Previous Validated ID", self.current_card_label), 0, 1)
        columns_layout.addWidget(self.create_display_column("Next Expected ID", self.next_card_label), 0, 2)

        layout.addLayout(columns_layout)
        parent_layout.addWidget(frame)

    def create_display_column(self, title_text, data_label):
        column = QFrame()
        column.setObjectName("accentPanel")
        layout = QVBoxLayout(column)
        layout.setSpacing(5)
        title = QLabel(title_text)
        title.setObjectName("subtitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        data_label.setObjectName("accent")
        data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        data_label.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(data_label)
        return column

    def create_validation_log(self, parent_layout):
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(25,20,25,25)

        header_layout = QHBoxLayout()
        title = QLabel("Scan Validation Log")
        title.setObjectName("h2")

        header_layout.addWidget(title)
        header_layout.addStretch()

        self.log_table = QTableWidget()
        self.setup_log_table_columns()
        self.log_table.setAlternatingRowColors(True)
        self.log_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        layout.addLayout(header_layout)
        
        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(self.log_table) # Index 0: Log Table

        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        movie = QMovie(resource_path("assets/gear_loader.gif"))
        self.loading_label.setMovie(movie)
        movie.start()
        self.stacked_layout.addWidget(self.loading_label) # Index 1: Loading Indicator

        layout.addLayout(self.stacked_layout)

        pagination_layout = QHBoxLayout()
        self.first_page_button = QPushButton("<< First")
        self.prev_page_button = QPushButton("< Previous")
        self.page_status_label = QLabel("Page 0 of 0")
        self.next_page_button = QPushButton("Next >")
        self.last_page_button = QPushButton("Last >>")

        pagination_layout.addWidget(self.first_page_button)
        pagination_layout.addWidget(self.prev_page_button)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.page_status_label)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.next_page_button)
        pagination_layout.addWidget(self.last_page_button)
        layout.addLayout(pagination_layout)

        parent_layout.addWidget(frame, 1)

    def setup_log_table_columns(self):
        """Setup log table columns based on card type"""
        from ..card_types import CardType
        
        # Single Card: No scan side column (only 1 QR, no sides)
        # Half/Quarter Card: Show scan side column (multiple QRs, sides matter)
        if self.app_state.card_type == CardType.SINGLE:
            self.log_table.setColumnCount(5)
            self.log_table.setHorizontalHeaderLabels(["Entry #", "Time", "Scanned ID", "Expected ID", "Result"])
            header = self.log_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        else:  # Half or Quarter Card
            self.log_table.setColumnCount(6)
            self.log_table.setHorizontalHeaderLabels(["Entry #", "Time", "Scanned ID", "Expected ID", "Result", "Scan Side"])
            header = self.log_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
    
    def rebuild_log_table(self, card_type):
        """Rebuild log table when card type changes"""
        self.setup_log_table_columns()
        self.display_current_page()

    def display_current_page(self):
        self.log_table.setUpdatesEnabled(False)
        self.log_table.setRowCount(0)

        start_index = self.current_page * self.items_per_page
        end_index = start_index + self.items_per_page
        entries_to_display = self.filtered_log_entries[start_index:end_index]

        for i, log_entry in enumerate(entries_to_display):
            row_position = self.log_table.rowCount()
            self.log_table.insertRow(row_position)

            expected_code = log_entry["expected_code"]
            display_numcard = "---"

            # Find the numcard by searching all QR codes
            found_num = False
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

            self.log_table.setItem(row_position, 0, QTableWidgetItem(display_numcard))
            self.log_table.setItem(row_position, 1, QTableWidgetItem(log_entry["timestamp"]))
            self.log_table.setItem(row_position, 2, QTableWidgetItem(log_entry["scanned_code"]))
            self.log_table.setItem(row_position, 3, QTableWidgetItem(log_entry["expected_code"]))

            status_item = QTableWidgetItem(log_entry["status"])

            if "NOT OK" in log_entry["status"]:
                status_item.setForeground(QColor("#e74c3c"))
            elif "SKIPPED" in log_entry["status"]:
                status_item.setForeground(QColor("#f39c12"))
            elif "OK" in log_entry["status"]:
                status_item.setForeground(QColor("#2ecc71"))

            self.log_table.setItem(row_position, 4, status_item)
            
            # Add scan side column only for Half and Quarter cards
            from ..card_types import CardType
            if self.app_state.card_type != CardType.SINGLE:
                self.log_table.setItem(row_position, 5, QTableWidgetItem(log_entry.get("scanned_side", "N/A")))

        total_items = len(self.filtered_log_entries)
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        if self.current_page == total_pages - 1:
            self.log_table.scrollToBottom()

        self.log_table.setUpdatesEnabled(True)
        self.log_table.viewport().update()

        self.stacked_layout.setCurrentIndex(0)

    def update_pagination_controls(self):
        total_items = len(self.filtered_log_entries)
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        if total_pages == 0:
            total_pages = 1

        self.page_status_label.setText(f"Page {self.current_page + 1} of {total_pages}")

        self.first_page_button.setEnabled(self.current_page > 0)
        self.prev_page_button.setEnabled(self.current_page > 0)
        self.next_page_button.setEnabled(self.current_page < total_pages - 1)
        self.last_page_button.setEnabled(self.current_page < total_pages - 1)

    def go_to_first_page(self):
        self.current_page = 0
        self.display_current_page()
        self.update_pagination_controls()

    def go_to_previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.display_current_page()
            self.update_pagination_controls()

    def go_to_next_page(self):
        total_items = len(self.filtered_log_entries)
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.display_current_page()
            self.update_pagination_controls()

    def go_to_last_page(self):
        total_items = len(self.filtered_log_entries)
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        self.current_page = total_pages - 1
        self.display_current_page()
        self.update_pagination_controls()

    def update_displays(self):
        is_scanning = self.app_state.is_scanning
        has_port = bool(self.app_state.selected_com_port)
        has_file = bool(self.app_state.expected_cards)

        self.start_btn.setEnabled(not is_scanning and has_port and has_file)
        self.stop_btn.setEnabled(is_scanning)

        idx = self.app_state.current_card_index
        cards = self.app_state.expected_cards
        
        # Get the actual card index based on scan direction
        if self.app_state.scan_direction == "bottom_to_top" and cards:
            actual_idx = len(cards) - 1 - idx
        else:
            actual_idx = idx
        
        scan_side_index = 1 if self.app_state.scan_side == 'left' else 2

        if cards and idx > 0 and actual_idx >= 0 and actual_idx < len(cards):
            prev_actual_idx = len(cards) - idx if self.app_state.scan_direction == "bottom_to_top" else idx - 1
            if prev_actual_idx >= 0 and prev_actual_idx < len(cards):
                self.current_card_label.setText(cards[prev_actual_idx][scan_side_index])
            else:
                self.current_card_label.setText("N/A")
        elif has_file and idx == 0:
            self.current_card_label.setText("N/A")
        else:
            self.current_card_label.setText("No file loaded")

        if cards and idx < len(cards) and actual_idx >= 0 and actual_idx < len(cards):
            if self.app_state.start_card_has_been_scanned:
                self.next_card_label.setText(cards[actual_idx][scan_side_index])
            else:
                self.next_card_label.setText("Start scanning to set start card")
        elif has_file and self.app_state.start_card_has_been_scanned:
            self.next_card_label.setText("End of Sequence")
        elif has_file:
            self.next_card_label.setText("Start scanning to set start card")
        else:
            self.next_card_label.setText("No file loaded")

        if self.app_state.log_data:
            last_log = self.app_state.log_data[-1]
            self.scanner_input_label.setText(last_log["scanned_code"])
        else:
            self.scanner_input_label.setText("Awaiting Scan Input...")

    def perform_search(self, search_text):
        pass

    def update_theme(self, theme_name):
        if theme_name == "dark":
            self.setStyleSheet(DARK_THEME_STYLESHEET)
        else:
            self.setStyleSheet(LIGHT_THEME_STYLESHEET)
        # Re-polish all widgets to apply new stylesheet
        for widget in self.findChildren(QWidget):
            widget.style().unpolish(widget)
            widget.style().polish(widget)
