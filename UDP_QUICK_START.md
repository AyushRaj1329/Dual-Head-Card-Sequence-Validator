# UDP Quick Start Guide

## 5-Minute Setup

### Step 1: Configure Your Network (2 minutes)

**Assign IP Addresses**:
- Validator PC: `192.168.1.100`
- Main Scanner: `192.168.1.50`
- On-Demand Scanner: `192.168.1.51`
- PLC: `192.168.1.200`

### Step 2: Configure Firewall (1 minute)

**Run as Administrator** (PowerShell):
```powershell
New-NetFirewallRule -DisplayName "Card Validator - Main" -Direction Inbound -Protocol UDP -LocalPort 5000 -Action Allow
New-NetFirewallRule -DisplayName "Card Validator - OnDemand" -Direction Inbound -Protocol UDP -LocalPort 5100 -Action Allow
```

### Step 3: Configure Application (2 minutes)

1. Open **Network Setup** from home page
2. **Main Scanner Input**:
   - Local IP: `192.168.1.100`
   - Local Port: `5000`
   - Remote IP: (leave empty)
   - Remote Port: (leave empty)

3. **On-Demand Scanner Input**:
   - Local IP: `192.168.1.100`
   - Local Port: `5100`
   - Remote IP: (leave empty)
   - Remote Port: (leave empty)

4. **Output Configuration**:
   - Local IP: `0.0.0.0`
   - Local Port: `0`
   - Remote IP: `192.168.1.200`
   - Remote Port: `6000`

5. Click **Apply Configuration**

### Step 4: Test

**Test Main Scanner**:
```powershell
$udpClient = New-Object System.Net.Sockets.UdpClient
$bytes = [System.Text.Encoding]::UTF8.GetBytes("TEST123")
$udpClient.Send($bytes, $bytes.Length, "192.168.1.100", 5000)
$udpClient.Close()
```

**Expected**: Connection log shows "Listening on 192.168.1.100:5000" in green

---

## Common Configurations

### Configuration 1: Single Scanner
```
Main Scanner: 192.168.1.50 → 192.168.1.100:5000
Output: 192.168.1.100 → 192.168.1.200:6000
```

### Configuration 2: Two Scanners
```
Main Scanner: 192.168.1.50 → 192.168.1.100:5000
On-Demand: 192.168.1.51 → 192.168.1.100:5100
Output: 192.168.1.100 → 192.168.1.200:6000
```

### Configuration 3: Multiple Validators
```
Validator 1: 192.168.1.100:5000
Validator 2: 192.168.1.101:5000
Scanner: Sends to both (duplicate packets)
```

---

## Troubleshooting

### Problem: "Not Connected"
**Solution**: Check firewall, verify IP address

### Problem: No Data Received
**Solution**: Verify scanner is sending to correct IP:port

### Problem: Output Not Working
**Solution**: Verify PLC IP and port, check PLC is listening

---

## Scanner Configuration Examples

### Honeywell Scanner
```
Menu → Communication → Network
- Mode: UDP
- Target IP: 192.168.1.100
- Target Port: 5000
```

### Zebra Scanner
```
Settings → Interface → Ethernet
- Protocol: UDP
- Destination: 192.168.1.100:5000
```

---

## Need More Help?

See `UDP_MIGRATION_GUIDE.md` for complete documentation.

---

**Quick Start Version**: 1.0  
**Last Updated**: February 8, 2026
