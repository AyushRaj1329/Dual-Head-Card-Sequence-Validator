# Dual Head Implementation Progress

## Overview
Converting the Card Sequence Validator from single-instance switching to simultaneous dual-head operation.

## Terminology
- **Head A** = Instance 1 (Right side of split windows)
- **Head B** = Instance 2 (Left side of split windows)

## Completed Changes

### 1. ✅ Core Architecture
- Created `src/dual_head_manager.py` - Manages both Head A and Head B simultaneously
- Modified `main.py` - Now creates DualHeadManager instead of single AppState
- Each head has independent:
  - Network configuration (Input/Output UDP)
  - File loading and validation
  - Scan direction
  - Logs (saved separately)
  - On-demand scanner

### 2. ✅ Main Window (Home Page)
- **NOT split** - Unified view as requested
- Removed instance selector toggle
- Updated title: "Card Sequence Validator - Dual Head"
- Updated subtitle: "Automated Quality Control - Head A & Head B"
- Status section now shows BOTH heads:
  - **Head A (Right)** - Green label with all status indicators
  - **Head B (Left)** - Blue label with all status indicators
- Each head shows:
  - Scanner status (Scanning/Idle)
  - Input Port status
  - Output Port status
  - Scan Card Port status
  - File Loaded status
- Theme toggle applies to both heads

### 3. ✅ Signal Connections
- Both heads connected to status updates
- Output port status updates work for both heads independently
- State changes from either head trigger UI updates

### 4. ✅ Network Setup Window (SPLIT)
- **COMPLETE** - Split left/right layout
- Head B (left) and Head A (right)
- Independent configuration for each head:
  - Main Scanner (UDP input)
  - Output (UDP to PLC)
  - On-Demand Scanner (Serial COM)
- Separate apply buttons per head
- Unified status log
- Network detection and refresh
- Configuration persistence per head

### 5. ✅ File Management Window (SPLIT)
- **COMPLETE** - Split left/right layout
- Head B (left) and Head A (right)
- Independent file operations for each head:
  - Load sequence file
  - Scan direction toggle
  - Preview sequence
  - Clear sequence
- **ON-DEMAND SCANNER FUNCTIONS** (both heads):
  - ✅ Scan Card Details - View card information
  - ✅ Count Card Range - Count cards between two scans
  - Cancel buttons for both functions
  - Real-time status updates
- Independent log management:
  - Export logs to CSV
  - Clear logs
  - Statistics display
- Dynamic QR fields based on card type
- Card type change handling

## In Progress / Next Steps

### 4. ⏳ Network Setup Window (SPLIT)
**Layout:**
```
┌─────────────────────────────────────────────────┐
│      Network & COM Port Configuration           │
├────────────────────┬────────────────────────────┤
│      HEAD B        │         HEAD A             │
│     (Left)         │        (Right)             │
│                    │                            │
│  Main Scanner      │   Main Scanner             │
│  - Local IP:Port   │   - Local IP:Port          │
│  - Remote IP:Port  │   - Remote IP:Port         │
│                    │                            │
│  Output            │   Output                   │
│  - Local IP:Port   │   - Local IP:Port          │
│  - Remote IP:Port  │   - Remote IP:Port         │
│  - Format          │   - Format                 │
│                    │                            │
│  On-Demand Scanner │   On-Demand Scanner        │
│  - COM Port        │   - COM Port               │
│  - Baud Rate       │   - Baud Rate              │
│                    │                            │
│  [Apply Config B]  │   [Apply Config A]         │
└────────────────────┴────────────────────────────┘
```

**TODO:**
- Split window into left/right panels
- Duplicate all network configuration controls for each head
- Each side applies configuration to its respective head
- Separate status logs for each head

### 5. ⏳ File Management Window (SPLIT)
**Layout:**
```
┌─────────────────────────────────────────────────┐
│           File Management                        │
├────────────────────┬────────────────────────────┤
│      HEAD B        │         HEAD A             │
│     (Left)         │        (Right)             │
│                    │                            │
│  [Browse File]     │   [Browse File]            │
│  File: ______      │   File: ______             │
│  Card Type: ___    │   Card Type: ___           │
│                    │                            │
│  Direction:        │   Direction:               │
│  ○ Top→Bottom      │   ○ Top→Bottom             │
│  ○ Bottom→Top      │   ○ Bottom→Top             │
│                    │                            │
│  [Preview]         │   [Preview]                │
│  [Clear File]      │   [Clear File]             │
│                    │                            │
│  Sequence Tools:   │   Sequence Tools:          │
│  [Scan Card]       │   [Scan Card]              │
│  [Count Range]     │   [Count Range]            │
│  [Set Start]       │   [Set Start]              │
│                    │                            │
│  Log Management:   │   Log Management:          │
│  [Export Logs]     │   [Export Logs]            │
│  [Clear Logs]      │   [Clear Logs]             │
└────────────────────┴────────────────────────────┘
```

