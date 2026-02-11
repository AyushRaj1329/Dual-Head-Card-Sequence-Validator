# src/ui/network_setup.py
import sys
import socket
import serial.tools.list_ports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QHBoxLayout,
    QVBoxLayout, QComboBox, QTextEdit, QScrollArea, QFrame, QMessageBox, 
    QGridLayout, QLineEdit, QSizePolicy
)
from PyQt6.QtCore import Qt
from .styles import DARK_THEME_STYLESHEET, LIGHT_THEME_STYLESHEET
from .widgets import ClockWidget

class NetworkSetupWindow(QMainWindow):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.setWindowTitle("Network & COM Port Configuration")
        self.setMinimumSize(950, 750)  # Increased minimum size for better layout
        self.resize(1000, 800)  # Set initial size
        
        try:
            self.update_theme(self.app_state.current_theme)
            self.app_state.theme_changed.connect(self.update_theme)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setFrameShape(QFrame.Shape.NoFrame)  # Remove frame for cleaner look
            
            central_widget = QWidget()
            scroll.setWidget(central_widget)
            self.setCentralWidget(scroll)

            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(30, 25, 30, 25)
            main_layout.setSpacing(18)  # Consistent spacing throughout

            self.create_header(main_layout)
            self.create_network_sections(main_layout)
            self.create_action_buttons(main_layout)
            self.create_status_log(main_layout)
            
            # Add stretch at the end to prevent uneven spacing
            main_layout.addStretch(1)
            
            self.app_state.state_changed.connect(self.update_ui_from_state)
            self.app_state.com_status_changed.connect(self.update_input_status)
            self.app_state.output_com_status_changed.connect(self.update_output_status)
            self.app_state.ondemand_scan_status_update.connect(self.update_ondemand_status)
            
            # Connect focus events to refresh remote IPs when user interacts with dropdown
            self.main_remote_ip.activated.connect(lambda: self.refresh_remote_ip_dropdown(self.main_remote_ip))
            self.output_remote_ip.activated.connect(lambda: self.refresh_remote_ip_dropdown(self.output_remote_ip))
            
            self.populate_format_dropdown()
            self.update_ui_from_state()
            
            # Initialize IP detection
            self.detected_local_ips = []
            self.detected_remote_ips = []
            
            # Populate local IP dropdowns for main scanner and output
            self.populate_local_ip_dropdown(self.main_local_ip)
            self.populate_local_ip_dropdown(self.output_local_ip)
            
            # Detect remote IPs
            remote_ips = self.detect_remote_ips()
            
            # Populate remote IP dropdowns with detected IPs
            if remote_ips:
                self.populate_remote_ip_dropdowns(remote_ips)
            
            # Auto-apply saved configuration if available
            self.auto_apply_saved_configuration()
        except Exception as e:
            print(f"Error initializing Network Setup Window: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Initialization Error", 
                               f"Failed to initialize Network & COM Port Configuration window:\n\n{str(e)}\n\n"
                               "Please check the console for details.")

    def detect_local_ips(self):
        """Detect available local IP addresses and populate dropdowns"""
        try:
            # Populate both local IP dropdowns
            self.populate_local_ip_dropdown(self.main_local_ip)
            self.populate_local_ip_dropdown(self.output_local_ip)
        except Exception as e:
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
        has_output_config = (hasattr(self.app_state, 'output_config') and 
                            self.app_state.output_config)
        
        if not (has_main_config or has_output_config):
            # No saved configuration
            return
        
        # Check if saved remote IPs are currently available on network
        auto_apply = False
        
        if has_main_config:
            remote_ip = self.app_state.main_scanner_config.get('remote_ip')
            if remote_ip and remote_ip in self.detected_remote_ips:
                auto_apply = True
                self.add_log_entry(f"Main scanner remote IP {remote_ip} detected on network", "green")
        
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
            if has_main_config or has_output_config:
                self.add_log_entry("Saved configuration found but remote devices not detected", "orange")
                self.add_log_entry("Click 'Refresh Network' to scan for devices", "blue")
    
    def refresh_network_info(self):
        """Refresh both local and remote IP information"""
        self.add_log_entry("Refreshing network information...", "blue")
        
        # Refresh local IP dropdowns
        self.detect_local_ips()
        
        # Refresh remote IPs
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
        output_current = self.output_remote_ip.currentText()
        
        # Clear and repopulate both dropdowns
        for combo in [self.main_remote_ip, self.output_remote_ip]:
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
        
        if output_current:
            index = self.output_remote_ip.findText(output_current)
            if index >= 0:
                self.output_remote_ip.setCurrentIndex(index)
            else:
                self.output_remote_ip.setEditText(output_current)

    def apply_main_scanner_configuration(self):
        """Apply main scanner UDP configuration"""
        try:
            main_local_ip_text = self.main_local_ip.currentText().strip()
            if " (" in main_local_ip_text:
                main_local_ip = main_local_ip_text.split(" (")[0]
            elif main_local_ip_text == "0.0.0.0 (All interfaces)":
                main_local_ip = "0.0.0.0"
            elif main_local_ip_text == "127.0.0.1 (Localhost)":
                main_local_ip = "127.0.0.1"
            else:
                main_local_ip = main_local_ip_text
            
            main_local_port = self.main_local_port.currentText().strip()
            main_remote_ip = self.main_remote_ip.currentText().strip() or None
            main_remote_port = self.main_remote_port.currentText().strip() or None
            
            if main_local_ip and main_local_port:
                try:
                    main_local_port_int = int(main_local_port)
                    if not (1 <= main_local_port_int <= 65535):
                        raise ValueError("Port must be between 1 and 65535")
                except ValueError as e:
                    QMessageBox.warning(self, "Validation Error", f"Local Port: {e}")
                    return
                
                self.app_state.stop_scanning()
                self.app_state.main_scanner_config = {
                    'local_ip': main_local_ip,
                    'local_port': int(main_local_port),
                    'remote_ip': main_remote_ip,
                    'remote_port': int(main_remote_port) if main_remote_port else None
                }
            else:
                self.app_state.main_scanner_config = None
            
            self.app_state.state_changed.emit()
            self.app_state.save_cache()
            QMessageBox.information(self, "Success", "Main scanner applied.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply: {e}")

    def apply_ondemand_configuration(self):
        """Apply on-demand scanner serial configuration"""
        try:
            ondemand_com_port = self.ondemand_com_port.currentText().strip()
            
            if not ondemand_com_port or "No ports" in ondemand_com_port:
                # Disconnect the on-demand scanner
                self.app_state.connect_ondemand_serial(port=None)
                QMessageBox.information(self, "Success", "On-demand scanner disconnected.")
                return
            
            # Get serial settings
            ondemand_baud_rate = int(self.ondemand_baud_rate.currentText())
            ondemand_data_bits = int(self.ondemand_data_bits.currentText())
            
            parity_map = {"None": "N", "Even": "E", "Odd": "O", "Mark": "M", "Space": "S"}
            ondemand_parity = parity_map.get(self.ondemand_parity.currentText(), "N")
            
            stop_bits_map = {"1": 1, "1.5": 1.5, "2": 2}
            ondemand_stop_bits = stop_bits_map.get(self.ondemand_stop_bits.currentText(), 1)
            
            ondemand_timeout = float(self.ondemand_timeout.currentText().strip() or "1")
            
            # Connect using the new method
            self.app_state.connect_ondemand_serial(
                port=ondemand_com_port,
                baudrate=ondemand_baud_rate,
                bytesize=ondemand_data_bits,
                parity=ondemand_parity,
                stopbits=ondemand_stop_bits,
                timeout=ondemand_timeout
            )
            
            QMessageBox.information(self, "Success", "On-demand scanner applied.")
            
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Error", f"Failed to apply: {e}\n\nTraceback:\n{traceback.format_exc()}")

    def apply_output_configuration(self):
        """Apply output UDP configuration"""
        try:
            output_local_ip_text = self.output_local_ip.currentText().strip()
            if " (" in output_local_ip_text:
                output_local_ip = output_local_ip_text.split(" (")[0]
            elif output_local_ip_text == "0.0.0.0 (All interfaces)":
                output_local_ip = "0.0.0.0"
            elif output_local_ip_text == "127.0.0.1 (Localhost)":
                output_local_ip = "127.0.0.1"
            else:
                output_local_ip = output_local_ip_text
            
            output_local_port = self.output_local_port.currentText().strip() or "0"
            output_remote_ip = self.output_remote_ip.currentText().strip()
            output_remote_port = self.output_remote_port.currentText().strip()
            
            if output_remote_ip and output_remote_port:
                try:
                    output_remote_port_int = int(output_remote_port)
                    if not (1 <= output_remote_port_int <= 65535):
                        raise ValueError("Port must be between 1 and 65535")
                except ValueError as e:
                    QMessageBox.warning(self, "Validation Error", f"Remote Port: {e}")
                    return
                
                self.app_state.connect_output_udp(
                    output_local_ip or "0.0.0.0",
                    int(output_local_port) if output_local_port else 0,
                    output_remote_ip,
                    int(output_remote_port)
                )
            else:
                self.app_state.connect_output_udp(None, None, None, None)
            
            self.app_state.selected_output_format = self.output_format_combo.currentText()
            
            self.app_state.state_changed.emit()
            self.app_state.save_cache()
            QMessageBox.information(self, "Success", "Output applied.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply: {e}")

    def apply_configuration(self):
        """Apply the network configuration (UDP for main/output, Serial for on-demand)"""
        self.apply_main_scanner_configuration()
        self.apply_ondemand_configuration()
        self.apply_output_configuration()

    def update_ui_from_state(self):
        """Update UI fields from app state"""
        try:
            # Main scanner
            if hasattr(self.app_state, 'main_scanner_config') and self.app_state.main_scanner_config:
                config = self.app_state.main_scanner_config
                local_ip = config.get('local_ip', '')
                if local_ip:
                    # Try to find and select the IP in dropdown
                    found = False
                    for i in range(self.main_local_ip.count()):
                        item_text = self.main_local_ip.itemText(i)
                        # Check if this item contains the IP
                        if item_text.startswith(local_ip) or local_ip in item_text:
                            self.main_local_ip.setCurrentIndex(i)
                            found = True
                            break
                    # If not found in list, set it as text (editable combo box)
                    if not found:
                        self.main_local_ip.setEditText(local_ip)
                
                self.main_local_port.setEditText(str(config.get('local_port', '')))
                remote_ip = config.get('remote_ip', '') or ''
                if remote_ip:
                    self.main_remote_ip.setEditText(remote_ip)
                self.main_remote_port.setEditText(str(config.get('remote_port', '')) if config.get('remote_port') else '')
            
            # On-demand scanner (serial)
            if hasattr(self.app_state, 'start_card_scan_port') and self.app_state.start_card_scan_port:
                # Set COM port
                index = self.ondemand_com_port.findText(self.app_state.start_card_scan_port)
                if index >= 0:
                    self.ondemand_com_port.setCurrentIndex(index)
                
                # Set serial settings from app_state
                if hasattr(self.app_state, 'baud_rate'):
                    self.ondemand_baud_rate.setCurrentText(str(self.app_state.baud_rate))
                if hasattr(self.app_state, 'data_bits'):
                    self.ondemand_data_bits.setCurrentText(str(self.app_state.data_bits))
                
                # Convert parity back to display format
                if hasattr(self.app_state, 'parity'):
                    parity_reverse_map = {"N": "None", "E": "Even", "O": "Odd", "M": "Mark", "S": "Space"}
                    self.ondemand_parity.setCurrentText(parity_reverse_map.get(self.app_state.parity, "None"))
                
                # Convert stop bits back to display format
                if hasattr(self.app_state, 'stop_bits'):
                    self.ondemand_stop_bits.setCurrentText(str(self.app_state.stop_bits))
                if hasattr(self.app_state, 'timeout'):
                    self.ondemand_timeout.setEditText(str(self.app_state.timeout))
            
            # Output
            if hasattr(self.app_state, 'output_config') and self.app_state.output_config:
                config = self.app_state.output_config
                local_ip = config.get('local_ip', '')
                if local_ip:
                    # Try to find and select the IP in dropdown
                    found = False
                    for i in range(self.output_local_ip.count()):
                        item_text = self.output_local_ip.itemText(i)
                        # Check if this item contains the IP
                        if item_text.startswith(local_ip) or local_ip in item_text:
                            self.output_local_ip.setCurrentIndex(i)
                            found = True
                            break
                    # If not found in list, set it as text (editable combo box)
                    if not found:
                        self.output_local_ip.setEditText(local_ip)
                
                self.output_local_port.setEditText(str(config.get('local_port', '')) if config.get('local_port') else '0')
                remote_ip = config.get('remote_ip', '')
                if remote_ip:
                    self.output_remote_ip.setEditText(remote_ip)
                self.output_remote_port.setEditText(str(config.get('remote_port', '')))
        except Exception as e:
            print(f"Warning: Error updating UI from state: {e}")

    def create_header(self, parent_layout):
        title = QLabel("Network & COM Port Configuration")
        title.setObjectName("h1")
        subtitle = QLabel("Configure UDP network for main scanner/output and serial COM port for on-demand scanner.")
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
        # Create a grid layout for side-by-side sections
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Row 0: Main Scanner (UDP) and Output (UDP) side by side
        grid.addWidget(self.create_main_scanner_section(), 0, 0)
        grid.addWidget(self.create_output_section(), 0, 1)
        
        # Row 1: On-Demand Scanner (Serial) spans both columns at bottom
        grid.addWidget(self.create_ondemand_scanner_section(), 1, 0, 1, 2)
        
        parent_layout.addLayout(grid)

    def create_main_scanner_section(self):
        section = QFrame()
        section.setObjectName("panel")
        section.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        section.setMaximumWidth(500)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        title = QLabel("Main Scanner Input (UDP)")
        title.setObjectName("h2")
        layout.addWidget(title)
        
        desc = QLabel("Listen for QR codes from main scanner:")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setColumnStretch(1, 1)
        
        # Local IP (dropdown with available network interfaces)
        grid.addWidget(QLabel("Local IP:"), 0, 0)
        self.main_local_ip = QComboBox()
        self.main_local_ip.setEditable(True)
        self.main_local_ip.setMaximumWidth(250)
        grid.addWidget(self.main_local_ip, 0, 1)
        
        # Refresh button for local IPs
        refresh_main_ip_btn = QPushButton("🔄")
        refresh_main_ip_btn.setMaximumWidth(35)
        refresh_main_ip_btn.setFixedHeight(28)
        refresh_main_ip_btn.setToolTip("Refresh network interfaces")
        refresh_main_ip_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #2d2d2d;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #777;
            }
            QPushButton:pressed {
                background-color: #1d1d1d;
            }
        """)
        refresh_main_ip_btn.clicked.connect(lambda: self.populate_local_ip_dropdown(self.main_local_ip))
        grid.addWidget(refresh_main_ip_btn, 0, 2)
        
        # Local Port
        grid.addWidget(QLabel("Local Port:"), 1, 0)
        self.main_local_port = QComboBox()
        self.main_local_port.setEditable(True)
        self.main_local_port.addItems(["5000", "5001", "5002", "5003", "5004", "5005", "6000", "7000", "8000", "9000"])
        self.main_local_port.setCurrentText("5000")
        self.main_local_port.setMaximumWidth(250)
        grid.addWidget(self.main_local_port, 1, 1, 1, 2)
        
        # Remote IP and Port (optional filter)
        grid.addWidget(QLabel("Remote IP:"), 2, 0)
        self.main_remote_ip = QComboBox()
        self.main_remote_ip.setEditable(True)
        self.main_remote_ip.setPlaceholderText("Optional")
        self.main_remote_ip.setMaximumWidth(250)
        self.main_remote_ip.addItem("")
        self.main_remote_ip.showPopup = lambda: self._show_popup_with_refresh(self.main_remote_ip)
        grid.addWidget(self.main_remote_ip, 2, 1, 1, 2)
        
        grid.addWidget(QLabel("Remote Port:"), 3, 0)
        self.main_remote_port = QComboBox()
        self.main_remote_port.setEditable(True)
        self.main_remote_port.addItems(["", "5001", "5002", "5003", "5004", "5005", "6000", "7000", "8000", "9000"])
        self.main_remote_port.setCurrentText("")
        self.main_remote_port.setMaximumWidth(250)
        grid.addWidget(self.main_remote_port, 3, 1, 1, 2)
        
        layout.addLayout(grid)
        
        self.main_status_text = QLabel("Not Connected")
        self.main_status_text.setObjectName("statusError")
        layout.addWidget(self.main_status_text)
        
        # Apply button for main scanner section
        apply_main_btn = QPushButton("Apply Main Scanner")
        apply_main_btn.setObjectName("primary")
        apply_main_btn.clicked.connect(self.apply_main_scanner_configuration)
        layout.addWidget(apply_main_btn)
        
        return section

    def create_ondemand_scanner_section(self):
        section = QFrame()
        section.setObjectName("panel")
        section.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        title = QLabel("On-Demand Scanner Input (Serial)")
        title.setObjectName("h2")
        layout.addWidget(title)
        
        desc = QLabel("Serial COM port for on-demand scans:")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        grid = QGridLayout()
        grid.setSpacing(8)
        
        # COM Port Selection
        grid.addWidget(QLabel("COM Port:"), 0, 0)
        self.ondemand_com_port = QComboBox()
        self.ondemand_com_port.setEditable(False)
        self.ondemand_com_port.setPlaceholderText("Select COM port")
        self.ondemand_com_port.setMaximumWidth(200)
        self.populate_ondemand_com_ports()
        grid.addWidget(self.ondemand_com_port, 0, 1)
        
        # Refresh button for COM ports
        refresh_com_btn = QPushButton("🔄")
        refresh_com_btn.setMaximumWidth(35)
        refresh_com_btn.setFixedHeight(28)
        refresh_com_btn.setToolTip("Refresh COM ports")
        refresh_com_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #2d2d2d;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #777;
            }
            QPushButton:pressed {
                background-color: #1d1d1d;
            }
        """)
        refresh_com_btn.clicked.connect(self.populate_ondemand_com_ports)
        grid.addWidget(refresh_com_btn, 0, 2)
        
        # Baud Rate
        grid.addWidget(QLabel("Baud Rate:"), 0, 3)
        self.ondemand_baud_rate = QComboBox()
        self.ondemand_baud_rate.addItems(["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"])
        self.ondemand_baud_rate.setCurrentText("115200")
        self.ondemand_baud_rate.setMaximumWidth(150)
        grid.addWidget(self.ondemand_baud_rate, 0, 4)
        
        # Hidden fields with default values (not shown in UI)
        self.ondemand_data_bits = QComboBox()
        self.ondemand_data_bits.addItems(["8"])
        self.ondemand_data_bits.setCurrentText("8")
        self.ondemand_data_bits.setVisible(False)
        
        self.ondemand_parity = QComboBox()
        self.ondemand_parity.addItems(["None"])
        self.ondemand_parity.setCurrentText("None")
        self.ondemand_parity.setVisible(False)
        
        self.ondemand_stop_bits = QComboBox()
        self.ondemand_stop_bits.addItems(["1"])
        self.ondemand_stop_bits.setCurrentText("1")
        self.ondemand_stop_bits.setVisible(False)
        
        self.ondemand_timeout = QComboBox()
        self.ondemand_timeout.addItems(["1"])
        self.ondemand_timeout.setCurrentText("1")
        self.ondemand_timeout.setVisible(False)
        
        layout.addLayout(grid)
        
        self.ondemand_status_text = QLabel("Not Connected")
        self.ondemand_status_text.setObjectName("statusError")
        layout.addWidget(self.ondemand_status_text)
        
        # Apply button for on-demand scanner section
        apply_ondemand_btn = QPushButton("Apply On-Demand Scanner")
        apply_ondemand_btn.setObjectName("primary")
        apply_ondemand_btn.clicked.connect(self.apply_ondemand_configuration)
        layout.addWidget(apply_ondemand_btn)
        
        return section
    
    def populate_ondemand_com_ports(self):
        """Populate the on-demand COM port dropdown with available ports"""
        try:
            import serial.tools.list_ports
            
            # Store current selection
            current_port = self.ondemand_com_port.currentText()
            
            # Clear and repopulate
            self.ondemand_com_port.clear()
            self.ondemand_com_port.addItem("")  # Empty option
            
            # Get available ports
            ports = serial.tools.list_ports.comports()
            for port in ports:
                self.ondemand_com_port.addItem(port.device)
            
            # Restore selection if it still exists
            if current_port:
                index = self.ondemand_com_port.findText(current_port)
                if index >= 0:
                    self.ondemand_com_port.setCurrentIndex(index)
        except Exception as e:
            # If COM port enumeration fails, just add empty option
            self.ondemand_com_port.clear()
            self.ondemand_com_port.addItem("")
            print(f"Warning: Could not enumerate COM ports: {e}")
    
    def populate_local_ip_dropdown(self, combo_box):
        """Populate a local IP dropdown with operational Ethernet interfaces only"""
        try:
            import psutil
            
            # Store current selection
            current_ip = combo_box.currentText()
            
            # Clear and repopulate
            combo_box.clear()
            
            # Add special addresses first
            combo_box.addItem("0.0.0.0 (All interfaces)")
            combo_box.addItem("127.0.0.1 (Localhost)")
            
            # Get all network interfaces with their stats
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            ip_list = []
            ethernet_count = 0
            
            for interface_name, addrs in interfaces.items():
                # Check if interface is up and operational
                if interface_name in stats:
                    stat = stats[interface_name]
                    # Only include interfaces that are UP
                    if not stat.isup:
                        continue
                
                # Filter for Ethernet interfaces (exclude virtual, loopback, etc.)
                interface_lower = interface_name.lower()
                is_ethernet = any(keyword in interface_lower for keyword in 
                                ['ethernet', 'eth', 'local area connection', 'wi-fi', 'wlan'])
                
                # Skip virtual adapters
                is_virtual = any(keyword in interface_lower for keyword in 
                               ['virtual', 'vmware', 'virtualbox', 'vbox', 'hyper-v', 
                                'vpn', 'tap', 'tun', 'loopback'])
                
                if not is_ethernet or is_virtual:
                    continue
                
                # Get IPv4 addresses for this interface
                for addr in addrs:
                    if addr.family == 2:  # AF_INET (IPv4)
                        ip = addr.address
                        if ip and ip not in ['127.0.0.1', '0.0.0.0']:
                            ethernet_count += 1
                            # Create display name with status
                            status = "UP" if interface_name in stats and stats[interface_name].isup else "DOWN"
                            ip_display = f"{ip} ({interface_name} - {status})"
                            ip_list.append((ip, ip_display, interface_name))
            
            # Sort by IP address
            ip_list = sorted(ip_list, key=lambda x: x[0])
            
            # Add to dropdown
            for ip, display, iface in ip_list:
                combo_box.addItem(display, ip)  # Store actual IP as data
            
            # Restore selection if it still exists
            if current_ip:
                # Try to find exact match first
                index = combo_box.findText(current_ip)
                if index >= 0:
                    combo_box.setCurrentIndex(index)
                else:
                    # Try to find by IP value (in case display format changed)
                    for i in range(combo_box.count()):
                        item_data = combo_box.itemData(i)
                        if item_data == current_ip or combo_box.itemText(i).startswith(current_ip):
                            combo_box.setCurrentIndex(i)
                            break
            
            if ethernet_count > 0:
                self.add_log_entry(f"Found {ethernet_count} operational Ethernet interface(s)", "green")
            else:
                self.add_log_entry("No operational Ethernet interfaces found", "orange")
            
        except ImportError:
            # psutil not available, fall back to basic detection
            self.add_log_entry("psutil not installed - using basic detection (install: pip install psutil)", "orange")
            try:
                import socket
                hostname = socket.gethostname()
                local_ips = socket.gethostbyname_ex(hostname)[2]
                local_ips = [ip for ip in local_ips if not ip.startswith("127.")]
                
                combo_box.clear()
                combo_box.addItem("0.0.0.0 (All interfaces)")
                combo_box.addItem("127.0.0.1 (Localhost)")
                
                for ip in local_ips:
                    combo_box.addItem(ip)
                
                self.add_log_entry(f"Found {len(local_ips)} IP address(es) (basic detection)", "blue")
            except Exception as e:
                combo_box.clear()
                combo_box.addItem("0.0.0.0 (All interfaces)")
                combo_box.addItem("127.0.0.1 (Localhost)")
                print(f"Warning: Could not detect network interfaces: {e}")
                self.add_log_entry("Could not detect network interfaces, using defaults", "orange")
        except Exception as e:
            combo_box.clear()
            combo_box.addItem("0.0.0.0 (All interfaces)")
            combo_box.addItem("127.0.0.1 (Localhost)")
            print(f"Warning: Could not populate local IPs: {e}")
            self.add_log_entry(f"Error detecting network interfaces: {e}", "orange")

    def create_output_section(self):
        section = QFrame()
        section.setObjectName("panel")
        section.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        title = QLabel("Output Configuration (UDP)")
        title.setObjectName("h2")
        layout.addWidget(title)
        
        desc = QLabel("Send validation results to PLC/controller:")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        grid = QGridLayout()
        grid.setSpacing(8)
        
        # Local IP (dropdown with available network interfaces)
        grid.addWidget(QLabel("Local IP:"), 0, 0)
        self.output_local_ip = QComboBox()
        self.output_local_ip.setEditable(True)
        self.output_local_ip.setMaximumWidth(250)
        grid.addWidget(self.output_local_ip, 0, 1)
        
        # Refresh button for local IPs
        refresh_output_ip_btn = QPushButton("🔄")
        refresh_output_ip_btn.setMaximumWidth(35)
        refresh_output_ip_btn.setFixedHeight(28)
        refresh_output_ip_btn.setToolTip("Refresh network interfaces")
        refresh_output_ip_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #2d2d2d;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #777;
            }
            QPushButton:pressed {
                background-color: #1d1d1d;
            }
        """)
        refresh_output_ip_btn.clicked.connect(lambda: self.populate_local_ip_dropdown(self.output_local_ip))
        grid.addWidget(refresh_output_ip_btn, 0, 2)
        
        # Local Port
        grid.addWidget(QLabel("Local Port:"), 0, 3)
        self.output_local_port = QComboBox()
        self.output_local_port.setEditable(True)
        self.output_local_port.addItems(["0", "5000", "5001", "5002", "6000", "7000", "8000", "9000"])
        self.output_local_port.setCurrentText("0")
        self.output_local_port.setMaximumWidth(120)
        grid.addWidget(self.output_local_port, 0, 4)
        
        grid.addWidget(QLabel("Remote IP:"), 1, 0)
        self.output_remote_ip = QComboBox()
        self.output_remote_ip.setEditable(True)
        self.output_remote_ip.setPlaceholderText("PLC IP")
        self.output_remote_ip.setMaximumWidth(250)
        self.output_remote_ip.addItem("")
        self.output_remote_ip.showPopup = lambda: self._show_popup_with_refresh(self.output_remote_ip)
        grid.addWidget(self.output_remote_ip, 1, 1, 1, 2)
        
        grid.addWidget(QLabel("Remote Port:"), 1, 3)
        self.output_remote_port = QComboBox()
        self.output_remote_port.setEditable(True)
        self.output_remote_port.addItems(["6000", "6001", "6002", "5000", "5001", "7000", "8000", "9000", "10000"])
        self.output_remote_port.setCurrentText("6000")
        self.output_remote_port.setMaximumWidth(120)
        grid.addWidget(self.output_remote_port, 1, 4)
        
        grid.addWidget(QLabel("Format:"), 2, 0)
        self.output_format_combo = QComboBox()
        self.output_format_combo.setMaximumWidth(250)
        grid.addWidget(self.output_format_combo, 2, 1, 1, 2)
        
        layout.addLayout(grid)
        
        self.output_status_text = QLabel("Not Connected")
        self.output_status_text.setObjectName("statusError")
        layout.addWidget(self.output_status_text)
        
        # Apply button for output section
        apply_output_btn = QPushButton("Apply Output")
        apply_output_btn.setObjectName("primary")
        apply_output_btn.clicked.connect(self.apply_output_configuration)
        layout.addWidget(apply_output_btn)
        
        return section

    def create_action_buttons(self, parent_layout):
        layout = QHBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(0, 10, 0, 10)
        
        test_btn = QPushButton("🔍 Test Connection")
        test_btn.setObjectName("secondary")
        test_btn.setFixedHeight(40)
        test_btn.clicked.connect(self.test_udp_connection)
        test_btn.setToolTip("Test UDP connectivity")
        
        disconnect_btn = QPushButton("Disconnect All")
        disconnect_btn.setObjectName("secondary")
        disconnect_btn.setFixedHeight(40)
        disconnect_btn.clicked.connect(self.disconnect_all)
        
        refresh_btn = QPushButton("🔄 Refresh Network")
        refresh_btn.setObjectName("secondary")
        refresh_btn.setFixedHeight(40)
        refresh_btn.clicked.connect(self.refresh_network_info)
        refresh_btn.setToolTip("Refresh network info")
        
        layout.addWidget(test_btn)
        layout.addWidget(disconnect_btn)
        layout.addWidget(refresh_btn)
        layout.addStretch()
        parent_layout.addLayout(layout)

    def test_udp_connection(self):
        """Test UDP connectivity for configured interfaces"""
        import socket
        import subprocess
        
        self.add_log_entry("=== Starting UDP Connection Test ===", "blue")
        
        # Test Main Scanner Local IP
        main_local_ip_text = self.main_local_ip.currentText().strip()
        if " (" in main_local_ip_text:
            main_local_ip = main_local_ip_text.split(" (")[0]
        else:
            main_local_ip = main_local_ip_text
        
        if main_local_ip and main_local_ip != "0.0.0.0":
            self.add_log_entry(f"Testing Main Scanner Local IP: {main_local_ip}", "blue")
            
            # Ping test
            try:
                result = subprocess.run(['ping', '-n', '1', '-w', '1000', main_local_ip], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    self.add_log_entry(f"  ✓ Ping successful: {main_local_ip}", "green")
                else:
                    self.add_log_entry(f"  ✗ Ping failed: {main_local_ip}", "red")
            except Exception as e:
                self.add_log_entry(f"  ✗ Ping error: {e}", "orange")
            
            # Socket bind test
            try:
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                test_port = int(self.main_local_port.currentText()) if self.main_local_port.currentText() else 5000
                test_socket.bind((main_local_ip, test_port))
                test_socket.close()
                self.add_log_entry(f"  ✓ Can bind to {main_local_ip}:{test_port}", "green")
            except Exception as e:
                self.add_log_entry(f"  ✗ Cannot bind to {main_local_ip}:{test_port} - {e}", "red")
        
        # Test Output Local IP
        output_local_ip_text = self.output_local_ip.currentText().strip()
        if " (" in output_local_ip_text:
            output_local_ip = output_local_ip_text.split(" (")[0]
        else:
            output_local_ip = output_local_ip_text
        
        if output_local_ip and output_local_ip != "0.0.0.0":
            self.add_log_entry(f"Testing Output Local IP: {output_local_ip}", "blue")
            
            # Ping test
            try:
                result = subprocess.run(['ping', '-n', '1', '-w', '1000', output_local_ip], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    self.add_log_entry(f"  ✓ Ping successful: {output_local_ip}", "green")
                else:
                    self.add_log_entry(f"  ✗ Ping failed: {output_local_ip}", "red")
            except Exception as e:
                self.add_log_entry(f"  ✗ Ping error: {e}", "orange")
            
            # Socket bind test
            try:
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                test_port = int(self.output_local_port.currentText()) if self.output_local_port.currentText() else 0
                test_socket.bind((output_local_ip, test_port))
                test_socket.close()
                self.add_log_entry(f"  ✓ Can bind to {output_local_ip}:{test_port}", "green")
            except Exception as e:
                self.add_log_entry(f"  ✗ Cannot bind to {output_local_ip}:{test_port} - {e}", "red")
        
        # Test Remote IPs (ping only)
        main_remote_ip = self.main_remote_ip.currentText().strip()
        if main_remote_ip:
            self.add_log_entry(f"Testing Main Scanner Remote IP: {main_remote_ip}", "blue")
            try:
                result = subprocess.run(['ping', '-n', '1', '-w', '1000', main_remote_ip], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    self.add_log_entry(f"  ✓ Scanner reachable: {main_remote_ip}", "green")
                else:
                    self.add_log_entry(f"  ✗ Scanner not reachable: {main_remote_ip}", "orange")
            except Exception as e:
                self.add_log_entry(f"  ✗ Ping error: {e}", "orange")
        
        output_remote_ip = self.output_remote_ip.currentText().strip()
        if output_remote_ip:
            self.add_log_entry(f"Testing Output Remote IP (PLC): {output_remote_ip}", "blue")
            try:
                result = subprocess.run(['ping', '-n', '1', '-w', '1000', output_remote_ip], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    self.add_log_entry(f"  ✓ PLC reachable: {output_remote_ip}", "green")
                else:
                    self.add_log_entry(f"  ✗ PLC not reachable: {output_remote_ip}", "orange")
            except Exception as e:
                self.add_log_entry(f"  ✗ Ping error: {e}", "orange")
        
        self.add_log_entry("=== UDP Connection Test Complete ===", "blue")
        QMessageBox.information(self, "Test Complete", 
                               "UDP connection test complete. Check the Connection Log for results.")

    def disconnect_all(self):
        """Disconnect all connections and clear settings"""
        # Disconnect all ports
        self.app_state.disconnect_all_ports()
        
        # Clear main scanner settings (reset local IP to first option)
        if self.main_local_ip.count() > 0:
            self.main_local_ip.setCurrentIndex(0)  # Set to first option (usually 0.0.0.0)
        self.main_local_port.setCurrentText("5000")
        self.main_remote_ip.setCurrentIndex(0)  # Set to empty
        self.main_remote_ip.setEditText("")
        self.main_remote_port.setCurrentText("")
        
        # Clear on-demand scanner serial settings
        self.ondemand_com_port.setCurrentIndex(0)  # Set to empty
        self.ondemand_baud_rate.setCurrentText("115200")
        self.ondemand_data_bits.setCurrentText("8")
        self.ondemand_parity.setCurrentText("None")
        self.ondemand_stop_bits.setCurrentText("1")
        self.ondemand_timeout.setCurrentText("1")
        
        # Clear output settings (reset local IP to first option)
        if self.output_local_ip.count() > 0:
            self.output_local_ip.setCurrentIndex(0)  # Set to first option (usually 0.0.0.0)
        self.output_local_port.setCurrentText("0")
        self.output_remote_ip.setCurrentIndex(0)  # Set to empty
        self.output_remote_ip.setEditText("")
        self.output_remote_port.setCurrentText("")
        
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
        
        self.add_log_entry("All connections disconnected", "blue")
        QMessageBox.information(self, "Disconnected", 
                               "All connections have been closed.\n\n"
                               "Settings cleared and ready for reconfiguration.")

    def create_status_log(self, parent_layout):
        frame = QFrame()
        frame.setObjectName("panel")
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(10)
        
        title = QLabel("Connection Log")
        title.setObjectName("h2")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(180)  # Fixed height for consistent layout
        self.log_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
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
