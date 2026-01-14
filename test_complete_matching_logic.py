"""
Comprehensive test for matching and skipping logic
Simulates the actual app behavior
"""

class MockAppState:
    def __init__(self, total_cards, scan_direction):
        self.expected_cards = [(f"Card_{i}", f"QR_{i}") for i in range(total_cards)]
        self.scan_direction = scan_direction
        self.current_card_index = 0
        self.qr_to_index = {f"QR_{i}": (i, 0) for i in range(total_cards)}
        
    def get_current_expected_card_index(self):
        """Get the current card index based on scan direction"""
        if self.scan_direction == "bottom_to_top":
            return len(self.expected_cards) - 1 - self.current_card_index
        else:
            return self.current_card_index
    
    def handle_scan(self, scanned_qr):
        """Simulate the matching logic"""
        actual_card_index = self.get_current_expected_card_index()
        expected_qr = self.expected_cards[actual_card_index][1]
        
        print(f"\nScan #{self.current_card_index + 1}:")
        print(f"  Scanned: {scanned_qr}")
        print(f"  Expected: {expected_qr} (array index {actual_card_index})")
        
        if scanned_qr == expected_qr:
            print(f"  ✓ MATCH - OK")
            self.current_card_index += 1
            return "OK"
        else:
            # Check if scanned code exists elsewhere
            if scanned_qr in self.qr_to_index:
                future_match_index, _ = self.qr_to_index[scanned_qr]
                
                if self.scan_direction == "bottom_to_top":
                    if future_match_index < actual_card_index:
                        num_skipped = actual_card_index - future_match_index
                        future_scan_position = len(self.expected_cards) - 1 - future_match_index
                        print(f"  ⚠ MISMATCH - Found {num_skipped} positions ahead")
                        print(f"     Future card at array index {future_match_index}, scan position {future_scan_position}")
                        return ("SKIP_PROMPT", num_skipped, future_scan_position)
                    else:
                        print(f"  ✗ MISMATCH - Card is behind, NOT OK")
                        return "NOT_OK"
                else:  # top_to_bottom
                    if future_match_index > actual_card_index:
                        num_skipped = future_match_index - actual_card_index
                        print(f"  ⚠ MISMATCH - Found {num_skipped} positions ahead")
                        print(f"     Future card at array index {future_match_index}")
                        return ("SKIP_PROMPT", num_skipped, future_match_index)
                    else:
                        print(f"  ✗ MISMATCH - Card is behind, NOT OK")
                        return "NOT_OK"
            else:
                print(f"  ✗ MISMATCH - Card not in sequence, NOT OK")
                return "NOT_OK"
    
    def resolve_skip(self, future_index):
        """Simulate the skip resolution logic"""
        actual_card_index = self.get_current_expected_card_index()
        
        print(f"\n  Resolving skip...")
        
        if self.scan_direction == "bottom_to_top":
            actual_future_index = len(self.expected_cards) - 1 - future_index
            
            skipped_indices = list(range(actual_card_index - 1, actual_future_index, -1))
            print(f"  Skipping array indices: {skipped_indices[:3]}...{skipped_indices[-3:]} ({len(skipped_indices)} cards)")
            print(f"  Marking array index {actual_future_index} as OK (JUMPED)")
            
            self.current_card_index = len(self.expected_cards) - actual_future_index
            print(f"  New scan position: {self.current_card_index}")
        else:
            skipped_indices = list(range(actual_card_index, future_index))
            print(f"  Skipping array indices: {skipped_indices[:3]}...{skipped_indices[-3:]} ({len(skipped_indices)} cards)")
            print(f"  Marking array index {future_index} as OK (JUMPED)")
            
            self.current_card_index = future_index + 1
            print(f"  New scan position: {self.current_card_index}")


def test_top_to_bottom_scenario():
    """Test a complete top-to-bottom scanning scenario"""
    print("=" * 60)
    print("TOP-TO-BOTTOM SCANNING TEST")
    print("=" * 60)
    
    app = MockAppState(total_cards=20, scan_direction="top_to_bottom")
    
    # Normal scans
    app.handle_scan("QR_0")  # OK
    app.handle_scan("QR_1")  # OK
    app.handle_scan("QR_2")  # OK
    
    # Skip ahead
    result = app.handle_scan("QR_10")  # Should prompt to skip
    if isinstance(result, tuple) and result[0] == "SKIP_PROMPT":
        _, num_skipped, future_index = result
        print(f"\n  User approves skipping {num_skipped} cards")
        app.resolve_skip(future_index)
    
    # Continue scanning
    app.handle_scan("QR_11")  # OK
    
    # Try scanning a card behind
    app.handle_scan("QR_5")  # Should be NOT OK
    
    print(f"\nFinal position: {app.current_card_index}")


def test_bottom_to_top_scenario():
    """Test a complete bottom-to-top scanning scenario"""
    print("\n" + "=" * 60)
    print("BOTTOM-TO-TOP SCANNING TEST")
    print("=" * 60)
    
    app = MockAppState(total_cards=20, scan_direction="bottom_to_top")
    
    # Normal scans (starting from the end)
    app.handle_scan("QR_19")  # OK (last card)
    app.handle_scan("QR_18")  # OK
    app.handle_scan("QR_17")  # OK
    
    # Skip ahead (toward the beginning)
    result = app.handle_scan("QR_10")  # Should prompt to skip
    if isinstance(result, tuple) and result[0] == "SKIP_PROMPT":
        _, num_skipped, future_index = result
        print(f"\n  User approves skipping {num_skipped} cards")
        app.resolve_skip(future_index)
    
    # Continue scanning
    app.handle_scan("QR_9")  # OK
    
    # Try scanning a card behind (in scan order)
    app.handle_scan("QR_15")  # Should be NOT OK
    
    print(f"\nFinal position: {app.current_card_index}")


def test_edge_cases():
    """Test edge cases"""
    print("\n" + "=" * 60)
    print("EDGE CASES TEST")
    print("=" * 60)
    
    # Test skipping to the last card
    print("\n--- Skip to last card (top-to-bottom) ---")
    app = MockAppState(total_cards=10, scan_direction="top_to_bottom")
    app.handle_scan("QR_0")
    result = app.handle_scan("QR_9")
    if isinstance(result, tuple) and result[0] == "SKIP_PROMPT":
        _, num_skipped, future_index = result
        app.resolve_skip(future_index)
    print(f"Final position: {app.current_card_index} (should be 10)")
    
    # Test skipping to the first card
    print("\n--- Skip to first card (bottom-to-top) ---")
    app = MockAppState(total_cards=10, scan_direction="bottom_to_top")
    app.handle_scan("QR_9")
    result = app.handle_scan("QR_0")
    if isinstance(result, tuple) and result[0] == "SKIP_PROMPT":
        _, num_skipped, future_index = result
        app.resolve_skip(future_index)
    print(f"Final position: {app.current_card_index} (should be 10)")


if __name__ == "__main__":
    test_top_to_bottom_scenario()
    test_bottom_to_top_scenario()
    test_edge_cases()
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
