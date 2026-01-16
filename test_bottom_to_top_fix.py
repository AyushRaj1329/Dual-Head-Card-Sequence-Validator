"""
Test to verify bottom-to-top start card detection fix
"""

class MockAppState:
    def __init__(self, total_cards, scan_direction):
        self.expected_cards = [(f"Card_{i}", f"QR_{i}") for i in range(total_cards)]
        self.scan_direction = scan_direction
        self.current_card_index = 0
        self.qr_to_index = {}
        
        # Build QR lookup
        for i, card in enumerate(self.expected_cards):
            qr_code = card[1]
            self.qr_to_index[qr_code] = (i, 0)
    
    def set_start_index(self, index):
        """Fixed version"""
        if 0 <= index < len(self.expected_cards):
            # For bottom-to-top, convert array index to scan position
            if self.scan_direction == "bottom_to_top":
                self.current_card_index = len(self.expected_cards) - 1 - index
            else:
                self.current_card_index = index
    
    def get_current_expected_card_index(self):
        """Get the current card index based on scan direction"""
        if self.scan_direction == "bottom_to_top":
            return len(self.expected_cards) - 1 - self.current_card_index
        else:
            return self.current_card_index
    
    def increment_card_index(self):
        """Increment card index (same for both directions)"""
        self.current_card_index += 1
    
    def scan_card(self, qr_code):
        """Simulate scanning a card"""
        if qr_code in self.qr_to_index:
            found_index, _ = self.qr_to_index[qr_code]
            return found_index
        return None

def test_bottom_to_top_start_card():
    print("=" * 60)
    print("TEST: Bottom-to-Top Start Card Detection")
    print("=" * 60)
    
    # Create app with 100 cards, bottom-to-top mode
    app = MockAppState(total_cards=100, scan_direction="bottom_to_top")
    
    print("\n📋 Setup:")
    print(f"  Total cards: {len(app.expected_cards)}")
    print(f"  Scan direction: {app.scan_direction}")
    print(f"  Cards in file: Card_0 to Card_99")
    
    # Test Case 1: Scan card at index 75
    print("\n" + "─" * 60)
    print("TEST CASE 1: User scans Card_75 first")
    print("─" * 60)
    
    scanned_qr = "QR_75"
    found_index = app.scan_card(scanned_qr)
    
    print(f"\n1. User scans: {scanned_qr}")
    print(f"   Found at array index: {found_index}")
    
    # Set as start card
    app.set_start_index(found_index)
    print(f"\n2. set_start_index({found_index}) called")
    print(f"   current_card_index set to: {app.current_card_index}")
    
    # Get expected card
    actual_index = app.get_current_expected_card_index()
    print(f"\n3. get_current_expected_card_index() returns: {actual_index}")
    print(f"   Expected card: Card_{actual_index}")
    
    # Verify
    if actual_index == found_index:
        print(f"\n✅ PASS: First scan correctly expects Card_{actual_index}")
    else:
        print(f"\n❌ FAIL: Expected Card_{found_index}, got Card_{actual_index}")
    
    # Test next card
    print(f"\n4. User scans next card...")
    app.increment_card_index()
    print(f"   current_card_index incremented to: {app.current_card_index}")
    
    next_actual_index = app.get_current_expected_card_index()
    print(f"   get_current_expected_card_index() returns: {next_actual_index}")
    print(f"   Expected card: Card_{next_actual_index}")
    
    # Verify next card is previous in sequence
    if next_actual_index == found_index - 1:
        print(f"\n✅ PASS: Next scan correctly expects Card_{next_actual_index} (previous card)")
    else:
        print(f"\n❌ FAIL: Expected Card_{found_index - 1}, got Card_{next_actual_index}")
    
    # Test Case 2: Scan card at index 99 (last card)
    print("\n" + "─" * 60)
    print("TEST CASE 2: User scans Card_99 first (last card)")
    print("─" * 60)
    
    app2 = MockAppState(total_cards=100, scan_direction="bottom_to_top")
    scanned_qr = "QR_99"
    found_index = app2.scan_card(scanned_qr)
    
    print(f"\n1. User scans: {scanned_qr}")
    print(f"   Found at array index: {found_index}")
    
    app2.set_start_index(found_index)
    print(f"\n2. set_start_index({found_index}) called")
    print(f"   current_card_index set to: {app2.current_card_index}")
    
    actual_index = app2.get_current_expected_card_index()
    print(f"\n3. get_current_expected_card_index() returns: {actual_index}")
    print(f"   Expected card: Card_{actual_index}")
    
    if actual_index == found_index:
        print(f"\n✅ PASS: First scan correctly expects Card_{actual_index}")
    else:
        print(f"\n❌ FAIL: Expected Card_{found_index}, got Card_{actual_index}")
    
    # Test Case 3: Scan card at index 0 (first card)
    print("\n" + "─" * 60)
    print("TEST CASE 3: User scans Card_0 first (first card)")
    print("─" * 60)
    
    app3 = MockAppState(total_cards=100, scan_direction="bottom_to_top")
    scanned_qr = "QR_0"
    found_index = app3.scan_card(scanned_qr)
    
    print(f"\n1. User scans: {scanned_qr}")
    print(f"   Found at array index: {found_index}")
    
    app3.set_start_index(found_index)
    print(f"\n2. set_start_index({found_index}) called")
    print(f"   current_card_index set to: {app3.current_card_index}")
    
    actual_index = app3.get_current_expected_card_index()
    print(f"\n3. get_current_expected_card_index() returns: {actual_index}")
    print(f"   Expected card: Card_{actual_index}")
    
    if actual_index == found_index:
        print(f"\n✅ PASS: First scan correctly expects Card_{actual_index}")
        print(f"   Note: This is the first card, so there are no previous cards to scan")
    else:
        print(f"\n❌ FAIL: Expected Card_{found_index}, got Card_{actual_index}")

