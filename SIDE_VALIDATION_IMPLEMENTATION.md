# Side Validation Implementation

## Overview
The system now enforces **strict side validation** for Half and Quarter card types. Once scanning starts on a particular side (e.g., "Left" for half cards or "Top-Left" for quarter cards), the system will ONLY accept QR codes from that same side throughout the entire scanning session.

## How It Works

### 1. Side Detection on First Scan
When you scan the first card, the system automatically detects which side you're scanning:
- **Half Cards**: Detects "Left" or "Right"
- **Quarter Cards**: Detects "Top-Left", "Top-Right", "Bottom-Left", or "Bottom-Right"
- **Single Cards**: No side detection needed (only one QR per card)

### 2. Side Enforcement During Scanning
After the first scan establishes the side, all subsequent scans must be from the SAME side:

#### Example: Half Card (Left Side)
```
✓ Scan QR_1_LEFT  → OK
✓ Scan QR_2_LEFT  → OK
✗ Scan QR_3_RIGHT → NOT OK (Wrong Side: Right)
✓ Scan QR_3_LEFT  → OK
```

#### Example: Quarter Card (Top-Left Side)
```
✓ Scan QR_1_TL → OK
✗ Scan QR_2_TR → NOT OK (Wrong Side: Top-Right)
✗ Scan QR_2_BL → NOT OK (Wrong Side: Bottom-Left)
✗ Scan QR_2_BR → NOT OK (Wrong Side: Bottom-Right)
✓ Scan QR_2_TL → OK
```

### 3. Skip Detection with Side Validation
The skip/jump feature now also respects side validation:

**Scenario**: Scanning Left side, currently at card 2
- Scan `QR_5_RIGHT` → ✗ NOT OK (Wrong Side: Right) - No skip prompt
- Scan `QR_5_LEFT` → ⚠ Skip prompt appears (correct side, 3 cards ahead)

**Key Point**: You can only skip to cards on the SAME side you're scanning.

## Error Messages

The system provides clear error messages when wrong sides are scanned:

### Half Cards
- `NOT OK (Wrong Side: Left)` - You scanned a Left QR when expecting Right
- `NOT OK (Wrong Side: Right)` - You scanned a Right QR when expecting Left

### Quarter Cards
- `NOT OK (Wrong Side: Top-Left)` - You scanned Top-Left when expecting another side
- `NOT OK (Wrong Side: Top-Right)` - You scanned Top-Right when expecting another side
- `NOT OK (Wrong Side: Bottom-Left)` - You scanned Bottom-Left when expecting another side
- `NOT OK (Wrong Side: Bottom-Right)` - You scanned Bottom-Right when expecting another side

## Benefits

1. **Prevents Confusion**: Users can't accidentally mix sides during scanning
2. **Clear Feedback**: Immediate notification when wrong side is scanned
3. **Consistent Workflow**: Once you start on a side, you stay on that side
4. **Skip Safety**: Skip/jump feature only works with correct side QR codes

## Technical Implementation

The validation works by:
1. Storing the QR position (0, 1, 2, or 3) along with the card index in `qr_to_index`
2. Comparing the scanned QR's position with the expected position based on `scan_side`
3. Rejecting any QR codes that don't match the expected position
4. Only allowing skip prompts for QR codes from the correct side

## Code Location
- Implementation: `src/app_state.py` → `handle_main_scan()` method (lines ~330-370)
- Position mapping stored in: `qr_to_index` dictionary
- Side tracking: `self.scan_side` attribute
