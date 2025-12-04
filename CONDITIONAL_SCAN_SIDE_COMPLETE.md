# Conditional Scan Side Display - Complete! ✅

## Summary

Updated the UI to **conditionally show scan side** based on card type:
- **Single Card**: No scan side column (only 1 QR, sides don't matter)
- **Half Card**: Shows scan side column (Left/Right matters)
- **Quarter Card**: Shows scan side column (TL/TR/BL/BR matters)

## Rationale

### Single Card:
- Only 1 QR code per card
- No concept of "sides" or "corners"
- Scan side is always "Single"
- Showing it is redundant and confusing

### Half Card:
- 2 QR codes per card (Left/Right)
- User needs to know which side they're scanning
- Scan side helps verify consistency
- Important for troubleshooting

### Quarter Card:
- 4 QR codes per card (TL/TR/BL/BR)
- User needs to know which corner they're scanning
- Scan side is critical information
- Essential for proper validation

## Changes Made

### 1. Scanner Logging Window (`src/ui/scanner_logging.py`)

**Added Methods:**
- `setup_log_table_columns()` - Sets up columns based on card type
- `rebuild_log_table()` - Rebuilds table when card type changes

**Dynamic Column Count:**
```python
# Single Card
Columns: 5 (Entry #, Time, Scanned ID, Expected ID, Result)

# Half/Quarter Card
Columns: 6 (Entry #, Time, Scanned ID, Expected ID, Result, Scan Side)
```

**Connected Signal:**
- `card_type_changed` → `rebuild_log_table()`
- Automatically rebuilds when card type changes

### 2. Log Export (`src/ui/file_management.py`)

**Conditional CSV Fields:**
```python
# Single Card CSV
index,timestamp,scanned_code,expected_code,status

# Half/Quarter Card CSV
index,timestamp,scanned_code,expected_code,status,scanned_side
```

**Dynamic Export:**
- Checks `app_state.card_type`
- Includes `scanned_side` only for Half/Quarter
- Cleaner exports for Single Card

## User Experience

### Single Card:
```
Scanner Log:
| Entry # | Time        | Scanned ID   | Expected ID  | Result |
|---------|-------------|--------------|--------------|--------|
| Card_001| 12:34:56.789| QR123456     | QR123456     | OK     |
```
**Clean and simple** - No unnecessary columns

### Half Card:
```
Scanner Log:
| Entry # | Time        | Scanned ID   | Expected ID  | Result | Scan Side |
|---------|-------------|--------------|--------------|--------|-----------|
| Card_001| 12:34:56.789| ICCID123     | ICCID123     | OK     | Left      |
| Card_002| 12:34:57.123| ICCID234     | ICCID234     | OK     | Left      |
```
**Informative** - Shows which side is being scanned

### Quarter Card:
```
Scanner Log:
| Entry # | Time        | Scanned ID   | Expected ID  | Result | Scan Side  |
|---------|-------------|--------------|--------------|--------|------------|
| Card_001| 12:34:56.789| TL_QR123     | TL_QR123     | OK     | Top-Left   |
| Card_002| 12:34:57.123| TL_QR234     | TL_QR234     | OK     | Top-Left   |
```
**Essential** - Shows which corner is being scanned

## Technical Implementation

### Column Setup:
```python
def setup_log_table_columns(self):
    if self.app_state.card_type == CardType.SINGLE:
        # 5 columns without scan side
        self.log_table.setColumnCount(5)
        headers = ["Entry #", "Time", "Scanned ID", "Expected ID", "Result"]
    else:  # Half or Quarter
        # 6 columns with scan side
        self.log_table.setColumnCount(6)
        headers = ["Entry #", "Time", "Scanned ID", "Expected ID", "Result", "Scan Side"]
```

### Display Logic:
```python
def display_current_page(self):
    # ... populate first 5 columns ...
    
    # Add scan side only for Half/Quarter
    if self.app_state.card_type != CardType.SINGLE:
        self.log_table.setItem(row, 5, QTableWidgetItem(log_entry["scanned_side"]))
```

### Export Logic:
```python
def download_logs(self):
    if self.app_state.card_type == CardType.SINGLE:
        fieldnames = ['index', 'timestamp', 'scanned_code', 'expected_code', 'status']
    else:
        fieldnames = ['index', 'timestamp', 'scanned_code', 'expected_code', 'status', 'scanned_side']
```

## Benefits

### For Single Card Users:
- ✅ **Cleaner UI** - No confusing "Single" column
- ✅ **Simpler logs** - Only relevant information
- ✅ **Smaller CSV files** - One less column
- ✅ **Better UX** - No redundant data

### For Half/Quarter Card Users:
- ✅ **Important info visible** - Know which side/corner
- ✅ **Easier troubleshooting** - See scan pattern
- ✅ **Verify consistency** - Ensure same side scanned
- ✅ **Complete logs** - All relevant data exported

## Automatic Adaptation

### When Loading Files:
1. **Load Single Card file**:
   - Card type detected: Single
   - Log table rebuilds: 5 columns
   - No scan side shown

2. **Load Half Card file**:
   - Card type detected: Half
   - Log table rebuilds: 6 columns
   - Scan side shown (Left/Right)

3. **Load Quarter Card file**:
   - Card type detected: Quarter
   - Log table rebuilds: 6 columns
   - Scan side shown (TL/TR/BL/BR)

### Seamless Switching:
```
User: Loads test_single_card.csv
App: Rebuilds table → 5 columns

User: Loads test_half_card.csv
App: Rebuilds table → 6 columns (adds Scan Side)

User: Loads test_quarter_card.csv
App: Keeps 6 columns (updates Scan Side labels)

User: Loads test_single_card.csv again
App: Rebuilds table → 5 columns (removes Scan Side)
```

## Testing

### Test Single Card:
1. Load `test_single_card.csv`
2. Check log table: **5 columns** (no Scan Side)
3. Scan some cards
4. Export logs: CSV has **5 fields** (no scanned_side)
5. ✅ Clean and simple

### Test Half Card:
1. Load `test_half_card.csv`
2. Check log table: **6 columns** (with Scan Side)
3. Scan some cards
4. Verify Scan Side shows "Left" or "Right"
5. Export logs: CSV has **6 fields** (includes scanned_side)
6. ✅ Informative and complete

### Test Quarter Card:
1. Load `test_quarter_card.csv`
2. Check log table: **6 columns** (with Scan Side)
3. Scan some cards
4. Verify Scan Side shows "Top-Left", "Top-Right", etc.
5. Export logs: CSV has **6 fields** (includes scanned_side)
6. ✅ Essential information visible

### Test Switching:
1. Load Single → 5 columns
2. Load Half → 6 columns
3. Load Quarter → 6 columns
4. Load Single → 5 columns
5. ✅ Smooth transitions

## Comparison

### Before (All Types Same):
| Card Type | Columns | Scan Side Column |
|-----------|---------|------------------|
| Single    | 5       | ❌ Hidden        |
| Half      | 5       | ❌ Hidden        |
| Quarter   | 5       | ❌ Hidden        |

### After (Conditional):
| Card Type | Columns | Scan Side Column |
|-----------|---------|------------------|
| Single    | 5       | ❌ Not shown (not needed) |
| Half      | 6       | ✅ Shown (Left/Right) |
| Quarter   | 6       | ✅ Shown (TL/TR/BL/BR) |

## Backend

### Scan Side Still Tracked:
- ✅ All card types track scan side internally
- ✅ Used for validation logic
- ✅ Stored in log_data
- ✅ Just conditionally displayed

### Validation Logic Unchanged:
- Single: Validates against single QR
- Half: Validates against left or right QR
- Quarter: Validates against TL/TR/BL/BR QR
- All based on detected scan side

## CSV Export Examples

### Single Card Export:
```csv
index,timestamp,scanned_code,expected_code,status
Card_001,'12:34:56.789','QR123','QR123',OK
Card_002,'12:34:57.123','QR234','QR234',OK
```

### Half Card Export:
```csv
index,timestamp,scanned_code,expected_code,status,scanned_side
Card_001,'12:34:56.789','ICCID123','ICCID123',OK,Left
Card_002,'12:34:57.123','ICCID234','ICCID234',OK,Left
```

### Quarter Card Export:
```csv
index,timestamp,scanned_code,expected_code,status,scanned_side
Card_001,'12:34:56.789','TL_QR123','TL_QR123',OK,Top-Left
Card_002,'12:34:57.123','TL_QR234','TL_QR234',OK,Top-Left
```

## Conclusion

**Conditional scan side display is complete!** 🎉

### Smart UI:
- Shows scan side only when it matters
- Adapts automatically to card type
- Cleaner for Single Card
- Informative for Half/Quarter Card

### Benefits:
- ✅ Better UX for each card type
- ✅ No redundant information
- ✅ Essential info always visible
- ✅ Automatic adaptation

### Result:
- Single Card users: Clean, simple interface
- Half/Quarter Card users: Complete, informative logs
- Everyone: Appropriate level of detail

**Status**: Production ready with intelligent, context-aware UI! 🚀
