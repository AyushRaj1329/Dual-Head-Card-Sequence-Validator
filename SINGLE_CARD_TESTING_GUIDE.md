# Single Card Type - Testing Guide

## What's Been Implemented

We've successfully implemented support for **Single Card** and **Half Card** types as a proof of concept. The application now:

1. **Shows a card type selector** at startup
2. **Dynamically adapts** the UI based on selected card type
3. **Parses files** correctly for both card types
4. **Validates scans** using the appropriate QR code structure

## Changes Made

### Core Files Updated:
- ✅ `src/card_types.py` - Card type enum and utilities
- ✅ `src/ui/card_type_selector.py` - Startup dialog
- ✅ `main.py` - Shows selector before app launch
- ✅ `src/app_state.py` - Unified QR lookup system
- ✅ `src/services/utilities.py` - Dynamic file parsing
- ✅ `src/logic/file_parser.py` - Passes card type to parsers
- ✅ `src/ui/file_management.py` - Dynamic QR fields

### Key Improvements:
1. **Unified QR Lookup**: Replaced separate `left_qr_to_index` and `right_qr_to_index` with a single `qr_to_index` dictionary that stores `(index, position)` tuples
2. **Dynamic UI**: Card details section now shows 1 or 2 QR fields based on card type
3. **Smart Scanning**: First scan automatically detects card type and scan position

## Testing Steps

### Test 1: Single Card Type

1. **Start the application**
   ```bash
   python main.py
   ```

2. **Select "Single Card"** in the card type dialog

3. **Load the test file**:
   - Go to File Management window
   - Click "📁 Load Sequence File"
   - Select `test_single_card.csv`
   - Should see: "Loaded 10 cards."

4. **Preview the file**:
   - Click "👁 Preview Sequence"
   - Should see 2 columns: "Card Number" and "QR Code"
   - Verify all 10 cards are displayed

5. **Test Card Details**:
   - Click "Scan Card Details"
   - Manually enter a QR code (e.g., `QR1234567890`)
   - Should see:
     - Card Number: Card_001
     - QR Code: QR1234567890
     - Position: 1 of 10

6. **Test Scanning** (if you have a scanner):
   - Go to Scanner & Logging window
   - Click "Start Validation"
   - Scan the first card (QR1234567890)
   - Should automatically set as start card
   - Continue scanning in sequence
   - Verify "OK" status for correct scans

### Test 2: Half Card Type (Existing Functionality)

1. **Restart the application**

2. **Select "Half Card (Default)"** in the card type dialog

3. **Load the test file**:
   - Load `test_half_card.csv`
   - Should see: "Loaded 10 cards."

4. **Preview the file**:
   - Should see 3 columns: "Card Number", "Left QR (ICCID)", "Right QR (IMSI)"

5. **Test Card Details**:
   - Scan a card
   - Should see 2 QR fields populated

6. **Test Scanning**:
   - Start validation
   - First scan sets start card and detects left/right side
   - Continue scanning

### Test 3: File Format Compatibility

Test with different file formats:

#### Single Card - TXT Format
Create `test_single.txt`:
```
QR1234567890
QR2345678901
QR3456789012
```
- Should load successfully
- Card numbers auto-generated as Card_1, Card_2, etc.

#### Single Card - CPD Format
Create `test_single.cpd`:
```
NUMCARD;QR
Card_1;QR1234567890
Card_2;QR2345678901
```
- Should parse correctly

## Expected Behavior

### Single Card Mode:
- **Scan Side**: Always "Single" (no left/right distinction)
- **QR Fields**: 1 field in card details
- **Preview Columns**: 2 (Card Number + QR Code)
- **Validation**: Compares scanned code to single QR per card

### Half Card Mode:
- **Scan Side**: "Left" or "Right" (auto-detected on first scan)
- **QR Fields**: 2 fields in card details
- **Preview Columns**: 3 (Card Number + Left QR + Right QR)
- **Validation**: Compares to appropriate side based on first scan

## Known Limitations

### Not Yet Implemented:
- ❌ Quarter Card type (4 QR codes)
- ❌ Ability to change card type after startup (requires app restart)
- ❌ Card type indicator in main window status

### Current Behavior:
- Card type is selected once at startup
- Cached for next session
- All loaded files must match the selected card type

## Troubleshooting

### Issue: "Card not found in file"
- **Cause**: QR code doesn't match any in the loaded file
- **Solution**: Verify QR code format matches file exactly

### Issue: Preview shows wrong number of columns
- **Cause**: File format doesn't match selected card type
- **Solution**: Restart app and select correct card type

### Issue: Scan side not detected
- **Cause**: First scanned card not in sequence
- **Solution**: Scan a card that exists in the loaded file

## Next Steps

To add Quarter Card support:
1. Update `handle_main_scan()` to handle 4 positions
2. Add scan side labels for top_left, top_right, bottom_left, bottom_right
3. Update UI to show 4 QR fields
4. Create test files with 4 QR codes per card
5. Test thoroughly

## File Format Reference

### Single Card CSV:
```csv
NUMCARD,QR
Card_001,QR_CODE_HERE
```

### Half Card CSV:
```csv
NUMCARD,ICCID,IMSI
Card_001,LEFT_QR_HERE,RIGHT_QR_HERE
```

### Quarter Card CSV (Future):
```csv
NUMCARD,TL,TR,BL,BR
Card_001,TL_QR,TR_QR,BL_QR,BR_QR
```

## Success Criteria

✅ Single card type can be selected at startup
✅ Single card files load correctly
✅ Preview shows correct columns for card type
✅ Card details display correct number of QR fields
✅ Scanning works with single QR per card
✅ Half card type still works (backward compatibility)
✅ Cache remembers card type selection

## Support

If you encounter issues:
1. Check the console for error messages
2. Verify file format matches card type
3. Restart application and reselect card type
4. Check that test files are in correct format
