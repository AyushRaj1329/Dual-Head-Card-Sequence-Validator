# src/ui/network_setup.py
import sys
import socket
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QHBoxLayout,
    QVBoxLayout, QComboBox, QTextEdit, QScrollArea, QFrame, QMessageBox, 
    QGridLayout, QLineEdit
)
from PyQt6.QtCore import Qt
from .styles import DARK_THEME_STYLESHEET, LIGHT_THEME_STYLESHEET
from .widgets import ClockWidget

class NetworkSetupWindow(QMainWindow):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.setWindowTitle("Network Configuration (UDP)")
        
        self.update_theme(self.app_state.current_theme)
        self.app_state.theme_changed.connect(self.update_theme)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        central_widget = QWidget()
        scroll.setWidget(central_widget)
        self.setCentralWidget(scroll)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(25)

        self.create_header(main_layout)
        self.create_network_sections(main_layout)
        self.create_action_buttons(main_layout)
        self.create_status_log(main_layout)
        
        self.app_state.state_changed.connect(self.update_ui_from_state)
        self.app_state.com_status_changed.connect(self.update_input_status)
        self.app_state.output_com_status_changed.connect(self.update_output_status)
        self.app_state.ondemand_scan_status_update.connect(self.update_ondemand_status)
        
        # Connect focus events to refresh remote IPs when user interacts with dropdown
        self.main_remote_ip.activated.connect(lambda: self.refresh_remote_ip_dropdown(self.main_remote_ip))
        self.ondemand_remote_ip.activated.connect(lambda: self.refresh_remote_ip_dropdown(self.ondemand_remote_ip))
        self.output_remote_ip.activated.connect(lambda: self.refresh_remote_ip_dropdown(self.output_remote_ip))
        
        self.populate_format_dropdown()
        self.update_ui_from_state()
        
        # Initialize IP detection
        self.detected_local_ips = []
        self.detected_remote_ips = []
        self.detect_local_ips()
        remote_ips = self.detect_remote_ips()
        
        # Populate remote IP dropdowns with detected IPs
        if remote_ips:
            self.populate_remote_ip_dropdowns(remote_ips)
        
        # Auto-apply saved configuration if available
        self.auto_apply_saved_configuration()

    def detect_local_ips(self):
        """Detect available local IP addresses"""
        try:
            hostname = socket.gethostname()
            local_ips = socket.gethostbyname_ex(hostname)[2]
            local_ips = [ip for ip in local_ips if not ip.startswith("127.")]
            
            # Store detected IPs
            self.detected_local_ips = local_ips
            
            # Auto-fill local IP fields with the first detected IP
            if local_ips:
                primary_ip = local_ips[0]
                
                # Auto-fill if fields are empty
                if not self.main_local_ip.text():
                    self.main_local_ip.setText(primary_ip)
                if not self.ondemand_local_ip.text():
                    self.ondemand_local_ip.setText(primary_ip)
                if not self.output_local_ip.text():
                    self.output_local_ip.setText(primary_ip)
                
                info_text = f"Detected Local IPs: {', '.join(local_ips)}"
                self.add_log_entry(info_text, "blue")
            else:
                self.detected_local_ips = []
                self.add_log_entry("No local IPs detected. Using 0.0.0.0 (all interfaces)", "orange")
        except Exception as e:
            self.detected_local_ips = []
            self.add_log_entry(f"Could not detect local IPs: {e}", "orange")
    
    def detect_remote_ips(self):
        """Detect devices on the local network using ARP"""
        try:
            import subprocess
            import re
            
            # Run arp -a command to get connected devices
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True, timeout=5)
            
            # Parse ARP output to extract IP addresses
            ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            ips = re.findall(ip_pattern, result.stdout)
            
            # Filter out invalid IPs
            remote_ips = []
            for ip in ips:
                # Skip loopback
                if ip.startswith('127.'):
                    continue
                # Skip link-local
                if ip.startswith('169.254.'):
                    continue
                # Skip multicast (224-239)
                if ip.startswith('224.') or ip.startswith('239.'):
                    continue
                # Skip broadcast
                if ip == '255.255.255.255':
                    continue
                # Skip local IPs
                if ip in self.detected_local_ips:
                    continue
                # Add valid remote IP
                remote_ips.append(ip)
            
            # Remove duplicates and sort
            remote_ips = sorted(list(set(remote_ips)))
            
            self.detected_remote_ips = remote_ips
            
            if remote_ips:
                self.add_log_entry(f"Detected {len(remote_ips)} remote device(s) on network", "green")
            else:
                self.add_log_entry("No remote devices detected on network", "orange")
                
            return remote_ips
            
        except Exception as e:
            self.detected_remote_ips = []
            self.add_log_entry(f"Could not detect remote devices: {e}", "orange")
            return []
    
    def _show_popup_with_refresh(self, combo_box):
        """Show popup and refresh remote IPs before displaying"""
        # Refresh remote IPs
        self.refresh_remote_ip_dropdown(combo_box)
        # Call the original showPopup method
        QComboBox.showPopup(combo_box)
    
    def refresh_remote_ip_dropdown(self, combo_box):
        """Refresh remote IPs when user clicks on dropdown"""
        # Store current selection
        current_text = combo_box.currentText()
        
        # Check if we have recently detected remote IPs (within last 5 seconds)
        # If not, scan the network again
        if not self.detected_remote_ips:
            self.add_log_entry("Scanning network for devices...", "blue")
            remote_ips = self.detect_remote_ips()
        else:
            # Use cached detected IPs
            remote_ips = self.detected_remote_ips
        
        # Update this specific combo box
        combo_box.clear()
        combo_box.addItem("")  # Empty option
        
        if remote_ips:
            for ip in remote_ips:
                combo_box.addItem(ip)
            # Only log if we just scanned
            if not self.detected_remote_ips or remote_ips != self.detected_remote_ips:
                self.add_log_entry(f"Found {len(remote_ips)} device(s)", "green")
                for ip in remote_ips:
                    self.add_log_entry(f"  → {ip}", "green")
        else:
            self.add_log_entry("No remote devices detected", "orange")
        
        # Restore selection if it exists in the new list
        if current_text:
            index = combo_box.findText(current_text)
            if index >= 0:
                combo_box.setCurrentIndex(index)
            else:
                combo_box.setEditText(current_text)
    
    def auto_apply_saved_configuration(self):
        """Automatically apply saved network configuration if remote devices are available"""
        # Check if we have saved configurations
        has_main_config = (hasattr(self.app_state, 'main_scanner_config') and 
                          self.app_state.main_scanner_config)
        has_ondemand_config = (hasattr(self.app_state, 'ondemand_scanner_config') and 
                               self.app_state.ondemand_scanner_config)
        has_output_config = (hasattr(self.app_state, 'output_config') and 
                            self.app_state.output_config)
        
        if not (has_main_config or has_ondemand_config or has_output_config):
            # No saved configuration
            return
        
        # Check if saved remote IPs are currently available on network
        auto_apply = False
        
        if has_main_config:
            remote_ip = self.app_state.main_scanner_config.get('remote_ip')
            if remote_ip and remote_ip in self.detected_remote_ips:
                auto_apply = True
                self.add_log_entry(f"Main scanner remote IP {remote_ip} detected on network", "green")
        
        if has_ondemand_config:
            remote_ip = self.app_state.ondemand_scanner_config.get('remote_ip')
            if remote_ip and remote_ip in self.detected_remote_ips:
                auto_apply = True
                self.add_log_entry(f"On-demand scanner remote IP {remote_ip} detected on network", "green")
        
        if has_output_config:
            remote_ip = self.app_state.output_config.get('remote_ip')
            if remote_ip and remote_ip in self.detected_remote_ips:
                auto_apply = True
                self.add_log_entry(f"Output PLC IP {remote_ip} detected on network", "green")
        
        # Auto-apply if any saved remote device is detected
        if auto_apply:
            self.add_log_entry("Auto-applying saved network configuration...", "blue")
            try:
                # Apply main scanner configuration
                if has_main_config:
                    config = self.app_state.main_scanner_config
                    local_ip = config.get('local_ip')
                    local_port = config.get('local_port')
                    remote_ip = config.get('remote_ip')
                    remote_port = config.get('remote_port')
                    
                    if local_ip and local_port:
                        # Reconnect with saved settings
                        self.app_state.stop_scanning()
                        self.app_state.main_scanner_config = config
                        # Don't auto-start scanning, just configure
                        self.add_log_entry(f"Main scanner configured: {local_ip}:{local_port}", "green")
                
                # Apply on-demand scanner configuration
                if has_ondemand_config:
                    config = self.app_state.ondemand_scanner_config
                    local_ip = config.get('local_ip')
                    local_port = config.get('local_port')
                    remote_ip = config.get('remote_ip')
                    remote_port = config.get('remote_port')
                    
                    if local_ip and local_port:
                        self.app_state.connect_ondemand_udp(
                            local_ip, local_port, remote_ip, remote_port
                        )
                
                # Apply output configuration
                if has_output_config:
                    config = self.app_state.output_config
                    local_ip = config.get('local_ip')
                    local_port = config.get('local_port')
                    remote_ip = config.get('remote_ip')
                    remote_port = config.get('remote_port')
                    
                    if remote_ip and remote_port:
                        self.app_state.connect_output_udp(
                            local_ip or "0.0.0.0",
                            local_port or 0,
                            remote_ip,
                            remote_port
                        )
                
                self.add_log_entry("Saved configuration applied successfully", "green")
                
            except Exception as e:
                self.add_log_entry(f"Error auto-applying configuration: {e}", "red")
        else:
            if has_main_config or has_ondemand_config or has_output_config:
                self.add_log_entry("Saved configuration found but remote devices not detected", "orange")
                self.add_log_entry("Click 'Refresh Network' to scan for devices", "blue")
    
    def refresh_network_info(self):
        """Refresh both local and remote IP information"""
        self.add_log_entry("Refreshing network information...", "blue")
        self.detect_local_ips()
        remote_ips = self.detect_remote_ips()
        
        # Update remote IP dropdowns
        if remote_ips:
            self.populate_remote_ip_dropdowns(remote_ips)
            # Log each detected remote IP
            for ip in remote_ips:
                self.add_log_entry(f"  → Remote IP available: {ip}", "green")
        
        self.add_log_entry("Network refresh complete", "green")
    
    def populate_remote_ip_dropdowns(self, remote_ips):
        """Populate remote IP combo boxes with detected IPs"""
        # Store the detected remote IPs for later use
        self.detected_remote_ips = remote_ips
        
        # Store current selections
        main_current = self.main_remote_ip.currentText()
        ondemand_current = self.ondemand_remote_ip.currentText()
        output_current = self.output_remote_ip.currentText()
        
        # Clear and repopulate all three dropdowns
        for combo in [self.main_remote_ip, self.ondemand_remote_ip, self.output_remote_ip]:
            combo.clear()
            combo.addItem("")  # Empty option
            if remote_ips:
                for ip in remote_ips:
                    combo.addItem(ip)
        
        # Restore selections if they still exist
        if main_current:
            index = self.main_remote_ip.findText(main_current)
            if index >= 0:
                self.main_remote_ip.setCurrentIndex(index)
            else:
                self.main_remote_ip.setEditText(main_current)
        
        if ondemand_current:
            index = self.ondemand_remote_ip.findText(ondemand_current)
            if index >= 0:
                self.ondemand_remote_ip.setCurrentIndex(index)
            else:
                self.ondemand_remote_ip.setEditText(ondemand_current)
        
        if output_current:
            index = self.output_remote_ip.findText(output_current)
            if index >= 0:
                self.output_remote_ip.setCurrentIndex(index)
            else:
                self.output_remote_ip.setEditText(output_current)

    def apply_configuration(self):
        """Apply the UDP network configuration"""
        try:
            # Get main scanner input settings
            main_local_ip = self.main_local_ip.text().strip()
            main_local_port = self.main_local_port.text().strip()
            main_remote_ip = self.main_remote_ip.currentText().strip() or None
            main_remote_port = self.main_remote_port.text().strip() or None
            
            # Get on-demand scanner input settings
            ondemand_local_ip = self.ondemand_local_ip.text().strip()
            ondemand_local_port = self.ondemand_local_port.text().strip()
            ondemand_remote_ip = self.ondemand_remote_ip.currentText().strip() or None
            ondemand_remote_port = self.ondemand_remote_port.text().strip() or None
            
            # Get output settings
            output_local_ip = self.output_local_ip.text().strip()
            output_local_port = self.output_local_port.text().strip() or "0"
            output_remote_ip = self.output_remote_ip.currentText().strip()
            output_remote_port = self.output_remote_port.text().strip()
            
            # Validate main scanner settings
            if main_local_ip and main_local_port:
                try:
                    main_local_port_int = int(main_local_port)
                    if not (1 <= main_local_port_int <= 65535):
                        raise ValueError("Port must be between 1 and 65535")
                except ValueError as e:
                    QMessageBox.warning(self, "Validation Error", 
                                      f"Main Scanner Local Port: {e}")
                    return
            
            # Validate on-demand scanner settings
            if ondemand_local_ip and ondemand_local_port:
                try:
                    ondemand_local_port_int = int(ondemand_local_port)
                    if not (1 <= ondemand_local_port_int <= 65535):
                        raise ValueError("Port must be between 1 and 65535")
                except ValueError as e:
                    QMessageBox.warning(self, "Validation Error", 
                                      f"On-Demand Scanner Local Port: {e}")
                    return
            
            # Validate output settings
            if output_remote_ip and output_remote_port:
                try:
                    output_remote_port_int = int(output_remote_port)
                    if not (1 <= output_remote_port_int <= 65535):
                        raise ValueError("Port must be between 1 and 65535")
                except ValueError as e:
                    QMessageBox.warning(self, "Validation Error", 
                                      f"Output Remote Port: {e}")
                    return
            
            # Check for port conflicts on same local IP
            if (main_local_ip == ondemand_local_ip and 
                main_local_port == ondemand_local_port and 
                main_local_ip and main_local_port):
                QMessageBox.warning(self, "Configuration Error", 
                    "Main Scanner and On-Demand Scanner cannot use the same local IP:Port combination.")
                return
            
            # Apply main scanner configuration
            if main_local_ip and main_local_port:
                self.app_state.stop_scanning()
                self.app_state.main_scanner_config = {
                    'local_ip': main_local_ip,
                    'local_port': int(main_local_port),
                    'remote_ip': main_remote_ip,
                    'remote_port': int(main_remote_port) if main_remote_port else None
                }
            else:
                self.app_state.main_scanner_config = None
            
            # Apply on-demand scanner configuration
            if ondemand_local_ip and ondemand_local_port:
                self.app_state.connect_ondemand_udp(
                    ondemand_local_ip, int(ondemand_local_port),
                    ondemand_remote_ip, 
                    int(ondemand_remote_port) if ondemand_remote_port else None
                )
            else:
                self.app_state.connect_ondemand_udp(None, None, None, None)
            
            # Apply output configuration
            if output_remote_ip and output_remote_port:
                self.app_state.connect_output_udp(
                    output_local_ip or "0.0.0.0",
                    int(output_local_port) if output_local_port else 0,
                    output_remote_ip,
                    int(output_remote_port)
                )
            else:
                self.app_state.connect_output_udp(None, None, None, None)
            
            # Save output format
            self.app_state.selected_output_format = self.output_format_combo.currentText()
            
            self.app_state.state_changed.emit()
            self.app_state.save_cache()
            QMessageBox.information(self, "Success", "Network configuration has been applied.")
            
        except Exception as e:
            QMessageBox.critical(self, "Configuration Error", f"Failed to apply configuration: {e}")

    def update_ui_from_state(self):
        """Update UI fields from app state"""
        # Main scanner
        if hasattr(self.app_state, 'main_scanner_config') and self.app_state.main_scanner_config:
            config = self.app_state.main_scanner_config
            self.main_local_ip.setText(config.get('local_ip', ''))
            self.main_local_port.setText(str(config.get('local_port', '')))
            remote_ip = config.get('remote_ip', '') or ''
            if remote_ip:
                self.main_remote_ip.setEditText(remote_ip)
            self.main_remote_port.setText(str(config.get('remote_port', '')) if config.get('remote_port') else '')
        
        # On-demand scanner
        if hasattr(self.app_state, 'ondemand_scanner_config') and self.app_state.ondemand_scanner_config:
            config = self.app_state.ondemand_scanner_config
            self.ondemand_local_ip.setText(config.get('local_ip', ''))
            self.ondemand_local_port.setText(str(config.get('local_port', '')))
            remote_ip = config.get('remote_ip', '') or ''
            if remote_ip:
                self.ondemand_remote_ip.setEditText(remote_ip)
            self.ondemand_remote_port.setText(str(config.get('remote_port', '')) if config.get('remote_port') else '')
        
        # Output
        if hasattr(self.app_state, 'output_config') and self.app_state.output_config:
            config = self.app_state.output_config
            self.output_local_ip.setText(config.get('local_ip', ''))
            self.output_local_port.setText(str(config.get('local_port', '')) if config.get('local_port') else '0')
            remote_ip = config.get('remote_ip', '')
            if remote_ip:
                self.output_remote_ip.setEditText(remote_ip)
            self.output_remote_port.setText(str(config.get('remote_port', '')))

    def create_header(self, parent_layout):
        title = QLabel("Network Configuration (UDP)")
        title.setObjectName("h1")
        subtitle = QLabel("Configure UDP network connections for data input and output.")
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

    def create_network_sections(self, parent_layout):
        # Main Scanner Input Section
        parent_layout.addWidget(self.create_main_scanner_section())
        
        # On-Demand Scanner Input Section
        parent_layout.addWidget(self.create_ondemand_scanner_section())
        
        # Output Section
        parent_layout.addWidget(self.create_output_section())

    def create_main_scanner_section(self):
        section = QFrame()
        section.setObjectName("panel")
        layout = QVBoxLayout(section)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)
        
        title = QLabel("Main Scanner Input (UDP)")
        title.setObjectName("h2")
        layout.addWidget(title)
        
        desc = QLabel("Configure where this PC listens for QR codes from the main scanner:")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # Local IP and Port (where this PC listens)
        grid.addWidget(QLabel("Local IP (this PC):"), 0, 0)
        self.main_local_ip = QLineEdit()
        self.main_local_ip.setPlaceholderText("e.g., 192.168.1.100 or 0.0.0.0")
        grid.addWidget(self.main_local_ip, 0, 1)
        
        grid.addWidget(QLabel("Local Port (listen):"), 1, 0)
        self.main_local_port = QLineEdit()
        self.main_local_port.setPlaceholderText("e.g., 5000")
        grid.addWidget(self.main_local_port, 1, 1)
        
        # Remote IP and Port (optional filter) - now with dropdown
        grid.addWidget(QLabel("Remote IP (scanner):"), 2, 0)
        self.main_remote_ip = QComboBox()
        self.main_remote_ip.setEditable(True)
        self.main_remote_ip.setPlaceholderText("Optional: Select or enter scanner IP")
        self.main_remote_ip.addItem("")  # Empty option
        # Refresh list when dropdown is opened
        self.main_remote_ip.showPopup = lambda: self._show_popup_with_refresh(self.main_remote_ip)
        grid.addWidget(self.main_remote_ip, 2, 1)
        
        grid.addWidget(QLabel("Remote Port (scanner):"), 3, 0)
        self.main_remote_port = QLineEdit()
        self.main_remote_port.setPlaceholderText("Optional: e.g., 5001 (leave empty for any)")
        grid.addWidget(self.main_remote_port, 3, 1)
        
        layout.addLayout(grid)
        
        self.main_status_text = QLabel("Not Connected")
        self.main_status_text.setObjectName("statusError")
        layout.addWidget(self.main_status_text)
        
        return section

    def create_ondemand_scanner_section(self):
        section = QFrame()
        section.setObjectName("panel")
        layout = QVBoxLayout(section)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)
        
        title = QLabel("On-Demand Scanner Input (UDP)")
        title.setObjectName("h2")
        layout.addWidget(title)
        
        desc = QLabel("Configure where this PC listens for on-demand scans (card details/counting):")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        
        grid.addWidget(QLabel("Local IP (this PC):"), 0, 0)
        self.ondemand_local_ip = QLineEdit()
        self.ondemand_local_ip.setPlaceholderText("e.g., 192.168.1.100 or 0.0.0.0")
        grid.addWidget(self.ondemand_local_ip, 0, 1)
        
        grid.addWidget(QLabel("Local Port (listen):"), 1, 0)
        self.ondemand_local_port = QLineEdit()
        self.ondemand_local_port.setPlaceholderText("e.g., 5100")
        grid.addWidget(self.ondemand_local_port, 1, 1)
        
        grid.addWidget(QLabel("Remote IP (scanner):"), 2, 0)
        self.ondemand_remote_ip = QComboBox()
        self.ondemand_remote_ip.setEditable(True)
        self.ondemand_remote_ip.setPlaceholderText("Optional: Select or enter scanner IP")
        self.ondemand_remote_ip.addItem("")  # Empty option
        # Refresh list when dropdown is opened
        self.ondemand_remote_ip.showPopup = lambda: self._show_popup_with_refresh(self.ondemand_remote_ip)
        grid.addWidget(self.ondemand_remote_ip, 2, 1)
        
        grid.addWidget(QLabel("Remote Port (scanner):"), 3, 0)
        self.ondemand_remote_port = QLineEdit()
        self.ondemand_remote_port.setPlaceholderText("Optional: e.g., 5101 (leave empty for any)")
        grid.addWidget(self.ondemand_remote_port, 3, 1)
        
        layout.addLayout(grid)
        
        self.ondemand_status_text = QLabel("Not Connected")
        self.ondemand_status_text.setObjectName("statusError")
        layout.addWidget(self.ondemand_status_text)
        
        return section

    def create_output_section(self):
        section = QFrame()
        section.setObjectName("panel")
        layout = QVBoxLayout(section)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)
        
        title = QLabel("Output Configuration (UDP)")
        title.setObjectName("h2")
        layout.addWidget(title)
        
        desc = QLabel("Configure where this PC sends validation results (to PLC/controller):")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        
        grid.addWidget(QLabel("Local IP (this PC):"), 0, 0)
        self.output_local_ip = QLineEdit()
        self.output_local_ip.setPlaceholderText("e.g., 192.168.1.100 or 0.0.0.0")
        grid.addWidget(self.output_local_ip, 0, 1)
        
        grid.addWidget(QLabel("Local Port (send from):"), 1, 0)
        self.output_local_port = QLineEdit()
        self.output_local_port.setPlaceholderText("0 for auto-assign")
        grid.addWidget(self.output_local_port, 1, 1)
        
        grid.addWidget(QLabel("Remote IP (PLC):"), 2, 0)
        self.output_remote_ip = QComboBox()
        self.output_remote_ip.setEditable(True)
        self.output_remote_ip.setPlaceholderText("Select or enter PLC IP")
        self.output_remote_ip.addItem("")  # Empty option
        # Refresh list when dropdown is opened
        self.output_remote_ip.showPopup = lambda: self._show_popup_with_refresh(self.output_remote_ip)
        grid.addWidget(self.output_remote_ip, 2, 1)
        
        grid.addWidget(QLabel("Remote Port (PLC):"), 3, 0)
        self.output_remote_port = QLineEdit()
        self.output_remote_port.setPlaceholderText("e.g., 6000")
        grid.addWidget(self.output_remote_port, 3, 1)
        
        layout.addLayout(grid)
        
        layout.addWidget(QLabel("Data Output Format:"))
        self.output_format_combo = QComboBox()
        layout.addWidget(self.output_format_combo)
        
        self.output_status_text = QLabel("Not Connected")
        self.output_status_text.setObjectName("statusError")
        layout.addWidget(self.output_status_text)
        
        return section

    def create_action_buttons(self, parent_layout):
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        apply_btn = QPushButton("Apply Configuration")
        apply_btn.setObjectName("primary")
        apply_btn.clicked.connect(self.apply_configuration)
        
        disconnect_btn = QPushButton("Disconnect All")
        disconnect_btn.setObjectName("secondary")
        disconnect_btn.clicked.connect(self.disconnect_all)
        
        refresh_btn = QPushButton("🔄 Refresh Network")
        refresh_btn.setObjectName("secondary")
        refresh_btn.clicked.connect(self.refresh_network_info)
        refresh_btn.setToolTip("Refresh local and remote IP addresses")
        
        layout.addWidget(apply_btn)
        layout.addWidget(disconnect_btn)
        layout.addWidget(refresh_btn)
        layout.addStretch()
        parent_layout.addLayout(layout)

    def disconnect_all(self):
        """Disconnect all UDP connections and clear ports/remote IPs (keep local IPs)"""
        # Disconnect all ports
        self.app_state.disconnect_all_ports()
        
        # Clear ports and remote IPs, but KEEP local IPs
        # Main scanner
        self.main_local_port.clear()
        self.main_remote_ip.setCurrentIndex(0)  # Set to empty
        self.main_remote_ip.setEditText("")
        self.main_remote_port.clear()
        
        # On-demand scanner
        self.ondemand_local_port.clear()
        self.ondemand_remote_ip.setCurrentIndex(0)  # Set to empty
        self.ondemand_remote_ip.setEditText("")
        self.ondemand_remote_port.clear()
        
        # Output
        self.output_local_port.clear()
        self.output_remote_ip.setCurrentIndex(0)  # Set to empty
        self.output_remote_ip.setEditText("")
        self.output_remote_port.clear()
        
        # Update status labels
        self.main_status_text.setText("Not Connected")
        self.main_status_text.setObjectName("statusError")
        self.ondemand_status_text.setText("Not Connected")
        self.ondemand_status_text.setObjectName("statusError")
        self.output_status_text.setText("Not Connected")
        self.output_status_text.setObjectName("statusError")
        
        # Refresh styles
        self.main_status_text.style().unpolish(self.main_status_text)
        self.main_status_text.style().polish(self.main_status_text)
        self.ondemand_status_text.style().unpolish(self.ondemand_status_text)
        self.ondemand_status_text.style().polish(self.ondemand_status_text)
        self.output_status_text.style().unpolish(self.output_status_text)
        self.output_status_text.style().polish(self.output_status_text)
        
        self.add_log_entry("All connections disconnected (local IPs preserved)", "blue")
        QMessageBox.information(self, "Disconnected", 
                               "All network connections have been closed.\n\n"
                               "Ports and remote IPs cleared.\n"
                               "Local IPs preserved for quick reconnection.")

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

    def populate_format_dropdown(self):
        self.output_format_combo.clear()
        if self.app_state.output_formats:
            self.output_format_combo.addItems(self.app_state.output_formats.keys())
            if self.app_state.selected_output_format in self.app_state.output_formats:
                self.output_format_combo.setCurrentText(self.app_state.selected_output_format)
            elif self.app_state.output_formats:
                first_format = list(self.app_state.output_formats.keys())[0]
                self.output_format_combo.setCurrentText(first_format)
                self.app_state.selected_output_format = first_format
        else:
            self.output_format_combo.addItems(["No formats found"])
    
    def add_log_entry(self, message, color="black"):
        self.log_text.append(f"[{self.app_state.get_timestamp()}] {message}")
    
    def update_output_status(self, message, color):
        self.add_log_entry(message, color)
        self.output_status_text.setText(message)
        if color == "green":
            self.output_status_text.setObjectName("statusOK")
        elif color == "red":
            self.output_status_text.setObjectName("statusError")
        elif color == "orange":
            self.output_status_text.setObjectName("statusWarning")
        else:
            self.output_status_text.setObjectName("statusIdle")
        self.output_status_text.style().unpolish(self.output_status_text)
        self.output_status_text.style().polish(self.output_status_text)

    def update_ondemand_status(self, message, color):
        self.add_log_entry(message, color)
        if message.startswith("Listening on") or message == "Not Connected":
            self.ondemand_status_text.setText(message)
            if color == "green":
                self.ondemand_status_text.setObjectName("statusOK")
            elif color == "red":
                self.ondemand_status_text.setObjectName("statusError")
            self.ondemand_status_text.style().unpolish(self.ondemand_status_text)
            self.ondemand_status_text.style().polish(self.ondemand_status_text)

    def update_input_status(self, message, color):
        self.add_log_entry(message, color)
        self.main_status_text.setText(message)
        if color == "green":
            self.main_status_text.setObjectName("statusOK")
        elif color == "red":
            self.main_status_text.setObjectName("statusError")
        elif color == "orange":
            self.main_status_text.setObjectName("statusWarning")
        else:
            self.main_status_text.setObjectName("statusIdle")
        self.main_status_text.style().unpolish(self.main_status_text)
        self.main_status_text.style().polish(self.main_status_text)

    def update_theme(self, theme_name):
        stylesheet = DARK_THEME_STYLESHEET if theme_name == "dark" else LIGHT_THEME_STYLESHEET
        self.setStyleSheet(stylesheet)
        for widget in self.findChildren(QWidget):
            widget.style().unpolish(widget)
            widget.style().polish(widget)
