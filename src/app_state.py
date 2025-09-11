# src/app_state.py
import serial
import threading
import re # Re-add the import for regular expressions
import json
import os
import sys
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal
from appdirs import user_data_dir
import serial.tools.list_ports
import winreg # Import winreg for Windows theme detection

from .ui.widgets import ApprovalDialog
import constants
from .logic.file_parser import parse_file
from .services.com_writer import ComPortWriter

APP_NAME = "CardSequenceValidator"
APP_AUTHOR = "YourCompany"

def get_cache_file_path():
    cache_dir = user_data_dir(APP_NAME, APP_AUTHOR)
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, "app_cache.json")

def get_windows_theme():
    """Detects the current Windows theme (light or dark) for apps."""
    # Theme detection using the registry is only supported on Windows 10 and newer.
    # For older systems (like Windows 7), default to 'light' theme.
    if sys.platform == 'win32' and sys.getwindowsversion().major < 10:
        return "light"
    
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        # AppsUseLightTheme: 0 for dark, 1 for light
        theme_value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return "light" if theme_value == 1 else "dark"
    except Exception:
        # Default to dark if detection fails for any other reason
        return "dark"

class ComPortReader:
    def __init__(self, port, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1, callback=None, error_callback=None):
        self.port, self.baudrate, self.bytesize = port, baudrate, bytesize
        self.parity, self.stopbits, self.timeout = parity, stopbits, timeout
        self.callback, self.error_callback = callback, error_callback
        self.running, self.thread, self.serial_instance = False, None, None
        self.paused = threading.Event()
        self.paused.set() # Initially not paused

    def start_reading(self):
        if self.running: return
        self.running = True
        self.thread = threading.Thread(target=self.read_loop)
        self.thread.daemon = True
        self.thread.start()

    def stop_reading(self):
        self.running = False
        self.resume() # Ensure thread is not blocked before joining
        if self.thread and self.thread.is_alive(): self.thread.join()
        if self.serial_instance and self.serial_instance.is_open: self.serial_instance.close()

    def pause(self):
        self.paused.clear()

    def resume(self):
        self.paused.set()

    def read_loop(self):
        try:
            self.serial_instance = serial.Serial(
                port=self.port, baudrate=self.baudrate, bytesize=self.bytesize,
                parity=self.parity, stopbits=self.stopbits, timeout=0.1
            )
            if self.error_callback: self.error_callback(f"Successfully connected to {self.port}", "green")

            while self.running:
                self.paused.wait() # This will block if pause() is called
                if not self.running: break # Exit if stopped while paused

                if self.serial_instance.in_waiting > 0:
                    raw_data = self.serial_instance.readline()
                    decoded_data = raw_data.decode(errors='ignore').strip()

                    # --- THIS IS THE FIX: Re-add the cleaning step ---
                    # Remove non-printable ASCII characters
                    decoded_data = re.sub(r'[^\x20-\x7E]', '', decoded_data)

                    if decoded_data and self.callback:
                        self.callback(decoded_data)
        except serial.SerialException as e:
            if self.error_callback: self.error_callback(f"Error connecting to {self.port}: {e}", "red")
        finally:
            self.running = False
            if self.error_callback: self.error_callback(f"Disconnected from {self.port}", "orange")

