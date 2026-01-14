# Card Type Implementation Plan

## Overview
Implement support for three card types in a single application:
1. **Single Card**: 1 QR code per card
2. **Half Card**: 2 QR codes per card (Left/Right or ICCID/IMSI) - **Current Default**
3. **Quarter Card**: 4 QR codes per card (Bottom-Left, Top-Left, Top-Right, Bottom-Right)

## Implementation Status

### ✅ Completed
1. Created `src/card_types.py` - Enum and utility functions for card types
2. Created `src/ui/card_type_selector.py` - Dialog for selecting card type at startup
3. Updated `main.py` - Shows card type selector before app starts
4. Updated `src/services/utilities.py` - File parsers now support all three card types
5. Updated `src/logic/file_parser.py` - Passes card type to parsers
6. Updated `src/app_state.py` (partial):
   - Added card_type parameter to __init__
   - Changed from separate left/right dictionaries to unified qr_to_index
   - Updated load_file() to build dynamic QR lookups
   - Updated clear_file() to use new structure
   - Updated cache save/load for card type

### 🔄 In Progress - Need to Complete

#### 1. Update `src/app_state.py` - handle_main_scan()
Current code assumes left/right QR codes. Need to:
- Use `qr_to_index` instead of `left_qr_to_index` and `right_qr_to_index`
- Get scan position from qr_to_index lookup: `(index, position)`
- Update scan_side logic to work with all card types
- Handle expected QR based on current scan_side position

#### 2. Update `src/app_state.py` - process_start_card_scan()
- Use `qr_to_index` for lookup
- Display all QR codes based on card type
- Format message with appropriate labels

#### 3. Update `src/app_state.py` - process_count_card methods
- Use `qr_to_index` for lookups
- Handle all card types

#### 4. Update `src/app_state.py` - _perform_mismatch_resolution()
- Use dynamic QR position instead of hardcoded left/right

#### 5. Update UI Files

##### `src/ui/file_management.py`
- Update card details fields to be dynamic based on card type
- Show 1, 2, or 4 QR fields depending on card type
- Update labels using `CardType.get_qr_labels()`

##### `src/ui/scanner_logging.py`
- Update display to show current scan position
- Handle different scan sides for each card type

##### `src/ui/com_port_setup.py`
- No changes needed (card type agnostic)

##### `src/ui/main_application.py`
- Possibly show card type in system status
- No major changes needed

#### 6. Update Preview Window
- `src/ui/file_management.py` - PreviewWindow class
- Dynamic columns based on card type
- Use `CardType.get_qr_labels()` for headers

## File Format Examples

### Single Card CSV
```csv
NUMCARD,QR
Card_1,QR123456789
Card_2,QR987654321
```

### Half Card CSV (Current)
```csv
NUMCARD,ICCID,IMSI
Card_1,ICCID123,IMSI456
Card_2,ICCID789,IMSI012
```

### Quarter Card CSV
```csv
NUMCARD,TL,TR,BL,BR
Card_1,TL_QR1,TR_QR1,BL_QR1,BR_QR1
Card_2,TL_QR2,TR_QR2,BL_QR2,BR_QR2
```

## Scan Side Mapping

### Single Card
- scan_side: "single"
- Position index: 0

### Half Card
- scan_side: "left" → Position index: 0
- scan_side: "right" → Position index: 1

### Quarter Card
- scan_side: "top_left" → Position index: 0
- scan_side: "top_right" → Position index: 1
- scan_side: "bottom_left" → Position index: 2
- scan_side: "bottom_right" → Position index: 3

## Next Steps

1. Complete app_state.py updates for all scanning methods
2. Update UI files to be dynamic
3. Test with sample files for each card type
4. Update documentation
5. Create sample files for testing

## Testing Checklist

- [ ] Single card file loading
- [ ] Half card file loading (existing functionality)
- [ ] Quarter card file loading
- [ ] Scanning with single card
- [ ] Scanning with half card
- [ ] Scanning with quarter card
- [ ] Card details display for all types
- [ ] Count card range for all types
- [ ] Preview window for all types
- [ ] Log export for all types
- [ ] Cache persistence of card type