**TODO:**
- Split window into left/right panels
- Duplicate all file management controls for each head
- Each head can load different files independently
- Separate log export for each head

### 6. ⏳ Scanner Logging Window (SPLIT)
**Layout:**
```
┌─────────────────────────────────────────────────┐
│         Scanner & Logging                        │
├────────────────────┬────────────────────────────┤
│      HEAD B        │         HEAD A             │
│     (Left)         │        (Right)             │
│                    │                            │
│  [Start Scan]      │   [Start Scan]             │
│  [Stop Scan]       │   [Stop Scan]              │
│                    │                            │
│  Live Feed:        │   Live Feed:               │
│  ┌──────────────┐  │   ┌──────────────┐         │
│  │ Validation   │  │   │ Validation   │         │
│  │ Logs for     │  │   │ Logs for     │         │
│  │ Head B       │  │   │ Head A       │         │
│  │              │  │   │              │         │
│  └──────────────┘  │   └──────────────┘         │
│                    │                            │
│  Stats: 0 OK       │   Stats: 0 OK              │
│         0 NOT OK   │          0 NOT OK          │
└────────────────────┴────────────────────────────┘
```

**TODO:**
- Split window into left/right panels
- Duplicate scanner controls for each head
- Each head has independent start/stop buttons
- Separate live log feeds
- Separate statistics

### 7. ⏳ Persistent Logging
**TODO:**
- Modify AppState to write logs to disk immediately after each scan
- Log file structure:
  ```
  AppData/Local/YourCompany/CardSequenceValidator/
  ├── instance_1/  (Head A)
  │   ├── app_cache.json
  │   └── logs/
  │       ├── session_20260216_140000.log
  │       └── session_20260216_150000.log
  └── instance_2/  (Head B)
      ├── app_cache.json
      └── logs/
          ├── session_20260216_140100.log
          └── session_20260216_150100.log
  ```
- Implement atomic write for crash protection
- Auto-create new log file per session
- Keep logs in RAM AND disk simultaneously

## Key Design Decisions

1. **Main Window NOT Split** - Unified control panel showing both heads' status
2. **Other Windows Split** - Left/Right panels for independent head configuration
3. **Head A = Right Side** - Consistent across all windows
4. **Head B = Left Side** - Consistent across all windows
5. **Independent Operation** - Each head validates independently and simultaneously
6. **Separate Files** - Each head can load different files (or same file twice)
7. **Persistent Logs** - Written to disk immediately to prevent data loss

## Testing Checklist

### Main Window
- [ ] Both heads' status displayed correctly
- [ ] Status updates when configurations change
- [ ] Theme toggle works for both heads
- [ ] No instance selector visible
- [ ] Window opens without errors

### Network Setup (When Implemented)
- [ ] Window splits into left/right panels
- [ ] Head B controls on left work independently
- [ ] Head A controls on right work independently
- [ ] Each head can have different network configs
- [ ] Apply buttons work for respective heads
- [ ] Status updates correctly for each head

### File Management (When Implemented)
- [ ] Window splits into left/right panels
- [ ] Each head can load different files
- [ ] Same file can be loaded twice (once per head)
- [ ] Direction toggle works independently
- [ ] Preview shows correct data for each head
- [ ] Sequence tools work for respective heads

### Scanner Logging (When Implemented)
- [ ] Window splits into left/right panels
- [ ] Start/Stop works independently for each head
- [ ] Live logs display correctly for each head
- [ ] No cross-contamination of logs
- [ ] Statistics accurate for each head
- [ ] Pagination works independently

### Persistent Logging (When Implemented)
- [ ] Logs written to disk after each scan
- [ ] Separate log files for each head
- [ ] Logs survive application crash
- [ ] Logs survive power loss
- [ ] Log files have correct timestamps
- [ ] Old logs can be read and exported

## Current Status

**Completed:** Main Window dual-head display
**Next:** Implement split Network Setup Window

The foundation is in place. The DualHeadManager handles both heads simultaneously, and the main window correctly displays status for both. Now we need to implement the split windows for configuration and operation.
