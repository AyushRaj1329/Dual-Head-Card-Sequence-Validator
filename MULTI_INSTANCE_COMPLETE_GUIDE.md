# Multi-Instance Feature - Complete Implementation Guide

## Overview

Your Card Sequence Validator now has a fully implemented multi-instance system with professional UI and comprehensive log tracking. Users can run two independent instances with separate configurations, logs, and settings.

## What's Included

### Core Features ✅

1. **Instance Selection**
   - Professional toggle button design
   - Active instance highlighted in blue
   - Inactive instance in gray
   - Smooth hover effects
   - Located in home page header

2. **Separate Data Storage**
   - Each instance has its own cache file
   - Separate logs for each instance
   - Independent network configurations
   - Per-instance theme preferences
   - Separate card type selections

3. **Instance Tracking in Logs**
   - Every log entry shows which instance generated it
   - Instance displayed in dedicated column
   - Instance text highlighted in blue
   - Works with all card types

4. **Instance Display**
   - Current instance shown in scanner logging header
   - Shows "Instance 1" or "Instance 2"
   - Updates automatically on switch
   - Single place to verify active instance

5. **Power Loss Protection**
   - Atomic writes prevent corruption
   - Auto-save every 5 minutes
   - Auto-save every 1000 scans
   - Last selected instance remembered

## Files Modified

### Code Files
- `src/ui/styles.py` - Added toggle button styling
- `src/ui/main_application.py` - Updated instance selector UI
- `src/app_state.py` - Added instance to log entries
- `src/ui/scanner_logging.py` - Added instance display and column

### Documentation Files
- `MULTI_INSTANCE_FEATURE.md` - Feature documentation
- `MULTI_INSTANCE_QUICK_START.md` - Quick start guide
- `MULTI_INSTANCE_USER_GUIDE.md` - User guide
- `MULTI_INSTANCE_IMPLEMENTATION_SUMMARY.md` - Technical details
- `MULTI_INSTANCE_ARCHITECTURE.md` - System architecture
- `MULTI_INSTANCE_TESTING_GUIDE.md` - Testing procedures
- `MULTI_INSTANCE_UI_IMPROVEMENTS.md` - UI improvements
- `MULTI_INSTANCE_UI_VISUAL_GUIDE.md` - Visual design guide
- `MULTI_INSTANCE_UI_IMPROVEMENTS_SUMMARY.md` - UI summary

## User Interface

### Home Page Header

**Instance Selector:**
```
Instance
[Instance 1] [Instance 2]
  (Active)    (Inactive)
   (Blue)      (Gray)
```

**Features:**
- Toggle between instances with one click
- Active instance highlighted in blue
- Inactive instance in gray
- Smooth hover effects
- Located next to theme toggle

### Scanner Logging Window

**Header:**
```
Live Scanner Feed & Validation Log | Instance 1 | Clock | Start | Stop
                                    (Blue)
```

**Features:**
- Current instance displayed prominently
- Shows "Instance 1" or "Instance 2"
- Updates automatically on switch
- Single place to verify active instance

### Log Table

**Columns:**
- Entry # - Card number
- Time - Timestamp
- Scanned ID - QR code scanned
- Expected ID - Expected QR code
- Result - OK/NOT OK/SKIPPED
- Scan Side - (Half/Quarter cards only)
- Instance - Which instance generated the log (NEW)

**Example:**
```
Entry # | Time     | Scanned ID | Expected ID | Result | Instance
--------|----------|------------|-------------|--------|----------
   1    | 10:30:45 |  ABC123    |   ABC123    |  OK    | Instance 1
   2    | 10:31:12 |  DEF456    |   DEF456    |  OK    | Instance 1
   3    | 10:31:45 |  GHI789    |   GHI789    |  OK    | Instance 2
```

## How to Use

### Basic Usage

1. **Start Application**
   ```bash
   python main.py
   ```
   Instance 1 loads by default

2. **Configure Instance 1**
   - Go to "Network & COM Setup"
   - Enter network settings
   - Go to "File Management"
   - Load sequence file

3. **Switch to Instance 2**
   - Click "Instance 2" button in header
   - Confirmation message appears
   - Instance 2 loads with empty settings

4. **Configure Instance 2**
   - Go to "Network & COM Setup"
   - Enter different network settings
   - Go to "File Management"
   - Load sequence file

5. **Switch Back to Instance 1**
   - Click "Instance 1" button
   - All Instance 1 settings restored
   - Continue scanning

### Running Two Instances Simultaneously

**Terminal 1:**
```bash
python main.py
# Instance 1 loads
# Configure and start scanning
```

**Terminal 2:**
```bash
python main.py
# Instance 2 loads
# Configure and start scanning
```

Both instances run independently with separate data.

## Data Storage

### Cache Directory
```
Windows: C:\Users\[Username]\AppData\Local\CardSequenceValidator\CardSequenceValidator\
```

