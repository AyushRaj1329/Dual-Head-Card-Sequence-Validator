# services/utilities.py
import csv
import subprocess
import threading
import platform
from ..card_types import CardType

def ping_remote_ip_async(remote_ip, callback=None):
    """
    Ping a remote IP address in a background thread.
    Opens command prompt, runs ping, and closes it automatically.
    
    Args:
        remote_ip (str): IP address to ping
        callback (callable): Optional callback function to call when ping completes
                           Receives (success: bool, message: str) as arguments
    """
    def ping_worker():
        try:
            # Determine OS and set appropriate ping command
            if platform.system().lower() == 'windows':
                # Windows: ping 4 times and close
                cmd = f'ping -n 4 {remote_ip}'
                # Use CREATE_NEW_CONSOLE to open in new command prompt window
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                # Linux/Mac: ping 4 times
                cmd = f'ping -c 4 {remote_ip}'
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            # Wait for process to complete
            stdout, stderr = process.communicate(timeout=30)
            
            # Check if ping was successful
            success = process.returncode == 0
            
            if success:
                message = f"Ping to {remote_ip} successful"
            else:
                message = f"Ping to {remote_ip} failed - Device may be unreachable"
            
            # Call callback if provided
            if callback:
                callback(success, message)
                
        except subprocess.TimeoutExpired:
            process.kill()
            if callback:
                callback(False, f"Ping to {remote_ip} timed out")
    # Start ping in background thread
    thread = threading.Thread(target=ping_worker, daemon=True)
    thread.start()

def parse_cpd_cards(file_path, card_type=CardType.HALF):
    """Parse CPD file based on card type with new positioning logic - using only ICCID"""
    card_data = []
    start_reading = False
    total_cards = 0
    header = None
    numcard_idx = None
    iccid_idx = None
    
    # First pass: validate format and count total cards
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            lines = f.readlines()
            
            # Validate file is not empty
            if not lines:
                raise ValueError("CPD file is empty.")
            
            # Find and validate header
            header_found = False
            for line_num, line in enumerate(lines, start=1):
                line = line.strip()
                if line.startswith("NUMCARD"):
                    header_found = True
                    header = line.split(";")
                    
                    # Validate header is not empty
                    if not header or all(not h.strip() for h in header):
                        raise ValueError("CPD file has an empty or invalid header row.")
                    
                    # Check for NUMCARD column (required)
                    try:
                        numcard_idx = header.index("NUMCARD")
                    except ValueError:
                        raise ValueError("CPD file header must contain 'NUMCARD' column.")
                    
                    # Find ICCID column (required)
                    iccid_idx = next((i for i, h in enumerate(header) if "ICCID" in h), None)
                    if iccid_idx is None:
                        raise ValueError("CPD file header must contain 'ICCID' column.")
                    
                    start_reading = True
                    continue
                
                if start_reading and line and not line.startswith("NUMCARD"):
                    # Validate row has correct number of fields
                    parts = line.split(";")
                    if len(parts) != len(header):
                        raise ValueError(f"CPD file line {line_num} has {len(parts)} fields, but header has {len(header)} fields. All rows must match the header.")
                    total_cards += 1
            
            # Validate header was found
            if not header_found:
                raise ValueError("CPD file must contain a header row starting with 'NUMCARD'.")
            
            # Validate file has data rows
            if total_cards == 0:
                raise ValueError("CPD file has no data rows (only header).")
    
    except UnicodeDecodeError:
        raise ValueError("CPD file has invalid encoding. File must be UTF-8 encoded text.")
    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Error reading CPD file: {str(e)}")
    
    # Second pass: parse with positioning logic
    start_reading = False
    with open(file_path, mode='r', encoding='utf-8') as f:
        line_num = 0
        for line in f:
            line_num += 1
            line = line.strip()
            if line.startswith("NUMCARD"):
                start_reading = True
                continue
            
            if start_reading and line and not line.startswith("NUMCARD"):
                parts = line.split(";")
                numcard = parts[numcard_idx].strip()
                
                # Validate NUMCARD is not empty
                if not numcard:
                    raise ValueError(f"CPD file line {line_num}: NUMCARD is empty.")
                
                # Validate NUMCARD is numeric
                try:
                    card_index = int(numcard)
                except ValueError:
                    raise ValueError(f"CPD file line {line_num}: NUMCARD '{numcard}' is not a valid number.")
                
                # Get ICCID as the QR code
                qr_code = parts[iccid_idx].strip() if iccid_idx is not None else ""
                
                # Validate ICCID is not empty
                if not qr_code:
                    raise ValueError(f"CPD file line {line_num}: ICCID is empty for card {numcard}.")
                
                if card_type == CardType.SINGLE:
                    # Single card: use ICCID as the single QR
                    card_data.append((numcard, qr_code))
                    
                elif card_type == CardType.HALF:
                    # Half card: Left at position 1-total/2, Right at position (total/2+1)-total
                    half_point = total_cards // 2
                    if card_index <= half_point:
                        # This is a left card - store temporarily
                        card_data.append((numcard, qr_code, "LEFT"))
                    else:
                        # This is a right card - find corresponding left card
                        corresponding_left = card_index - half_point
                        card_data.append((str(corresponding_left), qr_code, "RIGHT"))
                        
                elif card_type == CardType.QUARTER:
                    # Quarter card: 1st->BL, 2nd->TL, 3rd->TR, 4th->BR
                    quarter_size = total_cards // 4
                    if card_index <= quarter_size:
                        # First quarter -> Bottom-Left
                        position = "BL"
                        base_card = card_index
                    elif card_index <= 2 * quarter_size:
                        # Second quarter -> Top-Left
                        position = "TL"
                        base_card = card_index - quarter_size
                    elif card_index <= 3 * quarter_size:
                        # Third quarter -> Top-Right
                        position = "TR"
                        base_card = card_index - 2 * quarter_size
                    else:
                        # Fourth quarter -> Bottom-Right
                        position = "BR"
                        base_card = card_index - 3 * quarter_size
                    
                    card_data.append((str(base_card), qr_code, position))
    
    # Post-process half and quarter cards to merge into single entries
    if card_type == CardType.HALF:
        merged_cards = {}
        for numcard, qr_code, position in card_data:
            if numcard not in merged_cards:
                merged_cards[numcard] = {"LEFT": "", "RIGHT": ""}
            merged_cards[numcard][position] = qr_code
        
        # Convert back to list format
        card_data = []
        for numcard in sorted(merged_cards.keys(), key=int):
            card = merged_cards[numcard]
            card_data.append((numcard, card["LEFT"], card["RIGHT"]))
    
    elif card_type == CardType.QUARTER:
        merged_cards = {}
        for numcard, qr_code, position in card_data:
            if numcard not in merged_cards:
                merged_cards[numcard] = {"BL": "", "TL": "", "TR": "", "BR": ""}
            merged_cards[numcard][position] = qr_code
        
        # Convert back to list format with new order: BL, TL, TR, BR
        card_data = []
        for numcard in sorted(merged_cards.keys(), key=int):
            card = merged_cards[numcard]
            card_data.append((numcard, card["BL"], card["TL"], card["TR"], card["BR"]))
    
    return card_data
