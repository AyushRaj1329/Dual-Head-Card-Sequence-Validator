# Quick Reference Guide - Dual Head System

## Running the Application

```bash
python main.py
```

## Window Overview

### Main Window
- **Purpose**: Home page with status overview
- **Layout**: Unified (not split)
- **Shows**: Status for both Head A and Head B
- **Features**: Theme toggle, navigation buttons

### Network Setup Window
- **Purpose**: Configure network and COM port settings
- **Layout**: Split (Head B left, Head A right)
- **Sections**: Main Scanner Input, Output, On-Demand Scanner
- **Features**: Port validation, conflict detection, status updates

### File Management Window
- **Purpose**: Load files and manage logs
- **Layout**: Split (Head B left, Head A right)
- **Features**: File loading, scan direction, on-demand functions, log export

### Scanner Logging Window
- **Purpose**: Live validation and log viewing
- **Layout**: Split (Head B left, Head A right)
- **Features**: Start/stop validation, live logs, pagination, mismatch dialogs

## Configuration Steps

### 1. Configure Main Scanner Input
1. Open Network Setup window
2. Enter Local IP and Port (where you listen)
3. Enter Remote IP and Port (where scanner sends from)
4. Click "Apply Main Scanner"
5. Status shows: `Ready: [local_ip]:[port] ← [remote_ip]:[port]`

### 2. Configure Output
1. Enter Local IP and Port (where you send from)
2. Enter Remote IP and Port (where you send to)
3. Click "Apply Output"
4. Status shows: `Ready: [local_ip]:[port] → [remote_ip]:[port]`

### 3. Configure On-Demand Scanner
1. Click "🔄 Refresh Network & Scan IPs" to see available COM ports
2. Select COM port from dropdown
3. Select Baud Rate (default: 115200)
4. Click "Apply On-Demand Scanner"
5. Status shows: `Connected to [COM port]`

### 4. Load Sequence File
1. Open File Management window
2. Click "Browse" and select .CPD file
3. Select Card Type (Single/Half/Quarter)
4. Choose Scan Direction (Top→Bottom or Bottom→Top)
5. Click "Preview" to verify

### 5. Start Validation
1. Open Scanner Logging window
2. Click "Start Validation" for desired head
3. Scan cards
4. View real-time logs and validation results

## Status Indicators

### Colors
- 🟢 **Green**: Connected and ready
- 🟠 **Orange**: Warning or intentional disconnect
- 🔴 **Red**: Error or not connected

### Status Messages

**Input Section**:
- `Ready: 192.168.1.100:5000 ← 192.168.1.200:5001` - Connected
- `Configuration changed - disconnected` - Settings changed
- `Port 5000 is already in use` - Port unavailable
- `Not Connected` - Disconnected

**Output Section**:
- `Ready: 192.168.1.100:6000 → 192.168.1.200:6001` - Connected
- `Not Connected` - Disconnected

**On-Demand Scanner**:
- `Connected to COM3` - Connected
- `COM port 'COM3' not found` - Port unavailable
- `Not Connected` - Disconnected

## Error Messages

### Port Already in Use
```
Port 5000 is already in use

Please choose a different port or close 
the application using this port.
```
**Solution**: Choose different port or close other application

### Port Conflict Between Heads
```
Port 5000 is already used by Head A main scanner input
```
**Solution**: Use different port for Head B

### COM Port Not Found
```
COM port 'COM3' is not available.

Available ports: COM4, COM5

Please refresh and select an available COM port.
```
**Solution**: Refresh and select available port

### Invalid IP Format
```
Local IP '999.999.999.999' is not a valid IP address.
Format: xxx.xxx.xxx.xxx (0-255 for each octet)
```
**Solution**: Enter valid IP address

## Keyboard Shortcuts

- **F5**: Refresh (in Network Setup window)
- **Ctrl+S**: Save logs (in File Management window)
- **Esc**: Close dialog boxes

## Cache Files Location

**Windows**:
```
C:\Users\[USERNAME]\AppData\Local\CardSequenceValidator\CardSequenceValidator\
  - app_cache_instance_1.json (Head A)
  - app_cache_instance_2.json (Head B)
```

## Troubleshooting

### Settings Not Saving
1. Check cache file permissions
2. Verify cache files exist
3. Check for "Failed to save cache" errors in console

### Connection Failed
1. Verify IP addresses are correct
2. Check port is not in use
3. Ensure network is accessible
4. Test with ping command

### COM Port Issues
1. Click "Refresh Network & Scan IPs"
2. Check Device Manager for COM ports
3. Verify COM port is not in use by other application
4. Try different COM port

### Status Not Updating
1. Close and reopen window
2. Check console for errors
3. Verify connections are established
4. Restart application

## Best Practices

### Network Configuration
- Use specific IP addresses instead of 0.0.0.0 when possible
- Use different ports for each head
- Test connection after applying settings
- Document your IP/port assignments

### File Management
- Preview files before starting validation
- Export logs regularly
- Use descriptive file names
- Keep backup of sequence files

### Validation
- Start with small test files
- Monitor logs for errors
- Handle mismatch dialogs promptly
- Stop validation before changing settings

### Maintenance
- Clear old logs periodically
- Backup cache files
- Update sequence files as needed
- Monitor system resources

## Common Workflows

### Workflow 1: Single Head Operation
1. Configure Head A only
2. Load file for Head A
3. Start validation on Head A
4. Monitor logs
5. Export logs when complete

### Workflow 2: Dual Head Operation
1. Configure Head A with ports 5000/6000
2. Configure Head B with ports 5001/6001
3. Load different files for each head
4. Start validation on both heads
5. Monitor both log tables
6. Export logs separately

### Workflow 3: Testing Configuration
1. Configure settings
2. Click "Apply"
3. Check status indicators
4. Verify in status log
5. Test with actual scanner
6. Adjust if needed

## Tips and Tricks

### Network Setup
- Use "Refresh Network & Scan IPs" to discover devices
- Status log shows all available IPs on network
- COM ports show with descriptions for easy identification
- Settings are saved automatically when applied

### File Management
- Use "Preview" to verify file loaded correctly
- Scan direction can be changed without reloading file
- On-demand functions work independently of main validation
- Logs are saved automatically during scanning

### Scanner Logging
- Pagination shows 100 entries per page
- Auto-jumps to last page for new entries
- Color-coded status makes errors easy to spot
- Mismatch dialogs allow sequence advancement

## Quick Commands

### View Cache Files
```cmd
cd %LOCALAPPDATA%\CardSequenceValidator\CardSequenceValidator
type app_cache_instance_1.json
```

### Clear Cache (if corrupted)
```cmd
cd %LOCALAPPDATA%\CardSequenceValidator\CardSequenceValidator
del app_cache_instance_1.json
del app_cache_instance_2.json
```

### Check Port Usage (Windows)
```cmd
netstat -ano | findstr :5000
```

### List COM Ports (PowerShell)
```powershell
[System.IO.Ports.SerialPort]::getportnames()
```

## Support

For issues or questions:
1. Check console output for errors
2. Review status log messages
3. Verify cache files are valid JSON
4. Check network connectivity
5. Restart application if needed

## Version Information

- **Application**: Card Sequence Validator - Dual Head
- **Architecture**: Dual-head simultaneous operation
- **UI Framework**: PyQt6
- **Network Protocol**: UDP
- **Serial Protocol**: PySerial
- **Cache Format**: JSON

---

**Last Updated**: Current session
**Status**: ✅ Production Ready
