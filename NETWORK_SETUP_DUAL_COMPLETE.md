# Network Setup Dual Head - Implementation Complete

## Overview
Successfully implemented split-view Network Setup window for dual-head operation.

## Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│         Network & COM Port Configuration - Dual Head                 │
│    Configure UDP network and serial COM ports for both heads         │
├───────────────────────────────┬──────────────────────────────────────┤
│         HEAD B (Left)         │         HEAD A (Right)               │
│         [Blue Label]          │         [Green Label]                │
├───────────────────────────────┼──────────────────────────────────────┤
│                               │                                      │
│  Main Scanner Input (UDP)     │  Main Scanner Input (UDP)            │
│  ┌─────────────────────────┐  │  ┌─────────────────────────┐         │
│  │ Local IP:    [______]   │  │  │ Local IP:    [______]   │         │
│  │ Local Port:  [5000  ]   │  │  │ Local Port:  [5000  ]   │         │
│  │ Remote IP:   [______]   │  │  │ Remote IP:   [______]   │         │
│  │ Remote Port: [______]   │  │  │ Remote Port: [______]   │         │
│  │ Status: Not Connected   │  │  │ Status: Not Connected   │         │
│  │ [Apply Main Scanner]    │  │  │ [Apply Main Scanner]    │         │
│  └─────────────────────────┘  │  └─────────────────────────┘         │
│                               │                                      │
│  Output Configuration (UDP)   │  Output Configuration (UDP)          │
│  ┌─────────────────────────┐  │  ┌─────────────────────────┐         │
│  │ Local IP:    [______]   │  │  │ Local IP:    [______]   │         │
│  │ Local Port:  [0     ]   │  │  │ Local Port:  [0     ]   │         │
│  │ Remote IP:   [______]   │  │  │ Remote IP:   [______]   │         │
│  │ Remote Port: [6000  ]   │  │  │ Remote Port: [6000  ]   │         │
│  │ Status: Not Connected   │  │  │ Status: Not Connected   │         │
│  │ [Apply Output]          │  │  │ [Apply Output]          │         │
│  └─────────────────────────┘  │  └─────────────────────────┘         │
│                               │                                      │
│  On-Demand Scanner (Serial)   │  On-Demand Scanner (Serial)          │
│  ┌─────────────────────────┐  │  ┌─────────────────────────┐         │
│  │ COM Port:  [COM3    ]   │  │  │ COM Port:  [COM4    ]   │         │
│  │ Baud Rate: [115200  ]   │  │  │ Baud Rate: [115200  ]   │         │
│  │ Status: Not Connected   │  │  │ Status: Not Connected   │         │
│  │ [Apply On-Demand]       │  │  │ [Apply On-Demand]       │         │
│  └─────────────────────────┘  │  └─────────────────────────┘         │
│                               │                                      │
│  [Refresh Network]            │  [Refresh Network]                   │
│  [Disconnect Head B]          │  [Disconnect Head A]                 │
│                               │                                      │
└───────────────────────────────┴──────────────────────────────────────┘
│                         Status Log                                   │
│  [Timestamp] Head A: Main scanner configured                         │
│  [Timestamp] Head B: Output configured                               │
└──────────────────────────────────────────────────────────────────────┘
```

## Features Implemented

### 1. Split View Layout
- **Left Panel**: Head B configuration (Blue label)
- **Right Panel**: Head A configuration (Green label)
- **Vertical Separator**: Visual divider between panels
- **Equal Width**: Both panels have equal space (50/50 split)

### 2. Independent Configuration
Each head has its own:
- Main Scanner Input (UDP)
  - Local IP and Port
  - Remote IP and Port (scanner)
  - Status indicator
  - Apply button
- Output Configuration (UDP)
  - Local IP and Port
  - Remote IP and Port (PLC)
  - Status indicator
  - Apply button
- On-Demand Scanner (Serial)
  - COM port selection
  - Baud rate selection
  - Status indicator
  - Apply button

### 3. Network Detection
- Auto-detects local IP addresses
- Populates COM ports from system
- Loads output formats from configuration
- Refresh button updates all dropdowns

### 4. Status Tracking
- Real-time status updates for each head
- Color-coded status labels:
  - Green: Connected/OK
  - Red: Error/Not Connected
  - Orange: Warning
- Unified status log at bottom showing all events

### 5. Configuration Persistence
- Loads saved configurations on startup
- Saves configurations independently per head
- Uses existing cache system (instance_1 for Head A, instance_2 for Head B)

### 6. Action Buttons
- **Apply Main Scanner**: Configures UDP input for selected head
- **Apply Output**: Configures UDP output for selected head
- **Apply On-Demand Scanner**: Configures serial COM port for selected head
- **Refresh Network**: Re-scans network interfaces and COM ports
- **Disconnect Head X**: Disconnects all ports for selected head

## Technical Implementation

### File Structure
```
src/ui/network_setup_dual.py  (NEW - 800+ lines)
  ├── NetworkSetupWindow class
  ├── create_split_configuration()
  ├── create_head_panel(head_id, title)
  ├── create_main_scanner_section(head_id)
  ├── create_output_section(head_id)
  ├── create_ondemand_scanner_section(head_id)
  ├── apply_main_scanner(head_id)
  ├── apply_output(head_id)
  ├── apply_ondemand(head_id)
  └── Status update methods for each head
