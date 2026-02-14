# Main Scanner Status Update Fix

## Problem
When clicking "Apply Configuration" in the Main Scanner section of the Network Setup window, the status was showing "Connected" even when only Local IP/Port were entered, without requiring Remote IP/Port like the Output section does.

## Root Cause
The `apply_main_scanner_configuration()` method was treating Remote IP and Port as optional fields, allowing configuration to be saved with only Local IP/Port. This was inconsistent with the Output section which requires both Remote IP and Remote Port.

## Solution

### 1. Updated Validation Logic
Changed Main Scanner to match Output section behavior:
- **Requires BOTH Remote IP AND Remote Port** to be filled
- Only shows "Connected" status when all required fields are provided
- Validates both Local Port and Remote Port ranges (1-65535)

### 2. Updated `apply_main_scanner_configuration()` Method

**When ALL fields are valid (Local IP, Local Port, Remote IP, Remote Port):**
- Saves configuration to `app_state.main_scanner_config`
- Sets status text to: `"Configured: {local_ip}:{local_port} → {remote_ip}:{remote_port}"`
- Sets status style to: `statusOK` (green)
- Adds log entry with green color
- Example: "Configured: 192.168.1.100:5000 → 192.168.1.50:6000"

**When Remote IP or Remote Port is missing:**
- Clears configuration (`main_scanner_config = None`)
- Sets status text to: `"Not Connected"`
- Sets status style to: `statusError` (red)
- Adds log entry: "Main scanner disconnected - Remote IP and Port required"

### 3. Updated `update_ui_from_state()` Method
Added validation when loading configuration from cache:

**When configuration exists with Remote IP and Port:**
- If scanning: `"Listening on {local_ip}:{local_port}"` (green)
- If not scanning: `"Configured: {local_ip}:{local_port} → {remote_ip}:{remote_port}"` (green)

**When configuration exists but missing Remote IP or Port:**
- Sets status to: `"Not Connected"` (red)

**When no configuration exists:**
- Sets status to: `"Not Connected"` (red)

### 4. Updated Placeholder Text
Changed placeholder text to indicate fields are required:
- Remote IP: "Required - Scanner IP address" (was "Optional - Scanner IP address")
- Remote Port: "Required" (was "Optional")

## Consistency with Output Section

The Main Scanner now behaves EXACTLY like the Output section:

| Aspect | Main Scanner | Output Section | Match? |
|--------|-------------|----------------|--------|
| Requires Remote IP | ✅ Yes | ✅ Yes | ✅ |
| Requires Remote Port | ✅ Yes | ✅ Yes | ✅ |
| Validates Port Range | ✅ 1-65535 | ✅ 1-65535 | ✅ |
| Status when incomplete | ❌ Not Connected | ❌ Not Connected | ✅ |
| Status when complete | ✅ Configured | ✅ Connected | ✅ |
| Shows connection details | ✅ Yes | ✅ Yes | ✅ |

## Code Changes

### File: `src/ui/network_setup.py`

#### Method: `apply_main_scanner_configuration()`
```python
# Require both remote IP and remote port (like Output section)
if main_remote_ip and main_remote_port:
    # Validate local port
    main_local_port_int = int(main_local_port)
    if not (1 <= main_local_port_int <= 65535):
        raise ValueError("Port must be between 1 and 65535")
    
    # Validate remote port
    main_remote_port_int = int(main_remote_port)
    if not (1 <= main_remote_port_int <= 65535):
        raise ValueError("Port must be between 1 and 65535")
    
    # Save configuration
    self.app_state.main_scanner_config = {
        'local_ip': main_local_ip or "0.0.0.0",
        'local_port': int(main_local_port),
        'remote_ip': main_remote_ip,
        'remote_port': int(main_remote_port)
    }
    
    # Update status
    config_msg = f"Configured: {main_local_ip}:{main_local_port} → {main_remote_ip}:{main_remote_port}"
    self.main_status_text.setText(config_msg)
    self.main_status_text.setObjectName("statusOK")
else:
    # Clear configuration if remote IP/port not provided
    self.app_state.main_scanner_config = None
    self.main_status_text.setText("Not Connected")
    self.main_status_text.setObjectName("statusError")
```

#### Method: `update_ui_from_state()`
```python
# Update status - require both remote IP and port (like Output section)
if remote_ip and remote_port:
    if self.app_state.is_scanning:
        status_msg = f"Listening on {local_ip}:{local_port}"
    else:
        status_msg = f"Configured: {local_ip}:{local_port} → {remote_ip}:{remote_port}"
    self.main_status_text.setText(status_msg)
    self.main_status_text.setObjectName("statusOK")
else:
    # No remote IP/port - not connected
    self.main_status_text.setText("Not Connected")
    self.main_status_text.setObjectName("statusError")
```

## Status States

| State | Status Text | Color | Requirements |
|-------|-------------|-------|--------------|
| Not Connected | "Not Connected" | Red | Missing Remote IP or Remote Port |
| Configured | "Configured: 192.168.1.100:5000 → 192.168.1.50:6000" | Green | All fields valid, not scanning |
| Listening | "Listening on 192.168.1.100:5000" | Green | All fields valid, actively scanning |
| Not Set | "Not Set" | Red | Scanning stopped |

## Required Fields

### Main Scanner Section (Input)
1. ✅ **Local IP** - Required (where to listen)
2. ✅ **Local Port** - Required (which port to listen on)
3. ✅ **Remote IP** - Required (scanner device IP)
4. ✅ **Remote Port** - Required (scanner device port)

### Output Section
1. ✅ **Local IP** - Required (where to send from)
2. ✅ **Local Port** - Required (which port to send from)
3. ✅ **Remote IP** - Required (PLC/controller IP)
4. ✅ **Remote Port** - Required (PLC/controller port)

Both sections now have identical validation requirements!

## Testing

To verify the fix:

### Test 1: Incomplete Configuration
1. Open Network Setup window
2. Enter only Local IP and Local Port
3. Leave Remote IP and Remote Port empty
4. Click "Apply Configuration"
5. **Expected**: Status shows "Not Connected" (red)
6. **Expected**: Log shows "Remote IP and Port required"

### Test 2: Complete Configuration
1. Enter Local IP: 192.168.1.100
2. Enter Local Port: 5000
3. Enter Remote IP: 192.168.1.50
4. Enter Remote Port: 6000
5. Click "Apply Configuration"
6. **Expected**: Status shows "Configured: 192.168.1.100:5000 → 192.168.1.50:6000" (green)
7. **Expected**: Log shows configuration details

### Test 3: Start Scanning
1. After complete configuration, go to Home page
2. Load a file and click "Start Scanning"
3. **Expected**: Status updates to "Listening on 192.168.1.100:5000" (green)

### Test 4: Stop Scanning
1. Click "Stop Scanning"
2. **Expected**: Status shows "Not Set" (red)
3. Return to Network Setup
4. **Expected**: Configuration persists, status shows "Configured: ..." (green)

## Files Modified
- `src/ui/network_setup.py` - Updated `apply_main_scanner_configuration()`, `update_ui_from_state()`, and placeholder text
