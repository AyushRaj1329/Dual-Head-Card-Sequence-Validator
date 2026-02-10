# On-Demand Scanner Serial Configuration - Quick Guide

## What Changed?

The on-demand scanner now uses **Serial (COM Port)** instead of UDP network connection.

## How to Configure

### Step 1: Open Configuration Window
Click **"Network & COM Setup"** from the home page.

### Step 2: Locate On-Demand Scanner Section
Scroll to the **"On-Demand Scanner Input (Serial)"** panel.

### Step 3: Select COM Port
```
COM Port: [Select from dropdown ▼] [🔄 Refresh]
```
- Click the dropdown to see available COM ports
- Click the 🔄 button to refresh the list
- Select your scanner's COM port (e.g., COM3, COM4)

### Step 4: Configure Serial Settings (Optional)
Most scanners work with default settings, but you can adjust:

```
Baud Rate:  [115200 ▼]  ← Speed of communication
Data Bits:  [8 ▼]       ← Bits per character
Parity:     [None ▼]    ← Error checking
Stop Bits:  [1 ▼]       ← End of character marker
Timeout:    [1]         ← Seconds to wait
```

**Default Settings (Recommended):**
- Baud Rate: 115200
- Data Bits: 8
- Parity: None
- Stop Bits: 1
- Timeout: 1 second

### Step 5: Apply Configuration
Click **"Apply Configuration"** button at the bottom.

### Step 6: Verify Connection
Status should change from:
- ❌ "Not Connected" (red)
- ✅ "COM3" (green) ← Your port name

## Using On-Demand Scanner

### Scan Card Details
1. Go to **"File & Log Management"**
2. Load a sequence file
3. Click **"Scan Card Details"**
4. Scan a card with your on-demand scanner
5. Card information appears in the fields

### Count Card Range
1. Go to **"File & Log Management"**
2. Load a sequence file
3. Click **"Count Card Range"**
4. Scan the FIRST card
5. Scan the LAST card
6. Total count appears

## Troubleshooting

### Problem: No COM ports in dropdown
**Solution:**
1. Check scanner is plugged in
2. Check USB cable connection
3. Click the 🔄 refresh button
4. Check Device Manager (Windows) for COM port

### Problem: "Not Connected" after applying
**Solution:**
1. Verify correct COM port selected
2. Check scanner is powered on
3. Try different baud rate (9600 or 19200)
4. Check no other program is using the COM port

### Problem: Scanner was working, now doesn't
**Solution:**
1. Click "Disconnect All"
2. Unplug and replug scanner
3. Click 🔄 to refresh COM ports
4. Reselect COM port
5. Click "Apply Configuration"

### Problem: Wrong data received
**Solution:**
1. Check baud rate matches scanner
2. Check data bits (usually 8)
3. Check parity (usually None)
4. Consult scanner manual for settings

## Common Scanner Settings

### Standard USB Scanner
```
Baud Rate: 115200
Data Bits: 8
Parity: None
Stop Bits: 1
```

### Older Serial Scanner
```
Baud Rate: 9600
Data Bits: 8
Parity: None
Stop Bits: 1
```

### Industrial Scanner
```
Baud Rate: 38400 or 57600
Data Bits: 8
Parity: Even or None
Stop Bits: 1
```

## Quick Reference

| Setting | Common Values | Default |
|---------|--------------|---------|
| Baud Rate | 9600, 19200, 38400, 57600, 115200 | 115200 |
| Data Bits | 7, 8 | 8 |
| Parity | None, Even, Odd | None |
| Stop Bits | 1, 2 | 1 |
| Timeout | 0.5 - 5 seconds | 1 |

## Benefits of Serial Connection

✅ **Direct Connection** - No network configuration needed
✅ **Reliable** - More stable than UDP for local devices
✅ **Simple** - Just plug in and select COM port
✅ **Standard** - Works with most industrial scanners
✅ **Fast** - Low latency for on-demand scans

## Comparison: UDP vs Serial

| Feature | UDP (Old) | Serial (New) |
|---------|-----------|--------------|
| Setup | Configure IP and ports | Select COM port |
| Connection | Network-based | Direct USB/Serial |
| Reliability | Can have network issues | Very stable |
| Configuration | 4 fields | 6 fields (more control) |
| Discovery | Network scan | System COM ports |
| Typical Use | Remote devices | Local scanners |

## Need Help?

1. Check scanner manual for correct settings
2. Use Device Manager to verify COM port
3. Try default settings first
4. Test with a simple serial terminal program
5. Contact support with COM port number and error message

---

**Remember:** The on-demand scanner is now serial-based. Make sure to configure the COM port in the "Network & COM Setup" window before using card details or counting features!
