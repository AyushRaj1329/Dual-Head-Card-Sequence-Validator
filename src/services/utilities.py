# services/utilities.py
import csv
from ..card_types import CardType

def parse_cpd_cards(file_path, card_type=CardType.HALF):
    """Parse CPD file based on card type"""
    card_data = []
    start_reading = False
    with open(file_path, mode='r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Detect header based on card type
            if card_type == CardType.SINGLE:
                if line.startswith("NUMCARD") and "QR" in line:
                    start_reading = True
                    header = line.split(";")
                    numcard_idx = header.index("NUMCARD")
                    qr_idx = next((i for i, h in enumerate(header) if "QR" in h), None)
                    continue
            elif card_type == CardType.HALF:
                if line.startswith("NUMCARD;MAXCARD;DATAFILE;ICCID;IMSI") or \
                   (line.startswith("NUMCARD") and ("ICCID" in line or "LEFT" in line)):
                    start_reading = True
                    header = line.split(";")
                    numcard_idx = header.index("NUMCARD")
                    iccid_idx = next((i for i, h in enumerate(header) if "ICCID" in h or "LEFT" in h), None)
                    imsi_idx = next((i for i, h in enumerate(header) if "IMSI" in h or "RIGHT" in h), None)
                    continue
            elif card_type == CardType.QUARTER:
                if line.startswith("NUMCARD") and ("TL" in line or "TOP_LEFT" in line):
                    start_reading = True
                    header = line.split(";")
                    numcard_idx = header.index("NUMCARD")
                    tl_idx = next((i for i, h in enumerate(header) if "TL" in h or "TOP_LEFT" in h), None)
                    tr_idx = next((i for i, h in enumerate(header) if "TR" in h or "TOP_RIGHT" in h), None)
                    bl_idx = next((i for i, h in enumerate(header) if "BL" in h or "BOTTOM_LEFT" in h), None)
                    br_idx = next((i for i, h in enumerate(header) if "BR" in h or "BOTTOM_RIGHT" in h), None)
                    continue
            
            if start_reading and line:
                parts = line.split(";")
                numcard = parts[numcard_idx]
                
                if card_type == CardType.SINGLE:
                    qr = parts[qr_idx] if qr_idx is not None else parts[1]
                    card_data.append((numcard, qr))
                elif card_type == CardType.HALF:
                    iccid = parts[iccid_idx] if iccid_idx is not None else parts[1]
                    imsi = parts[imsi_idx] if imsi_idx is not None else parts[2]
                    card_data.append((numcard, iccid, imsi))
                elif card_type == CardType.QUARTER:
                    tl = parts[tl_idx] if tl_idx is not None else parts[1]
                    tr = parts[tr_idx] if tr_idx is not None else parts[2]
                    bl = parts[bl_idx] if bl_idx is not None else parts[3]
                    br = parts[br_idx] if br_idx is not None else parts[4]
                    card_data.append((numcard, tl, tr, bl, br))
    return card_data

def parse_txt_file(file_path, card_type=CardType.HALF):
    """Parse TXT file - one QR per line, duplicated based on card type"""
    card_data = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            qr = line.strip()
            if qr:
                numcard = f"Card_{i+1}"
                if card_type == CardType.SINGLE:
                    card_data.append((numcard, qr))
                elif card_type == CardType.HALF:
                    card_data.append((numcard, qr, qr))
                elif card_type == CardType.QUARTER:
                    card_data.append((numcard, qr, qr, qr, qr))
    return card_data

def parse_csv_file(file_path, card_type=CardType.HALF):
    """Parse CSV file based on card type"""
    card_data = []
    with open(file_path, mode='r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        try:
            numcard_idx = header.index("NUMCARD")
        except ValueError:
            raise ValueError("CSV file must contain 'NUMCARD' column.")
        
        if card_type == CardType.SINGLE:
            qr_idx = next((i for i, h in enumerate(header) if "QR" in h.upper()), None)
            if qr_idx is None:
                raise ValueError("CSV file must contain a QR column for single card type.")
            
            for row in reader:
                numcard = row[numcard_idx]
                qr = row[qr_idx]
                card_data.append((numcard, qr))
                
        elif card_type == CardType.HALF:
            iccid_idx = next((i for i, h in enumerate(header) if "ICCID" in h.upper() or "LEFT" in h.upper()), None)
            imsi_idx = next((i for i, h in enumerate(header) if "IMSI" in h.upper() or "RIGHT" in h.upper()), None)
            
            if iccid_idx is None:
                raise ValueError("CSV file must contain ICCID or LEFT column for half card type.")
            
            for row in reader:
                numcard = row[numcard_idx]
                iccid = row[iccid_idx]
                imsi = row[imsi_idx] if imsi_idx is not None else iccid
                card_data.append((numcard, iccid, imsi))
                
        elif card_type == CardType.QUARTER:
            tl_idx = next((i for i, h in enumerate(header) if "TL" in h.upper() or "TOP_LEFT" in h.upper()), None)
            tr_idx = next((i for i, h in enumerate(header) if "TR" in h.upper() or "TOP_RIGHT" in h.upper()), None)
            bl_idx = next((i for i, h in enumerate(header) if "BL" in h.upper() or "BOTTOM_LEFT" in h.upper()), None)
            br_idx = next((i for i, h in enumerate(header) if "BR" in h.upper() or "BOTTOM_RIGHT" in h.upper()), None)
            
            if None in [tl_idx, tr_idx, bl_idx, br_idx]:
                raise ValueError("CSV file must contain TL, TR, BL, BR columns for quarter card type.")
            
            for row in reader:
                numcard = row[numcard_idx]
                tl = row[tl_idx]
                tr = row[tr_idx]
                bl = row[bl_idx]
                br = row[br_idx]
                card_data.append((numcard, tl, tr, bl, br))
    
    return card_data