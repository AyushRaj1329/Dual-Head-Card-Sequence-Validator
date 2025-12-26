#!/usr/bin/env python3
"""
Test script to verify the new positioning logic for card types using real files from card_example folder
"""

import sys
import os
sys.path.append('.')

from src.logic.file_parser import parse_file
from src.card_types import CardType

def test_positioning_logic():
    print("Testing New Positioning Logic with Real Files")
    print("=" * 60)
    
    # Test Single Card with real file
    print("\n1. Testing Single Card (HESH1355.CPD):")
    try:
        cards, card_type = parse_file("card_example/single_card/HESH1355.CPD", CardType.SINGLE)
        print(f"   Card Type: {card_type}")
        print(f"   Total Cards: {len(cards)}")
        print("   First 3 cards:")
        for i, card in enumerate(cards[:3]):
            print(f"     Card {i+1}: NUMCARD={card[0]}, ICCID={card[1]}")
        print("   Last 3 cards:")
        for i, card in enumerate(cards[-3:], len(cards)-2):
            print(f"     Card {i}: NUMCARD={card[0]}, ICCID={card[1]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test Half Card with real file
    print("\n2. Testing Half Card (RILS5622.CPD):")
    try:
        cards, card_type = parse_file("card_example/half_Card/RILS5622.CPD", CardType.HALF)
        print(f"   Card Type: {card_type}")
        print(f"   Total Logical Cards: {len(cards)}")
        print("   First 3 logical cards:")
        for i, card in enumerate(cards[:3]):
            print(f"     Card {i+1}: NUMCARD={card[0]}, Left_ICCID={card[1]}, Right_ICCID={card[2]}")
        print("   Last 3 logical cards:")
        for i, card in enumerate(cards[-3:], len(cards)-2):
            print(f"     Card {i}: NUMCARD={card[0]}, Left_ICCID={card[1]}, Right_ICCID={card[2]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test Quarter Card with real file
    print("\n3. Testing Quarter Card (HESH1356.CPD):")
    try:
        cards, card_type = parse_file("card_example/quater_card/HESH1356.CPD", CardType.QUARTER)
        print(f"   Card Type: {card_type}")
        print(f"   Total Logical Cards: {len(cards)}")
        print("   First 3 logical cards:")
        for i, card in enumerate(cards[:3]):
            print(f"     Card {i+1}: NUMCARD={card[0]}")
            print(f"       TL_ICCID={card[1]}")
            print(f"       TR_ICCID={card[2]}")
            print(f"       BL_ICCID={card[3]}")
            print(f"       BR_ICCID={card[4]}")
        print("   Last logical card:")
        card = cards[-1]
        print(f"     Card {len(cards)}: NUMCARD={card[0]}")
        print(f"       TL_ICCID={card[1]}")
        print(f"       TR_ICCID={card[2]}")
        print(f"       BL_ICCID={card[3]}")
        print(f"       BR_ICCID={card[4]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 60)
    print("Real file testing completed!")
    
    # Show positioning logic explanation
    print("\n" + "=" * 60)
    print("POSITIONING LOGIC EXPLANATION:")
    print("=" * 60)
    print("\nFor a file with N total cards:")
    print("\n📱 SINGLE CARD:")
    print("   - Cards 1 to N: Each card has 1 ICCID")
    print("   - Result: N logical cards")
    
    print("\n📱 HALF CARD:")
    print("   - Cards 1 to N/2: Left ICCIDs")
    print("   - Cards (N/2+1) to N: Right ICCIDs")
    print("   - Result: N/2 logical cards (each with Left + Right ICCID)")
    
    print("\n📱 QUARTER CARD:")
    print("   - Cards 1 to N/4: Top-Left ICCIDs")
    print("   - Cards (N/4+1) to N/2: Top-Right ICCIDs")
    print("   - Cards (N/2+1) to 3N/4: Bottom-Left ICCIDs")
    print("   - Cards (3N/4+1) to N: Bottom-Right ICCIDs")
    print("   - Result: N/4 logical cards (each with TL + TR + BL + BR ICCID)")

if __name__ == "__main__":
    test_positioning_logic()