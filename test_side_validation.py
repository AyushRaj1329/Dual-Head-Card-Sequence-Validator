"""
Test to verify that the system only accepts QR codes from the correct side
"""

class MockCardType:
    SINGLE = "single"
    HALF = "half"
    QUARTER = "quarter"

class MockAppState:
    def __init__(self, card_type):
        self.card_type = card_type
        self.scan_side = None
        self.current_card_index = 0
        self.scan_direction = "top_to_bottom"
        
        # Setup test data based on card type
        if card_type == MockCardType.SINGLE:
            # Single card: only one QR per card
            self.expected_cards = [
                ("Card_1", "QR_1_SINGLE"),
                ("Card_2", "QR_2_SINGLE"),
                ("Card_3", "QR_3_SINGLE"),
            ]
            self.qr_to_index = {
                "QR_1_SINGLE": (0, 0),
                "QR_2_SINGLE": (1, 0),
                "QR_3_SINGLE": (2, 0),
            }
            self.scan_side = "single"
            
        elif card_type == MockCardType.HALF:
            # Half card: left (position 0) and right (position 1)
            self.expected_cards = [
                ("Card_1", "QR_1_LEFT", "QR_1_RIGHT"),
                ("Card_2", "QR_2_LEFT", "QR_2_RIGHT"),
                ("Card_3", "QR_3_LEFT", "QR_3_RIGHT"),
            ]
            self.qr_to_index = {
                "QR_1_LEFT": (0, 0),
                "QR_1_RIGHT": (0, 1),
                "QR_2_LEFT": (1, 0),
                "QR_2_RIGHT": (1, 1),
                "QR_3_LEFT": (2, 0),
                "QR_3_RIGHT": (2, 1),
            }
            self.scan_side = "left"  # Start with left side
            
        elif card_type == MockCardType.QUARTER:
            # Quarter card: TL(0), TR(1), BL(2), BR(3)
            self.expected_cards = [
                ("Card_1", "QR_1_TL", "QR_1_TR", "QR_1_BL", "QR_1_BR"),
                ("Card_2", "QR_2_TL", "QR_2_TR", "QR_2_BL", "QR_2_BR"),
                ("Card_3", "QR_3_TL", "QR_3_TR", "QR_3_BL", "QR_3_BR"),
            ]
            self.qr_to_index = {
                "QR_1_TL": (0, 0), "QR_1_TR": (0, 1), "QR_1_BL": (0, 2), "QR_1_BR": (0, 3),
                "QR_2_TL": (1, 0), "QR_2_TR": (1, 1), "QR_2_BL": (1, 2), "QR_2_BR": (1, 3),
                "QR_3_TL": (2, 0), "QR_3_TR": (2, 1), "QR_3_BL": (2, 2), "QR_3_BR": (2, 3),
            }
            self.scan_side = "top_left"  # Start with top-left
    
    def get_current_expected_card_index(self):
        return self.current_card_index
    
    def handle_scan(self, scanned_code):
        """Simulate the matching logic with side validation"""
        actual_card_index = self.get_current_expected_card_index()
        
        # Get expected QR based on scan side and card type
        if self.card_type == MockCardType.SINGLE:
            expected_qr = self.expected_cards[actual_card_index][1]
            qr_position = 1
        elif self.card_type == MockCardType.HALF:
            qr_position = 1 if self.scan_side == 'left' else 2
            expected_qr = self.expected_cards[actual_card_index][qr_position]
        elif self.card_type == MockCardType.QUARTER:
            position_map = {"top_left": 1, "top_right": 2, "bottom_left": 3, "bottom_right": 4}
            qr_position = position_map.get(self.scan_side, 1)
            expected_qr = self.expected_cards[actual_card_index][qr_position]
        
        print(f"\nScan #{self.current_card_index + 1} (Expecting {self.scan_side}):")
        print(f"  Scanned: {scanned_code}")
        print(f"  Expected: {expected_qr}")
        
        if scanned_code == expected_qr:
            print(f"  ✓ OK")
            self.current_card_index += 1
            return "OK"
        else:
            # Check if scanned code exists elsewhere in sequence
            if scanned_code in self.qr_to_index:
                future_match_index, scanned_position = self.qr_to_index[scanned_code]
                
                # Determine the expected position based on card type and scan side
                if self.card_type == MockCardType.SINGLE:
                    expected_position = 0
                elif self.card_type == MockCardType.HALF:
                    expected_position = 0 if self.scan_side == 'left' else 1
                elif self.card_type == MockCardType.QUARTER:
                    position_map = {"top_left": 0, "top_right": 1, "bottom_left": 2, "bottom_right": 3}
                    expected_position = position_map.get(self.scan_side, 0)
                else:
                    expected_position = 0
                
                # Check if the scanned QR is from the correct side
                if scanned_position != expected_position:
                    # Wrong side scanned
                    if self.card_type == MockCardType.HALF:
                        wrong_side = "Right" if scanned_position == 1 else "Left"
                        print(f"  ✗ NOT OK (Wrong Side: {wrong_side})")
                        print(f"     You're scanning {self.scan_side} side, but this is a {wrong_side} QR code")
                    elif self.card_type == MockCardType.QUARTER:
                        side_names = ["Top-Left", "Top-Right", "Bottom-Left", "Bottom-Right"]
                        wrong_side = side_names[scanned_position]
                        print(f"  ✗ NOT OK (Wrong Side: {wrong_side})")
                        print(f"     You're scanning {self.scan_side.replace('_', '-')} side, but this is a {wrong_side} QR code")
                    return "NOT_OK_WRONG_SIDE"
                else:
                    # Correct side, check if ahead
                    if future_match_index > actual_card_index:
                        num_skipped = future_match_index - actual_card_index
                        print(f"  ⚠ Found {num_skipped} positions ahead (correct side)")
                        return "SKIP_PROMPT"
                    else:
                        print(f"  ✗ NOT OK (card is behind)")
                        return "NOT_OK"
            else:
                print(f"  ✗ NOT OK (not in sequence)")
                return "NOT_OK"


