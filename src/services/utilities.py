# services/utilities.py
import csv
from ..card_types import CardType

def parse_cpd_cards(file_path, card_type=CardType.HALF):
    """Parse CPD file based on card type with new positioning logic - using only ICCID"""
    card_data = []
    start_reading = False
    total_cards = 0
    
    # First pass: count total cards
    with open(file_path, mode='r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith("NUMCARD"):
                start_reading = True
                continue
            if start_reading and line and not line.startswith("NUMCARD"):
                total_cards += 1
    
    # Second pass: parse with positioning logic
    start_reading = False
    with open(file_path, mode='r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith("NUMCARD"):
                start_reading = True
                header = line.split(";")
                numcard_idx = header.index("NUMCARD")
                # Find ICCID column (main QR code)
                iccid_idx = next((i for i, h in enumerate(header) if "ICCID" in h), None)
                continue
            
            if start_reading and line and not line.startswith("NUMCARD"):
                parts = line.split(";")
                numcard = parts[numcard_idx]
                card_index = int(numcard)
                
                # Get ICCID as the QR code
                qr_code = parts[iccid_idx] if iccid_idx is not None else ""
                
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
                    # Quarter card: TL at 1-total/4, TR at (total/4+1)-total/2, BL at (total/2+1)-3*total/4, BR at (3*total/4+1)-total
                    quarter_size = total_cards // 4
                    if card_index <= quarter_size:
                        # Top-Left quarter
                        position = "TL"
                        base_card = card_index
                    elif card_index <= 2 * quarter_size:
                        # Top-Right quarter
                        position = "TR"
                        base_card = card_index - quarter_size
                    elif card_index <= 3 * quarter_size:
                        # Bottom-Left quarter
                        position = "BL"
                        base_card = card_index - 2 * quarter_size
                    else:
                        # Bottom-Right quarter
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
                merged_cards[numcard] = {"TL": "", "TR": "", "BL": "", "BR": ""}
            merged_cards[numcard][position] = qr_code
        
        # Convert back to list format
        card_data = []
        for numcard in sorted(merged_cards.keys(), key=int):
            card = merged_cards[numcard]
            card_data.append((numcard, card["TL"], card["TR"], card["BL"], card["BR"]))
    
    return card_data

def parse_txt_file(file_path, card_type=CardType.HALF):
    """Parse TXT file with new positioning logic - using only ICCID"""
    lines = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    total_cards = len(lines)
    card_data = []
    
    if card_type == CardType.SINGLE:
        for i, qr in enumerate(lines):
            card_data.append((f"Card_{i+1}", qr))
            
    elif card_type == CardType.HALF:
        # Half card logic: Left at 1-total/2, Right at (total/2+1)-total
        half_point = total_cards // 2
        for i in range(half_point):
            left_qr = lines[i]
            right_qr = lines[i + half_point] if i + half_point < total_cards else ""
            card_data.append((f"Card_{i+1}", left_qr, right_qr))
            
    elif card_type == CardType.QUARTER:
        # Quarter card logic: TL, TR, BL, BR
        quarter_size = total_cards // 4
        for i in range(quarter_size):
            tl_qr = lines[i] if i < total_cards else ""
            tr_qr = lines[i + quarter_size] if i + quarter_size < total_cards else ""
            bl_qr = lines[i + 2 * quarter_size] if i + 2 * quarter_size < total_cards else ""
            br_qr = lines[i + 3 * quarter_size] if i + 3 * quarter_size < total_cards else ""
            card_data.append((f"Card_{i+1}", tl_qr, tr_qr, bl_qr, br_qr))
    
    return card_data

def parse_csv_file(file_path, card_type=CardType.HALF):
    """Parse CSV file with new positioning logic - using only ICCID"""
    card_data = []
    with open(file_path, mode='r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        try:
            numcard_idx = header.index("NUMCARD")
        except ValueError:
            raise ValueError("CSV file must contain 'NUMCARD' column.")
        
        # Find ICCID column
        iccid_idx = next((i for i, h in enumerate(header) if "ICCID" in h.upper()), None)
        if iccid_idx is None:
            raise ValueError("CSV file must contain 'ICCID' column.")
        
        # Read all rows first to get total count
        rows = list(reader)
        total_cards = len(rows)
        
        if card_type == CardType.SINGLE:
            for row in rows:
                numcard = row[numcard_idx]
                qr = row[iccid_idx]
                card_data.append((numcard, qr))
                
        elif card_type == CardType.HALF:
            # Apply half card positioning logic
            half_point = total_cards // 2
            for i in range(half_point):
                left_row = rows[i]
                right_row = rows[i + half_point] if i + half_point < total_cards else left_row
                
                numcard = left_row[numcard_idx]
                left_qr = left_row[iccid_idx]
                right_qr = right_row[iccid_idx] if i + half_point < total_cards else ""
                card_data.append((numcard, left_qr, right_qr))
                
        elif card_type == CardType.QUARTER:
            # Apply quarter card positioning logic
            quarter_size = total_cards // 4
            for i in range(quarter_size):
                tl_row = rows[i] if i < total_cards else None
                tr_row = rows[i + quarter_size] if i + quarter_size < total_cards else None
                bl_row = rows[i + 2 * quarter_size] if i + 2 * quarter_size < total_cards else None
                br_row = rows[i + 3 * quarter_size] if i + 3 * quarter_size < total_cards else None
                
                numcard = tl_row[numcard_idx] if tl_row else f"Card_{i+1}"
                tl_qr = tl_row[iccid_idx] if tl_row else ""
                tr_qr = tr_row[iccid_idx] if tr_row else ""
                bl_qr = bl_row[iccid_idx] if bl_row else ""
                br_qr = br_row[iccid_idx] if br_row else ""
                
                card_data.append((numcard, tl_qr, tr_qr, bl_qr, br_qr))
    
    return card_data