"""
Test to verify the matching and skipping logic
"""

def test_top_to_bottom_matching():
    """Test top-to-bottom scan direction"""
    print("\n=== TOP TO BOTTOM TEST ===")
    total_cards = 100
    current_card_index = 10  # We've scanned 10 cards
    scan_direction = "top_to_bottom"
    
    # Calculate actual array index
    if scan_direction == "bottom_to_top":
        actual_card_index = total_cards - 1 - current_card_index
    else:
        actual_card_index = current_card_index
    
    print(f"Current scan position: {current_card_index}")
    print(f"Actual array index: {actual_card_index}")
    
    # Scenario 1: Scan a card at array position 50 (ahead of us)
    future_match_index = 50
    print(f"\nScanned card at array index: {future_match_index}")
    
    if scan_direction == "top_to_bottom":
        if future_match_index > actual_card_index:
            num_skipped = future_match_index - actual_card_index
            print(f"✓ Card is ahead! Skip {num_skipped} cards")
            print(f"  Will skip array indices: {actual_card_index} to {future_match_index-1}")
            print(f"  After jump, current_card_index should be: {future_match_index + 1}")
        else:
            print(f"✗ Card is behind or same - mark as NOT OK")
    
    # Scenario 2: Scan a card at array position 5 (behind us)
    future_match_index = 5
    print(f"\nScanned card at array index: {future_match_index}")
    
    if scan_direction == "top_to_bottom":
        if future_match_index > actual_card_index:
            num_skipped = future_match_index - actual_card_index
            print(f"✓ Card is ahead! Skip {num_skipped} cards")
        else:
            print(f"✗ Card is behind or same - mark as NOT OK")


def test_bottom_to_top_matching():
    """Test bottom-to-top scan direction"""
    print("\n=== BOTTOM TO TOP TEST ===")
    total_cards = 100
    current_card_index = 10  # We've scanned 10 cards from the bottom
    scan_direction = "bottom_to_top"
    
    # Calculate actual array index
    if scan_direction == "bottom_to_top":
        actual_card_index = total_cards - 1 - current_card_index
    else:
        actual_card_index = current_card_index
    
    print(f"Current scan position: {current_card_index}")
    print(f"Actual array index: {actual_card_index} (card #{actual_card_index + 1})")
    
    # Scenario 1: Scan a card at array position 50 (ahead in array, but behind in scan order)
    future_match_index = 50
    print(f"\nScanned card at array index: {future_match_index} (card #{future_match_index + 1})")
    
    if scan_direction == "bottom_to_top":
        if future_match_index < actual_card_index:
            num_skipped = actual_card_index - future_match_index
            future_scan_position = total_cards - 1 - future_match_index
            print(f"✓ Card is ahead in scan order! Skip {num_skipped} cards")
            print(f"  Will skip array indices: {future_match_index + 1} to {actual_card_index - 1}")
            print(f"  Future scan position: {future_scan_position}")
            print(f"  After jump, current_card_index should be: {future_scan_position + 1}")
        else:
            print(f"✗ Card is behind in scan order - mark as NOT OK")
    
    # Scenario 2: Scan a card at array position 95 (behind in array, ahead in scan order)
    future_match_index = 95
    print(f"\nScanned card at array index: {future_match_index} (card #{future_match_index + 1})")
    
    if scan_direction == "bottom_to_top":
        if future_match_index < actual_card_index:
            num_skipped = actual_card_index - future_match_index
            future_scan_position = total_cards - 1 - future_match_index
            print(f"✓ Card is ahead in scan order! Skip {num_skipped} cards")
        else:
            print(f"✗ Card is behind in scan order - mark as NOT OK")


def test_resolution_logic():
    """Test the resolution logic after approval"""
    print("\n=== RESOLUTION LOGIC TEST ===")
    
    # Top-to-bottom scenario
    print("\nTop-to-bottom: Jump from position 10 to 50")
    total_cards = 100
    actual_card_index = 10
    future_index = 50  # This is array index for top-to-bottom
    
    print(f"Current array index: {actual_card_index}")
    print(f"Future array index: {future_index}")
    print(f"Skip cards from array index {actual_card_index} to {future_index - 1}")
    skipped = list(range(actual_card_index, future_index))
    print(f"Skipped indices: {skipped[:5]}...{skipped[-5:]} (total: {len(skipped)})")
    print(f"✓ Mark array index {future_index} as OK (JUMPED)")
    print(f"✓ Set current_card_index = {future_index + 1}")
    
    # Bottom-to-top scenario
    print("\nBottom-to-top: Jump from scan position 10 to scan position 50")
    current_card_index = 10
    actual_card_index = total_cards - 1 - current_card_index  # = 89
    future_scan_position = 50
    actual_future_index = total_cards - 1 - future_scan_position  # = 49
    
    print(f"Current array index: {actual_card_index}")
    print(f"Future array index: {actual_future_index}")
    print(f"Skip cards from array index {actual_future_index + 1} to {actual_card_index - 1}")
    
    if actual_card_index > actual_future_index:
        # FIXED: range should be (actual_card_index - 1, actual_future_index, -1)
        skipped = list(range(actual_card_index - 1, actual_future_index, -1))
        print(f"Skipped indices: {skipped[:5]}...{skipped[-5:]} (total: {len(skipped)})")
    
    print(f"✓ Mark array index {actual_future_index} as OK (JUMPED)")
    new_current_card_index = total_cards - actual_future_index
    print(f"✓ Set current_card_index = {total_cards} - {actual_future_index} = {new_current_card_index}")
    
    # Verify the logic
    print("\n=== VERIFICATION ===")
    print(f"Top-to-bottom: After jump, next expected card is at array index {future_index + 1} ✓")
    print(f"Bottom-to-top: After jump, next expected card is at array index {actual_future_index - 1}")
    print(f"  (scan position {new_current_card_index} = array index {total_cards - 1 - new_current_card_index}) ✓")


if __name__ == "__main__":
    test_top_to_bottom_matching()
    test_bottom_to_top_matching()
    test_resolution_logic()
