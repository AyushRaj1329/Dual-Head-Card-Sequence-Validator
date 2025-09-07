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
                continue
            if start_reading and line:
                parts = line.split(";")
                numcard = parts[numcard_idx]
                iccid = parts[iccid_idx]
                card_data.append((numcard, iccid))
    paired_cards = []
    for i in range(len(card_data)):
        current = card_data[i]
        next_card = card_data[i + 1] if i + 1 < len(card_data) else None
        paired_cards.append((current, next_card))
    return paired_cards

def parse_txt_file(file_path):
    iccid_data = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            iccid = line.strip()
            if iccid:
                iccid_data.append((f"Card_{i+1}", iccid)) # Assign a generic NUMCARD
    paired_cards = []
    for i in range(len(iccid_data)):
        current = iccid_data[i]
        next_card = iccid_data[i + 1] if i + 1 < len(iccid_data) else None
        paired_cards.append((current, next_card))
    return paired_cards

def parse_csv_file(file_path):
    card_data = []
    with open(file_path, mode='r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        try:
            numcard_idx = header.index("NUMCARD")
            iccid_idx = header.index("ICCID")
        except ValueError:
            raise ValueError("CSV file must contain 'NUMCARD' and 'ICCID' columns.")
        for row in reader:
            numcard = row[numcard_idx]
            iccid = row[iccid_idx]
            card_data.append((numcard, iccid))
    paired_cards = []
    for i in range(len(card_data)):
        current = card_data[i]
        next_card = card_data[i + 1] if i + 1 < len(card_data) else None
        paired_cards.append((current, next_card))
    return paired_cards