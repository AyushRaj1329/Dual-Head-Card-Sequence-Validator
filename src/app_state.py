# src/app_state.py
import serial
import threading
import re
import json
import os
import sys
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox
from appdirs import user_data_dir
import serial.tools.list_ports
import winreg

from .ui.widgets import ApprovalDialog
import constants
from .logic.file_parser import parse_file
from .services.com_writer import ComPortWriter
from .card_types import CardType

APP_NAME = "CardSequenceValidator"
APP_AUTHOR = "YourCompany"

def get_cache_file_path():
    cache_dir = user_data_dir(APP_NAME, APP_AUTHOR)
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, "app_cache.json")

def get_windows_theme():
    if sys.platform == 'win32' and sys.getwindowsversion().major < 10:
        return "light"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        theme_value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return "light" if theme_value == 1 else "dark"
    except Exception:
        return "dark"

class ComPortReader:
    def __init__(self, port, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=0.1, callback=None, error_callback=None):
        self.port, self.baudrate, self.bytesize = port, baudrate, bytesize
        self.parity, self.stopbits, self.timeout = parity, stopbits, timeout
        self.callback, self.error_callback = callback, error_callback
        self.running, self.thread, self.serial_instance = False, None, None
        self.paused = threading.Event()
        self.paused.set()

    def start_reading(self):
        if self.running: return
        self.running = True
        self.thread = threading.Thread(target=self.read_loop)
        self.thread.daemon = True
        self.thread.start()

    def stop_reading(self):
        self.running = False
        self.resume()
        if self.thread and self.thread.is_alive():
            self.thread.join()
        if self.serial_instance and self.serial_instance.is_open:
            self.serial_instance.close()

    def pause(self):
        self.paused.clear()

    def resume(self):
        if self.serial_instance:
            self.serial_instance.reset_input_buffer()
        self.paused.set()

    def read_loop(self):
        try:
            self.serial_instance = serial.Serial(
                port=self.port, baudrate=self.baudrate, bytesize=self.bytesize,
                parity=self.parity, stopbits=self.stopbits, timeout=self.timeout,
                inter_byte_timeout=0.05
            )
            if self.error_callback:
                self.error_callback(f"Connected to {self.port}", "green")

            while self.running:
                self.paused.wait()
                if not self.running: break

                if self.serial_instance.in_waiting > 0:
                    raw_data = self.serial_instance.read(256)
                    decoded_data = raw_data.decode(errors='ignore').strip()
                    decoded_data = re.sub(r'[^\x20-\x7E]', '', decoded_data)
                    if decoded_data and self.callback:
                        self.callback(decoded_data)
        except serial.SerialException as e:
            if self.error_callback:
                self.error_callback(f"Error connecting to {self.port}: {e}", "red")
        finally:
            self.running = False
            if self.error_callback and self.port:
                self.error_callback("Not Connected", "red")

