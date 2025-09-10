# services/utilities.py
import csv

def parse_cpd_cards(file_path):
    card_data = []
    start_reading = False
    with open(file_path, mode='r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith("NUMCARD;MAXCARD;DATAFILE;ICCID;IMSI"):
                start_reading = True
                header = line.split(";")
                numcard_idx = header.index("NUMCARD")
                iccid_idx = header.index("ICCID")
                imsi_idx = header.index("IMSI") # Get index for IMSI (right QR)
                continue
            if start_reading and line:
                parts = line.split(";")
                numcard = parts[numcard_idx]
                iccid = parts[iccid_idx]
                imsi = parts[imsi_idx]
                card_data.append((numcard, iccid, imsi))
    return card_data

def parse_txt_file(file_path):
    iccid_data = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            iccid = line.strip()
            if iccid:
                # For TXT files, we assume left and right QR are the same
                iccid_data.append((f"Card_{i+1}", iccid, iccid))
    return iccid_data

def parse_csv_file(file_path):
    card_data = []
    with open(file_path, mode='r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        try:
            numcard_idx = header.index("NUMCARD")
            iccid_idx = header.index("ICCID")
            # Try to find an IMSI column, but don't require it
            imsi_idx = header.index("IMSI") if "IMSI" in header else None
        except ValueError:
            raise ValueError("CSV file must contain at least 'NUMCARD' and 'ICCID' columns.")
        for row in reader:
            numcard = row[numcard_idx]
            iccid = row[iccid_idx]
            # Use IMSI if available, otherwise duplicate ICCID
            imsi = row[imsi_idx] if imsi_idx is not None else iccid
            card_data.append((numcard, iccid, imsi))
    return card_data