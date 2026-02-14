# src/app_state.py
import serial
import serial.tools.list_ports
import threading
import re
import json
import os
import sys
import time
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox
from appdirs import user_data_dir
import winreg

from .ui.widgets import ApprovalDialog
import constants
from .logic.file_parser import parse_file
from .services.udp_reader import UDPReader
from .services.udp_writer import UDPWriter
from .card_types import CardType

APP_NAME = "CardSequenceValidator"
APP_AUTHOR = "YourCompany"

# Global instance tracker
_current_instance = 1

def set_current_instance(instance_num):
    """Set the current instance (1 or 2)"""
    global _current_instance
    if instance_num in (1, 2):
        _current_instance = instance_num

def get_current_instance():
    """Get the current instance number"""
    return _current_instance

def get_cache_file_path():
    cache_dir = user_data_dir(APP_NAME, APP_AUTHOR)
    try:
        os.makedirs(cache_dir, exist_ok=True)
    except PermissionError:
        # If we can't write to the default location, use temp directory
        import tempfile
        cache_dir = os.path.join(tempfile.gettempdir(), APP_NAME)
        os.makedirs(cache_dir, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create cache directory: {e}")
    
    # Use instance-specific cache file
    instance = get_current_instance()
    cache_filename = f"app_cache_instance_{instance}.json"
    return os.path.join(cache_dir, cache_filename)

def atomic_write_cache(cache_file_path, cache_data):
    """Write cache atomically to prevent corruption on power loss.
    
    Uses temp file + rename pattern to ensure either old or new data exists,
    never partial/corrupted data.
    """
    temp_file_path = cache_file_path + ".tmp"
    try:
        # Write to temporary file
        with open(temp_file_path, 'w') as f:
            json.dump(cache_data, f, indent=4)
            f.flush()  # Flush Python buffer to OS
            os.fsync(f.fileno())  # Force OS to write to physical disk
        
        # Atomic rename (replaces old file with new one)
        # On Windows, this removes the old file and renames temp to final name
        if os.path.exists(cache_file_path):
            os.replace(temp_file_path, cache_file_path)
        else:
            os.rename(temp_file_path, cache_file_path)
        
        # Sync the directory to ensure rename is persisted (Windows-safe)
        try:
            dir_path = os.path.dirname(cache_file_path)
            if dir_path and os.path.exists(dir_path):
                dir_fd = os.open(dir_path, os.O_RDONLY)
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)
        except (OSError, NotImplementedError):
            # Directory sync not supported on this OS/filesystem, skip it
            pass
    except Exception as e:
        # Clean up temp file if it exists
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        except:
            pass
        raise e

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
    """Serial COM port reader for receiving QR code data from scanners."""
    def __init__(self, port, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=0.1, callback=None, error_callback=None):
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.callback = callback
        self.error_callback = error_callback
        self.running = False
        self.thread = None
        self.serial_instance = None
        self.paused = threading.Event()
        self.paused.set()

    def start_reading(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self.read_loop, daemon=True)
        self.thread.start()

    def stop_reading(self):
        self.running = False
        self.resume()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        if self.serial_instance and self.serial_instance.is_open:
            try:
                self.serial_instance.close()
            except:
                pass

    def pause(self):
        self.paused.clear()

    def resume(self):
        if self.serial_instance:
            try:
                self.serial_instance.reset_input_buffer()
            except:
                pass
        self.paused.set()

    def read_loop(self):
        try:
            self.serial_instance = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=self.timeout,
                inter_byte_timeout=0.05
            )
            if self.error_callback:
                self.error_callback(f"Connected to {self.port}", "green")

            while self.running:
                self.paused.wait()
                if not self.running:
                    break

                if self.serial_instance.in_waiting > 0:
                    raw_data = self.serial_instance.read(256)
                    decoded_data = raw_data.decode(errors='ignore').strip()
                    decoded_data = re.sub(r'[^\x20-\x7E]', '', decoded_data)
                    if decoded_data and self.callback:
                        self.callback(decoded_data)
        except serial.SerialException as e:
            if self.error_callback:
                self.error_callback(f"Error connecting to {self.port}: {e}", "red")
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"Unexpected error: {e}", "red")
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
        self.output_udp_writer = UDPWriter()

        # Instance tracking
        self.current_instance = get_current_instance()

        # UDP Configuration (replaces COM port configuration)
        self.main_scanner_config = None  # {'local_ip': str, 'local_port': int, 'remote_ip': str, 'remote_port': int}
        self.ondemand_scanner_config = None
        self.output_config = None
        
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
        
        # Legacy serial settings (kept for backward compatibility, not used with UDP)
        self.baud_rate, self.data_bits, self.parity, self.stop_bits, self.timeout = 115200, 8, 'N', 1, 1
        self.current_theme = None

        # Auto-save configuration for power loss protection
        self.last_save_time = time.time()
        self.scans_since_save = 0
        self.auto_save_interval = 300  # Save every 5 minutes (300 seconds)
        self.auto_save_batch_size = 1000  # Save every 1000 scans

        # On-demand scanning state machine
        self.is_waiting_for_start_card = False
        self.is_waiting_for_count_card_1 = False
        self.is_waiting_for_count_card_2 = False
        self.first_card_index = -1

        # Load instance selection first (before loading cache)
        self.load_instance_selection()
        
        self.load_output_formats()
        self.load_cache()

        if self.current_theme is None:
            self.current_theme = get_windows_theme()
        
        # Restore UDP connections from cache
        if self.ondemand_scanner_config:
            config = self.ondemand_scanner_config
            self.connect_ondemand_udp(
                config.get('local_ip'), config.get('local_port'),
                config.get('remote_ip'), config.get('remote_port')
            )
        
        if self.output_config:
            config = self.output_config
            self.connect_output_udp(
                config.get('local_ip'), config.get('local_port'),
                config.get('remote_ip'), config.get('remote_port')
            )

        # Emit state_changed after all initial configurations
        self.state_changed.emit()
        self.theme_changed.emit(self.current_theme)

    def load_cache(self):
        try:
            with open(get_cache_file_path(), 'r') as f:
                cache = json.load(f)
                
                # Load UDP configurations
                self.main_scanner_config = cache.get('main_scanner_config')
                self.ondemand_scanner_config = cache.get('ondemand_scanner_config')
                self.output_config = cache.get('output_config')
                
                # Backward compatibility: Handle old serial cache format
                # If UDP configs don't exist but old serial configs do, initialize as None
                if not self.main_scanner_config and 'selected_com_port' in cache:
                    self.main_scanner_config = None
                if not self.ondemand_scanner_config and 'start_card_scan_port' in cache:
                    self.ondemand_scanner_config = None
                if not self.output_config and 'selected_output_port' in cache:
                    self.output_config = None
                
                # Legacy serial settings (kept for backward compatibility)
                self.baud_rate = cache.get('baud_rate', 115200)
                self.data_bits = cache.get('data_bits', 8)
                self.parity = cache.get('parity', 'N')
                self.stop_bits = cache.get('stop_bits', 1)
                self.timeout = cache.get('timeout', 1)
                
                self.selected_output_format = cache.get('selected_output_format', "")
                self.current_theme = cache.get('current_theme', "dark")
                self.start_card_code = cache.get('start_card_code')
                self.scan_direction = cache.get('scan_direction', 'top_to_bottom')
                
                # Load card type from cache
                cached_card_type = cache.get('card_type')
                if cached_card_type and not hasattr(self, '_card_type_set_by_user'):
                    self.card_type = CardType.from_string(cached_card_type)
                
                # Don't auto-load files - just clear the path since file isn't loaded
                # User must manually load files with card type selection
                selected_file_path = cache.get('selected_file_path')
                if selected_file_path:
                    # Clear the file path since we don't auto-load anymore
                    self.selected_file_path = ""
                
                self.log_data = cache.get('log_data', [])
                self.log_updated.emit(self.log_data)
                self.state_changed.emit()
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def save_cache(self):
        cache_data = {
            'card_type': self.card_type.value,
            'main_scanner_config': self.main_scanner_config,
            'ondemand_scanner_config': self.ondemand_scanner_config,
            'output_config': self.output_config,
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
        cache_file_path = get_cache_file_path()
        try:
            atomic_write_cache(cache_file_path, cache_data)
        except Exception as e:
            print(f"Warning: Failed to save cache: {e}")
        
        # Also save the current instance selection globally
        self.save_instance_selection()

    def save_instance_selection(self):
        """Save the current instance selection to a global config file"""
        cache_dir = user_data_dir(APP_NAME, APP_AUTHOR)
        try:
            os.makedirs(cache_dir, exist_ok=True)
        except:
            pass
        
        instance_config_path = os.path.join(cache_dir, "instance_config.json")
        try:
            config = {'current_instance': self.current_instance}
            with open(instance_config_path, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Warning: Failed to save instance selection: {e}")

    def load_instance_selection(self):
        """Load the last selected instance from global config"""
        cache_dir = user_data_dir(APP_NAME, APP_AUTHOR)
        instance_config_path = os.path.join(cache_dir, "instance_config.json")
        try:
            if os.path.exists(instance_config_path):
                with open(instance_config_path, 'r') as f:
                    config = json.load(f)
                    instance = config.get('current_instance', 1)
                    if instance in (1, 2):
                        set_current_instance(instance)
                        self.current_instance = instance
        except Exception as e:
            print(f"Warning: Failed to load instance selection: {e}")

    def load_output_formats(self):
        try:
            with open(constants.OUTPUT_FORMATS_PATH, 'r') as f:
                self.output_formats = json.load(f)
            if self.output_formats and not self.selected_output_format:
                self.selected_output_format = list(self.output_formats.keys())[0]
        except (FileNotFoundError, json.JSONDecodeError):
            self.output_formats = {}

    def start_scanning(self):
        if not self.main_scanner_config or self.is_scanning:
            return
        
        config = self.main_scanner_config
        self.main_port_reader = UDPReader(
            local_ip=config['local_ip'],
            local_port=config['local_port'],
            remote_ip=config.get('remote_ip'),
            remote_port=config.get('remote_port'),
            callback=self.handle_main_scan,
            error_callback=lambda msg, color: self.com_status_changed.emit(msg, color)
        )
        self.is_scanning = True
        self.main_port_reader.start_reading()
        
        bind_msg = f"Listening on {config['local_ip']}:{config['local_port']}"
        self.com_status_changed.emit(bind_msg, "green")
        
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
                    # Position in tuple: 0=BL, 1=TL, 2=TR, 3=BR
                    scan_sides = ["bottom_left", "top_left", "top_right", "bottom_right"]
                    self.scan_side = scan_sides[position] if position < len(scan_sides) else "bottom_left"
                
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
                position_map = {"bottom_left": 1, "top_left": 2, "top_right": 3, "bottom_right": 4}
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
                    future_match_index, scanned_position = self.qr_to_index[scanned_code]
                    
                    # Determine the expected position based on card type and scan side
                    if self.card_type == CardType.SINGLE:
                        expected_position = 0  # Only one position for single cards
                    elif self.card_type == CardType.HALF:
                        expected_position = 0 if self.scan_side == 'left' else 1
                    elif self.card_type == CardType.QUARTER:
                        position_map = {"bottom_left": 0, "top_left": 1, "top_right": 2, "bottom_right": 3}
                        expected_position = position_map.get(self.scan_side, 0)
                    else:
                        expected_position = 0
                    
                    # Check if the scanned QR is from the correct side
                    if scanned_position != expected_position:
                        # Wrong side scanned - just mark as NOT OK (simplified status)
                        status = "NOT OK"
                        log_entry = self.add_log_entry(scanned_code, expected_qr, status, scanned_side)
                        self.send_output_signal("NOT OK")
                    else:
                        # Correct side, check if it's ahead in sequence
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

    def connect_ondemand_udp(self, local_ip, local_port, remote_ip=None, remote_port=None):
        """Connect on-demand scanner via UDP"""
        if self.ondemand_port_reader:
            self.ondemand_port_reader.stop_reading()
        
        if not local_ip or not local_port:
            self.ondemand_scanner_config = None
            self.ondemand_port_reader = None
            self.ondemand_scan_status_update.emit("Not Connected", "red")
            return

        self.ondemand_port_reader = UDPReader(
            local_ip=local_ip,
            local_port=local_port,
            remote_ip=remote_ip,
            remote_port=remote_port,
            callback=self.handle_ondemand_scan,
            error_callback=lambda msg, color: self.ondemand_scan_status_update.emit(msg, color)
        )
        
        self.ondemand_scanner_config = {
            'local_ip': local_ip,
            'local_port': local_port,
            'remote_ip': remote_ip,
            'remote_port': remote_port
        }
        
        self.ondemand_port_reader.start_reading()
        self.ondemand_scan_status_update.emit(f"Connected to {local_ip}:{local_port}", "green")
        self.state_changed.emit()
        self.save_cache()

    def connect_ondemand_serial(self, port, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1):
        """Connect on-demand scanner via serial COM port"""
        if self.ondemand_port_reader:
            self.ondemand_port_reader.stop_reading()
        
        if not port:
            self.start_card_scan_port = None
            self.ondemand_port_reader = None
            self.ondemand_scan_status_update.emit("Not Connected", "red")
            self.state_changed.emit()
            self.save_cache()
            return

        # Update app_state attributes with the new settings
        self.baud_rate = baudrate
        self.data_bits = bytesize
        self.parity = parity
        self.stop_bits = stopbits
        self.timeout = timeout

        self.ondemand_port_reader = ComPortReader(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            timeout=timeout,
            callback=self.handle_ondemand_scan,
            error_callback=lambda msg, color: self.ondemand_scan_status_update.emit(msg, color)
        )
        
        self.start_card_scan_port = port
        self.ondemand_port_reader.start_reading()
        self.ondemand_scan_status_update.emit(f"Connected to {port}", "green")
        self.state_changed.emit()
        self.save_cache()

    def connect_output_udp(self, local_ip, local_port, remote_ip, remote_port):
        """Connect output via UDP"""
        if self.output_udp_writer.is_connected:
            self.output_udp_writer.disconnect()
        
        if not remote_ip or not remote_port:
            self.output_config = None
            self.output_com_status_changed.emit("Not Connected", "red")
            self.state_changed.emit()
            self.save_cache()
            return
        
        success, message = self.output_udp_writer.connect(
            local_ip=local_ip or "0.0.0.0",
            local_port=local_port or 0,
            remote_ip=remote_ip,
            remote_port=remote_port
        )
        
        if success:
            self.output_config = {
                'local_ip': local_ip,
                'local_port': local_port,
                'remote_ip': remote_ip,
                'remote_port': remote_port
            }
            self.output_com_status_changed.emit(message, "green")
        else:
            self.output_config = None
            self.output_com_status_changed.emit(message, "red")
        
        self.state_changed.emit()
        self.save_cache()

    def disconnect_all_ports(self):
        self.stop_scanning()
        if self.ondemand_port_reader:
            self.ondemand_port_reader.stop_reading()
            self.ondemand_port_reader = None
            self.ondemand_scan_status_update.emit("Not Connected", "red")
        if self.output_udp_writer.is_connected:
            self.output_udp_writer.disconnect()
            self.output_com_status_changed.emit("Not Connected", "red")
        
        self.main_scanner_config = None
        self.ondemand_scanner_config = None
        self.output_config = None
        self.state_changed.emit()
        self.save_cache()

    def get_timestamp(self):
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]

    def add_log_entry(self, scanned_code, expected_code, status, scanned_side="N/A"):
        log_entry = {
            "timestamp": self.get_timestamp(),
            "scanned_code": scanned_code,
            "expected_code": expected_code,
            "status": status,
            "scanned_side": scanned_side,
            "instance": self.current_instance
        }
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
        """Set the start card index based on scan direction"""
        if 0 <= index < len(self.expected_cards):
            # For top-to-bottom: current_card_index = array_index
            # For bottom-to-top: current_card_index = scan_position (total - 1 - array_index)
            if self.scan_direction == "bottom_to_top":
                self.current_card_index = len(self.expected_cards) - 1 - index
            else:
                self.current_card_index = index
            
            # For bottom-to-top, convert array index to scan position
            if self.scan_direction == "bottom_to_top":
                # If we found card at array index 75 in a 100-card file,
                # the scan position should be 24 (100 - 1 - 75)
                self.current_card_index = len(self.expected_cards) - 1 - index
            else:
                # For top-to-bottom, scan position = array index
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
        if not self.output_udp_writer.is_connected:
            return
        
        # Get card type key for output format lookup
        card_type_key = self.card_type.value  # "single", "half", or "quarter"
        
        # Get the format for this card type and status
        format_config = self.output_formats.get(self.selected_output_format, {})
        card_type_config = format_config.get(card_type_key, {})
        output_signal = card_type_config.get(status)
        
        if output_signal:
            # Send as ASCII text string (not binary)
            self.output_udp_writer.send(output_signal, as_binary_int=False)

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
            position_map = {"bottom_left": 1, "top_left": 2, "top_right": 3, "bottom_right": 4}
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
                
                # Skip cards from current array position down to future array position (exclusive)
                # Range should go from (actual_card_index - 1) down to (actual_future_index + 1)
                if actual_card_index > actual_future_index:
                    for i in range(actual_card_index - 1, actual_future_index, -1):
                        if i >= 0:  # Bounds check
                            skipped_qr = self.expected_cards[i][qr_position]
                            log_entries.append(self.add_log_entry("MISSING", skipped_qr, "SKIPPED", scanned_side))
                
                expected_jumped_qr = self.expected_cards[actual_future_index][qr_position]
                log_entries.append(self.add_log_entry(scanned_code, expected_jumped_qr, "OK (JUMPED)", scanned_side))
                self.send_output_signal("OK (JUMPED)")
                # Set current_card_index to scan position after the jumped card
                # For bottom-to-top: convert array index back to scan position
                self.current_card_index = len(self.expected_cards) - actual_future_index
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
                # For top-to-bottom: array index equals scan position
                self.current_card_index = future_index + 1
        else:
            log_entries.append(self.add_log_entry(scanned_code, expected_qr, "NOT OK", scanned_side))
            self.send_output_signal("NOT OK")
        
        self.log_data.extend(log_entries)
        self.log_updated.emit(log_entries)
        self.resume_scanning()
        self.state_changed.emit()