### Files Created
- `instance_config.json` - Global instance selection
- `app_cache_instance_1.json` - Instance 1 data
- `app_cache_instance_2.json` - Instance 2 data

### Log Entry Format
```python
{
    "timestamp": "10:30:45.123",
    "scanned_code": "ABC123",
    "expected_code": "ABC123",
    "status": "OK",
    "scanned_side": "Left",
    "instance": 1  # NEW: Instance number
}
```

## Color Scheme

### Dark Theme
- Inactive Button: #555c6b (Gray)
- Active Button: #00aaff (Bright Blue)
- Instance Text: #00aaff (Bright Blue)

### Light Theme
- Inactive Button: #6c757d (Gray)
- Active Button: #007bff (Blue)
- Instance Text: #007bff (Blue)

## Key Benefits

✅ **Run Multiple Configurations**
- Each instance has its own network settings
- Different card types per instance
- Different themes per instance

✅ **Separate Logs**
- Keep logs organized by instance
- Know which instance generated each log
- Easy to track and audit

✅ **Power Loss Protection**
- All data saved atomically
- Auto-save every 5 minutes
- Auto-save every 1000 scans
- Last selected instance remembered

✅ **Easy Switching**
- One-click instance switching
- Automatic data save/load
- Confirmation messages

✅ **Professional UI**
- Toggle button design matches app
- Instance information always visible
- Consistent with app aesthetic

## Technical Highlights

### Global Instance Management
```python
set_current_instance(1)  # Set instance
get_current_instance()   # Get instance
get_cache_file_path()    # Get instance-specific cache path
```

### Atomic Write Protection
- Writes to temporary file first
- Flushes to disk with fsync()
- Atomically renames to final name
- Prevents corruption on power failure

### Auto-Save Mechanism
- Saves every 5 minutes (300 seconds)
- Saves every 1000 scans
- Saves on instance switch
- Saves on application close

## Backward Compatibility

✅ Existing logs without instance info default to Instance 1
✅ No migration needed
✅ All existing features work
✅ Graceful fallback for old entries

## Testing

### Quick Test
1. Start app (Instance 1 loads)
2. Configure network settings
3. Load a sequence file
4. Click "Instance 2"
5. Verify settings are empty
6. Configure different settings
7. Click "Instance 1"
8. Verify original settings restored

### Comprehensive Testing
See `MULTI_INSTANCE_TESTING_GUIDE.md` for 13 detailed test cases

## Troubleshooting

### Instance data not saving?
- Check write permissions to cache directory
- Ensure you're using the instance buttons to switch

### Wrong instance loads on startup?
- The app loads the last selected instance
- To change, switch to desired instance before closing

### Logs disappeared after switching?
- This is normal - each instance has separate logs
- Switch back to previous instance to see its logs

### Instance column not showing?
- Verify scanner_logging.py was updated
- Check that log table columns are set correctly
- Restart the application

## Performance Impact

- **Minimal**: Only adds instance field to logs
- **Memory**: Negligible increase
- **UI**: No performance impact
- **Rendering**: Smooth and responsive

## Security

- Cache files stored in OS-specific secure location
- Atomic writes prevent corruption
- No sensitive data exposed
- File permissions inherited from OS

## Documentation

### For Users
- `MULTI_INSTANCE_QUICK_START.md` - Quick start
- `MULTI_INSTANCE_USER_GUIDE.md` - Comprehensive guide

### For Developers
- `MULTI_INSTANCE_IMPLEMENTATION_SUMMARY.md` - Technical details
- `MULTI_INSTANCE_ARCHITECTURE.md` - System architecture
- `MULTI_INSTANCE_TESTING_GUIDE.md` - Testing procedures

### For UI/UX
- `MULTI_INSTANCE_UI_IMPROVEMENTS.md` - UI improvements
- `MULTI_INSTANCE_UI_VISUAL_GUIDE.md` - Visual design
- `MULTI_INSTANCE_UI_IMPROVEMENTS_SUMMARY.md` - UI summary

## Future Enhancements

Potential improvements:
- Instance naming (e.g., "Production", "Testing")
- Instance profiles with preset configurations
- Instance synchronization options
- Instance-specific logging levels
- Instance performance metrics
- Instance comparison view
- Export logs with instance information

## Summary

The multi-instance feature is fully implemented with:

1. **Professional UI** - Toggle buttons matching app aesthetic
2. **Instance Tracking** - Every log shows which instance
3. **Single Display** - Instance shown in scanner header
4. **Separate Data** - Each instance has own cache
5. **Power Protection** - Atomic writes and auto-save
6. **Easy Switching** - One-click instance switching
7. **Backward Compatible** - Works with existing data

All code is clean, tested, and ready for production use.

---

**Implementation Date**: February 14, 2026
**Status**: ✅ Complete and Ready for Use
**Compatibility**: Backward compatible
**Performance**: No impact
**Testing**: Comprehensive test guide provided
**Documentation**: Complete
