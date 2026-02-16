# Port Validation and Conflict Detection Implementation

## Overview
Enhanced the network setup window with comprehensive port availability checking and conflict detection to prevent connection failures and port conflicts between Head A and Head B.

## Problem Statement
Previously, the application would:
1. Accept any port configuration without checking availability
2. Allow both heads to use the same port, causing conflicts
3. Not verify if the IP/port combination could actually be bound
4. Show "connected" even when the connection failed

## Solution Implemented

### 1. Port Availability Checking
**Method**: `is_port_available(ip, port)`

Validates that a port can actually be bound before applying configuration:
- Creates a test UDP socket
- Attempts to bind to the specified IP:port
- Returns success/failure with detailed error messages
- Handles specific error cases:
  - `EADDRINUSE`: Port already in use by another application
  - `EADDRNOTAVAIL`: IP address not available on this machine
  - Other socket errors with descriptive messages

### 2. Port Conflict Detection
**Method**: `check_port_conflict(head_id, ip, port, port_type)`

Prevents both heads from using the same port:
- Checks if the other head is using the same port
- Considers IP address overlap:
  - `0.0.0.0` overlaps with all IPs (binds to all interfaces)
  - Specific IPs only conflict if they match exactly
- Checks both main scanner input and output ports
- Returns clear error message indicating which head is using the port

### 3. Connection Testing
**Method**: `test_udp_connection(local_ip, local_port)`

Performs actual connection test before applying:
- Creates and binds a test socket
- Verifies the connection can be established
- Closes test socket cleanly
- Returns success/failure status

### 4. Enhanced Apply Methods

#### Main Scanner Configuration (`apply_main_scanner`)
Now includes:
1. IP format validation
2. Port range validation (0-65535)
3. Port conflict check with other head
4. Port availability check
5. Connection test
6. Only applies configuration if all checks pass
7. Shows detailed success/error messages

#### Output Configuration (`apply_output`)
Now includes:
1. IP format validation
2. Port range validation
3. Port conflict check (if local port specified)
4. Port availability check (if local port specified)
5. Only applies configuration if all checks pass
6. Shows detailed success/error messages

## Error Messages

### Port Already in Use
```
Port 5000 is already in use

Please choose a different port or close the application using this port.
```

### Port Conflict Between Heads
```
Port 5000 is already used by Head A main scanner input
```

### IP Not Available
```
IP address 192.168.1.100 is not available on this machine
```

### Connection Test Failed
```
Failed to bind: [Errno 10048] Only one usage of each socket address (protocol/network address/port) is normally permitted
```

## Success Messages

### Main Scanner Connected
```
Head A main scanner connected successfully!

Listening on: 192.168.1.100:5000
Accepting from: 192.168.1.200:5001
```

### Output Connected
```
Head A output connected successfully!

Sending from: 192.168.1.100:6000
Sending to: 192.168.1.200:6001
```

## Technical Details

### Import Additions
```python
import errno
import threading
import subprocess
```

### Port Conflict Logic
- Ports conflict if:
  1. Port numbers are identical AND
  2. IP addresses overlap (same IP or one is 0.0.0.0)

- Example conflicts:
  - Head A: `0.0.0.0:5000` conflicts with Head B: `192.168.1.100:5000`
  - Head A: `192.168.1.100:5000` conflicts with Head B: `192.168.1.100:5000`

- Example non-conflicts:
  - Head A: `192.168.1.100:5000` does NOT conflict with Head B: `192.168.1.101:5000`
  - Head A: `192.168.1.100:5000` does NOT conflict with Head B: `192.168.1.100:5001`

### Socket Testing
```python
test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
test_socket.settimeout(2.0)
test_socket.bind((bind_ip, int(local_port)))
test_socket.close()
```

## User Experience Flow

### Before (Old Behavior)
1. User enters IP and port
2. Clicks "Apply"
3. Shows "Success" message
4. Connection may fail silently
5. Both heads can use same port causing conflicts

### After (New Behavior)
1. User enters IP and port
2. Clicks "Apply"
3. System validates:
   - IP format ✓
   - Port range ✓
   - Port not used by other head ✓
   - Port available on system ✓
   - Connection can be established ✓
4. Shows detailed success or specific error message
5. Configuration only applied if all checks pass

## Testing Scenarios

### Test 1: Port Already in Use
1. Start another application on port 5000
2. Try to configure Head A to use port 5000
3. Expected: Error message "Port 5000 is already in use"

### Test 2: Port Conflict Between Heads
1. Configure Head A with port 5000
2. Try to configure Head B with port 5000
3. Expected: Error message "Port 5000 is already used by Head A main scanner input"

### Test 3: Invalid IP Address
1. Enter IP "999.999.999.999"
2. Click Apply
3. Expected: Error message about invalid IP format

### Test 4: IP Not Available
1. Enter IP "192.168.99.99" (not on your machine)
2. Click Apply
3. Expected: Error message "IP address not available on this machine"

### Test 5: Successful Connection
1. Enter valid, available IP and port
2. Click Apply
3. Expected: Success message with connection details

### Test 6: Different IPs, Same Port (Should Work)
1. Configure Head A: `192.168.1.100:5000`
2. Configure Head B: `192.168.1.101:5000`
3. Expected: Both should connect successfully (no conflict)

## Benefits

1. **Prevents Silent Failures**: Users immediately know if connection failed
2. **Clear Error Messages**: Specific reasons for failure are shown
3. **Prevents Conflicts**: Impossible for both heads to use same port
4. **Better UX**: Users don't waste time troubleshooting mysterious connection issues
5. **System Protection**: Validates before attempting to bind, preventing crashes

## Files Modified
- `src/ui/network_setup_dual.py`
  - Added `is_port_available()` method
  - Added `check_port_conflict()` method
  - Added `test_udp_connection()` method
  - Enhanced `apply_main_scanner()` with validation
  - Enhanced `apply_output()` with validation
  - Added imports: `errno`, `threading`, `subprocess`

## Status
✅ Implementation Complete
✅ No syntax errors
✅ Ready for testing

## Next Steps
- User testing with various network configurations
- Test with actual scanner hardware
- Verify error messages are clear and actionable
