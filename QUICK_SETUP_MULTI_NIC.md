# Quick Setup Guide - Multi-NIC UDP Configuration

## Prerequisites

Install psutil for proper interface detection:
```bash
pip install psutil
```

## Quick Setup (5 Steps)

### Step 1: Open Configuration
Click **"Network & COM Setup"** from home page.

### Step 2: Configure Main Scanner Input

```
Main Scanner Input (UDP)
├─ Local IP (this PC):    [192.168.1.100 (Ethernet - UP) ▼]
├─ Local Port (listen):   [5000]
├─ Remote IP (scanner):   [192.168.1.50]  (optional)
└─ Remote Port (scanner): [5001]          (optional)
```

**Tips:**
- Select the Ethernet interface connected to your scanner network
- Use specific IP, not "0.0.0.0 (All interfaces)"
- Local Port: Where this PC listens for scanner data
- Remote IP/Port: Optional filter (only accept from this scanner)

### Step 3: Configure Output to PLC

```
Output Configuration (UDP)
├─ Local IP (this PC):    [192.168.2.100 (Ethernet 2 - UP) ▼]
├─ Local Port (send from):[0]  (auto-assign)
├─ Remote IP (PLC):       [192.168.2.50]
└─ Remote Port (PLC):     [6000]
```

**Tips:**
- Select the Ethernet interface connected to your PLC network
- Can be same or different interface as scanner
- Local Port: 0 = auto-assign (recommended)
- Remote IP/Port: Where to send validation results

### Step 4: Test Connection

Click **"🔍 Test Connection"** button.

**Check Log for:**
```
✓ Ping successful: 192.168.1.100
✓ Can bind to 192.168.1.100:5000
✓ Scanner reachable: 192.168.1.50
✓ PLC reachable: 192.168.2.50
```

**If any test fails:**
- ✗ Ping failed → Check network cable, interface status
- ✗ Cannot bind → Port in use, try different port
- ✗ Not reachable → Check device IP, power, network

### Step 5: Apply Configuration

Click **"Apply Configuration"** button.

**Success message:**
```
Configuration has been applied.
```

## Common Configurations

### Configuration A: Two Separate Networks

**Scenario:** Scanner on one network, PLC on another

```
Ethernet 1 (192.168.1.100) → Scanner Network
Ethernet 2 (192.168.2.100) → PLC Network

Main Scanner:
  Local IP: 192.168.1.100 (Ethernet - UP)
  Local Port: 5000
  Remote IP: 192.168.1.50

Output:
  Local IP: 192.168.2.100 (Ethernet 2 - UP)
  Local Port: 0
  Remote IP: 192.168.2.50
  Remote Port: 6000
```

### Configuration B: Same Network

**Scenario:** Scanner and PLC on same network

```
Ethernet (192.168.1.100) → Industrial Network

Main Scanner:
  Local IP: 192.168.1.100 (Ethernet - UP)
  Local Port: 5000
  Remote IP: 192.168.1.50

Output:
  Local IP: 192.168.1.100 (Ethernet - UP)
  Local Port: 0
  Remote IP: 192.168.1.60
  Remote Port: 6000
```

### Configuration C: Single Interface, Multiple Devices

**Scenario:** One Ethernet, multiple scanners/PLCs

```
Ethernet (192.168.1.100) → Industrial Network

Main Scanner:
  Local IP: 192.168.1.100 (Ethernet - UP)
  Local Port: 5000
  Remote IP: (leave empty - accept from any)

Output:
  Local IP: 192.168.1.100 (Ethernet - UP)
  Local Port: 0
  Remote IP: 192.168.1.60
  Remote Port: 6000
```

## Troubleshooting

### Problem: No Ethernet Interfaces Shown

**Solution:**
```bash
# Install psutil
pip install psutil

# Restart application
```

### Problem: Interface Shows "DOWN"

**Solution:**
1. Check network cable is plugged in
2. Enable interface in Windows Network Settings
3. Click "🔄 Refresh Network" button

### Problem: Cannot Bind to Port

**Solution:**
```bash
# Check if port is in use
netstat -an | findstr :5000

# Try different port or close other application
```

### Problem: Remote Device Not Reachable

**Solution:**
1. Verify device IP address
2. Check device is powered on
3. Verify same subnet (e.g., both 192.168.1.x)
4. Test with ping: `ping 192.168.1.50`

## Key Differences from Old Configuration

| Old (0.0.0.0) | New (Specific IP) |
|---------------|-------------------|
| ❌ OS chooses interface | ✅ You choose interface |
| ❌ May use wrong adapter | ✅ Always correct adapter |
| ❌ No testing tools | ✅ Built-in testing |
| ❌ Generic errors | ✅ Specific errors |

## Why This Matters

**Multi-NIC Systems:**
```
Before: Bind to 0.0.0.0
  → OS picks interface randomly
  → Scanner data may go to wrong network
  → Communication fails

After: Bind to 192.168.1.100
  → Forces use of Ethernet 1
  → Scanner data always on correct network
  → Communication works reliably
```

## Quick Reference

### Buttons:
- **Apply Configuration**: Save and activate settings
- **🔍 Test Connection**: Test connectivity (ping + bind)
- **Disconnect All**: Stop all connections, clear settings
- **🔄 Refresh Network**: Re-scan network interfaces

### Dropdown Options:
- **0.0.0.0 (All interfaces)**: Let OS choose (not recommended for multi-NIC)
- **127.0.0.1 (Localhost)**: Local testing only
- **192.168.x.x (Ethernet - UP)**: Specific interface (recommended)

### Status Indicators:
- **Green**: Connected and working
- **Red**: Error or not connected
- **Orange**: Warning or partial connection

## Need Help?

1. Click "🔍 Test Connection" to diagnose issues
2. Check "Connection Log" for detailed messages
3. Verify interface status shows "UP"
4. Ensure devices are on same subnet
5. Test with ping command first

---

**Remember:** Always use specific interface IPs (not 0.0.0.0) on multi-NIC systems for reliable communication!
