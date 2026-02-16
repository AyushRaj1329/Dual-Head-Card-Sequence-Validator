# File Management Dual Head - Implementation Complete

## Overview
Successfully implemented split-view File Management window for dual-head operation with ALL on-demand scanner functions.

## Features Implemented

### Split View Layout
- **Left Panel**: Head B (Blue label)
- **Right Panel**: Head A (Green label)
- **Equal Width**: 50/50 split
- **Vertical Separator**: Visual divider

### File Operations (Both Heads)
Each head has independent:
1. **Load Sequence File**
   - Browse and select .cpd/.txt/.csv files
   - Card type selector dialog
   - Handles unsaved log data
   - Independent file loading

2. **Scan Direction Toggle**
   - Top → Bottom (normal order)
   - Bottom → Top (reverse order)
   - Cannot change during active scanning
   - Saved per head

3. **Preview Sequence**
   - View loaded card data in table
   - Shows all QR codes based on card type
   - Separate preview per head

4. **Clear Sequence**
   - Clears loaded file
   - Stops scanning if active

### Sequence Control Tools (Both Heads)

#### 1. Scan Card Details
- **Purpose**: View information about a specific card
- **How it works**:
  1. Click "Scan Card" button
  2. Scan any card with on-demand scanner
  3. Displays:
     - Card Number
     - All QR codes (based on card type)
     - Position in sequence
- **Cancel button**: Stop waiting for scan
- **Status updates**: Real-time feedback

#### 2. Count Card Range
- **Purpose**: Count number of cards between two scanned cards
- **How it works**:
  1. Click "Count Range" button
  2. Scan FIRST card
  3. Scan LAST card
  4. Displays:
     - First card QR code
     - Last card QR code
     - Total count between them
- **Cancel button**: Stop waiting for scan
- **Error handling**: Validates card order

### Log Management (Both Heads)
Each head has independent:
1. **Export Logs**
   - Save to CSV file
   - Includes all validation data
   - Filename includes head ID and timestamp
   - Auto-clears after export

2. **Clear Logs**
   - Confirmation dialog
   - Clears all validation logs

3. **Statistics Display**
   - Total Scans
   - Successful Scans (OK)
   - Failed Scans (NOT OK)
   - Skipped Entries
   - Real-time updates

## On-Demand Scanner Functions

### ✅ Scan Card Details
- **Status**: IMPLEMENTED for both heads
- **Location**: Sequence Control Tools section
- **Features**:
  - Scan any card to view its information
  - Shows card number, all QR codes, and position
  - Works independently for each head
  - Cancel button to stop scanning
  - Real-time status updates

### ✅ Count Card Range
- **Status**: IMPLEMENTED for both heads
- **Location**: Sequence Control Tools section
- **Features**:
  - Scan first and last card to count range
  - Displays first card, last card, and total count
  - Works independently for each head
  - Cancel button to stop scanning
  - Error validation (last card must come after first)

## Technical Implementation

### Dynamic Widget Creation
Uses `setattr()` and `getattr()` pattern:
```python
# Create widget for specific head
setattr(self, f'scan_card_details_btn_{head_id}', button)

# Access widget for specific head
button = getattr(self, f'scan_card_details_btn_{head_id}')
```

### Signal Connections
```python
# Head A signals
self.head_a.start_card_scan_complete.connect(
    lambda msg, success: self.handle_start_card_scan_complete('A', msg, success)
)
self.head_a.card_count_update.connect(
    lambda type, msg: self.handle_card_count_update('A', type, msg)
)
self.head_a.ondemand_scan_status_update.connect(
    lambda status, msg: self.handle_ondemand_scan_status('A', status, msg)
)

# Head B signals (same pattern)
```

### Card Type Handling
- Dynamic QR fields based on card type
- Rebuilds fields when card type changes
- Supports Single, Half, and Quarter cards
- Independent card types per head

## Usage Examples

### Head A: Load File and Scan Card Details
1. Click "📁 Load Sequence File" on right panel
2. Select file and choose card type
3. Ensure on-demand scanner is configured (Network Setup)
4. Click "Scan Card" in Sequence Control Tools
5. Scan any card with on-demand scanner
6. View card information in fields

### Head B: Count Card Range
1. Load file on left panel
2. Click "Count Range" in Sequence Control Tools
3. Scan FIRST card
4. Scan LAST card
5. View count in Total field

### Both Heads: Independent Operation
- Head A can be loading a file while Head B is counting cards
- Each head maintains its own state
- No interference between heads
- Separate logs and statistics

## File Structure
```
src/ui/file_management_dual.py  (NEW - 500+ lines)
  ├── FileManagementWindow class
  ├── create_split_panels()
  ├── create_head_panel(head_id, title)
  ├── create_file_operations_section(head_id)
  ├── create_sequence_tools_section(head_id)
  │   ├── Scan Card Details subsection
  │   └── Count Card Range subsection
  ├── create_log_management_section(head_id)
  ├── File operation methods (select, clear, preview, toggle direction)
  ├── On-demand scanner methods (scan details, count range, cancel)
  ├── Log management methods (export, clear)
  ├── Signal handlers (card scan complete, count update, status update)
  └── UI update methods
```

## Testing Checklist

- [x] Window opens without errors
- [x] Split view displays correctly
- [x] Head A panel on right (green label)
- [x] Head B panel on left (blue label)
- [x] File loading works independently
- [x] Scan direction toggle works per head
- [x] Preview shows correct data per head
- [x] Clear file works per head
- [x] Scan Card Details works for both heads
- [x] Count Card Range works for both heads
- [x] Cancel buttons work correctly
- [x] Status updates show correct head
- [x] Log export works independently
- [x] Log clear works independently
- [x] Statistics update correctly
- [x] Card type changes rebuild fields
- [x] Theme changes apply correctly

## Next Steps

1. ✅ Network Setup Window - COMPLETE
2. ✅ File Management Window - COMPLETE (with on-demand functions)
3. ⏳ Scanner Logging Window - Split view for live validation logs

## Notes

- Window minimum size: 1400x800 pixels
- Recommended size: 1600x900 pixels
- All on-demand scanner functions preserved and working
- Each head operates completely independently
- Separate files, logs, and statistics per head
- On-demand scanner must be configured in Network Setup before using sequence tools
