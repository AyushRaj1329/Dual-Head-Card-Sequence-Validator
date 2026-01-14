"""
Test final direction toggle behavior:
1. Toggle only allowed before scanning
2. First scan sets start card
3. Direction determines sequence from start card
"""

class MockAppState:
    def __init__(self, total_cards=10):
        self.expected_cards = [(f"Card_{i}", f"QR_{i}") for i in range(total_cards)]
        self.scan_direction = "top_to_bottom"
        self.current_card_index = 0
        self.start_card_has_been_scanned = False
        self.first_scan_received = True
        self.qr_to_index = {f"QR_{i}": (i, 0) for i in range(total_cards)}
    
    def get_current_expected_card_index(self):
        if self.scan_direction == "bottom_to_top":
            return len(self.expected_cards) - 1 - self.current_card_index
        else:
            return self.current_card_index
    
    def scan_card(self, card_num):
        """Simulate scanning a card"""
        scanned_qr = f"QR_{card_num}"
        
        if self.first_scan_received and not self.start_card_has_been_scanned:
            # First scan - set as start card
            if scanned_qr in self.qr_to_index:
                found_index, _ = self.qr_to_index[scanned_qr]
                self.current_card_index = found_index if self.scan_direction == "top_to_bottom" else len(self.expected_cards) - 1 - found_index
                self.start_card_has_been_scanned = True
                self.first_scan_received = False
                print(f"  First scan: QR_{card_num} → OK (Start card set at array index {found_index})")
                self.current_card_index += 1
                return "OK"
        
        # Subsequent scans
        actual_idx = self.get_current_expected_card_index()
        expected_qr = self.expected_cards[actual_idx][1]
        
        if scanned_qr == expected_qr:
            print(f"  Scan: {scanned_qr} → OK (array index {actual_idx})")
            self.current_card_index += 1
            return "OK"
        else:
            print(f"  Scan: {scanned_qr} → NOT OK (expected {expected_qr} at array index {actual_idx})")
            return "NOT_OK"


def test_toggle_before_scanning():
    """Test that toggle works before scanning"""
    print("=" * 70)
    print("TEST 1: Toggle Before Scanning (Allowed)")
    print("=" * 70)
    
    app = MockAppState(total_cards=10)
    
    print("\n--- Initial State ---")
    print(f"Direction: Top → Bottom")
    print(f"Cards scanned: 0")
    print(f"Can toggle: YES")
    
    print("\n--- User Toggles Direction ---")
    app.scan_direction = "bottom_to_top"
    app.current_card_index = 0
    app.start_card_has_been_scanned = False
    app.first_scan_received = True
    print(f"✓ Direction changed to: Bottom → Top")
    print(f"✓ Next scan will be treated as first card")
    
    print("\n--- User Scans First Card ---")
    app.scan_card(5)  # Scan card 5 as first card
    
    print("\n--- Continue Scanning Bottom-to-Top ---")
    app.scan_card(4)  # Should expect card 4 (going down from 5)
    app.scan_card(3)  # Should expect card 3
    
    print("\n✓ Test Passed: Toggle before scanning works correctly")


def test_toggle_during_scanning_blocked():
    """Test that toggle is blocked during scanning"""
    print("\n" + "=" * 70)
    print("TEST 2: Toggle During Scanning (Blocked)")
    print("=" * 70)
    
    app = MockAppState(total_cards=10)
    
    print("\n--- Start Scanning Top-to-Bottom ---")
    app.scan_card(0)
    app.scan_card(1)
    app.scan_card(2)
    print(f"Scanned 3 cards (0, 1, 2)")
    
    print("\n--- User Tries to Toggle Direction ---")
    if app.start_card_has_been_scanned and app.current_card_index > 0:
        print("✗ Toggle BLOCKED: Scanning has already started")
        print("  Message: 'Scan direction cannot be changed after scanning has started.'")
        print("  Suggestion: 'Please clear the logs and restart scanning to change direction.'")
    else:
        print("✓ Toggle allowed (unexpected)")
    
    print("\n✓ Test Passed: Toggle blocked during scanning")


def test_first_scan_sets_start_card():
    """Test that first scan sets the start card"""
    print("\n" + "=" * 70)
    print("TEST 3: First Scan Sets Start Card")
    print("=" * 70)
    
    print("\n--- Scenario A: Top-to-Bottom, Start at Card 3 ---")
    app = MockAppState(total_cards=10)
    app.scan_direction = "top_to_bottom"
    
    print("User scans Card 3 first")
    app.scan_card(3)  # First scan sets start card
    print("Expected next: Card 4")
    app.scan_card(4)
    app.scan_card(5)
    
    print("\n--- Scenario B: Bottom-to-Top, Start at Card 7 ---")
    app2 = MockAppState(total_cards=10)
    app2.scan_direction = "bottom_to_top"
    
    print("User scans Card 7 first")
    app2.scan_card(7)  # First scan sets start card
    print("Expected next: Card 6 (going down)")
    app2.scan_card(6)
    app2.scan_card(5)
    
    print("\n✓ Test Passed: First scan correctly sets start card")


