# src/ui/scanner_logging_dual.py
import sys
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QAbstractItemView, QStackedLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QApplication, QGridLayout, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QMovie
from .styles import DARK_THEME_STYLESHEET, LIGHT_THEME_STYLESHEET
from .widgets import ClockWidget, ApprovalDialog

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ScannerLoggingDualWindow(QMainWindow):
    def __init__(self, dual_head_manager):
        super().__init__()
        self.dual_head_manager = dual_head_manager
        self.head_a = dual_head_manager.head_a
        self.head_b = dual_head_manager.head_b
        
        self.setWindowTitle("Live Scanner Feed & Validation Log - Dual Head")
        
        # Set initial theme
        self.update_theme(self.head_a.current_theme)
        self.head_a.theme_changed.connect(self.update_theme)

        # Pagination variables for both heads
        self.head_a_current_page = 0
        self.head_b_current_page = 0
        self.items_per_page = 100
        
        self.head_a_total_log_entries = []
        self.head_a_filtered_log_entries = []
        self.head_b_total_log_entries = []
        self.head_b_filtered_log_entries = []

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(25)

        # Header
        self.create_header(main_layout)

        # Split view for Head B (left) and Head A (right)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Head B (Left) - Blue
        head_b_widget = self.create_head_section("Head B (Left)", self.head_b, "head_b")
        splitter.addWidget(head_b_widget)
        
        # Head A (Right) - Green
        head_a_widget = self.create_head_section("Head A (Right)", self.head_a, "head_a")
        splitter.addWidget(head_a_widget)
        
        splitter.setSizes([500, 500])
        main_layout.addWidget(splitter, 1)

        # Connect signals for both heads
        self.connect_head_signals(self.head_a, "head_a")
        self.connect_head_signals(self.head_b, "head_b")

        # Manually populate logs if they exist from cache
        if self.head_a.log_data:
            self.on_log_updated(self.head_a.log_data, "head_a")
        if self.head_b.log_data:
            self.on_log_updated(self.head_b.log_data, "head_b")

        self.update_displays("head_a")
        self.update_displays("head_b")

    def create_header(self, parent_layout):
        layout = QHBoxLayout()
        title = QLabel("Live Scanner Feed & Validation Log - Dual Head")
        title.setObjectName("h1")

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(ClockWidget())
        parent_layout.addLayout(layout)

    def create_head_section(self, title, app_state, head_id):
        """Create a complete section for one head"""
        container = QFrame()
        container.setObjectName("panel")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 15, 20, 20)
        layout.setSpacing(20)

        # Head title with color
        head_label = QLabel(title)
        head_label.setObjectName("h2")
        if head_id == "head_a":
            head_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        else:
            head_label.setStyleSheet("color: #3498db; font-weight: bold;")

        # Control buttons
        button_layout = QHBoxLayout()
        start_btn = QPushButton("Start Validation")
        start_btn.setObjectName("primary")
        start_btn.clicked.connect(lambda: self.start_scanning_clicked(app_state, head_id))
        
        stop_btn = QPushButton("Stop Validation")
        stop_btn.setObjectName("secondary")
        stop_btn.clicked.connect(app_state.stop_scanning)
        
        button_layout.addWidget(start_btn)
        button_layout.addWidget(stop_btn)
        
        # Store buttons for later access
        if head_id == "head_a":
            self.head_a_start_btn = start_btn
            self.head_a_stop_btn = stop_btn
        else:
            self.head_b_start_btn = start_btn
            self.head_b_stop_btn = stop_btn

        layout.addWidget(head_label)
        layout.addLayout(button_layout)

        # Scanner section
        self.create_scanner_section(layout, app_state, head_id)

        # Validation log
        self.create_validation_log(layout, app_state, head_id)

        return container

    def create_scanner_section(self, parent_layout, app_state, head_id):
        frame = QFrame()
        frame.setObjectName("accentPanel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)

        columns_layout = QGridLayout()
        columns_layout.setSpacing(15)
        
        scanner_input_label = QLabel()
        current_card_label = QLabel()
        next_card_label = QLabel()

        # Store labels for later access
        if head_id == "head_a":
            self.head_a_scanner_input_label = scanner_input_label
            self.head_a_current_card_label = current_card_label
            self.head_a_next_card_label = next_card_label
        else:
            self.head_b_scanner_input_label = scanner_input_label
            self.head_b_current_card_label = current_card_label
            self.head_b_next_card_label = next_card_label

        columns_layout.addWidget(self.create_display_column("Last Scanned ID", scanner_input_label), 0, 0)
        columns_layout.addWidget(self.create_display_column("Previous Validated ID", current_card_label), 0, 1)
        columns_layout.addWidget(self.create_display_column("Next Expected ID", next_card_label), 0, 2)

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

    def create_validation_log(self, parent_layout, app_state, head_id):
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)

        header_layout = QHBoxLayout()
        title = QLabel("Scan Validation Log")
        title.setObjectName("subtitle")
        header_layout.addWidget(title)
        header_layout.addStretch()

        log_table = QTableWidget()
        self.setup_log_table_columns(log_table, app_state)
        log_table.setAlternatingRowColors(True)
        log_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        layout.addLayout(header_layout)
        
        stacked_layout = QStackedLayout()
        stacked_layout.addWidget(log_table)

        loading_label = QLabel()
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        movie = QMovie(resource_path("assets/gear_loader.gif"))
        loading_label.setMovie(movie)
        movie.start()
        stacked_layout.addWidget(loading_label)

        layout.addLayout(stacked_layout)

        # Pagination controls
        pagination_layout = QHBoxLayout()
        first_page_button = QPushButton("<<")
        prev_page_button = QPushButton("<")
        page_status_label = QLabel("Page 0 of 0")
        next_page_button = QPushButton(">")
        last_page_button = QPushButton(">>")

        pagination_layout.addWidget(first_page_button)
        pagination_layout.addWidget(prev_page_button)
        pagination_layout.addStretch()
        pagination_layout.addWidget(page_status_label)
        pagination_layout.addStretch()
        pagination_layout.addWidget(next_page_button)
        pagination_layout.addWidget(last_page_button)
        layout.addLayout(pagination_layout)

        # Store references for later access
        if head_id == "head_a":
            self.head_a_log_table = log_table
            self.head_a_stacked_layout = stacked_layout
            self.head_a_first_page_button = first_page_button
            self.head_a_prev_page_button = prev_page_button
            self.head_a_page_status_label = page_status_label
            self.head_a_next_page_button = next_page_button
            self.head_a_last_page_button = last_page_button
        else:
            self.head_b_log_table = log_table
            self.head_b_stacked_layout = stacked_layout
            self.head_b_first_page_button = first_page_button
            self.head_b_prev_page_button = prev_page_button
            self.head_b_page_status_label = page_status_label
            self.head_b_next_page_button = next_page_button
            self.head_b_last_page_button = last_page_button

        # Connect pagination buttons
        first_page_button.clicked.connect(lambda: self.go_to_first_page(head_id))
        prev_page_button.clicked.connect(lambda: self.go_to_previous_page(head_id))
        next_page_button.clicked.connect(lambda: self.go_to_next_page(head_id))
        last_page_button.clicked.connect(lambda: self.go_to_last_page(head_id))

        parent_layout.addWidget(frame, 1)

    def setup_log_table_columns(self, log_table, app_state):
        """Setup log table columns based on card type"""
        from ..card_types import CardType
        
        if app_state.card_type == CardType.SINGLE:
            log_table.setColumnCount(5)
            log_table.setHorizontalHeaderLabels(["Entry #", "Time", "Scanned ID", "Expected ID", "Result"])
            header = log_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        else:
            log_table.setColumnCount(6)
            log_table.setHorizontalHeaderLabels(["Entry #", "Time", "Scanned ID", "Expected ID", "Result", "Scan Side"])
            header = log_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

    def connect_head_signals(self, app_state, head_id):
        """Connect signals for a specific head"""
        app_state.log_updated.connect(lambda entries: self.on_log_updated(entries, head_id))
        app_state.log_cleared.connect(lambda: self.on_log_cleared(head_id))
        app_state.state_changed.connect(lambda: self.update_displays(head_id))
        app_state.card_type_changed.connect(lambda card_type: self.rebuild_log_table(card_type, head_id))
        app_state.mismatch_found_in_sequence.connect(
            lambda scanned_code, num_skipped, future_index: self.show_approval_dialog(
                scanned_code, num_skipped, future_index, app_state, head_id
            )
        )

    def on_log_updated(self, new_entries, head_id):
        if head_id == "head_a":
            self.head_a_total_log_entries.extend(new_entries)
            self.head_a_filtered_log_entries.extend(new_entries)
            total_items = len(self.head_a_filtered_log_entries)
            total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
            self.head_a_current_page = max(0, total_pages - 1)
        else:
            self.head_b_total_log_entries.extend(new_entries)
            self.head_b_filtered_log_entries.extend(new_entries)
            total_items = len(self.head_b_filtered_log_entries)
            total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
            self.head_b_current_page = max(0, total_pages - 1)
        
        self.update_pagination_controls(head_id)
        self.display_current_page(head_id)

    def on_log_cleared(self, head_id):
        if head_id == "head_a":
            self.head_a_total_log_entries = []
            self.head_a_filtered_log_entries = []
            self.head_a_current_page = 0
        else:
            self.head_b_total_log_entries = []
            self.head_b_filtered_log_entries = []
            self.head_b_current_page = 0
        
        self.update_pagination_controls(head_id)
        self.display_current_page(head_id)

    def show_approval_dialog(self, scanned_code, num_skipped, future_index, app_state, head_id):
        head_name = "Head A (Right)" if head_id == "head_a" else "Head B (Left)"
        dialog = ApprovalDialog(
            f"Sequence Mismatch - {head_name}",
            f"The scanned card ({scanned_code}) was found {num_skipped} position(s) ahead of the expected sequence. Would you like to advance the sequence to this card?",
            parent=self
        )
        approved = dialog.exec()

        if approved:
            stacked_layout = self.head_a_stacked_layout if head_id == "head_a" else self.head_b_stacked_layout
            stacked_layout.setCurrentIndex(1)
            QApplication.processEvents()

        app_state.resolve_mismatch(scanned_code, approved, future_index)

    def start_scanning_clicked(self, app_state, head_id):
        if app_state.log_data:
            msg_box = QMessageBox(self)
            head_name = "Head A (Right)" if head_id == "head_a" else "Head B (Left)"
            msg_box.setWindowTitle(f"Existing Logs Found - {head_name}")
            msg_box.setText("There are existing logs in the table.")
            msg_box.setInformativeText("Do you want to clear the logs before starting a new scan?\n\nYou can save the logs from the File & Log Management window.")
            clear_button = msg_box.addButton("Clear Logs and Start", QMessageBox.ButtonRole.AcceptRole)
            continue_button = msg_box.addButton("Continue with Existing Logs", QMessageBox.ButtonRole.DestructiveRole)
            cancel_button = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            msg_box.exec()

            clicked_button = msg_box.clickedButton()

            if clicked_button == clear_button:
                app_state.clear_logs()
                app_state.start_scanning()
            elif clicked_button == continue_button:
                app_state.start_scanning()
        else:
            app_state.start_scanning()

    def display_current_page(self, head_id):
        if head_id == "head_a":
            log_table = self.head_a_log_table
            app_state = self.head_a
            current_page = self.head_a_current_page
            filtered_entries = self.head_a_filtered_log_entries
        else:
            log_table = self.head_b_log_table
            app_state = self.head_b
            current_page = self.head_b_current_page
            filtered_entries = self.head_b_filtered_log_entries

        log_table.setUpdatesEnabled(False)
        log_table.setRowCount(0)

        start_index = current_page * self.items_per_page
        end_index = start_index + self.items_per_page
        entries_to_display = filtered_entries[start_index:end_index]

        for i, log_entry in enumerate(entries_to_display):
            row_position = log_table.rowCount()
            log_table.insertRow(row_position)

            expected_code = log_entry["expected_code"]
            display_numcard = "---"

            found_num = False
            for numcard, qr_codes in app_state.numcard_to_qrs.items():
                if expected_code in qr_codes:
                    display_numcard = str(numcard)
                    found_num = True
                    break
            
            if not found_num:
                if expected_code == "N/A":
                    display_numcard = "N/A"
                elif expected_code == "End of Sequence":
                    display_numcard = "End"

            log_table.setItem(row_position, 0, QTableWidgetItem(display_numcard))
            log_table.setItem(row_position, 1, QTableWidgetItem(log_entry["timestamp"]))
            log_table.setItem(row_position, 2, QTableWidgetItem(log_entry["scanned_code"]))
            log_table.setItem(row_position, 3, QTableWidgetItem(log_entry["expected_code"]))

            status_item = QTableWidgetItem(log_entry["status"])

            if "NOT OK" in log_entry["status"]:
                status_item.setForeground(QColor("#e74c3c"))
            elif "SKIPPED" in log_entry["status"]:
                status_item.setForeground(QColor("#f39c12"))
            elif "OK" in log_entry["status"]:
                status_item.setForeground(QColor("#2ecc71"))

            log_table.setItem(row_position, 4, status_item)
            
            from ..card_types import CardType
            if app_state.card_type != CardType.SINGLE:
                log_table.setItem(row_position, 5, QTableWidgetItem(log_entry.get("scanned_side", "N/A")))

        total_items = len(filtered_entries)
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        if current_page == total_pages - 1:
            log_table.scrollToBottom()

        log_table.setUpdatesEnabled(True)
        log_table.viewport().update()

        stacked_layout = self.head_a_stacked_layout if head_id == "head_a" else self.head_b_stacked_layout
        stacked_layout.setCurrentIndex(0)

    def update_pagination_controls(self, head_id):
        if head_id == "head_a":
            current_page = self.head_a_current_page
            filtered_entries = self.head_a_filtered_log_entries
            page_status_label = self.head_a_page_status_label
            first_page_button = self.head_a_first_page_button
            prev_page_button = self.head_a_prev_page_button
            next_page_button = self.head_a_next_page_button
            last_page_button = self.head_a_last_page_button
        else:
            current_page = self.head_b_current_page
            filtered_entries = self.head_b_filtered_log_entries
            page_status_label = self.head_b_page_status_label
            first_page_button = self.head_b_first_page_button
            prev_page_button = self.head_b_prev_page_button
            next_page_button = self.head_b_next_page_button
            last_page_button = self.head_b_last_page_button

        total_items = len(filtered_entries)
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        if total_pages == 0:
            total_pages = 1

        page_status_label.setText(f"Page {current_page + 1} of {total_pages}")

        first_page_button.setEnabled(current_page > 0)
        prev_page_button.setEnabled(current_page > 0)
        next_page_button.setEnabled(current_page < total_pages - 1)
        last_page_button.setEnabled(current_page < total_pages - 1)

    def go_to_first_page(self, head_id):
        if head_id == "head_a":
            self.head_a_current_page = 0
        else:
            self.head_b_current_page = 0
        self.display_current_page(head_id)
        self.update_pagination_controls(head_id)

    def go_to_previous_page(self, head_id):
        if head_id == "head_a":
            if self.head_a_current_page > 0:
                self.head_a_current_page -= 1
        else:
            if self.head_b_current_page > 0:
                self.head_b_current_page -= 1
        self.display_current_page(head_id)
        self.update_pagination_controls(head_id)

    def go_to_next_page(self, head_id):
        if head_id == "head_a":
            filtered_entries = self.head_a_filtered_log_entries
            current_page = self.head_a_current_page
        else:
            filtered_entries = self.head_b_filtered_log_entries
            current_page = self.head_b_current_page

        total_items = len(filtered_entries)
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        if current_page < total_pages - 1:
            if head_id == "head_a":
                self.head_a_current_page += 1
            else:
                self.head_b_current_page += 1
        self.display_current_page(head_id)
        self.update_pagination_controls(head_id)

    def go_to_last_page(self, head_id):
        if head_id == "head_a":
            filtered_entries = self.head_a_filtered_log_entries
        else:
            filtered_entries = self.head_b_filtered_log_entries

        total_items = len(filtered_entries)
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        
        if head_id == "head_a":
            self.head_a_current_page = total_pages - 1
        else:
            self.head_b_current_page = total_pages - 1
        self.display_current_page(head_id)
        self.update_pagination_controls(head_id)

    def update_displays(self, head_id):
        if head_id == "head_a":
            app_state = self.head_a
            start_btn = self.head_a_start_btn
            stop_btn = self.head_a_stop_btn
            scanner_input_label = self.head_a_scanner_input_label
            current_card_label = self.head_a_current_card_label
            next_card_label = self.head_a_next_card_label
        else:
            app_state = self.head_b
            start_btn = self.head_b_start_btn
            stop_btn = self.head_b_stop_btn
            scanner_input_label = self.head_b_scanner_input_label
            current_card_label = self.head_b_current_card_label
            next_card_label = self.head_b_next_card_label

        is_scanning = app_state.is_scanning
        has_port = bool(app_state.main_scanner_config)
        has_file = bool(app_state.expected_cards)

        start_btn.setEnabled(not is_scanning and has_port and has_file)
        stop_btn.setEnabled(is_scanning)

        idx = app_state.current_card_index
        cards = app_state.expected_cards
        
        if app_state.scan_direction == "bottom_to_top" and cards:
            actual_idx = len(cards) - 1 - idx
        else:
            actual_idx = idx
        
        from ..card_types import CardType
        if app_state.card_type == CardType.SINGLE:
            scan_side_index = 1
        elif app_state.card_type == CardType.HALF:
            scan_side_index = 1 if app_state.scan_side == 'left' else 2
        elif app_state.card_type == CardType.QUARTER:
            position_map = {"bottom_left": 1, "top_left": 2, "top_right": 3, "bottom_right": 4}
            scan_side_index = position_map.get(app_state.scan_side, 1)
        else:
            scan_side_index = 1

        if cards and idx > 0 and actual_idx >= 0 and actual_idx < len(cards):
            prev_actual_idx = len(cards) - idx if app_state.scan_direction == "bottom_to_top" else idx - 1
            if prev_actual_idx >= 0 and prev_actual_idx < len(cards):
                current_card_label.setText(cards[prev_actual_idx][scan_side_index])
            else:
                current_card_label.setText("N/A")
        elif has_file and idx == 0:
            current_card_label.setText("N/A")
        else:
            current_card_label.setText("No file loaded")

        if cards and idx < len(cards) and actual_idx >= 0 and actual_idx < len(cards):
            if app_state.start_card_has_been_scanned:
                next_card_label.setText(cards[actual_idx][scan_side_index])
            else:
                next_card_label.setText("Start scanning to set start card")
        elif has_file and app_state.start_card_has_been_scanned:
            next_card_label.setText("End of Sequence")
        elif has_file:
            next_card_label.setText("Start scanning to set start card")
        else:
            next_card_label.setText("No file loaded")

        if app_state.log_data:
            last_log = app_state.log_data[-1]
            scanner_input_label.setText(last_log["scanned_code"])
        else:
            scanner_input_label.setText("Awaiting Scan Input...")

    def rebuild_log_table(self, card_type, head_id):
        """Rebuild log table when card type changes"""
        if head_id == "head_a":
            self.setup_log_table_columns(self.head_a_log_table, self.head_a)
        else:
            self.setup_log_table_columns(self.head_b_log_table, self.head_b)
        self.display_current_page(head_id)

    def update_theme(self, theme_name):
        if theme_name == "dark":
            self.setStyleSheet(DARK_THEME_STYLESHEET)
        else:
            self.setStyleSheet(LIGHT_THEME_STYLESHEET)
        for widget in self.findChildren(QWidget):
            widget.style().unpolish(widget)
            widget.style().polish(widget)
