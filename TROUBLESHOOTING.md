# Troubleshooting Guide

## UI Issues

### Problem: UI fields overlapping after loading file
**Status**: ✅ FIXED

**Cause**: When card type changed, old widgets weren't properly removed from grid layout before adding new ones.

**Solution**: Updated `rebuild_card_details_fields()` to:
1. Clear entire grid layout using `takeAt(0)` and `deleteLater()`
2. Rebuild all fields from scratch
3. Recreate all widget references

**How to verify fix**:
1. Start application
2. Load `test_single_card.csv` → Should show 1 QR field cleanly
3. Load `test_half_card.csv` → Should show 2 QR fields cleanly
4. Load `test_single_card.csv` again → Should show 1 QR field cleanly
5. No overlapping should occur

---

## Detection Issues

### Problem: Wrong card type detected
**Possible Causes**:
1. File headers don't match expected patterns
2. Delimiter not recognized (using `,` instead of `;` or vice versa)
3. Column names are non-standard

**Solutions**:
1. Check file headers match patterns:
   - Single: `NUMCARD,QR`
   - Half: `NUMCARD,ICCID,IMSI` or `NUMCARD,LEFT,RIGHT`
   - Quarter: `NUMCARD,TL,TR,BL,BR`

2. Ensure proper delimiter:
   - CSV files: use `,`
   - CPD files: use `;`

3. Use standard column names (case-insensitive):
   - Single: QR, QR_CODE, QRCODE
   - Half: ICCID/IMSI, LEFT/RIGHT
   - Quarter: TL/TR/BL/BR, TOP_LEFT/TOP_RIGHT/BOTTOM_LEFT/BOTTOM_RIGHT

### Problem: Always defaults to Half Card
**Cause**: Detection couldn't determine card type from headers

**Solution**: 
1. Verify file has proper headers in first line
2. Check column count matches card type
3. Ensure headers contain recognizable keywords

---

## File Loading Issues

### Problem: "Error loading file"
**Possible Causes**:
1. File format not supported
2. File encoding issues
3. Malformed data

**Solutions**:
1. Use supported formats: `.csv`, `.txt`, `.cpd`
2. Ensure UTF-8 encoding
3. Check for:
   - Missing columns
   - Empty rows
   - Special characters in data

### Problem: "Loaded 0 cards"
**Cause**: File has headers but no data rows

**Solution**: Add data rows after header line

---

## Scanning Issues

### Problem: "NOT IN SEQUENCE" on first scan
**Cause**: Scanned QR code not found in loaded file

**Solutions**:
1. Verify QR code matches exactly (case-sensitive)
2. Check file contains the scanned QR code
3. Ensure no extra spaces or characters

### Problem: Scan side not detected correctly
**Cause**: First scanned card determines scan side

**Solution**: 
- For Half Card: Scan the same side (left or right) consistently
- For Single Card: No scan side needed
- First scan sets the pattern for the session

---

## UI Update Issues

### Problem: Card details fields don't update after loading file
**Cause**: Signal not connected or rebuild method not called

**Solutions**:
1. Restart application
2. Check console for errors
3. Verify `card_type_changed` signal is emitted

### Problem: Preview window shows wrong columns
**Cause**: Preview created before card type updated

**Solution**: Close and reopen preview window after loading file

---

## Performance Issues

### Problem: Slow file loading
**Possible Causes**:
1. Very large file (>10,000 cards)
2. Complex file parsing

**Solutions**:
1. Split large files into smaller batches
2. Use CSV format (faster than CPD)
3. Remove unnecessary columns

### Problem: UI freezes during file load
**Cause**: Large file being parsed on main thread

**Solution**: Wait for parsing to complete (usually < 1 second for normal files)

---

## Cache Issues

### Problem: Wrong card type persists after restart
**Cause**: Card type cached from previous session

**Solution**: Load a new file - card type will be auto-detected and updated

### Problem: Old file path shown but file not loaded
**Cause**: Cached file path but file moved/deleted

**Solution**: Load file again from new location

---

## Testing Issues

### Problem: Test files not working
**Possible Causes**:
1. Test files not in correct location
2. Test files modified incorrectly

**Solutions**:
1. Ensure test files in root directory:
   - `test_single_card.csv`
   - `test_half_card.csv`

2. Verify file contents match expected format

3. Recreate test files if needed:

**test_single_card.csv**:
```csv
NUMCARD,QR
Card_001,QR1234567890
Card_002,QR2345678901
```

**test_half_card.csv**:
```csv
NUMCARD,ICCID,IMSI
Card_001,ICCID1234567890,IMSI1234567890
Card_002,ICCID2345678901,IMSI2345678901
```

---

## Common Error Messages

### "Unsupported file type"
**Cause**: File extension not `.csv`, `.txt`, or `.cpd`

**Solution**: Convert file to supported format

### "CSV file must contain 'NUMCARD' column"
**Cause**: Missing NUMCARD column in CSV

**Solution**: Add NUMCARD as first column

### "Card type detection failed"
**Cause**: Exception during header analysis

**Solution**: Check file format, defaults to Half Card

---

## Debug Mode

### Enable Console Logging
To see detailed detection information:

1. Check console output when loading files
2. Look for: "Card type detection failed" messages
3. Verify detected card type in success message

### Manual Testing
Test detection manually:
```python
from src.logic.file_parser import detect_card_type_from_file
from src.card_types import CardType

card_type = detect_card_type_from_file("your_file.csv")
print(f"Detected: {card_type}")
```

---

## Getting Help

If issues persist:

1. **Check Documentation**:
   - `AUTO_DETECTION_GUIDE.md` - Detection details
   - `QUICK_START.md` - Basic usage
   - `IMPLEMENTATION_SUMMARY.md` - Technical details

2. **Verify Setup**:
   - Python version: 3.8+
   - PyQt6 installed
   - All dependencies from `requirements.txt`

3. **Test with Sample Files**:
   - Use provided test files first
   - Verify they work before using custom files

4. **Check Console**:
   - Look for error messages
   - Note any exceptions
   - Check file paths

---

## Quick Fixes

### Reset Everything
1. Close application
2. Delete cache file: `~/.local/share/CardSequenceValidator/app_cache.json` (Linux/Mac) or `%APPDATA%\YourCompany\CardSequenceValidator\app_cache.json` (Windows)
3. Restart application
4. Load file fresh

### Force Rebuild UI
1. Load a different card type file
2. Load original file again
3. UI will rebuild automatically

### Verify Installation
```bash
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"
python -c "from src.card_types import CardType; print('Card types OK')"
python -c "from src.logic.file_parser import detect_card_type_from_file; print('Parser OK')"
```

All should print "OK" without errors.
