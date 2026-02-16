# src/ui/network_setup_dual.py
"""
Dual Head Network Setup Window - Split view for Head A and Head B
Left side: Head B configuration
Right side: Head A configuration
"""

import sys
import socket
import serial.tools.list_ports
import errno
import threading
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QHBoxLayout,
    QVBoxLayout, QComboBox, QTextEdit, QScrollArea, QFrame, QMessageBox, 
    QGridLayout, QLineEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator, QIntValidator
from .styles import DARK_THEME_STYLESHEET, LIGHT_THEME_STYLESHEET
from .widgets import ClockWidget

class NetworkSetupWindow(QMainWindow):
    def __init__(self, dual_head_manager):
        super().__init__()
        self.dual_head_manager = dual_head_manager
        self.head_a = dual_head_manager.head_a
        self.head_b = dual_head_manager.head_b
        
        self.setWindowTitle("Network & COM Port Configuration - Dual Head")
        self.setMinimumSize(1400, 800)
        self.resize(1600, 900)
        
        # Create validators for IP and Port inputs
        self.create_validators()
        
        try:
            self.update_theme(self.head_a.current_theme)
            self.head_a.theme_changed.connect(self.update_theme)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            
            central_widget = QWidget()
            scroll.setWidget(central_widget)
            self.setCentralWidget(scroll)

            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(30, 25, 30, 25)
            main_layout.setSpacing(18)

            self.create_header(main_layout)
            self.create_split_configuration(main_layout)
            self.create_status_log(main_layout)
            
            main_layout.addStretch(1)
            
            # Connect signals from both heads
            self.head_a.com_status_changed.connect(lambda msg, color: self.update_input_status('A', msg, color))
            self.head_b.com_status_changed.connect(lambda msg, color: self.update_input_status('B', msg, color))
            self.head_a.output_com_status_changed.connect(lambda msg, color: self.update_output_status('A', msg, color))
            self.head_b.output_com_status_changed.connect(lambda msg, color: self.update_output_status('B', msg, color))
            self.head_a.ondemand_scan_status_update.connect(lambda msg, color: self.update_ondemand_status('A', msg, color))
            self.head_b.ondemand_scan_status_update.connect(lambda msg, color: self.update_ondemand_status('B', msg, color))
            
            # Initialize network detection
            self.detected_local_ips = []
            self.detected_remote_ips = []
            
            # Populate dropdowns for both heads
            self.populate_all_dropdowns()
            
            # Load saved configurations
            self.update_ui_from_state()
            
        except Exception as e:
            print(f"Error initializing Network Setup Window: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Initialization Error", 
                               f"Failed to initialize Network & COM Port Configuration window:\n\n{str(e)}")

    def create_validators(self):
        """Create input validators for IP addresses and ports"""
        # IP Address validator: xxx.xxx.xxx.xxx where xxx is 0-255
        # Regex pattern for IP address
        ip_pattern = QRegularExpression(
            r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
            r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        )
        self.ip_validator = QRegularExpressionValidator(ip_pattern)
        
        # Port validator: 0-65535
        self.port_validator = QIntValidator(0, 65535)

    def create_header(self, parent_layout):
        title = QLabel("Network & COM Port Configuration - Dual Head")
        title.setObjectName("h1")
        subtitle = QLabel("Configure UDP network and serial COM ports for Head A (Right) and Head B (Left)")
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

    def create_split_configuration(self, parent_layout):
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

    def create_head_panel(self, head_id, title):
        """Create configuration panel for one head"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header with color coding
        header = QLabel(title)
        header.setObjectName("h1")
        if head_id == 'A':
            header.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 24px;")
        else:
            header.setStyleSheet("color: #2196F3; font-weight: bold; font-size: 24px;")
        layout.addWidget(header)
        
        # Main Scanner Section
        main_scanner = self.create_main_scanner_section(head_id)
        layout.addWidget(main_scanner)
        
        # Output Section
        output = self.create_output_section(head_id)
        layout.addWidget(output)
        
        # On-Demand Scanner Section
        ondemand = self.create_ondemand_scanner_section(head_id)
        layout.addWidget(ondemand)
        
        # Action Buttons
        buttons = self.create_action_buttons(head_id)
        layout.addLayout(buttons)
        
        layout.addStretch()
        
        return panel

    def create_main_scanner_section(self, head_id):
        """Create Main Scanner configuration section for specified head"""
        section = QFrame()
        section.setObjectName("panel")
        section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("Main Scanner Input (UDP)")
        title.setObjectName("h2")
        layout.addWidget(title)
        
        desc = QLabel("Receive QR codes from main scanner via UDP")
        desc.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(desc)
        
        # Form
        form = QGridLayout()
        form.setSpacing(10)
        form.setColumnStretch(1, 1)
        
        # Local IP
        form.addWidget(QLabel("Local IP:"), 0, 0, Qt.AlignmentFlag.AlignRight)
        local_ip = QComboBox()
        local_ip.setEditable(True)
        local_ip.setValidator(self.ip_validator)  # Add IP validator
        setattr(self, f'main_local_ip_{head_id}', local_ip)
        form.addWidget(local_ip, 0, 1)
        
        # Local Port
        form.addWidget(QLabel("Local Port:"), 1, 0, Qt.AlignmentFlag.AlignRight)
        local_port = QComboBox()
        local_port.setEditable(True)
        local_port.setValidator(self.port_validator)  # Add port validator
        local_port.addItems(["5000", "5001", "5002", "5003", "5004"])
        setattr(self, f'main_local_port_{head_id}', local_port)
        form.addWidget(local_port, 1, 1)
        
        # Remote IP
        form.addWidget(QLabel("Remote IP:"), 2, 0, Qt.AlignmentFlag.AlignRight)
        remote_ip = QComboBox()
        remote_ip.setEditable(True)
        remote_ip.setValidator(self.ip_validator)  # Add IP validator
        remote_ip.setPlaceholderText("Scanner IP")
        setattr(self, f'main_remote_ip_{head_id}', remote_ip)
        form.addWidget(remote_ip, 2, 1)
        
        # Remote Port
        form.addWidget(QLabel("Remote Port:"), 3, 0, Qt.AlignmentFlag.AlignRight)
        remote_port = QComboBox()
        remote_port.setEditable(True)
        remote_port.setValidator(self.port_validator)  # Add port validator
        remote_port.addItems(["", "6000", "6001", "6002"])
        setattr(self, f'main_remote_port_{head_id}', remote_port)
        form.addWidget(remote_port, 3, 1)
        
        layout.addLayout(form)
        
        # Status
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        status_label = QLabel("Not Connected")
        status_label.setObjectName("statusError")
        setattr(self, f'main_status_{head_id}', status_label)
        status_layout.addWidget(status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Apply button
        apply_btn = QPushButton("Apply Main Scanner")
        apply_btn.setObjectName("primary")
        apply_btn.clicked.connect(lambda: self.apply_main_scanner(head_id))
        layout.addWidget(apply_btn)
        
        return section

    def create_output_section(self, head_id):
        """Create Output configuration section for specified head"""
        section = QFrame()
        section.setObjectName("panel")
        section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("Output Configuration (UDP)")
        title.setObjectName("h2")
        layout.addWidget(title)
        
        desc = QLabel("Send validation results to PLC via UDP")
        desc.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(desc)
        
        # Form
        form = QGridLayout()
        form.setSpacing(10)
        form.setColumnStretch(1, 1)
        
        # Local IP
        form.addWidget(QLabel("Local IP:"), 0, 0, Qt.AlignmentFlag.AlignRight)
        local_ip = QComboBox()
        local_ip.setEditable(True)
        local_ip.setValidator(self.ip_validator)  # Add IP validator
        setattr(self, f'output_local_ip_{head_id}', local_ip)
        form.addWidget(local_ip, 0, 1)
        
        # Local Port
        form.addWidget(QLabel("Local Port:"), 1, 0, Qt.AlignmentFlag.AlignRight)
        local_port = QComboBox()
        local_port.setEditable(True)
        local_port.setValidator(self.port_validator)  # Add port validator
        local_port.addItems(["0", "7000", "7001", "7002"])
        setattr(self, f'output_local_port_{head_id}', local_port)
        form.addWidget(local_port, 1, 1)
        
        # Remote IP
        form.addWidget(QLabel("Remote IP:"), 2, 0, Qt.AlignmentFlag.AlignRight)
        remote_ip = QComboBox()
        remote_ip.setEditable(True)
        remote_ip.setValidator(self.ip_validator)  # Add IP validator
        remote_ip.setPlaceholderText("PLC IP")
        setattr(self, f'output_remote_ip_{head_id}', remote_ip)
        form.addWidget(remote_ip, 2, 1)
        
        # Remote Port
        form.addWidget(QLabel("Remote Port:"), 3, 0, Qt.AlignmentFlag.AlignRight)
        remote_port = QComboBox()
        remote_port.setEditable(True)
        remote_port.setValidator(self.port_validator)  # Add port validator
        remote_port.addItems(["6000", "6001", "8000", "8001"])
        setattr(self, f'output_remote_port_{head_id}', remote_port)
        form.addWidget(remote_port, 3, 1)
        
        layout.addLayout(form)
        
        # Status
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        status_label = QLabel("Not Connected")
        status_label.setObjectName("statusError")
        setattr(self, f'output_status_{head_id}', status_label)
        status_layout.addWidget(status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Apply button
        apply_btn = QPushButton("Apply Output")
        apply_btn.setObjectName("primary")
        apply_btn.clicked.connect(lambda: self.apply_output(head_id))
        layout.addWidget(apply_btn)
        
        return section

    def create_ondemand_scanner_section(self, head_id):
        """Create On-Demand Scanner configuration section for specified head"""
        section = QFrame()
        section.setObjectName("panel")
        section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("On-Demand Scanner (Serial)")
        title.setObjectName("h2")
        layout.addWidget(title)
        
        desc = QLabel("Serial COM port for manual scans")
        desc.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(desc)
        
        # Form
        form = QGridLayout()
        form.setSpacing(10)
        form.setColumnStretch(1, 1)
        
        # COM Port
        form.addWidget(QLabel("COM Port:"), 0, 0, Qt.AlignmentFlag.AlignRight)
        com_port = QComboBox()
        com_port.setEditable(False)
        setattr(self, f'ondemand_com_port_{head_id}', com_port)
        form.addWidget(com_port, 0, 1)
        
        # Baud Rate
        form.addWidget(QLabel("Baud Rate:"), 1, 0, Qt.AlignmentFlag.AlignRight)
        baud_rate = QComboBox()
        baud_rate.addItems(["9600", "19200", "38400", "57600", "115200"])
        baud_rate.setCurrentText("115200")
        setattr(self, f'ondemand_baud_rate_{head_id}', baud_rate)
        form.addWidget(baud_rate, 1, 1)
        
        layout.addLayout(form)
        
        # Status
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        status_label = QLabel("Not Connected")
        status_label.setObjectName("statusError")
        setattr(self, f'ondemand_status_{head_id}', status_label)
        status_layout.addWidget(status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Apply button
        apply_btn = QPushButton("Apply On-Demand Scanner")
        apply_btn.setObjectName("primary")
        apply_btn.clicked.connect(lambda: self.apply_ondemand(head_id))
        layout.addWidget(apply_btn)
        
        return section

    def create_action_buttons(self, head_id):
        """Create action buttons for specified head"""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        disconnect_btn = QPushButton(f"Disconnect Head {head_id}")
        disconnect_btn.setObjectName("secondary")
        disconnect_btn.clicked.connect(lambda: self.disconnect_head(head_id))
        
        layout.addWidget(disconnect_btn)
        layout.addStretch()
        
        return layout

    def create_status_log(self, parent_layout):
        """Create status log section with network refresh button"""
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Header with refresh button
        header_layout = QHBoxLayout()
        title = QLabel("Status Log")
        title.setObjectName("h2")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Single refresh network button
        refresh_btn = QPushButton("🔄 Refresh Network & Scan IPs")
        refresh_btn.setObjectName("primary")
        refresh_btn.setMinimumWidth(200)
        refresh_btn.clicked.connect(self.refresh_and_scan_network)
        refresh_btn.setToolTip("Refresh network interfaces and ping all available IPs on the network")
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Status log text area (increased size)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(300)  # Increased from default
        layout.addWidget(self.log_text)
        
        parent_layout.addWidget(frame)

    def populate_all_dropdowns(self):
        """Populate all dropdowns for both heads"""
        # Populate local IPs
        for head_id in ['A', 'B']:
            self.populate_local_ip_dropdown(head_id)
            self.populate_com_ports(head_id)
    
    def validate_and_clean_cache(self, head):
        """Validate and clean cache data to prevent corrupted values"""
        # Validate main_scanner_config
        if head.main_scanner_config:
            config = head.main_scanner_config
            if not isinstance(config, dict):
                head.main_scanner_config = None
            else:
                # Validate each field
                if not isinstance(config.get('local_ip', ''), str):
                    config['local_ip'] = '0.0.0.0'
                if not isinstance(config.get('remote_ip', ''), str):
                    config['remote_ip'] = ''
                try:
                    config['local_port'] = int(config.get('local_port', 0))
                    config['remote_port'] = int(config.get('remote_port', 0))
                except (ValueError, TypeError):
                    head.main_scanner_config = None
        
        # Validate output_config
        if head.output_config:
            config = head.output_config
            if not isinstance(config, dict):
                head.output_config = None
            else:
                # Validate each field
                if not isinstance(config.get('local_ip', ''), str):
                    config['local_ip'] = '0.0.0.0'
                if not isinstance(config.get('remote_ip', ''), str):
                    config['remote_ip'] = ''
                try:
                    config['local_port'] = int(config.get('local_port', 0))
                    config['remote_port'] = int(config.get('remote_port', 0))
                except (ValueError, TypeError):
                    head.output_config = None
        
        # Validate ondemand_scanner_config
        if head.ondemand_scanner_config:
            config = head.ondemand_scanner_config
            if not isinstance(config, dict):
                head.ondemand_scanner_config = None
            else:
                if not isinstance(config.get('port', ''), str):
                    config['port'] = ''
                try:
                    config['baudrate'] = int(config.get('baudrate', 115200))
                except (ValueError, TypeError):
                    config['baudrate'] = 115200

    def populate_local_ip_dropdown(self, head_id):
        """Populate local IP dropdown for specified head"""
        try:
            import socket
            hostname = socket.gethostname()
            local_ips = socket.gethostbyname_ex(hostname)[2]
            local_ips = [ip for ip in local_ips if not ip.startswith("127.")]
            
            # Get combo boxes
            main_combo = getattr(self, f'main_local_ip_{head_id}')
            output_combo = getattr(self, f'output_local_ip_{head_id}')
            
            for combo in [main_combo, output_combo]:
                combo.clear()
                combo.addItem("0.0.0.0 (All interfaces)")
                combo.addItem("127.0.0.1 (Localhost)")
                for ip in local_ips:
                    combo.addItem(ip)
        except Exception as e:
            print(f"Error populating local IPs for Head {head_id}: {e}")

    def populate_com_ports(self, head_id):
        """Populate COM port dropdown for specified head"""
        try:
            combo = getattr(self, f'ondemand_com_port_{head_id}')
            current_selection = combo.currentText()
            combo.clear()
            combo.addItem("")
            
            ports = serial.tools.list_ports.comports()
            available_ports = []
            for port in ports:
                combo.addItem(f"{port.device} - {port.description}")
                available_ports.append(port.device)
            
            # Log available ports
            if available_ports:
                self.add_log_entry(f"Head {head_id}: Found COM ports: {', '.join(available_ports)}", "green")
            else:
                self.add_log_entry(f"Head {head_id}: No COM ports detected", "orange")
            
            # Restore previous selection if still available
            if current_selection:
                index = combo.findText(current_selection, Qt.MatchFlag.MatchStartsWith)
                if index >= 0:
                    combo.setCurrentIndex(index)
        except Exception as e:
            self.add_log_entry(f"Head {head_id}: Error scanning COM ports - {str(e)}", "red")
            print(f"Error populating COM ports for Head {head_id}: {e}")

    def update_ui_from_state(self):
        """Load saved configurations for both heads"""
        # Validate and clean cache data first
        self.validate_and_clean_cache(self.head_a)
        self.validate_and_clean_cache(self.head_b)
        
        for head_id in ['A', 'B']:
            head = self.head_a if head_id == 'A' else self.head_b
            
            # Main scanner
            if head.main_scanner_config:
                config = head.main_scanner_config
                local_ip = config.get('local_ip', '')
                local_port = config.get('local_port', '')
                remote_ip = config.get('remote_ip', '')
                remote_port = config.get('remote_port', '')
                
                # Only set if values are valid strings/numbers
                if local_ip and isinstance(local_ip, str):
                    getattr(self, f'main_local_ip_{head_id}').setCurrentText(local_ip)
                if local_port and (isinstance(local_port, (int, str))):
                    getattr(self, f'main_local_port_{head_id}').setCurrentText(str(local_port))
                if remote_ip and isinstance(remote_ip, str):
                    getattr(self, f'main_remote_ip_{head_id}').setCurrentText(remote_ip)
                if remote_port and (isinstance(remote_port, (int, str))):
                    getattr(self, f'main_remote_port_{head_id}').setCurrentText(str(remote_port))
            
            # Output
            if head.output_config:
                config = head.output_config
                local_ip = config.get('local_ip', '')
                local_port = config.get('local_port', '')
                remote_ip = config.get('remote_ip', '')
                remote_port = config.get('remote_port', '')
                
                # Only set if values are valid strings/numbers
                if local_ip and isinstance(local_ip, str):
                    getattr(self, f'output_local_ip_{head_id}').setCurrentText(local_ip)
                if local_port and (isinstance(local_port, (int, str))):
                    getattr(self, f'output_local_port_{head_id}').setCurrentText(str(local_port))
                if remote_ip and isinstance(remote_ip, str):
                    getattr(self, f'output_remote_ip_{head_id}').setCurrentText(remote_ip)
                if remote_port and (isinstance(remote_port, (int, str))):
                    getattr(self, f'output_remote_port_{head_id}').setCurrentText(str(remote_port))
            
            # On-demand scanner
            if head.ondemand_scanner_config:
                config = head.ondemand_scanner_config
                port = config.get('port', '')
                baudrate = config.get('baudrate', 115200)
                
                if port and isinstance(port, str):
                    # Find the COM port in dropdown (may have description)
                    combo = getattr(self, f'ondemand_com_port_{head_id}')
                    index = combo.findText(port, Qt.MatchFlag.MatchStartsWith)
                    if index >= 0:
                        combo.setCurrentIndex(index)
                
                if baudrate:
                    getattr(self, f'ondemand_baud_rate_{head_id}').setCurrentText(str(baudrate))

    def apply_main_scanner(self, head_id):
        """Apply main scanner configuration for specified head"""
        try:
            head = self.head_a if head_id == 'A' else self.head_b
            
            local_ip = getattr(self, f'main_local_ip_{head_id}').currentText().strip()
            if " (" in local_ip:
                local_ip = local_ip.split(" (")[0]
            
            local_port = getattr(self, f'main_local_port_{head_id}').currentText().strip()
            remote_ip = getattr(self, f'main_remote_ip_{head_id}').currentText().strip()
            remote_port = getattr(self, f'main_remote_port_{head_id}').currentText().strip()
            
            # Check if settings are being changed while connected
            if head.main_scanner_config:
                old_config = head.main_scanner_config
                settings_changed = (
                    old_config.get('local_ip') != (local_ip or "0.0.0.0") or
                    old_config.get('local_port') != (int(local_port) if local_port else 0) or
                    old_config.get('remote_ip') != remote_ip or
                    old_config.get('remote_port') != (int(remote_port) if remote_port else 0)
                )
                
                if settings_changed and head.is_scanning:
                    head.stop_scanning()
                    self.add_log_entry(f"Head {head_id}: Stopped scanning due to configuration change", "orange")
                    self.update_input_status(head_id, "Configuration changed - disconnected", "orange")
            
            # Validate IP addresses
            if local_ip and local_ip not in ["0.0.0.0", "127.0.0.1"]:
                if not self.validate_ip(local_ip):
                    QMessageBox.warning(self, "Invalid IP", f"Head {head_id}: Local IP '{local_ip}' is not a valid IP address.\nFormat: xxx.xxx.xxx.xxx (0-255 for each octet)")
                    self.update_input_status(head_id, "Invalid IP format", "red")
                    return
            
            if remote_ip and not self.validate_ip(remote_ip):
                QMessageBox.warning(self, "Invalid IP", f"Head {head_id}: Remote IP '{remote_ip}' is not a valid IP address.\nFormat: xxx.xxx.xxx.xxx (0-255 for each octet)")
                self.update_input_status(head_id, "Invalid IP format", "red")
                return
            
            # Validate ports
            if local_port:
                if not self.validate_port(local_port):
                    QMessageBox.warning(self, "Invalid Port", f"Head {head_id}: Local Port '{local_port}' is not valid.\nPort must be between 0 and 65535")
                    self.update_input_status(head_id, "Invalid port number", "red")
                    return
            
            if remote_port:
                if not self.validate_port(remote_port):
                    QMessageBox.warning(self, "Invalid Port", f"Head {head_id}: Remote Port '{remote_port}' is not valid.\nPort must be between 0 and 65535")
                    self.update_input_status(head_id, "Invalid port number", "red")
                    return
            
            if remote_ip and remote_port:
                # Check for port conflicts with other head
                conflict_ok, conflict_msg = self.check_port_conflict(head_id, local_ip or "0.0.0.0", local_port, "main_input")
                if not conflict_ok:
                    QMessageBox.critical(self, "Port Conflict", f"Head {head_id}: {conflict_msg}")
                    self.add_log_entry(f"Head {head_id}: {conflict_msg}", "red")
                    self.update_input_status(head_id, conflict_msg, "red")
                    return
                
                # Check if port is available
                available, error_msg = self.is_port_available(local_ip or "0.0.0.0", local_port)
                if not available:
                    QMessageBox.critical(self, "Port Unavailable", f"Head {head_id}: {error_msg}\n\nPlease choose a different port or close the application using this port.")
                    self.add_log_entry(f"Head {head_id}: {error_msg}", "red")
                    self.update_input_status(head_id, error_msg, "red")
                    return
                
                # Test the connection
                test_ok, test_msg = self.test_udp_connection(local_ip or "0.0.0.0", local_port)
                if not test_ok:
                    QMessageBox.critical(self, "Connection Failed", f"Head {head_id}: {test_msg}")
                    self.add_log_entry(f"Head {head_id}: Connection test failed - {test_msg}", "red")
                    self.update_input_status(head_id, "Connection test failed", "red")
                    return
                
                # Stop scanning before changing configuration
                head.stop_scanning()
                
                # Apply configuration
                head.main_scanner_config = {
                    'local_ip': local_ip or "0.0.0.0",
                    'local_port': int(local_port),
                    'remote_ip': remote_ip,
                    'remote_port': int(remote_port)
                }
                
                # Update status immediately
                status_msg = f"Ready: {local_ip or '0.0.0.0'}:{local_port} ← {remote_ip}:{remote_port}"
                self.update_input_status(head_id, status_msg, "green")
                self.add_log_entry(f"Head {head_id}: Main scanner configured successfully on {local_ip or '0.0.0.0'}:{local_port}", "green")
                QMessageBox.information(self, "Success", f"Head {head_id} main scanner connected successfully!\n\nListening on: {local_ip or '0.0.0.0'}:{local_port}\nAccepting from: {remote_ip}:{remote_port}")
            else:
                # Disconnect
                if head.is_scanning:
                    head.stop_scanning()
                head.main_scanner_config = None
                self.update_input_status(head_id, "Not Connected", "red")
                self.add_log_entry(f"Head {head_id}: Main scanner disconnected", "orange")
                QMessageBox.information(self, "Disconnected", f"Head {head_id} main scanner disconnected")
            
            head.state_changed.emit()
            head.save_cache()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply: {e}")
            self.add_log_entry(f"Head {head_id}: Error - {str(e)}", "red")
            self.update_input_status(head_id, f"Error: {str(e)}", "red")

    def apply_output(self, head_id):
        """Apply output configuration for specified head"""
        try:
            head = self.head_a if head_id == 'A' else self.head_b
            
            local_ip = getattr(self, f'output_local_ip_{head_id}').currentText().strip()
            if " (" in local_ip:
                local_ip = local_ip.split(" (")[0]
            
            local_port = getattr(self, f'output_local_port_{head_id}').currentText().strip()
            remote_ip = getattr(self, f'output_remote_ip_{head_id}').currentText().strip()
            remote_port = getattr(self, f'output_remote_port_{head_id}').currentText().strip()
            
            # Check if settings are being changed while connected
            if head.output_udp_writer.is_connected:
                old_local_ip = head.output_udp_writer.local_ip
                old_local_port = head.output_udp_writer.local_port
                old_remote_ip = head.output_udp_writer.remote_ip
                old_remote_port = head.output_udp_writer.remote_port
                
                settings_changed = (
                    old_local_ip != (local_ip or "0.0.0.0") or
                    old_local_port != (int(local_port) if local_port else 0) or
                    old_remote_ip != remote_ip or
                    old_remote_port != (int(remote_port) if remote_port else 0)
                )
                
                if settings_changed:
                    head.output_udp_writer.disconnect()
                    self.add_log_entry(f"Head {head_id}: Disconnected output due to configuration change", "orange")
                    self.update_output_status(head_id, "Configuration changed - disconnected", "orange")
            
            # Validate IP addresses
            if local_ip and local_ip not in ["0.0.0.0", "127.0.0.1"]:
                if not self.validate_ip(local_ip):
                    QMessageBox.warning(self, "Invalid IP", f"Head {head_id}: Local IP '{local_ip}' is not a valid IP address.\nFormat: xxx.xxx.xxx.xxx (0-255 for each octet)")
                    self.update_output_status(head_id, "Invalid IP format", "red")
                    return
            
            if remote_ip and not self.validate_ip(remote_ip):
                QMessageBox.warning(self, "Invalid IP", f"Head {head_id}: Remote IP '{remote_ip}' is not a valid IP address.\nFormat: xxx.xxx.xxx.xxx (0-255 for each octet)")
                self.update_output_status(head_id, "Invalid IP format", "red")
                return
            
            # Validate ports
            if local_port:
                if not self.validate_port(local_port):
                    QMessageBox.warning(self, "Invalid Port", f"Head {head_id}: Local Port '{local_port}' is not valid.\nPort must be between 0 and 65535")
                    self.update_output_status(head_id, "Invalid port number", "red")
                    return
            
            if remote_port:
                if not self.validate_port(remote_port):
                    QMessageBox.warning(self, "Invalid Port", f"Head {head_id}: Remote Port '{remote_port}' is not valid.\nPort must be between 0 and 65535")
                    self.update_output_status(head_id, "Invalid port number", "red")
                    return
            
            if remote_ip and remote_port:
                # Check for port conflicts with other head (if using a local port)
                if local_port:
                    conflict_ok, conflict_msg = self.check_port_conflict(head_id, local_ip or "0.0.0.0", local_port, "output")
                    if not conflict_ok:
                        QMessageBox.critical(self, "Port Conflict", f"Head {head_id}: {conflict_msg}")
                        self.add_log_entry(f"Head {head_id}: {conflict_msg}", "red")
                        self.update_output_status(head_id, conflict_msg, "red")
                        return
                    
                    # Check if port is available
                    available, error_msg = self.is_port_available(local_ip or "0.0.0.0", local_port)
                    if not available:
                        QMessageBox.critical(self, "Port Unavailable", f"Head {head_id}: {error_msg}\n\nPlease choose a different port or close the application using this port.")
                        self.add_log_entry(f"Head {head_id}: {error_msg}", "red")
                        self.update_output_status(head_id, error_msg, "red")
                        return
                
                # Apply output configuration
                head.connect_output_udp(
                    local_ip or "0.0.0.0",
                    int(local_port) if local_port else 0,
                    remote_ip,
                    int(remote_port)
                )
                
                # Update status immediately
                status_msg = f"Ready: {local_ip or '0.0.0.0'}:{local_port or 'auto'} → {remote_ip}:{remote_port}"
                self.update_output_status(head_id, status_msg, "green")
                self.add_log_entry(f"Head {head_id}: Output configured successfully", "green")
                QMessageBox.information(self, "Success", f"Head {head_id} output connected successfully!\n\nSending from: {local_ip or '0.0.0.0'}:{local_port or 'auto'}\nSending to: {remote_ip}:{remote_port}")
            else:
                # Disconnect
                head.connect_output_udp(None, None, None, None)
                self.update_output_status(head_id, "Not Connected", "red")
                self.add_log_entry(f"Head {head_id}: Output disconnected", "orange")
                QMessageBox.information(self, "Disconnected", f"Head {head_id} output disconnected")
            
            head.state_changed.emit()
            head.save_cache()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply: {e}")
            self.add_log_entry(f"Head {head_id}: Error - {str(e)}", "red")
            self.update_output_status(head_id, f"Error: {str(e)}", "red")

    def apply_ondemand(self, head_id):
        """Apply on-demand scanner configuration for specified head"""
        try:
            head = self.head_a if head_id == 'A' else self.head_b
            
            com_port_text = getattr(self, f'ondemand_com_port_{head_id}').currentText().strip()
            
            # Extract just the COM port name (e.g., "COM3" from "COM3 - USB Serial Port")
            if " - " in com_port_text:
                com_port = com_port_text.split(" - ")[0].strip()
            else:
                com_port = com_port_text
            
            baud_rate = int(getattr(self, f'ondemand_baud_rate_{head_id}').currentText())
            
            if com_port:
                # Verify COM port exists
                available_ports = [port.device for port in serial.tools.list_ports.comports()]
                
                if com_port not in available_ports:
                    QMessageBox.critical(
                        self, 
                        "COM Port Not Found", 
                        f"Head {head_id}: COM port '{com_port}' is not available.\n\n"
                        f"Available ports: {', '.join(available_ports) if available_ports else 'None'}\n\n"
                        f"Please refresh and select an available COM port."
                    )
                    self.add_log_entry(f"Head {head_id}: COM port '{com_port}' not found", "red")
                    return
                
                # Check if other head is using this COM port
                other_head = self.head_b if head_id == 'A' else self.head_a
                other_head_id = 'B' if head_id == 'A' else 'A'
                
                if hasattr(other_head, 'start_card_scan_port') and other_head.start_card_scan_port == com_port:
                    QMessageBox.critical(
                        self,
                        "COM Port Conflict",
                        f"Head {head_id}: COM port '{com_port}' is already in use by Head {other_head_id}.\n\n"
                        f"Please select a different COM port."
                    )
                    self.add_log_entry(f"Head {head_id}: COM port '{com_port}' already used by Head {other_head_id}", "red")
                    return
                
                # Disconnect if already connected (settings changed)
                if hasattr(head, 'start_card_scan_port') and head.start_card_scan_port:
                    head.connect_ondemand_serial(port=None)
                    self.add_log_entry(f"Head {head_id}: Disconnected previous COM port connection", "orange")
                
                # Connect to COM port
                head.connect_ondemand_serial(
                    port=com_port,
                    baudrate=baud_rate,
                    bytesize=8,
                    parity='N',
                    stopbits=1,
                    timeout=1
                )
                self.add_log_entry(f"Head {head_id}: On-demand scanner connected to {com_port} at {baud_rate} baud", "green")
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Head {head_id} on-demand scanner connected!\n\n"
                    f"Port: {com_port}\n"
                    f"Baud Rate: {baud_rate}"
                )
            else:
                head.connect_ondemand_serial(port=None)
                self.add_log_entry(f"Head {head_id}: On-demand scanner disconnected", "orange")
                QMessageBox.information(self, "Disconnected", f"Head {head_id} on-demand scanner disconnected")
            
            head.state_changed.emit()
            head.save_cache()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply: {e}")
            self.add_log_entry(f"Head {head_id}: Error - {str(e)}", "red")

    def disconnect_head(self, head_id):
        """Disconnect all ports for specified head"""
        head = self.head_a if head_id == 'A' else self.head_b
        
        # Track what was disconnected
        disconnected_items = []
        
        # Check what's currently connected
        if head.main_scanner_config:
            disconnected_items.append("Main Scanner Input")
        if head.output_udp_writer.is_connected:
            disconnected_items.append("Output")
        if head.ondemand_port_reader or (hasattr(head, 'start_card_scan_port') and head.start_card_scan_port):
            disconnected_items.append("On-Demand Scanner")
        
        # Disconnect all ports
        head.disconnect_all_ports()
        
        # Update all status indicators
        self.update_input_status(head_id, "Not Connected", "red")
        self.update_output_status(head_id, "Not Connected", "red")
        self.update_ondemand_status(head_id, "Not Connected", "red")
        
        # Log the disconnection
        if disconnected_items:
            items_str = ", ".join(disconnected_items)
            self.add_log_entry(f"Head {head_id}: Disconnected - {items_str}", "orange")
            QMessageBox.information(
                self, 
                "Disconnected", 
                f"Head {head_id} disconnected successfully!\n\nDisconnected:\n• {chr(10).join(['• ' + item for item in disconnected_items])}"
            )
        else:
            self.add_log_entry(f"Head {head_id}: No active connections to disconnect", "orange")
            QMessageBox.information(
                self, 
                "Already Disconnected", 
                f"Head {head_id} has no active connections."
            )

    def refresh_and_scan_network(self):
        """Refresh network information and scan for available IPs"""
        import subprocess
        import threading
        
        self.add_log_entry("=" * 60, "blue")
        self.add_log_entry("🔄 Starting Network Refresh & IP Scan...", "blue")
        self.add_log_entry("=" * 60, "blue")
        
        # Refresh dropdowns first
        self.add_log_entry("Refreshing network interfaces...", "blue")
        self.populate_all_dropdowns()
        self.add_log_entry("✓ Network interfaces refreshed", "green")
        
        # Get local network information
        try:
            import socket
            hostname = socket.gethostname()
            local_ips = socket.gethostbyname_ex(hostname)[2]
            local_ips = [ip for ip in local_ips if not ip.startswith("127.")]
            
            self.add_log_entry(f"Local hostname: {hostname}", "blue")
            for ip in local_ips:
                self.add_log_entry(f"  → Local IP: {ip}", "green")
        except Exception as e:
            self.add_log_entry(f"Error getting local IPs: {e}", "red")
            local_ips = []
        
        # Scan network for available IPs
        if local_ips:
            self.add_log_entry("", "blue")
            self.add_log_entry("🔍 Scanning network for available devices...", "blue")
            self.add_log_entry("This may take a few seconds...", "blue")
            
            # Use the first local IP to determine network range
            base_ip = local_ips[0]
            network_prefix = '.'.join(base_ip.split('.')[:-1])
            
            self.add_log_entry(f"Scanning network: {network_prefix}.0/24", "blue")
            
            # Scan in background thread to avoid blocking UI
            def scan_network():
                available_ips = []
                
                # Scan common IP range (1-254)
                for i in range(1, 255):
                    ip = f"{network_prefix}.{i}"
                    
                    # Skip local IPs
                    if ip in local_ips:
                        continue
                    
                    try:
                        # Ping with 1 second timeout
                        result = subprocess.run(
                            ['ping', '-n', '1', '-w', '500', ip],
                            capture_output=True,
                            text=True,
                            timeout=1
                        )
                        
                        if result.returncode == 0:
                            available_ips.append(ip)
                            # Update log in real-time
                            self.add_log_entry(f"  ✓ {ip} - ONLINE", "green")
                    except:
                        pass  # Timeout or error, skip
                
                # Summary
                self.add_log_entry("", "blue")
                self.add_log_entry("=" * 60, "blue")
                self.add_log_entry(f"📊 Scan Complete: Found {len(available_ips)} device(s) online", "green")
                self.add_log_entry("=" * 60, "blue")
                
                if available_ips:
                    self.add_log_entry("Available devices:", "green")
                    for ip in available_ips:
                        self.add_log_entry(f"  → {ip}", "green")
                else:
                    self.add_log_entry("No remote devices found on network", "orange")
                
                self.add_log_entry("", "blue")
            
            # Start scan in background
            scan_thread = threading.Thread(target=scan_network, daemon=True)
            scan_thread.start()
        else:
            self.add_log_entry("Cannot scan network - no local IP detected", "orange")

    def refresh_network_info(self):
        """Legacy method - redirects to new method"""
        self.refresh_and_scan_network()

    def add_log_entry(self, message, color="black"):
        """Add entry to status log"""
        timestamp = self.head_a.get_timestamp()
        self.log_text.append(f"[{timestamp}] {message}")

    def update_input_status(self, head_id, message, color):
        """Update input status for specified head"""
        self.add_log_entry(f"Head {head_id} Input: {message}", color)
        status_label = getattr(self, f'main_status_{head_id}')
        status_label.setText(message)
        if color == "green":
            status_label.setObjectName("statusOK")
        elif color == "red":
            status_label.setObjectName("statusError")
        else:
            status_label.setObjectName("statusWarning")
        status_label.style().unpolish(status_label)
        status_label.style().polish(status_label)

    def update_output_status(self, head_id, message, color):
        """Update output status for specified head"""
        self.add_log_entry(f"Head {head_id} Output: {message}", color)
        status_label = getattr(self, f'output_status_{head_id}')
        status_label.setText(message)
        if color == "green":
            status_label.setObjectName("statusOK")
        elif color == "red":
            status_label.setObjectName("statusError")
        else:
            status_label.setObjectName("statusWarning")
        status_label.style().unpolish(status_label)
        status_label.style().polish(status_label)

    def update_ondemand_status(self, head_id, message, color):
        """Update on-demand status for specified head"""
        self.add_log_entry(f"Head {head_id} On-Demand: {message}", color)
        status_label = getattr(self, f'ondemand_status_{head_id}')
        if message.startswith("Connected") or message == "Not Connected":
            status_label.setText(message)
            if color == "green":
                status_label.setObjectName("statusOK")
            elif color == "red":
                status_label.setObjectName("statusError")
            status_label.style().unpolish(status_label)
            status_label.style().polish(status_label)

    def update_theme(self, theme_name):
        """Update theme for window"""
        stylesheet = DARK_THEME_STYLESHEET if theme_name == "dark" else LIGHT_THEME_STYLESHEET
        self.setStyleSheet(stylesheet)
        for widget in self.findChildren(QWidget):
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def validate_ip(self, ip_string):
        """Validate IP address format"""
        try:
            parts = ip_string.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    return False
            return True
        except:
            return False

    def validate_port(self, port_string):
        """Validate port number"""
        try:
            port = int(port_string)
            return 0 <= port <= 65535
        except:
            return False
    
    def is_port_available(self, ip, port):
        """Check if a port is available for binding"""
        try:
            # Create a test socket
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Try to bind to the port
            bind_ip = ip if ip and ip not in ["", "0.0.0.0"] else "0.0.0.0"
            test_socket.bind((bind_ip, int(port)))
            test_socket.close()
            return True, None
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                return False, f"Port {port} is already in use"
            elif e.errno == errno.EADDRNOTAVAIL:
                return False, f"IP address {ip} is not available on this machine"
            else:
                return False, f"Cannot bind to {ip}:{port} - {str(e)}"
        except Exception as e:
            return False, f"Error checking port: {str(e)}"
    
    def check_port_conflict(self, head_id, ip, port, port_type):
        """
        Check if port conflicts with existing configurations
        
        Rules:
        1. Cannot listen on same IP:Port in both heads (cross-head conflict)
        2. Cannot listen and send from same IP:Port within a head (same-head conflict)
        
        Args:
            head_id: 'A' or 'B'
            ip: IP address to check
            port: Port number to check
            port_type: 'main_input', 'output', or 'ondemand_input'
        """
        current_head = self.head_a if head_id == 'A' else self.head_b
        other_head = self.head_b if head_id == 'A' else self.head_a
        other_head_id = 'B' if head_id == 'A' else 'A'
        
        # Normalize IP for comparison
        check_ip = ip if ip and ip not in ["", "0.0.0.0"] else "0.0.0.0"
        check_port = int(port)
        
        def ips_overlap(ip1, ip2):
            """Check if two IPs overlap (0.0.0.0 overlaps with everything)"""
            if ip1 == "0.0.0.0" or ip2 == "0.0.0.0":
                return True
            return ip1 == ip2
        
        # ============================================
        # RULE 1: Check cross-head conflicts (other head)
        # ============================================
        
        # Check if other head's main scanner input uses this IP:Port
        if other_head.main_scanner_config:
            other_input_ip = other_head.main_scanner_config.get('local_ip', '0.0.0.0')
            other_input_port = other_head.main_scanner_config.get('local_port')
            
            if other_input_port == check_port and ips_overlap(check_ip, other_input_ip):
                return False, f"Port {port} on {ip} is already used by Head {other_head_id} main scanner input ({other_input_ip}:{other_input_port})"
        
        # Check if other head's output uses this IP:Port
        if hasattr(other_head, 'output_udp_writer') and other_head.output_udp_writer.is_connected:
            other_output_ip = other_head.output_udp_writer.local_ip or "0.0.0.0"
            other_output_port = other_head.output_udp_writer.local_port
            
            if other_output_port and other_output_port == check_port and ips_overlap(check_ip, other_output_ip):
                return False, f"Port {port} on {ip} is already used by Head {other_head_id} output ({other_output_ip}:{other_output_port})"
        
        # ============================================
        # RULE 2: Check same-head conflicts (current head)
        # ============================================
        
        # If configuring main input, check against current head's output
        if port_type == 'main_input':
            if hasattr(current_head, 'output_udp_writer') and current_head.output_udp_writer.is_connected:
                current_output_ip = current_head.output_udp_writer.local_ip or "0.0.0.0"
                current_output_port = current_head.output_udp_writer.local_port
                
                if current_output_port and current_output_port == check_port and ips_overlap(check_ip, current_output_ip):
                    return False, f"Head {head_id}: Cannot use same IP:Port ({ip}:{port}) for both input and output. Output is already using {current_output_ip}:{current_output_port}"
        
        # If configuring output, check against current head's main input
        if port_type == 'output':
            if current_head.main_scanner_config:
                current_input_ip = current_head.main_scanner_config.get('local_ip', '0.0.0.0')
                current_input_port = current_head.main_scanner_config.get('local_port')
                
                if current_input_port == check_port and ips_overlap(check_ip, current_input_ip):
                    return False, f"Head {head_id}: Cannot use same IP:Port ({ip}:{port}) for both input and output. Main scanner input is already using {current_input_ip}:{current_input_port}"
        
        return True, None
    
    def test_udp_connection(self, local_ip, local_port):
        """Test if UDP connection can be established"""
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            test_socket.settimeout(2.0)
            
            bind_ip = local_ip if local_ip and local_ip not in ["", "0.0.0.0"] else "0.0.0.0"
            test_socket.bind((bind_ip, int(local_port)))
            test_socket.close()
            return True, f"Successfully bound to {bind_ip}:{local_port}"
        except Exception as e:
            return False, f"Failed to bind: {str(e)}"
