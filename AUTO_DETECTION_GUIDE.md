# Auto-Detection Feature Guide

## Overview
The application now **automatically detects** the card type based on the file structure you load. No need to select the card type manually!

## How It Works

### 1. Start the Application
```bash
python main.py
```
- No card type selector dialog appears
- Application starts with Half Card as default

### 2. Load a File
When you load a file, the application:
1. **Analyzes the file headers**
2. **Detects the card type** automatically
3. **Updates the UI** to match the card type
4. **Shows a confirmation** message

### 3. UI Adapts Automatically
- Card details fields rebuild to show correct number of QR codes
- Preview window shows appropriate columns
- All features work with the detected card type

## Detection Logic

### Single Card Detection
**Triggers when file has:**
- TXT file (one QR per line)
- CSV/CPD with 2 columns: `NUMCARD` + one QR column
- Headers containing: `QR`

**Example:**
```csv
NUMCARD,QR
Card_001,QR1234567890
```

### Half Card Detection
**Triggers when file has:**
- CSV/CPD with 3 columns: `NUMCARD` + two QR columns
- Headers containing: `ICCID`, `IMSI`, `LEFT`, `RIGHT`

**Example:**
```csv
NUMCARD,ICCID,IMSI
Card_001,ICCID123,IMSI456
```

### Quarter Card Detection
**Triggers when file has:**
- CSV/CPD with 5 columns: `NUMCARD` + four QR columns
- Headers containing: `TL`, `TR`, `BL`, `BR` or `TOP_LEFT`, `TOP_RIGHT`, `BOTTOM_LEFT`, `BOTTOM_RIGHT`

**Example:**
```csv
NUMCARD,TL,TR,BL,BR
Card_001,TL_QR1,TR_QR1,BL_QR1,BR_QR1
```

## User Experience

### Loading Single Card File:
1. Click "📁 Load Sequence File"
2. Select `test_single_card.csv`
3. See message: **"Loaded 10 cards. Detected type: Single Card"**
4. Card details panel shows **1 QR field**
5. Preview shows **2 columns** (Card Number + QR Code)

### Loading Half Card File:
1. Click "📁 Load Sequence File"
2. Select `test_half_card.csv`
3. See message: **"Loaded 10 cards. Detected type: Half Card"**
4. Card details panel shows **2 QR fields**
5. Preview shows **3 columns** (Card Number + Left QR + Right QR)

### Switching Between Card Types:
1. Load a Single Card file → UI shows 1 QR field
2. Load a Half Card file → UI automatically rebuilds to show 2 QR fields
3. No restart needed!

## Benefits

### ✅ User-Friendly
- No confusing dialogs at startup
- No need to know card type in advance
- Just load your file and go!

### ✅ Flexible
- Switch between card types anytime
- Load different file types in same session
- UI adapts automatically

### ✅ Smart
- Analyzes file structure intelligently
- Handles various column naming conventions
- Falls back to Half Card if detection unclear

### ✅ Informative
- Shows detected card type in success message
- Updates status label when type changes
- Clear feedback at every step

## File Format Flexibility

The detection is **flexible** with column names:

### Single Card - Accepts:
- `QR`
- `QR_CODE`
- `QRCODE`

### Half Card - Accepts:
- `ICCID` and `IMSI`
- `LEFT` and `RIGHT`
- `LEFT_QR` and `RIGHT_QR`
- `QR1` and `QR2`

### Quarter Card - Accepts:
- `TL`, `TR`, `BL`, `BR`
- `TOP_LEFT`, `TOP_RIGHT`, `BOTTOM_LEFT`, `BOTTOM_RIGHT`
- `QR_TL`, `QR_TR`, `QR_BL`, `QR_BR`

## Edge Cases

### What if detection fails?
- **Defaults to Half Card** (most common type)
- You can still use the application
- Check your file format if issues occur

### What if file has unusual format?
- Detection looks for common patterns
- If unclear, assumes Half Card
- Ensure headers match expected patterns

### What if I load wrong file type?
- Detection will identify it correctly
- UI will adapt to actual file structure
- No manual intervention needed

## Testing

### Test Auto-Detection:
1. **Start with Single Card:**
   - Load `test_single_card.csv`
   - Verify: "Detected type: Single Card"
   - Check: 1 QR field in card details

2. **Switch to Half Card:**
   - Load `test_half_card.csv`
   - Verify: "Detected type: Half Card"
   - Check: 2 QR fields in card details
   - Notice: Fields rebuilt automatically!

3. **Back to Single Card:**
   - Load `test_single_card.csv` again
   - Verify: UI switches back to 1 QR field

## Technical Details

### Detection Process:
1. Open file and read first line (headers)
2. Parse headers based on delimiter (`,` or `;`)
3. Count QR-related columns
4. Match against known patterns
5. Return detected CardType enum
6. Update app_state.card_type
7. Emit card_type_changed signal
8. UI components rebuild automatically

### Signals:
- `card_type_changed(CardType)` - Emitted when type changes
- Connected to `rebuild_card_details_fields()` in FileManagementWindow
- Triggers dynamic UI updates

## Comparison: Before vs After

### Before (Manual Selection):
1. Start app → See dialog
2. Choose card type → Click Continue
3. Load file → Hope it matches!
4. Wrong type? → Restart app

### After (Auto-Detection):
1. Start app → Ready to go
2. Load file → Type detected automatically
3. UI adapts → Perfect match!
4. Different file? → Just load it!

## Troubleshooting

### Issue: "Detected type: Half Card" but I have Single Card file
**Cause:** File headers don't match Single Card patterns
**Solution:** Ensure file has only 2 columns: `NUMCARD,QR`

### Issue: UI doesn't update after loading file
**Cause:** Signal not connected properly
**Solution:** Restart application

### Issue: Wrong number of QR fields shown
**Cause:** Detection defaulted to Half Card
**Solution:** Check file format matches expected structure

## Future Enhancements

Possible improvements:
- Show card type indicator in main window status bar
- Add manual override option in settings
- Support custom column name mapping
- Detect card type from file content (not just headers)

## Summary

**Auto-detection makes the application:**
- ✅ Easier to use
- ✅ More flexible
- ✅ Less error-prone
- ✅ More intelligent

**No more guessing!** Just load your file and let the app figure it out. 🎯
