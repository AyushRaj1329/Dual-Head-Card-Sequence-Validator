# logic/file_parser.py
import os
import csv
from ..services.utilities import parse_cpd_cards, parse_txt_file, parse_csv_file
from ..card_types import CardType

def detect_card_type_from_file(file_path):
    """
    Auto-detect card type by analyzing file structure.
    Returns CardType enum.
    """
    _, file_extension = os.path.splitext(file_path)
    
    # TXT files: default to SINGLE (one QR per line)
    if file_extension.lower() == '.txt':
        return CardType.SINGLE
    
    # CSV and CPD files: analyze headers
    if file_extension.lower() in ['.csv', '.cpd']:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Read first line to get headers
                first_line = f.readline().strip()
                
                # Determine delimiter
                delimiter = ';' if file_extension.lower() == '.cpd' else ','
                if delimiter not in first_line:
                    delimiter = ',' if delimiter == ';' else ';'
                
                headers = [h.strip().upper() for h in first_line.split(delimiter)]
                
                # Count QR-related columns (excluding NUMCARD)
                qr_columns = 0
                
                # Check for various QR column patterns
                single_patterns = ['QR']
                half_patterns = ['ICCID', 'IMSI', 'LEFT', 'RIGHT']
                quarter_patterns = ['TL', 'TR', 'BL', 'BR', 'TOP_LEFT', 'TOP_RIGHT', 'BOTTOM_LEFT', 'BOTTOM_RIGHT']
                
                # Count matches for each pattern
                has_single = any(pattern in h for h in headers for pattern in single_patterns)
                has_half = sum(1 for h in headers for pattern in half_patterns if pattern in h)
                has_quarter = sum(1 for h in headers for pattern in quarter_patterns if pattern in h)
                
                # Determine card type based on column count
                if has_quarter >= 4:
                    return CardType.QUARTER
                elif has_half >= 2:
                    return CardType.HALF
                elif has_single or len(headers) == 2:  # NUMCARD + 1 QR column
                    return CardType.SINGLE
                else:
                    # Default to HALF if unclear
                    return CardType.HALF
                    
        except Exception as e:
            # If detection fails, default to HALF
            print(f"Card type detection failed: {e}. Defaulting to HALF.")
            return CardType.HALF
    
    # Default to HALF for unknown formats
    return CardType.HALF

def parse_file(file_path, card_type=None):
    """
    Parse file based on extension and card type.
    If card_type is None, it will be auto-detected.
    Returns (card_data, detected_card_type)
    """
    # Auto-detect card type if not provided
    if card_type is None:
        card_type = detect_card_type_from_file(file_path)
    
    _, file_extension = os.path.splitext(file_path)
    
    if file_extension.lower() == '.cpd':
        card_data = parse_cpd_cards(file_path, card_type)
    elif file_extension.lower() == '.txt':
        card_data = parse_txt_file(file_path, card_type)
    elif file_extension.lower() == '.csv':
        card_data = parse_csv_file(file_path, card_type)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")
    
    return card_data, card_type