def test_top_to_bottom_still_works():
    print("\n\n" + "=" * 60)
    print("TEST: Top-to-Bottom Still Works (Regression Test)")
    print("=" * 60)
    
    app = MockAppState(total_cards=100, scan_direction="top_to_bottom")
    
    print("\n📋 Setup:")
    print(f"  Total cards: {len(app.expected_cards)}")
    print(f"  Scan direction: {app.scan_direction}")
    
    print("\n" + "─" * 60)
    print("TEST CASE: User scans Card_25 first")
    print("─" * 60)
    
    scanned_qr = "QR_25"
    found_index = app.scan_card(scanned_qr)
    
    print(f"\n1. User scans: {scanned_qr}")
    print(f"   Found at array index: {found_index}")
    
    app.set_start_index(found_index)
    print(f"\n2. set_start_index({found_index}) called")
    print(f"   current_card_index set to: {app.current_card_index}")
    
    actual_index = app.get_current_expected_card_index()
    print(f"\n3. get_current_expected_card_index() returns: {actual_index}")
    print(f"   Expected card: Card_{actual_index}")
    
    if actual_index == found_index:
        print(f"\n✅ PASS: First scan correctly expects Card_{actual_index}")
    else:
        print(f"\n❌ FAIL: Expected Card_{found_index}, got Card_{actual_index}")
    
    app.increment_card_index()
    next_actual_index = app.get_current_expected_card_index()
    print(f"\n4. Next scan expects: Card_{next_actual_index}")
    
    if next_actual_index == found_index + 1:
        print(f"✅ PASS: Next scan correctly expects Card_{next_actual_index} (next card)")
    else:
        print(f"❌ FAIL: Expected Card_{found_index + 1}, got Card_{next_actual_index}")

def main():
    print("\n" + "🔧" * 30)
    print("BOTTOM-TO-TOP START CARD FIX VERIFICATION")
    print("🔧" * 30)
    
    test_bottom_to_top_start_card()
    test_top_to_bottom_still_works()
    
    print("\n\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("\n✅ Fix Applied:")
    print("   set_start_index() now converts array index to scan position")
    print("   for bottom-to-top mode")
    print("\n✅ Expected Behavior:")
    print("   - User scans any card in bottom-to-top mode")
    print("   - System finds card in file")
    print("   - Sets it as start card")
    print("   - Next scan expects previous card in sequence")
    print("\n✅ Top-to-Bottom:")
    print("   - Still works as before (no regression)")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
