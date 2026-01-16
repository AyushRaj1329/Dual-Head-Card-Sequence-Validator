# First Scan Bug Fix

## Problem
When starting a scan, the first scanned card was not being set correctly as the start card. The system was showing "NOT OK" status instead of accepting the first scan.

## Root Causes

### Bug #1: Incorrect Scan Side Detection for Quarter Cards
**Location:** `src/app_state.py` - `handle_main_scan()` method

**Problem:**
```python
# WRONG - Incorrect mapping
scan_sides = ["top_left", "top_right", "bottom_left", "bottom_right"]
```

This mapped position indices incorrectly:
- Position 0 → "top_left" (WRONG! Should be "bottom_left")
- Position 1 → "top_right" (WRONG! Should be "top_left")
- Position 2 → "bottom_left" (WRONG! Should be "top_right")
- Position 3 → "bottom_right" (CORRECT!)

**Fix:**
```python
# CORRECT - Matches tuple structure (numcard, BL, TL, TR, BR)
scan_sides = ["bottom_left", "top_left", "top_right", "bottom_right"]
```

Now correctly maps:
- Position 0 → "bottom_left" ✓
- Position 1 → "top_left" ✓
- Position 2 → "top_right" ✓
- Position 3 → "bottom_right" ✓

### Bug #2: Incorrect Position Mapping in Multiple Locations
**Location:** `src/app_state.py` - Multiple methods

**Problem:**
The position_map was incorrectly mapping scan sides to tuple indices:
```python
# WRONG
position_map = {"top_left": 1, "top_right": 2, "bottom_left": 3, "bottom_right": 4}
```

**Fix:**
```python
# CORRECT - Matches tuple structure
position_map = {"bottom_left": 1, "top_left": 2, "top_right": 3, "bottom_right": 4}
```

### Bug #3: set_start_index Doesn't Account for Scan Direction
**Location:** `src/app_state.py` - `set_start_index()` method

**Problem:**
```python
def set_start_index(self, index):
    if 0 <= index < len(self.expected_cards):
        self.current_card_index = index  # WRONG for bottom-to-top!
```

When scanning bottom-to-top, `current_card_index` should be the scan position, not the array index.

**Example of the bug:**
- Scan direction: Bottom-to-Top
- First scan: Card 3 (array index 2)
- Bug sets: `current_card_index = 2`
- But should be: `current_card_index = total_cards - 1 - 2 = 2` (for 5 cards)
- Next expected: Array index `5 - 1 - 2 = 2` ✓ (happens to work)
- But the logic is wrong!

**Fix:**
```python
def set_start_index(self, index):
    """Set the start card index based on scan direction"""
    if 0 <= index < len(self.expected_cards):
        # For top-to-bottom: current_card_index = array_index
        # For bottom-to-top: current_card_index = scan_position
        if self.scan_direction == "bottom_to_top":
            self.current_card_index = len(self.expected_cards) - 1 - index
        else:
            self.current_card_index = index
        
        self.first_scan_received = True
        self.state_changed.emit()
```

## Changes Made

### File: `src/app_state.py`

#### Change 1: Fixed scan side detection (Line ~295)
```python
elif self.card_type == CardType.QUARTER:
    # Position in tuple: 0=BL, 1=TL, 2=TR, 3=BR
    scan_sides = ["bottom_left", "top_left", "top_right", "bottom_right"]
    self.scan_side = scan_sides[position] if position < len(scan_sides) else "bottom_left"
```

#### Change 2: Fixed position_map for expected QR (Line ~324)
```python
elif self.card_type == CardType.QUARTER:
    position_map = {"bottom_left": 1, "top_left": 2, "top_right": 3, "bottom_right": 4}
    qr_position = position_map.get(self.scan_side, 1)
```

#### Change 3: Fixed position_map for side validation (Line ~344)
```python
elif self.card_type == CardType.QUARTER:
    position_map = {"bottom_left": 0, "top_left": 1, "top_right": 2, "bottom_right": 3}
    expected_position = position_map.get(self.scan_side, 0)
```

#### Change 4: Fixed position_map for skip resolution (Line ~717)
```python
elif self.card_type == CardType.QUARTER:
    position_map = {"bottom_left": 1, "top_left": 2, "top_right": 3, "bottom_right": 4}
    qr_position = position_map.get(self.scan_side, 1)
```

#### Change 5: Fixed set_start_index for scan direction (Line ~549)
```python
def set_start_index(self, index):
    """Set the start card index based on scan direction"""
    if 0 <= index < len(self.expected_cards):
        if self.scan_direction == "bottom_to_top":
            self.current_card_index = len(self.expected_cards) - 1 - index
        else:
            self.current_card_index = index
        
        self.first_scan_received = True
        self.state_changed.emit()
```

## Testing

All tests pass successfully:
- ✓ First scan correctly sets start card
- ✓ Works for both top-to-bottom and bottom-to-top
- ✓ Scan side correctly detected for all 4 corners
- ✓ Position mapping correct throughout codebase
- ✓ All edge cases handled

## Impact

### Before Fix
- First scan would show "NOT OK" for quarter cards
- Wrong scan side would be detected
- Subsequent scans would fail
- System unusable for quarter cards

### After Fix
- First scan correctly accepted as start card ✓
- Correct scan side detected ✓
- Subsequent scans work correctly ✓
- System fully functional for quarter cards ✓

## Files Modified
- `src/app_state.py` - 5 changes to fix position mapping and scan direction handling

## Files Created
- `test_first_scan_fix.py` - Comprehensive tests for first scan logic
- `FIRST_SCAN_BUG_FIX.md` - This documentation
- `QUARTER_CARD_SIDE_LOGIC_EXPLAINED.md` - Detailed explanation of quarter card logic

## Production Ready ✓
All bugs fixed and tested. Quarter card scanning now works correctly!