class AppState(QObject):
    log_updated = pyqtSignal(list)
    log_cleared = pyqtSignal()
    state_changed = pyqtSignal()
    com_status_changed = pyqtSignal(str, str)
    output_com_status_changed = pyqtSignal(str, str)
    com_data_received = pyqtSignal(str)
    theme_changed = pyqtSignal(str)
    start_card_scan_started = pyqtSignal(str)
    start_card_scan_complete = pyqtSignal(str, bool) # Message, success

    mismatch_found_in_sequence = pyqtSignal(str, int, int)
    card_count_update = pyqtSignal(str, str)  # type, message
    _single_scan_received = pyqtSignal(str)

    # --- MODIFIED: The mismatch_not_found signal is no longer needed ---
    # mismatch_not_found = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.selected_com_port = None
        self.start_card_scan_port = None
        self.com_port_reader = None
        self.is_scanning = False
        self.output_com_writer = ComPortWriter()
        self.selected_output_port = None
        self.output_formats = {}
        self.selected_output_format = ""
        self.scan_side = "left"  # Default to left side
        self.selected_file_path = ""
        self.expected_cards = []
        self.left_qr_to_index = {}
        self.right_qr_to_index = {}
        self.numcard_to_qrs = {}
        self.current_card_index = 0
        self.start_card_has_been_scanned = False
        self.first_scan_received = True
        self.log_data = []
        self.baud_rate, self.data_bits, self.parity, self.stop_bits, self.timeout = 115200, 8, 'N', 1, 1
        self.current_theme = None # Initialize to None, will be set by load_cache or get_windows_theme

        # Card counting state
        self.card_count_step = 0  # 0: idle, 1: waiting for first, 2: waiting for second
        self.first_card_index = -1

        self.load_output_formats()
        self.com_data_received.connect(self.handle_com_data)
        self._single_scan_received.connect(self.process_counted_card)
        self.load_cache() # Load cached theme first

        if self.current_theme is None: # If no theme was loaded from cache
            self.current_theme = get_windows_theme() # Set to system theme

        if self.selected_output_port:
            self.connect_output_port(self.selected_output_port)

        self.theme_changed.emit(self.current_theme) # Emit initial theme

    def load_cache(self):
        try:
            with open(get_cache_file_path(), 'r') as f:
                cache_data = json.load(f)
                self.selected_com_port = cache_data.get('selected_com_port')
                if self.selected_com_port:
                    available_ports = [port.device for port in serial.tools.list_ports.comports()]
                    if self.selected_com_port not in available_ports:
                        self.selected_com_port = None
                        self.com_status_changed.emit("Previously selected input COM port not found. Please select a new one.", "orange")
                self.selected_output_port = cache_data.get('selected_output_port')
                if self.selected_output_port:
                    available_ports = [port.device for port in serial.tools.list_ports.comports()]
                    if self.selected_output_port not in available_ports:
                        self.selected_output_port = None
                        self.output_com_status_changed.emit("Previously selected output COM port not found. Please select a new one.", "orange")
                self.start_card_scan_port = cache_data.get('start_card_scan_port')
                if self.start_card_scan_port:
                    available_ports = [port.device for port in serial.tools.list_ports.comports()]
                    if self.start_card_scan_port not in available_ports:
                        self.start_card_scan_port = None
                        # Optionally, emit a signal for the UI to know this port is gone
                        self.com_status_changed.emit("Previously selected start card scan port not found. Please select a new one.", "orange")
                self.baud_rate = cache_data.get('baud_rate', 115200)
                self.data_bits = cache_data.get('data_bits', 8)
                self.parity = cache_data.get('parity', 'N')
                self.stop_bits = cache_data.get('stop_bits', 1)
                self.timeout = cache_data.get('timeout', 1)
                self.selected_output_format = cache_data.get('selected_output_format', "")
                
                self.current_theme = cache_data.get('current_theme', "dark")
                selected_file_path = cache_data.get('selected_file_path', "")
                if selected_file_path:
                    self.load_file(selected_file_path)
                if 'log_data' in cache_data:
                    self.log_data = cache_data.get('log_data', [])
                self.log_updated.emit(self.log_data)
                self.state_changed.emit()
        except (FileNotFoundError, json.JSONDecodeError):
            # Cache file doesn't exist or is invalid, start with a clean state
            pass

    def save_cache(self):
        cache_data = {
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
            'log_data': self.log_data,
            'current_theme': self.current_theme
        }
        with open(get_cache_file_path(), 'w') as f:
            json.dump(cache_data, f, indent=4)

    def load_output_formats(self):
        try:
            with open(constants.OUTPUT_FORMATS_PATH, 'r') as f:
                self.output_formats = json.load(f)
            if self.output_formats:
                self.selected_output_format = list(self.output_formats.keys())[0]
        except FileNotFoundError:
            print(f"Warning: '{constants.OUTPUT_FORMATS_PATH}' not found. Output formats will be unavailable.")
            self.output_formats = {}
        except Exception as e:
            print(f"Error loading output_formats.json: {e}")
            self.output_formats = {}

    def start_scanning(self):
        if not self.selected_com_port:
            self.com_status_changed.emit("No COM port selected.", "red"); return
        if self.is_scanning: return

        self.com_port_reader = ComPortReader(
            port=self.selected_com_port, baudrate=self.baud_rate, bytesize=self.data_bits,
            parity=self.parity, stopbits=self.stop_bits, timeout=self.timeout,
            callback=self.com_data_received.emit, # Use the signal
            error_callback=lambda msg, color: self.com_status_changed.emit(msg, color)
        )
        self.is_scanning = True
        self.com_port_reader.start_reading()
        self.state_changed.emit()
        self.save_cache()

    def handle_com_data(self, scanned_code):
        log_entry = None
        scanned_side = self.scan_side.capitalize()

        if not self.expected_cards:
            log_entry = self.add_log_entry(scanned_code, "N/A", "NO FILE", scanned_side)
        elif self.current_card_index >= len(self.expected_cards):
            log_entry = self.add_log_entry(scanned_code, "End of Sequence", "EXTRA SCAN", scanned_side)
        else:
            # Determine which QR code to expect based on scan_side
            expected_qr = self.expected_cards[self.current_card_index][1 if self.scan_side == 'left' else 2]

            if scanned_code == expected_qr:
                status = "OK"
                log_entry = self.add_log_entry(scanned_code, expected_qr, status, scanned_side)
                self.send_output_signal(status)
                self.current_card_index += 1
            else:
                # Determine which lookup to use
                lookup_dict = self.left_qr_to_index if self.scan_side == 'left' else self.right_qr_to_index
                if scanned_code in lookup_dict:
                    future_match_index = lookup_dict[scanned_code]
                    if future_match_index > self.current_card_index:
                        num_skipped = future_match_index - self.current_card_index
                        # --- MODIFICATION: Pause scanning before showing dialog ---
                        self.pause_scanning()
                        self.mismatch_found_in_sequence.emit(scanned_code, num_skipped, future_match_index)
                    else:
                        # Scanned a card that was already scanned/skipped
                        status = "NOT OK"
                        log_entry = self.add_log_entry(scanned_code, expected_qr, status, scanned_side)
                        self.send_output_signal(status)
                else:
                    # Scanned card doesn't exist in the current scan side's list
                    status = "NOT OK"
                    log_entry = self.add_log_entry(scanned_code, expected_qr, status, scanned_side)
                    self.send_output_signal(status)
        
        if log_entry:
            self.log_updated.emit([log_entry])
        
        self.state_changed.emit()

    def connect_output_port(self, port):
        if self.output_com_writer.is_connected:
            self.output_com_writer.disconnect()

        # --- MODIFIED: Passes all settings to the writer's connect method ---
        success, message = self.output_com_writer.connect(
            port=port,
            baudrate=self.baud_rate,
            bytesize=self.data_bits,
            parity=self.parity,
            stopbits=self.stop_bits,
            timeout=self.timeout
        )
        if success:
            self.selected_output_port = port
            self.output_com_status_changed.emit(message, "green")
            self.save_cache()
        else:
            self.selected_output_port = None
            self.output_com_status_changed.emit(message, "red")
        self.state_changed.emit()

    def disconnect_output_port(self):
        self.output_com_writer.disconnect()
        self.selected_output_port = None
        self.output_com_status_changed.emit("Output port disconnected.", "orange")
        self.state_changed.emit()

    def disconnect_all_ports(self):
        self.stop_scanning()
        self.disconnect_output_port()
        self.selected_com_port = None
        self.start_card_scan_port = None # Also clear this port
        self.state_changed.emit()
        self.save_cache()

    def get_timestamp(self):
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]

    def add_log_entry(self, scanned_code, expected_code, status, scanned_side="N/A"):
        timestamp = self.get_timestamp()
        log_entry = {
            "timestamp": timestamp, "scanned_code": scanned_code,
            "expected_code": expected_code, "status": status,
            "scanned_side": scanned_side
        }
        self.log_data.append(log_entry)
        return log_entry

    def stop_scanning(self):
        if self.com_port_reader:
            self.com_port_reader.stop_reading()
        self.com_port_reader = None
        self.is_scanning = False
        self.state_changed.emit()
        self.save_cache()

    def pause_scanning(self):
        if self.com_port_reader:
            self.com_port_reader.pause()

    def resume_scanning(self):
        if self.com_port_reader:
            self.com_port_reader.resume()

    def load_file(self, file_path):
        try:
            self.expected_cards = parse_file(file_path)
            self.left_qr_to_index = {left_qr: i for i, (_, left_qr, _) in enumerate(self.expected_cards)}
            self.right_qr_to_index = {right_qr: i for i, (_, _, right_qr) in enumerate(self.expected_cards)}
            self.numcard_to_qrs = {numcard: (left_qr, right_qr) for numcard, left_qr, right_qr in self.expected_cards}
            self.selected_file_path = file_path
            self.current_card_index = 0
            self.start_card_has_been_scanned = False # Reset flag
            self.first_scan_received = True
            self.state_changed.emit()
            return True, f"Loaded {len(self.expected_cards)} cards."
        except Exception as e:
            self.selected_file_path = ""
            self.expected_cards = []
            self.left_qr_to_index = {}
            self.right_qr_to_index = {}
            self.numcard_to_qrs = {}
            self.state_changed.emit()
            return False, f"Error loading file: {e}"

    def clear_file(self):
        self.selected_file_path = ""
        self.expected_cards = []
        self.left_qr_to_index = {}
        self.right_qr_to_index = {}
        self.numcard_to_qrs = {}
        self.current_card_index = 0
        self.start_card_has_been_scanned = False # Reset flag
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

    def start_card_counting(self):
        if self.is_scanning:
            self.card_count_update.emit('error', "Cannot count cards while a scan is active.")
            return
        if not self.start_card_scan_port:
            self.card_count_update.emit('error', "Start card scan port not selected.")
            return
        if not self.expected_cards:
            self.card_count_update.emit('error', "No card file loaded.")
            return

        self.card_count_step = 1
        self.card_count_update.emit('prompt', "Scan the FIRST card...")
        self._get_single_scan_for_counting()

    def cancel_card_counting(self):
        self.card_count_step = 0
        self.first_card_index = -1
        self.card_count_update.emit('result', "Card counting cancelled.")

    def _get_single_scan_for_counting(self):
        thread = threading.Thread(target=self._scan_for_card_count_worker)
        thread.daemon = True
        thread.start()

    def _scan_for_card_count_worker(self):
        try:
            ser = serial.Serial(
                port=self.start_card_scan_port,
                baudrate=self.baud_rate,
                bytesize=self.data_bits,
                parity=self.parity,
                stopbits=self.stop_bits,
                timeout=10  # 10-second timeout
            )
        except serial.SerialException as e:
            self.card_count_update.emit('error', f"Error opening port: {e}")
            self.card_count_step = 0
            return

        try:
            self.card_count_update.emit('info', "Waiting for card scan...")
            raw_data = ser.readline()
            if not raw_data:
                self.card_count_update.emit('error', "No card scanned (timeout).")
                self.card_count_step = 0
                return

            scanned_code = raw_data.decode(errors='ignore').strip()
            scanned_code = re.sub(r'[^\x20-\x7E]', '', scanned_code)

            if scanned_code:
                self._single_scan_received.emit(scanned_code)
            else:
                self.card_count_update.emit('error', "No data received from scan.")
                self.card_count_step = 0

        except Exception as e:
            self.card_count_update.emit('error', f"An error occurred during scan: {e}")
            self.card_count_step = 0
        finally:
            if ser.is_open:
                ser.close()

    def process_counted_card(self, scanned_code):
        # Try to find the card in either left or right QR code lists
        scanned_index = -1
        if scanned_code in self.left_qr_to_index:
            scanned_index = self.left_qr_to_index[scanned_code]
        elif scanned_code in self.right_qr_to_index:
            scanned_index = self.right_qr_to_index[scanned_code]

        if scanned_index == -1:
            self.card_count_update.emit('error', f"Scanned card {scanned_code} not found in the file.")
            self.card_count_step = 0
            return

        if self.card_count_step == 1: # This was the first card
            self.first_card_index = scanned_index
            self.card_count_step = 2
            card_num = self.expected_cards[scanned_index][0]
            self.card_count_update.emit('prompt', f"First card: {card_num}.\nScan the LAST card...")
            self._get_single_scan_for_counting()

        elif self.card_count_step == 2: # This was the second card
            last_card_index = scanned_index

            if last_card_index < self.first_card_index:
                self.card_count_update.emit('error', "Last card cannot come before the first card.")
            else:
                count = last_card_index - self.first_card_index + 1
                first_card_num = self.expected_cards[self.first_card_index][0]
                last_card_num = self.expected_cards[last_card_index][0]
                self.card_count_update.emit('result', f"Found {count} cards between \n{first_card_num} and {last_card_num} (inclusive).")
            
            # Reset state regardless of outcome
            self.card_count_step = 0
            self.first_card_index = -1

    def scan_and_set_start_card(self):
        if not self.start_card_scan_port:
            self.start_card_scan_complete.emit("Start card scan port not selected.", False)
            return
        if self.is_scanning:
            self.start_card_scan_complete.emit("Cannot scan for start card while main scan is active.", False)
            return

        self.start_card_scan_started.emit("Waiting for start card scan...")
        thread = threading.Thread(target=self._scan_for_start_card_worker)
        thread.daemon = True
        thread.start()

    def _scan_for_start_card_worker(self):
        try:
            ser = serial.Serial(
                port=self.start_card_scan_port,
                baudrate=self.baud_rate,
                bytesize=self.data_bits,
                parity=self.parity,
                stopbits=self.stop_bits,
                timeout=5 # 5-second timeout to wait for a card
            )
        except serial.SerialException as e:
            self.start_card_scan_complete.emit(f"Error opening port {self.start_card_scan_port}: {e}", False)
            return

        try:
            raw_data = ser.readline()
            if not raw_data:
                self.start_card_scan_complete.emit("No card scanned (timeout).", False)
                return

            scanned_code = raw_data.decode(errors='ignore').strip()
            scanned_code = re.sub(r'[^\x20-\x7E]', '', scanned_code) # Clean the input

            if not scanned_code:
                self.start_card_scan_complete.emit("No data received from scan.", False)
                return

            # Automatically determine the scan side
            if scanned_code in self.left_qr_to_index:
                self.scan_side = "left"
                found_index = self.left_qr_to_index[scanned_code]
                self.set_start_index(found_index)
                self.start_card_has_been_scanned = True
                card_num = self.expected_cards[found_index][0]
                self.start_card_scan_complete.emit(f"Start card set to {card_num} ({scanned_code}). Scan side set to Left.", True)
            elif scanned_code in self.right_qr_to_index:
                self.scan_side = "right"
                found_index = self.right_qr_to_index[scanned_code]
                self.set_start_index(found_index)
                self.start_card_has_been_scanned = True
                card_num = self.expected_cards[found_index][0]
                self.start_card_scan_complete.emit(f"Start card set to {card_num} ({scanned_code}). Scan side set to Right.", True)
            else:
                self.start_card_scan_complete.emit(f"Scanned card {scanned_code} not found in the loaded file.", False)

        except Exception as e:
            self.start_card_scan_complete.emit(f"An error occurred during scan: {e}", False)
        finally:
            if ser.is_open:
                ser.close()

    def send_output_signal(self, status):
        if not self.output_com_writer.is_connected:
            return

        format_map = self.output_formats.get(self.selected_output_format, {})
        output_signal = format_map.get(status, None)

        if output_signal:
            self.output_com_writer.send(output_signal)

    def resolve_mismatch(self, scanned_code, approved, future_index=-1):
        thread = threading.Thread(
            target=self._perform_mismatch_resolution,
            args=(scanned_code, approved, future_index)
        )
        thread.daemon = True
        thread.start()

    def _perform_mismatch_resolution(self, scanned_code, approved, future_index):
        # Determine the expected QR based on the current scan side
        expected_qr = self.expected_cards[self.current_card_index][1 if self.scan_side == 'left' else 2]
        scanned_side = self.scan_side.capitalize()
        log_entries_to_add = []

        if approved and future_index != -1:
            # Log all the cards that were skipped
            for i in range(self.current_card_index, future_index):
                skipped_num, skipped_left, skipped_right = self.expected_cards[i]
                skipped_qr = skipped_left if self.scan_side == 'left' else skipped_right
                log_entries_to_add.append(self.add_log_entry("MISSING", skipped_qr, "SKIPPED", scanned_side))

            # Log the card that was actually scanned
            status = "OK (JUMPED)"
            expected_jumped_qr = self.expected_cards[future_index][1 if self.scan_side == 'left' else 2]
            log_entries_to_add.append(self.add_log_entry(scanned_code, expected_jumped_qr, status, scanned_side))
            
            self.send_output_signal(status)
            self.current_card_index = future_index + 1
            self.resume_scanning() # Resume scanning after successful jump
        else: # This block now runs if the user clicks "No"
            status = "NOT OK"
            log_entries_to_add.append(self.add_log_entry(scanned_code, expected_qr, status, scanned_side))
            self.send_output_signal(status)
            self.stop_scanning() # Stop scanning as requested by the user

        self.log_data.extend(log_entries_to_add)
        self.log_updated.emit(log_entries_to_add)
        self.state_changed.emit()