def test_half_card_side_validation():
    """Test that half cards only accept the correct side"""
    print("=" * 70)
    print("HALF CARD - SIDE VALIDATION TEST")
    print("=" * 70)
    
    app = MockAppState(MockCardType.HALF)
    print(f"\nScanning LEFT side only...")
    
    # Correct scans
    app.handle_scan("QR_1_LEFT")   # ✓ OK
    app.handle_scan("QR_2_LEFT")   # ✓ OK
    
    # Try scanning RIGHT side (should fail)
    app.handle_scan("QR_3_RIGHT")  # ✗ Wrong side
    
    # Continue with correct side
    app.handle_scan("QR_3_LEFT")   # ✓ OK
    
    print("\n" + "-" * 70)
    print("\nNow test RIGHT side scanning...")
    app2 = MockAppState(MockCardType.HALF)
    app2.scan_side = "right"
    
    app2.handle_scan("QR_1_RIGHT")  # ✓ OK
    app2.handle_scan("QR_1_LEFT")   # ✗ Wrong side (left when expecting right)
    app2.handle_scan("QR_2_RIGHT")  # ✓ OK


def test_quarter_card_side_validation():
    """Test that quarter cards only accept the correct side"""
    print("\n" + "=" * 70)
    print("QUARTER CARD - SIDE VALIDATION TEST")
    print("=" * 70)
    
    app = MockAppState(MockCardType.QUARTER)
    print(f"\nScanning TOP-LEFT side only...")
    
    # Correct scans
    app.handle_scan("QR_1_TL")     # ✓ OK
    
    # Try scanning different sides (should all fail)
    app.handle_scan("QR_2_TR")     # ✗ Wrong side (Top-Right)
    app.handle_scan("QR_2_BL")     # ✗ Wrong side (Bottom-Left)
    app.handle_scan("QR_2_BR")     # ✗ Wrong side (Bottom-Right)
    
    # Continue with correct side
    app.handle_scan("QR_2_TL")     # ✓ OK


def test_skip_with_correct_side():
    """Test that skipping only works with correct side"""
    print("\n" + "=" * 70)
    print("SKIP WITH SIDE VALIDATION TEST")
    print("=" * 70)
    
    app = MockAppState(MockCardType.HALF)
    print(f"\nScanning LEFT side, trying to skip...")
    
    app.handle_scan("QR_1_LEFT")   # ✓ OK
    
    # Try to skip with WRONG side (should fail, not prompt)
    print("\n--- Attempting to skip with WRONG side ---")
    app.handle_scan("QR_3_RIGHT")  # ✗ Wrong side (no skip prompt)
    
    # Skip with CORRECT side (should prompt)
    print("\n--- Attempting to skip with CORRECT side ---")
    app.handle_scan("QR_3_LEFT")   # ⚠ Skip prompt (correct side)


if __name__ == "__main__":
    test_half_card_side_validation()
    test_quarter_card_side_validation()
    test_skip_with_correct_side()
    print("\n" + "=" * 70)
    print("ALL SIDE VALIDATION TESTS COMPLETED")
    print("=" * 70)
