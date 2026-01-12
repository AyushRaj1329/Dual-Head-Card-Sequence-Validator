#!/usr/bin/env python3
"""
Test script to verify scan direction functionality
"""

import sys
import os
sys.path.append('.')

def test_scan_direction_logic():
    print("Testing Scan Direction Logic")
    print("=" * 50)
    
    # Test data - simulate a sequence of 10 cards
    test_cards = [
        ("1", "QR001"),
        ("2", "QR002"), 
        ("3", "QR003"),
        ("4", "QR004"),
        ("5", "QR005"),
        ("6", "QR006"),
        ("7", "QR007"),
        ("8", "QR008"),
        ("9", "QR009"),
        ("10", "QR010")
    ]
    
    print(f"Test sequence: {len(test_cards)} cards")
    print("Cards:", [card[1] for card in test_cards])
    
    def get_current_expected_card_index(current_index, scan_direction, total_cards):
        """Simulate the app_state method"""
        if scan_direction == "bottom_to_top":
            return total_cards - 1 - current_index
        else:
            return current_index
    
    def test_direction(direction):
        print(f"\n📍 Testing {direction.upper().replace('_', ' ')} direction:")
        print("-" * 30)
        
        for current_index in range(len(test_cards)):
            actual_index = get_current_expected_card_index(current_index, direction, len(test_cards))
            expected_qr = test_cards[actual_index][1]
            
            print(f"  Step {current_index + 1}: current_index={current_index}, actual_index={actual_index}, expected_qr={expected_qr}")
            
            if current_index >= 5:  # Stop after 5 steps for brevity
                print(f"  ... (continuing to card {len(test_cards)})")
                break
    
    # Test both directions
    test_direction("top_to_bottom")
    test_direction("bottom_to_top")
    
    print(f"\n✅ Scan direction logic test completed!")
    
    # Test the actual expected sequence for both directions
    print(f"\n📋 Expected Scanning Sequences:")
    print("-" * 40)
    
    print("Top → Bottom sequence:")
    for i in range(len(test_cards)):
        actual_idx = get_current_expected_card_index(i, "top_to_bottom", len(test_cards))
        print(f"  {i+1}. {test_cards[actual_idx][1]} (card {test_cards[actual_idx][0]})")
    
    print("\nBottom → Top sequence:")
    for i in range(len(test_cards)):
        actual_idx = get_current_expected_card_index(i, "bottom_to_top", len(test_cards))
        print(f"  {i+1}. {test_cards[actual_idx][1]} (card {test_cards[actual_idx][0]})")

def test_ui_integration():
    print(f"\n🖥️  UI Integration Test")
    print("=" * 50)
    
    print("The scan direction toggle should:")
    print("✅ Show 'Top → Bottom' when scan_direction = 'top_to_bottom'")
    print("✅ Show 'Bottom → Top' when scan_direction = 'bottom_to_top'")
    print("✅ Reset current_card_index to 0 when toggled")
    print("✅ Save the setting to cache")
    print("✅ Show confirmation message to user")
    print("✅ Update scanner logging to show correct next expected card")
    
    print(f"\nTo test in the application:")
    print("1. Load a sequence file")
    print("2. Click the scan direction toggle button")
    print("3. Verify the button text changes")
    print("4. Check that 'Next Expected' shows the correct card")
    print("5. Start scanning and verify sequence validation works")

if __name__ == "__main__":
    test_scan_direction_logic()
    test_ui_integration()