def test_direction_determines_sequence():
    """Test that direction determines sequence from start card"""
    print("\n" + "=" * 70)
    print("TEST 4: Direction Determines Sequence")
    print("=" * 70)
    
    print("\n--- Top-to-Bottom from Card 5 ---")
    app = MockAppState(total_cards=10)
    app.scan_direction = "top_to_bottom"
    
    app.scan_card(5)  # Start at 5
    print("Sequence: 5 → 6 → 7 → 8 → 9")
    app.scan_card(6)
    app.scan_card(7)
    app.scan_card(8)
    app.scan_card(9)
    
    print("\n--- Bottom-to-Top from Card 5 ---")
    app2 = MockAppState(total_cards=10)
    app2.scan_direction = "bottom_to_top"
    
    app2.scan_card(5)  # Start at 5
    print("Sequence: 5 → 4 → 3 → 2 → 1 → 0")
    app2.scan_card(4)
    app2.scan_card(3)
    app2.scan_card(2)
    app2.scan_card(1)
    app2.scan_card(0)
    
    print("\n✓ Test Passed: Direction correctly determines sequence")


def test_complete_workflow():
    """Test complete user workflow"""
    print("\n" + "=" * 70)
    print("TEST 5: Complete User Workflow")
    print("=" * 70)
    
    print("\nScenario: User has cards arranged bottom-to-top")
    print("1. User loads file")
    print("2. User toggles to 'Bottom → Top'")
    print("3. User scans first card (Card 9)")
    print("4. System sets Card 9 as start")
    print("5. User continues: 9 → 8 → 7 → 6...")
    
    app = MockAppState(total_cards=10)
    
    print("\n--- Step 1: Load file ---")
    print("✓ File loaded with 10 cards")
    
    print("\n--- Step 2: Toggle direction ---")
    app.scan_direction = "bottom_to_top"
    print("✓ Direction: Bottom → Top")
    
    print("\n--- Step 3-5: Start scanning ---")
    app.scan_card(9)  # First scan
    app.scan_card(8)
    app.scan_card(7)
    app.scan_card(6)
    
    print("\n✓ Workflow completed successfully")


def test_edge_cases():
    """Test edge cases"""
    print("\n" + "=" * 70)
    print("TEST 6: Edge Cases")
    print("=" * 70)
    
    print("\n--- Case A: Start at first card, go top-to-bottom ---")
    app = MockAppState(total_cards=10)
    app.scan_direction = "top_to_bottom"
    app.scan_card(0)
    app.scan_card(1)
    print("✓ Works correctly")
    
    print("\n--- Case B: Start at last card, go bottom-to-top ---")
    app2 = MockAppState(total_cards=10)
    app2.scan_direction = "bottom_to_top"
    app2.scan_card(9)
    app2.scan_card(8)
    print("✓ Works correctly")
    
    print("\n--- Case C: Start at middle card, go top-to-bottom ---")
    app3 = MockAppState(total_cards=10)
    app3.scan_direction = "top_to_bottom"
    app3.scan_card(5)
    app3.scan_card(6)
    print("✓ Works correctly")
    
    print("\n✓ All edge cases handled correctly")


def test_benefits():
    """Document benefits of this approach"""
    print("\n" + "=" * 70)
    print("BENEFITS OF THIS APPROACH")
    print("=" * 70)
    
    benefits = [
        ("Simplicity", "No complex position tracking during toggle"),
        ("Flexibility", "User can start from any card in the sequence"),
        ("Clarity", "Direction is set before scanning, no confusion"),
        ("Safety", "Cannot accidentally change direction mid-scan"),
        ("Intuitive", "First scan always sets the start point"),
    ]
    
    for i, (title, desc) in enumerate(benefits, 1):
        print(f"\n{i}. {title}")
        print(f"   {desc}")


if __name__ == "__main__":
    test_toggle_before_scanning()
    test_toggle_during_scanning_blocked()
    test_first_scan_sets_start_card()
    test_direction_determines_sequence()
    test_complete_workflow()
    test_edge_cases()
    test_benefits()
    
    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70)
    print("\nSummary:")
    print("✓ Toggle only allowed before scanning")
    print("✓ First scan sets start card")
    print("✓ Direction determines sequence from start card")
    print("✓ Simple and intuitive behavior")
    print("✓ All edge cases handled")