class AppState(QObject):
    log_updated = pyqtSignal(list)
    log_cleared = pyqtSignal()
    state_changed = pyqtSignal()
    com_status_changed = pyqtSignal(str, str)
    output_com_status_changed = pyqtSignal(str, str)
    ondemand_scan_status_update = pyqtSignal(str, str)
    theme_changed = pyqtSignal(str)
    start_card_scan_complete = pyqtSignal(str, bool)
    card_type_changed = pyqtSignal(object)  # Emits CardType enum

    mismatch_found_in_sequence = pyqtSignal(str, int, int)
    card_count_update = pyqtSignal(str, str)

    def __init__(self, card_type=CardType.HALF):
        super().__init__()
        self.card_type = card_type
        self.main_port_reader = None
        self.ondemand_port_reader = None
        self.output_com_writer = ComPortWriter()

        self.selected_com_port = None
        self.selected_output_port = None
        self.start_card_scan_port = None
        
        self.is_scanning = False
        self.output_formats = {}
        self.selected_output_format = ""
        self.scan_side = CardType.get_default_scan_side(card_type)
        self.selected_file_path = ""
        self.expected_cards = []
        
        # Dynamic QR code lookup dictionaries based on card type
        self.qr_to_index = {}  # Generic lookup: qr_code -> (index, position)
        self.numcard_to_qrs = {}
        
        self.current_card_index = 0
        self.scan_direction = "top_to_bottom"  # "top_to_bottom" or "bottom_to_top"
        self.start_card_has_been_scanned = False
        self.first_scan_received = True
        self.log_data = []
        self.start_card_code = None
        self.baud_rate, self.data_bits, self.parity, self.stop_bits, self.timeout = 115200, 8, 'N', 1, 1
        self.current_theme = None

        # On-demand scanning state machine
        self.is_waiting_for_start_card = False
        self.is_waiting_for_count_card_1 = False
        self.is_waiting_for_count_card_2 = False
        self.first_card_index = -1

        self.load_output_formats()
        self.load_cache()

        if self.current_theme is None:
            self.current_theme = get_windows_theme()
        
        # Connect to ports from cache, but do not start scanning automatically
        available_ports = [port.device for port in serial.tools.list_ports.comports()]

        if self.selected_com_port and self.selected_com_port not in available_ports:
            self.selected_com_port = None
        if self.start_card_scan_port and self.start_card_scan_port not in available_ports:
            self.start_card_scan_port = None
        if self.selected_output_port and self.selected_output_port not in available_ports:
            self.selected_output_port = None

        if self.start_card_scan_port:
            self.connect_start_card_port(self.start_card_scan_port)
        if self.selected_output_port:
            self.connect_output_port(self.selected_output_port)

        # Emit state_changed after all initial port validations and connections
        self.state_changed.emit()

        self.theme_changed.emit(self.current_theme)

    def load_cache(self):
        try:
            with open(get_cache_file_path(), 'r') as f:
                cache = json.load(f)
                self.selected_com_port = cache.get('selected_com_port')
                self.selected_output_port = cache.get('selected_output_port')
                self.start_card_scan_port = cache.get('start_card_scan_port')
                self.baud_rate = cache.get('baud_rate', 115200)
                self.data_bits = cache.get('data_bits', 8)
                self.parity = cache.get('parity', 'N')
                self.stop_bits = cache.get('stop_bits', 1)
                self.timeout = cache.get('timeout', 1)
                self.selected_output_format = cache.get('selected_output_format', "")
                self.current_theme = cache.get('current_theme', "dark")
                self.start_card_code = cache.get('start_card_code')
                self.scan_direction = cache.get('scan_direction', 'top_to_bottom')
                
                # Load card type from cache (but don't override constructor parameter)
                cached_card_type = cache.get('card_type')
                if cached_card_type and not hasattr(self, '_card_type_set_by_user'):
                    self.card_type = CardType.from_string(cached_card_type)
                
                selected_file_path = cache.get('selected_file_path')
                if selected_file_path:
                    # Don't auto-load files anymore - require manual selection with card type
                    # Just store the path for reference
                    self.selected_file_path = selected_file_path
                
                self.log_data = cache.get('log_data', [])
                self.log_updated.emit(self.log_data)
                self.state_changed.emit()
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def save_cache(self):
        cache_data = {
            'card_type': self.card_type.value,
            'selected_com_port': self.selected_com_port,
            'start_card_scan_port': self.start_card_scan_port,
            'selected_output_port': self.selected_output_port,
            'baud_rate': self.baud_rate,
            'data_bits': self.data_bits,
            'parity': self.parity,
            'stop_bits': self.stop_bits,
            'timeout': self.timeout,
            'selected_output_format': self.selected_output_format,
            'selected_file_path': self.selected_file_path,
            'start_card_code': self.start_card_code,
            'scan_direction': self.scan_direction,
            'log_data': self.log_data,
            'current_theme': self.current_theme
        }
        with open(get_cache_file_path(), 'w') as f:
            json.dump(cache_data, f, indent=4)

    def load_output_formats(self):
        try:
            with open(constants.OUTPUT_FORMATS_PATH, 'r') as f:
                self.output_formats = json.load(f)
            if self.output_formats and not self.selected_output_format:
                self.selected_output_format = list(self.output_formats.keys())[0]
        except (FileNotFoundError, json.JSONDecodeError):
            self.output_formats = {}

    def start_scanning(self):
        if not self.selected_com_port or self.is_scanning: return
        self.main_port_reader = ComPortReader(
            port=self.selected_com_port, baudrate=self.baud_rate, bytesize=self.data_bits,
            parity=self.parity, stopbits=self.stop_bits, timeout=self.timeout,
            callback=self.handle_main_scan,
            error_callback=lambda msg, color: self.com_status_changed.emit(msg, color)
        )
        self.is_scanning = True
        self.main_port_reader.start_reading()
        self.com_status_changed.emit(self.selected_com_port, "green")
        
        # Set start card on first scan if not already set
        if not self.start_card_has_been_scanned:
            self.first_scan_received = True
        
        self.state_changed.emit()

    def stop_scanning(self):
        if self.main_port_reader:
            self.main_port_reader.stop_reading()
            self.com_status_changed.emit("Not Set", "red")
        self.main_port_reader = None
        self.is_scanning = False
        self.state_changed.emit()

    def handle_main_scan(self, scanned_code):
        log_entry = None
        
        # Get scan side label for logging
        scan_side_labels = {
            "single": "Single",
            "left": "Left",
            "right": "Right",
            "top_left": "Top-Left",
            "top_right": "Top-Right",
            "bottom_left": "Bottom-Left",
            "bottom_right": "Bottom-Right"
        }
        scanned_side = scan_side_labels.get(self.scan_side, self.scan_side.replace('_', ' ').title())

        # Set start card on first scan
        if self.first_scan_received and not self.start_card_has_been_scanned:
            if scanned_code in self.qr_to_index:
                found_index, position = self.qr_to_index[scanned_code]
                
                # Set scan side based on position and card type
                if self.card_type == CardType.SINGLE:
                    self.scan_side = "single"
                elif self.card_type == CardType.HALF:
                    self.scan_side = "left" if position == 0 else "right"
                elif self.card_type == CardType.QUARTER:
                    scan_sides = ["top_left", "top_right", "bottom_left", "bottom_right"]
                    self.scan_side = scan_sides[position] if position < len(scan_sides) else "top_left"
                
                self.set_start_index(found_index)
                self.start_card_has_been_scanned = True
                self.start_card_code = scanned_code
                self.first_scan_received = False
                scanned_side = scan_side_labels.get(self.scan_side, self.scan_side.replace('_', ' ').title())
            else:
                # Card not found in sequence, log as error
                log_entry = self.add_log_entry(scanned_code, "N/A", "NOT IN SEQUENCE", scanned_side)
                if log_entry:
                    self.log_updated.emit([log_entry])
                self.state_changed.emit()
                return

        if not self.expected_cards:
            log_entry = self.add_log_entry(scanned_code, "N/A", "NO FILE", scanned_side)
        elif self.is_scan_complete():
            log_entry = self.add_log_entry(scanned_code, "End of Sequence", "EXTRA SCAN", scanned_side)
        else:
            # Get the actual card index based on scan direction
            actual_card_index = self.get_current_expected_card_index()
            
            # Get expected QR based on scan side and card type
            if self.card_type == CardType.SINGLE:
                expected_qr = self.expected_cards[actual_card_index][1]  # Position 1 (after numcard)
            elif self.card_type == CardType.HALF:
                qr_position = 1 if self.scan_side == 'left' else 2
                expected_qr = self.expected_cards[actual_card_index][qr_position]
            elif self.card_type == CardType.QUARTER:
                position_map = {"top_left": 1, "top_right": 2, "bottom_left": 3, "bottom_right": 4}
                qr_position = position_map.get(self.scan_side, 1)
                expected_qr = self.expected_cards[actual_card_index][qr_position]
            
            if scanned_code == expected_qr:
                status = "OK"
                log_entry = self.add_log_entry(scanned_code, expected_qr, status, scanned_side)
                self.send_output_signal(status)
                self.increment_card_index()
            else:
                # Check if scanned code exists elsewhere in sequence
                if scanned_code in self.qr_to_index:
                    future_match_index, _ = self.qr_to_index[scanned_code]
                    
                    # Compare actual array indices for both directions
                    if self.scan_direction == "bottom_to_top":
                        # For bottom-to-top, check if future card comes BEFORE current in array
                        if future_match_index < actual_card_index:
                            # Calculate number of cards to skip (in scan order)
                            num_skipped = actual_card_index - future_match_index
                            # Convert future_match_index to scan position for UI
                            future_scan_position = len(self.expected_cards) - 1 - future_match_index
                            self.pause_scanning()
                            self.mismatch_found_in_sequence.emit(scanned_code, num_skipped, future_scan_position)
                        else:
                            status = "NOT OK"
                            log_entry = self.add_log_entry(scanned_code, expected_qr, status, scanned_side)
                            self.send_output_signal(status)
                    else:
                        # Top-to-bottom logic: check if future card comes AFTER current
                        if future_match_index > actual_card_index:
                            num_skipped = future_match_index - actual_card_index
                            self.pause_scanning()
                            self.mismatch_found_in_sequence.emit(scanned_code, num_skipped, future_match_index)
                        else:
                            status = "NOT OK"
                            log_entry = self.add_log_entry(scanned_code, expected_qr, status, scanned_side)
                            self.send_output_signal(status)
                else:
                    status = "NOT OK"
                    log_entry = self.add_log_entry(scanned_code, expected_qr, status, scanned_side)
                    self.send_output_signal(status)
        
        if log_entry:
            self.log_updated.emit([log_entry])
        self.state_changed.emit()

    def connect_start_card_port(self, port):
        if self.ondemand_port_reader:
            self.ondemand_port_reader.stop_reading()
        
        if not port:
            self.start_card_scan_port = None
            self.ondemand_port_reader = None
            self.ondemand_scan_status_update.emit("Not Connected", "red")
            return

        self.ondemand_port_reader = ComPortReader(
            port=port, baudrate=self.baud_rate, bytesize=self.data_bits,
            parity=self.parity, stopbits=self.stop_bits,
            callback=self.handle_ondemand_scan,
            error_callback=lambda msg, color: self.ondemand_scan_status_update.emit(msg, color)
        )
        self.start_card_scan_port = port
        self.ondemand_port_reader.start_reading()
        self.ondemand_scan_status_update.emit(self.start_card_scan_port, "green")
        self.state_changed.emit()

    def connect_output_port(self, port):
        if self.output_com_writer.is_connected:
            self.output_com_writer.disconnect()
        
        # Handle empty or None port
        if not port:
            self.selected_output_port = None
            self.output_com_status_changed.emit("Not Connected", "red")
            self.state_changed.emit()
            self.save_cache()
            return
        
        success, message = self.output_com_writer.connect(
            port=port, baudrate=self.baud_rate, bytesize=self.data_bits,
            parity=self.parity, stopbits=self.stop_bits, timeout=self.timeout
        )
        if success:
            self.selected_output_port = port
            self.output_com_status_changed.emit(port, "green")
        else:
            self.selected_output_port = None
            self.output_com_status_changed.emit(message, "red")
        self.state_changed.emit()
        self.save_cache()

    def disconnect_all_ports(self):
        self.stop_scanning()
        if self.ondemand_port_reader:
            self.ondemand_port_reader.stop_reading()
            self.ondemand_port_reader = None
            self.ondemand_scan_status_update.emit("Not Connected", "red")
        if self.output_com_writer.is_connected:
            self.output_com_writer.disconnect()
            self.output_com_status_changed.emit("Not Connected", "red")
        
        self.selected_com_port = None
        self.start_card_scan_port = None
        self.selected_output_port = None
        self.state_changed.emit()
        self.save_cache()

    def get_timestamp(self):
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]

    def add_log_entry(self, scanned_code, expected_code, status, scanned_side="N/A"):
        log_entry = {"timestamp": self.get_timestamp(), "scanned_code": scanned_code, "expected_code": expected_code, "status": status, "scanned_side": scanned_side}
        self.log_data.append(log_entry)
        return log_entry

    def pause_scanning(self):
        if self.main_port_reader:
            self.main_port_reader.pause()

    def resume_scanning(self):
        if self.main_port_reader:
            self.main_port_reader.resume()

    def load_file(self, file_path, card_type=None):
        """Load file with manually specified card type (no auto-detection)"""
        if card_type is None:
            return False, "Card type must be selected manually. Please choose Single, Half, or Quarter card type."
        
        try:
            # Parse file with specified card type
            self.expected_cards, _ = parse_file(file_path, card_type)
            
            # Update card type
            old_card_type = self.card_type
            self.card_type = card_type
            
            # Reset scan side to default for new card type
            self.scan_side = CardType.get_default_scan_side(self.card_type)
            
            # Emit signal if card type changed
            if old_card_type != self.card_type:
                self.card_type_changed.emit(self.card_type)
            
            # Build QR lookup dictionaries based on card type
            self.qr_to_index = {}
            self.numcard_to_qrs = {}
            
            for i, card in enumerate(self.expected_cards):
                numcard = card[0]
                qr_codes = card[1:]  # All QR codes after numcard
                
                # Map each QR code to its index and position
                for pos, qr_code in enumerate(qr_codes):
                    self.qr_to_index[qr_code] = (i, pos)
                
                # Map numcard to all its QR codes
                self.numcard_to_qrs[numcard] = qr_codes
            
            self.selected_file_path = file_path
            self.current_card_index = 0
            self.start_card_has_been_scanned = False
            self.first_scan_received = True

            if self.start_card_code:
                is_valid = self.start_card_code in self.qr_to_index
                if is_valid:
                    found_index, _ = self.qr_to_index[self.start_card_code]
                    self.set_start_index(found_index)
                    self.start_card_has_been_scanned = True
                else:
                    self.start_card_code = None
            
            self.state_changed.emit()
            
            # Get card type name for user feedback
            card_type_names = {
                CardType.SINGLE: "Single Card",
                CardType.HALF: "Half Card",
                CardType.QUARTER: "Quarter Card"
            }
            card_type_name = card_type_names.get(self.card_type, "Unknown")
            
            return True, f"Loaded {len(self.expected_cards)} cards as {card_type_name} type."
        except Exception as e:
            self.selected_file_path = ""
            self.expected_cards = []
            self.qr_to_index = {}
            self.numcard_to_qrs = {}
            self.state_changed.emit()
            return False, f"Error loading file: {e}"

    def clear_file(self):
        self.selected_file_path = ""
        self.expected_cards = []
        self.qr_to_index = {}
        self.numcard_to_qrs = {}
        self.current_card_index = 0
        self.start_card_code = None
        self.start_card_has_been_scanned = False
        self.first_scan_received = True
        self.state_changed.emit()
        self.save_cache()

    def set_start_index(self, index):
        if 0 <= index < len(self.expected_cards):
            self.current_card_index = index
            self.first_scan_received = True
            self.state_changed.emit()

    def clear_logs(self):
        self.log_data = []
        self.log_cleared.emit()
        self.state_changed.emit()
        self.save_cache()

    def set_theme(self, theme_name):
        self.current_theme = theme_name
        self.save_cache()
        self.theme_changed.emit(theme_name)

    def scan_and_get_card_details(self):
        if not self.ondemand_port_reader:
            QMessageBox.warning(None, "Configuration Error", "The 'On-Demand Scanner Port' must be configured in COM Port Setup before this action can be performed.")
            return
        if not self.expected_cards:
            QMessageBox.warning(None, "File Error", "A sequence file must be loaded before scanning card details.")
            return
        self.is_waiting_for_start_card = True
        self.ondemand_scan_status_update.emit("active", "Scan a card to view its details...")

    def start_card_counting(self):
        if not self.ondemand_port_reader:
            QMessageBox.warning(None, "Configuration Error", "The 'On-Demand Scanner Port' must be configured in COM Port Setup before this action can be performed.")
            return
        if not self.expected_cards:
            QMessageBox.warning(None, "File Error", "A sequence file must be loaded before counting cards.")
            return
        
        self.is_waiting_for_count_card_1 = True
        self.card_count_update.emit('clear', '')
        self.ondemand_scan_status_update.emit("active", "Scan the FIRST card...")

    def _reset_ondemand_scan_state(self):
        self.is_waiting_for_start_card = False
        self.is_waiting_for_count_card_1 = False
        self.is_waiting_for_count_card_2 = False
        self.first_card_index = -1
        self.card_count_update.emit('clear', '')
        self.ondemand_scan_status_update.emit("", "Scan cancelled. Click a button to start.")

    def cancel_card_details_scan(self):
        self.is_waiting_for_start_card = False
        self._reset_ondemand_scan_state()

    def cancel_count_card_range_scan(self):
        self.is_waiting_for_count_card_1 = False
        self.is_waiting_for_count_card_2 = False
        self.first_card_index = -1
        self._reset_ondemand_scan_state()

    def handle_ondemand_scan(self, scanned_code):
        if self.is_waiting_for_start_card:
            self.process_start_card_scan(scanned_code)
        elif self.is_waiting_for_count_card_1:
            self.process_count_card_1(scanned_code)
        elif self.is_waiting_for_count_card_2:
            self.process_count_card_2(scanned_code)

    def process_start_card_scan(self, scanned_code):
        self.is_waiting_for_start_card = False
        if scanned_code in self.qr_to_index:
            found_index, _ = self.qr_to_index[scanned_code]
            card = self.expected_cards[found_index]
            card_num = card[0]
            qr_codes = card[1:]  # All QR codes after numcard
            
            # Build details string based on card type
            qr_labels = CardType.get_qr_labels(self.card_type)
            details = f"Card Number: {card_num}\n"
            
            for i, (label, qr_code) in enumerate(zip(qr_labels, qr_codes)):
                details += f"{label}: {qr_code}\n"
            
            details += f"Position: {found_index + 1} of {len(self.expected_cards)}"
            self.start_card_scan_complete.emit(details, True)
        else:
            self.start_card_scan_complete.emit(f"Scanned card {scanned_code} not found in file.", False)
            self.ondemand_scan_status_update.emit("", "Scan complete.")
        self.state_changed.emit()

    def process_count_card_1(self, scanned_code):
        self.is_waiting_for_count_card_1 = False
        scanned_index = -1
        
        if scanned_code in self.qr_to_index:
            scanned_index, _ = self.qr_to_index[scanned_code]

        if scanned_index == -1:
            self.card_count_update.emit('error', f"First card '{scanned_code}' not found.")
            self.ondemand_scan_status_update.emit("", "Error. Try again.")
        else:
            self.first_card_index = scanned_index
            self.card_count_update.emit('first_card', scanned_code)
            self.is_waiting_for_count_card_2 = True
            self.ondemand_scan_status_update.emit("active", "Scan the LAST card...")

    def process_count_card_2(self, scanned_code):
        self.is_waiting_for_count_card_2 = False
        scanned_index = -1
        
        if scanned_code in self.qr_to_index:
            scanned_index, _ = self.qr_to_index[scanned_code]

        if scanned_index == -1:
            self.card_count_update.emit('error', f"Last card '{scanned_code}' not found.")
            # self.ondemand_scan_status_update.emit("", "Error. Try again.")
        elif scanned_index < self.first_card_index:
            self.card_count_update.emit('error', "Last card cannot come before first card.")
            self.ondemand_scan_status_update.emit("", "Error. Try again.")
        else:
            self.card_count_update.emit('last_card', scanned_code)
            count = scanned_index - self.first_card_index + 1
            self.card_count_update.emit('total', str(count))
            # self.ondemand_scan_status_update.emit("", f"Successfully counted {count} cards.")
        
        self.first_card_index = -1

    def get_current_expected_card_index(self):
        """Get the current card index based on scan direction"""
        if self.scan_direction == "bottom_to_top":
            # For bottom-to-top, start from the end and work backwards
            return len(self.expected_cards) - 1 - self.current_card_index
        else:
            # For top-to-bottom, use normal indexing
            return self.current_card_index
    
    def increment_card_index(self):
        """Increment card index (same for both directions)"""
        self.current_card_index += 1
    
    def is_scan_complete(self):
        """Check if scanning is complete"""
        return self.current_card_index >= len(self.expected_cards)
    
    def get_scan_direction_description(self):
        """Get user-friendly description of current scan direction"""
        if self.scan_direction == "bottom_to_top":
            return "Bottom → Top (Last card first)"
        else:
            return "Top → Bottom (First card first)"

    def send_output_signal(self, status):
        if not self.output_com_writer.is_connected: return
        output_signal = self.output_formats.get(self.selected_output_format, {}).get(status)
        if output_signal:
            self.output_com_writer.send(output_signal)

    def resolve_mismatch(self, scanned_code, approved, future_index):
        thread = threading.Thread(target=self._perform_mismatch_resolution, args=(scanned_code, approved, future_index))
        thread.daemon = True
        thread.start()

    def _perform_mismatch_resolution(self, scanned_code, approved, future_index):
        # Get the actual card index based on scan direction
        actual_card_index = self.get_current_expected_card_index()
        
        # Get expected QR based on card type and scan side
        if self.card_type == CardType.SINGLE:
            qr_position = 1
        elif self.card_type == CardType.HALF:
            qr_position = 1 if self.scan_side == 'left' else 2
        elif self.card_type == CardType.QUARTER:
            position_map = {"top_left": 1, "top_right": 2, "bottom_left": 3, "bottom_right": 4}
            qr_position = position_map.get(self.scan_side, 1)
        
        expected_qr = self.expected_cards[actual_card_index][qr_position]
        
        # Get scan side label
        scan_side_labels = {
            "single": "Single",
            "left": "Left",
            "right": "Right",
            "top_left": "Top-Left",
            "top_right": "Top-Right",
            "bottom_left": "Bottom-Left",
            "bottom_right": "Bottom-Right"
        }
        scanned_side = scan_side_labels.get(self.scan_side, self.scan_side.replace('_', ' ').title())
        log_entries = []

        if approved and future_index != -1:
            # Handle skipping based on scan direction
            if self.scan_direction == "bottom_to_top":
                # For bottom-to-top: future_index is scan position, convert to array index
                actual_future_index = len(self.expected_cards) - 1 - future_index
                
                # Skip cards from current array position down to future array position
                # Range should go from actual_card_index down to actual_future_index (exclusive)
                if actual_card_index > actual_future_index:
                    for i in range(actual_card_index - 1, actual_future_index - 1, -1):
                        if i >= 0:  # Bounds check
                            skipped_qr = self.expected_cards[i][qr_position]
                            log_entries.append(self.add_log_entry("MISSING", skipped_qr, "SKIPPED", scanned_side))
                
                expected_jumped_qr = self.expected_cards[actual_future_index][qr_position]
                log_entries.append(self.add_log_entry(scanned_code, expected_jumped_qr, "OK (JUMPED)", scanned_side))
                self.send_output_signal("OK (JUMPED)")
                # Set current_card_index to scan position after the jumped card
                self.current_card_index = future_index + 1
            else:
                # Top-to-bottom: future_index is already array index
                # Skip cards from current array position up to future array position
                for i in range(actual_card_index, future_index):
                    skipped_qr = self.expected_cards[i][qr_position]
                    log_entries.append(self.add_log_entry("MISSING", skipped_qr, "SKIPPED", scanned_side))
                
                expected_jumped_qr = self.expected_cards[future_index][qr_position]
                log_entries.append(self.add_log_entry(scanned_code, expected_jumped_qr, "OK (JUMPED)", scanned_side))
                self.send_output_signal("OK (JUMPED)")
                # Set current_card_index to scan position after the jumped card
                self.current_card_index = future_index + 1
        else:
            log_entries.append(self.add_log_entry(scanned_code, expected_qr, "NOT OK", scanned_side))
            self.send_output_signal("NOT OK")
        
        self.log_data.extend(log_entries)
        self.log_updated.emit(log_entries)
        self.resume_scanning()
        self.state_changed.emit()