# src/ui/com_port_setup.py
import sys
import serial.tools.list_ports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QHBoxLayout,
    QVBoxLayout, QComboBox, QTextEdit, QScrollArea, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from .styles import DARK_THEME_STYLESHEET, LIGHT_THEME_STYLESHEET
from .widgets import ClockWidget

class ComPortSetupWindow(QMainWindow):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.setWindowTitle("Serial Port Configuration")
        self.setMinimumSize(800, 700)
        
        self.update_theme(self.app_state.current_theme) # Set initial theme
        self.app_state.theme_changed.connect(self.update_theme) # Connect to theme changes
        
        self.all_ports = []

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        central_widget = QWidget()
        scroll.setWidget(central_widget)
        self.setCentralWidget(scroll)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(25)

        self.create_header(main_layout)
        self.create_com_port_sections(main_layout)
        self.create_settings_section(main_layout)
        self.create_action_buttons(main_layout)
        self.create_status_log(main_layout)
        
        self.app_state.state_changed.connect(self.update_ui_from_state)
        self.app_state.com_status_changed.connect(self.add_log_entry)
        self.app_state.output_com_status_changed.connect(self.update_output_status)
        self.app_state.start_card_scan_started.connect(self.on_start_card_scan_started)
        self.app_state.start_card_scan_complete.connect(self.on_start_card_scan_complete)
        
        # --- MODIFIED: Connect each dropdown to its own specific update function ---
        self.input_port_combo.currentIndexChanged.connect(self._on_input_port_changed)
        self.output_port_combo.currentIndexChanged.connect(self._on_output_port_changed)
        self.start_card_input_port_combo.currentIndexChanged.connect(self._on_start_card_port_changed)
        
        self.refresh_ports()
        self.populate_format_dropdown()
        self.populate_settings_dropdowns()
        self.update_ui_from_state()

    # --- NEW: Independent handler for the input dropdown ---
    def _on_input_port_changed(self):
        self._update_port_availability()

    # --- NEW: Independent handler for the output dropdown ---
    def _on_output_port_changed(self):
        self._update_port_availability()

    # --- NEW: Independent handler for the start card dropdown ---
    def _on_start_card_port_changed(self):
        self._update_port_availability()

    # --- NEW: Unified method to update all port dropdowns ---
    def _update_port_availability(self):
        # Block signals to prevent infinite loops
        for combo in [self.input_port_combo, self.output_port_combo, self.start_card_input_port_combo]:
            combo.blockSignals(True)

        # Get current selections
        selected_input = self.input_port_combo.currentText()
        selected_output = self.output_port_combo.currentText()
        selected_start_card = self.start_card_input_port_combo.currentText()

        # Repopulate input_port_combo
        self.input_port_combo.clear()
        available_for_input = [p for p in self.all_ports if p not in [selected_output, selected_start_card] or not p]
        self.input_port_combo.addItems([""] + available_for_input)
        if selected_input in available_for_input:
            self.input_port_combo.setCurrentText(selected_input)

        # Repopulate output_port_combo
        self.output_port_combo.clear()
        available_for_output = [p for p in self.all_ports if p not in [selected_input, selected_start_card] or not p]
        self.output_port_combo.addItems([""] + available_for_output)
        if selected_output in available_for_output:
            self.output_port_combo.setCurrentText(selected_output)

        # Repopulate start_card_input_port_combo
        self.start_card_input_port_combo.clear()
        available_for_start = [p for p in self.all_ports if p not in [selected_input, selected_output] or not p]
        self.start_card_input_port_combo.addItems([""] + available_for_start)
        if selected_start_card in available_for_start:
            self.start_card_input_port_combo.setCurrentText(selected_start_card)

        # Unblock signals
        for combo in [self.input_port_combo, self.output_port_combo, self.start_card_input_port_combo]:
            combo.blockSignals(False)

    def refresh_ports(self):
        """Fetches the latest list of COM ports and updates the dropdowns."""
        self.all_ports = [port.device for port in serial.tools.list_ports.comports()]
        
        self.input_port_combo.blockSignals(True)
        self.output_port_combo.blockSignals(True)
        self.start_card_input_port_combo.blockSignals(True)

        self.input_port_combo.clear()
        self.output_port_combo.clear()
        self.start_card_input_port_combo.clear()
        
        port_list = [""] + self.all_ports if self.all_ports else ["No ports available"]
        self.input_port_combo.addItems(port_list)
        self.output_port_combo.addItems(port_list)
        self.start_card_input_port_combo.addItems(port_list)

        self.input_port_combo.blockSignals(False)
        self.output_port_combo.blockSignals(False)
        self.start_card_input_port_combo.blockSignals(False)
        
        # Let the state update trigger the filtering logic
        self.update_ui_from_state()

    # ... (Most other methods are unchanged) ...

    def apply_configuration(self):
        input_port = self.input_port_combo.currentText()
        output_port = self.output_port_combo.currentText()
        start_card_port = self.start_card_input_port_combo.currentText()

        # Check for port conflicts
        ports = [p for p in [input_port, output_port, start_card_port] if p and "No ports" not in p]
        if len(ports) != len(set(ports)):
            QMessageBox.warning(self, "Configuration Error", "Each COM port (Input, Output, Start Card) must be unique.")
            return

        # Apply settings (unchanged)
        self.app_state.baud_rate = int(self.baud_rate_combo.currentText())
        self.app_state.data_bits = int(self.data_bits_combo.currentText())
        self.app_state.parity = {'None': 'N', 'Even': 'E', 'Odd': 'O'}[self.parity_combo.currentText()]
        self.app_state.stop_bits = float(self.stop_bits_combo.currentText())
        self.app_state.timeout = float(self.timeout_combo.currentText())

        

        # Apply Input Port
        self.app_state.selected_com_port = input_port if "No ports" not in input_port and input_port else None
        if self.app_state.selected_com_port:
            self.add_log_entry(f"Input port set to {input_port}", "white")

        # Apply Start Card Scan Port
        self.app_state.start_card_scan_port = start_card_port if "No ports" not in start_card_port and start_card_port else None
        if self.app_state.start_card_scan_port:
            self.add_log_entry(f"Start card scan port set to {start_card_port}", "white")

        # Apply Output Port
        if output_port and "No ports" not in output_port:
            self.app_state.connect_output_port(output_port)
        else:
            self.app_state.disconnect_output_port()
        
        self.app_state.selected_output_format = self.output_format_combo.currentText()
        self.app_state.state_changed.emit()
        self.app_state.save_cache()
        QMessageBox.information(self, "Success", "Configuration has been applied.")

    def update_ui_from_state(self):
        # Temporarily block signals to prevent redundant updates
        self.input_port_combo.blockSignals(True)
        self.output_port_combo.blockSignals(True)
        self.start_card_input_port_combo.blockSignals(True)

        # Update input port UI
        if self.app_state.selected_com_port:
            self.input_port_combo.setCurrentText(self.app_state.selected_com_port)
            self.input_status_text.setText(f"Selected: {self.app_state.selected_com_port}")
            self.input_status_text.setObjectName("statusOK")
        else:
            self.input_port_combo.setCurrentIndex(0) # Select the empty option
            self.input_status_text.setText("Not Assigned")
            self.input_status_text.setObjectName("statusWarning")
        self.input_status_text.style().unpolish(self.input_status_text); self.input_status_text.style().polish(self.input_status_text)
        
        # Update output port UI
        if self.app_state.output_com_writer.is_connected:
            self.output_port_combo.setCurrentText(self.app_state.selected_output_port)
            self.output_status_text.setText(f"Connected: {self.app_state.selected_output_port}")
            self.output_status_text.setObjectName("statusOK")
        else:
            self.output_port_combo.setCurrentIndex(0) # Select the empty option
            self.output_status_text.setText("Not Connected")
            self.output_status_text.setObjectName("statusDisconnected")
        self.output_status_text.style().unpolish(self.output_status_text); self.output_status_text.style().polish(self.output_status_text)

        # Update start card scan port UI
        if self.app_state.start_card_scan_port:
            self.start_card_input_port_combo.setCurrentText(self.app_state.start_card_scan_port)
            self.start_card_input_status_text.setText(f"Selected: {self.app_state.start_card_scan_port}")
            self.start_card_input_status_text.setObjectName("statusOK")
        else:
            self.start_card_input_port_combo.setCurrentIndex(0)
            self.start_card_input_status_text.setText("Not Assigned")
            self.start_card_input_status_text.setObjectName("statusWarning")
        self.start_card_input_status_text.style().unpolish(self.start_card_input_status_text); self.start_card_input_status_text.style().polish(self.start_card_input_status_text)
            
        # Update settings UI (unchanged)
        self.baud_rate_combo.setCurrentText(str(self.app_state.baud_rate))
        self.data_bits_combo.setCurrentText(str(self.app_state.data_bits))
        self.parity_combo.setCurrentText({'N': 'None', 'E': 'Even', 'O': 'Odd'}.get(self.app_state.parity, 'None'))
        self.stop_bits_combo.setCurrentText(str(self.app_state.stop_bits))
        self.timeout_combo.setCurrentText(str(self.app_state.timeout))

        
        
        # Unblock signals
        self.input_port_combo.blockSignals(False)
        self.output_port_combo.blockSignals(False)
        self.start_card_input_port_combo.blockSignals(False)
        
        # Manually trigger the filtering after state is loaded
        self._update_port_availability()
    
    # ... (The rest of the file is unchanged) ...
    def create_header(self, parent_layout):
        title = QLabel("Serial Port Configuration")
        title.setObjectName("h1")
        subtitle = QLabel("Manage serial port connections for data input and output.")
        subtitle.setObjectName("subtitle")
        
        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 10)
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        header_layout = QHBoxLayout()
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(ClockWidget())

        parent_layout.addLayout(header_layout)

    def create_com_port_sections(self, parent_layout):
        layout = QHBoxLayout()
        layout.setSpacing(25)
        layout.addWidget(self.create_input_com_section())
        layout.addWidget(self.create_output_com_section())
        parent_layout.addLayout(layout)

    def create_input_com_section(self):
        section = QFrame()
        section.setObjectName("panel")
        layout = QVBoxLayout(section)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)
        
        title = QLabel("Input Port Settings")
        title.setObjectName("h2")
        layout.addWidget(title)

        # Main Scanner Input
        layout.addWidget(QLabel("Main Scanner Port:"))
        self.input_port_combo = QComboBox()
        self.input_status_text = QLabel()
        layout.addWidget(self.input_port_combo)
        layout.addWidget(self.input_status_text)

        # Start Card Scanner Input
        layout.addWidget(QLabel("Sequence Start Port:"))
        self.start_card_input_port_combo = QComboBox()
        self.start_card_input_status_text = QLabel()
        layout.addWidget(self.start_card_input_port_combo)
        layout.addWidget(self.start_card_input_status_text)

        layout.addStretch()
        return section

    def create_output_com_section(self):
        section = QFrame()
        section.setObjectName("panel")
        layout = QVBoxLayout(section)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)
        title = QLabel("Output Port Settings")
        title.setObjectName("h2")
        self.output_port_combo = QComboBox()
        self.output_format_combo = QComboBox()
        self.output_status_text = QLabel()
        
        layout.addWidget(title)
        layout.addWidget(QLabel("Output COM Port:"))
        layout.addWidget(self.output_port_combo)
        layout.addWidget(QLabel("Data Output Format:"))
        layout.addWidget(self.output_format_combo)
        layout.addWidget(self.output_status_text)
        layout.addStretch()
        return section

    

    def create_settings_section(self, parent_layout):
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(25, 20, 25, 20)
        title = QLabel("Advanced Serial Settings")
        title.setObjectName("h2")
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(20)
        
        self.baud_rate_combo = QComboBox()
        self.data_bits_combo = QComboBox()
        self.parity_combo = QComboBox()
        self.stop_bits_combo = QComboBox()
        self.timeout_combo = QComboBox()

        widgets = [
            ("Baud Rate", self.baud_rate_combo), ("Data Bits", self.data_bits_combo),
            ("Parity", self.parity_combo), ("Stop Bits", self.stop_bits_combo), ("Timeout (s)", self.timeout_combo)
        ]

        for label_text, combo_box in widgets:
            col_layout = QVBoxLayout()
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold;")
            col_layout.addWidget(label)
            col_layout.addWidget(combo_box)
            grid_layout.addLayout(col_layout)
        
        layout.addWidget(title)
        layout.addLayout(grid_layout)
        parent_layout.addWidget(frame)

    def create_action_buttons(self, parent_layout):
        layout = QHBoxLayout()
        layout.setSpacing(15)
        apply_btn = QPushButton("Apply Configuration")
        apply_btn.setObjectName("primary")
        apply_btn.clicked.connect(self.apply_configuration)
        disconnect_btn = QPushButton("Disconnect All Ports")
        disconnect_btn.setObjectName("secondary")
        disconnect_btn.clicked.connect(self.app_state.disconnect_all_ports)
        refresh_btn = QPushButton("Refresh Ports")
        refresh_btn.setObjectName("secondary")
        refresh_btn.clicked.connect(self.refresh_ports)
        
        layout.addWidget(apply_btn)
        layout.addWidget(disconnect_btn)
        layout.addWidget(refresh_btn)
        layout.addStretch()
        parent_layout.addLayout(layout)

    def create_status_log(self, parent_layout):
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(25, 20, 25, 20)
        title = QLabel("Connection Log")
        title.setObjectName("h2")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(150)
        layout.addWidget(title)
        layout.addWidget(self.log_text)
        parent_layout.addWidget(frame)

    def populate_settings_dropdowns(self):
        self.baud_rate_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        self.data_bits_combo.addItems(['7', '8'])
        self.parity_combo.addItems(['None', 'Even', 'Odd'])
        self.stop_bits_combo.addItems(['1', '1.5', '2'])
        # --- MODIFIED: Added smaller, fractional timeout options ---
        self.timeout_combo.addItems(['0.02', '0.05', '0.1', '0.2', '0.5', '1', '2', '5'])

    def populate_format_dropdown(self):
        self.output_format_combo.clear()
        self.output_format_combo.addItems(self.app_state.output_formats.keys() or ["No formats found"])
    
    def add_log_entry(self, message, color):
        self.log_text.append(f"[{self.app_state.get_timestamp()}] {message}")
        if self.app_state.selected_com_port and self.app_state.selected_com_port in message:
             self.update_ui_from_state()
    
    def update_output_status(self, message, color):
        self.add_log_entry(message, color)
        self.update_ui_from_state()

    def on_start_card_scan_started(self, message):
        self.start_card_input_status_text.setText(message)
        self.start_card_input_status_text.setObjectName("statusScanning") # Or a new style for waiting
        self.start_card_input_status_text.style().unpolish(self.start_card_input_status_text)
        self.start_card_input_status_text.style().polish(self.start_card_input_status_text)

    def on_start_card_scan_complete(self, message, success):
        self.update_ui_from_state() # This will reset the status text
        self.add_log_entry(message, "green" if success else "red")

    def update_theme(self, theme_name):
        if theme_name == "dark":
            self.setStyleSheet(DARK_THEME_STYLESHEET)
        else:
            self.setStyleSheet(LIGHT_THEME_STYLESHEET)
        # Re-polish all widgets to apply new stylesheet
        for widget in self.findChildren(QWidget):
            widget.style().unpolish(widget)
            widget.style().polish(widget)