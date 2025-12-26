# logic/file_parser.py
import os
import csv
from ..services.utilities import parse_cpd_cards, parse_txt_file, parse_csv_file
from ..card_types import CardType

def parse_file(file_path, card_type):
    """
    Parse file based on extension and card type.
    card_type must be provided (no auto-detection).
    Returns (card_data, card_type)
    """
    if card_type is None:
        raise ValueError("Card type must be specified. Auto-detection has been removed.")
    
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