```

### Signal Connections
```python
# Head A signals
self.head_a.com_status_changed.connect(lambda msg, color: self.update_input_status('A', msg, color))
self.head_a.output_com_status_changed.connect(lambda msg, color: self.update_output_status('A', msg, color))
self.head_a.ondemand_scan_status_update.connect(lambda msg, color: self.update_ondemand_status('A', msg, color))

# Head B signals
self.head_b.com_status_changed.connect(lambda msg, color: self.update_input_status('B', msg, color))
self.head_b.output_com_status_changed.connect(lambda msg, color: self.update_output_status('B', msg, color))
self.head_b.ondemand_scan_status_update.connect(lambda msg, color: self.update_ondemand_status('B', msg, color))
```

### Dynamic Widget Creation
Uses `setattr()` and `getattr()` to dynamically create and access widgets:
```python
# Create widget for specific head
setattr(self, f'main_local_ip_{head_id}', combo_box)

# Access widget for specific head
combo = getattr(self, f'main_local_ip_{head_id}')
```

## Usage

### Opening the Window
From main window, click "Network & COM Setup" button.

### Configuring Head A (Right Side)
1. Select local IP and port for scanner input
2. Enter remote scanner IP and port
3. Click "Apply Main Scanner"
4. Configure output PLC IP and port
5. Select output format
6. Click "Apply Output"
7. Select COM port for on-demand scanner
8. Click "Apply On-Demand Scanner"

### Configuring Head B (Left Side)
Same steps as Head A, but on the left panel.

### Network Refresh
Click "Refresh Network" to re-scan:
- Local IP addresses
- Available COM ports
- Network interfaces

### Disconnecting
Click "Disconnect Head A" or "Disconnect Head B" to disconnect all ports for that head.

## Testing Checklist

- [x] Window opens without errors
- [x] Split view displays correctly
- [x] Head A panel on right (green label)
- [x] Head B panel on left (blue label)
- [x] All dropdowns populate correctly
- [x] Apply buttons work independently
- [x] Status updates show correct head
- [x] Configurations save independently
- [x] Refresh network works
- [x] Disconnect works per head
- [x] Status log shows all events
- [x] Theme changes apply correctly

## Next Steps

1. ✅ Network Setup Window - COMPLETE
2. ⏳ File Management Window - Split view for file loading
3. ⏳ Scanner Logging Window - Split view for live validation logs

## Notes

- Window minimum size: 1400x800 pixels (to accommodate split view)
- Recommended size: 1600x900 pixels
- Both heads can have identical or different configurations
- Each head operates completely independently
- Status log shows events from both heads with head identification
