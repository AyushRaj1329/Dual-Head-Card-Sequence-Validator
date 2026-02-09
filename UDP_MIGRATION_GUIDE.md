# UDP Network Communication Migration Guide

## Overview

The Card Sequence Validator has been migrated from **Serial (COM Port)** communication to **UDP Network** communication. This document explains the changes, configuration, and usage of the new UDP-based system.

---

## What Changed?

### Before (Serial/COM Port)
- **Main Scanner**: Connected via COM port (e.g., COM3)
- **On-Demand Scanner**: Connected via COM port (e.g., COM4)
- **Output**: Sent to PLC via COM port (e.g., COM5)
- **Configuration**: Baud rate, data bits, parity, stop bits, timeout

### After (UDP Network)
- **Main Scanner**: Listens on local IP:Port, receives from remote IP:Port
- **On-Demand Scanner**: Listens on local IP:Port, receives from remote IP:Port
- **Output**: Sends from local IP:Port to remote IP:Port
- **Configuration**: IP addresses and port numbers

---

## Architecture

### UDP Communication Model

```
┌─────────────────────────────────────────────────────────────┐
│                    CARD VALIDATOR PC                         │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Main Scanner Input (UDP Reader)                   │    │
│  │  Listens: 192.168.1.100:5000                       │    │
│  │  Accepts from: 192.168.1.50:* (optional filter)    │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Validation Logic                                  │    │
│  │  - Sequence checking                               │    │
│  │  - QR code validation                              │    │
│  │  - Logging                                         │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Output (UDP Writer)                               │    │
│  │  Sends from: 192.168.1.100:0 (auto)                │    │
│  │  Sends to: 192.168.1.200:6000 (PLC)                │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  On-Demand Scanner (UDP Reader)                    │    │
│  │  Listens: 192.168.1.100:5100                       │    │
│  │  Accepts from: 192.168.1.51:* (optional filter)    │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
         ↑                                      ↓
         │                                      │
    ┌────┴────┐                          ┌─────┴─────┐
    │ Scanner │                          │    PLC    │
    │ Device  │                          │ Controller│
    └─────────┘                          └───────────┘
```

---

## Configuration Guide

### Network Setup Window

Access via: **Home Page → Network Setup**

### 1. Main Scanner Input Configuration

**Purpose**: Receive QR codes from the main scanner for sequence validation

**Settings**:
- **Local IP (this PC)**: IP address of the validator PC
  - Example: `192.168.1.100`
  - Use `0.0.0.0` to listen on all network interfaces
- **Local Port (listen)**: Port number to listen on
  - Example: `5000`
  - Range: 1-65535
- **Remote IP (scanner)**: IP address of the scanner device (optional filter)
  - Example: `192.168.1.50`
  - Leave empty to accept from any IP
- **Remote Port (scanner)**: Port number of the scanner (optional filter)
  - Example: `5001`
  - Leave empty to accept from any port

**Example Configuration**:
```
Local IP: 192.168.1.100
Local Port: 5000
Remote IP: 192.168.1.50 (optional)
Remote Port: (leave empty)
```

### 2. On-Demand Scanner Input Configuration

**Purpose**: Receive QR codes for card details and counting features

**Settings**:
- **Local IP (this PC)**: IP address of the validator PC
  - Example: `192.168.1.100`
- **Local Port (listen)**: Port number to listen on (must be different from main scanner)
  - Example: `5100`
- **Remote IP (scanner)**: IP address of the on-demand scanner (optional filter)
  - Example: `192.168.1.51`
  - Leave empty to accept from any IP
- **Remote Port (scanner)**: Port number of the scanner (optional filter)
  - Leave empty to accept from any port

**Example Configuration**:
```
Local IP: 192.168.1.100
Local Port: 5100
Remote IP: 192.168.1.51 (optional)
Remote Port: (leave empty)
```

### 3. Output Configuration

**Purpose**: Send validation results (OK/NOT OK/SKIPPED) to PLC or controller

**Settings**:
- **Local IP (this PC)**: IP address to send from
  - Example: `192.168.1.100`
  - Use `0.0.0.0` for automatic interface selection
- **Local Port (send from)**: Port to send from
  - Example: `0` (auto-assign)
  - Usually set to `0` for automatic assignment
- **Remote IP (PLC)**: IP address of the PLC/controller
  - Example: `192.168.1.200`
  - **Required**
- **Remote Port (PLC)**: Port number on the PLC/controller
  - Example: `6000`
  - **Required**

**Example Configuration**:
```
Local IP: 192.168.1.100
Local Port: 0 (auto-assign)
Remote IP: 192.168.1.200
Remote Port: 6000
```

---

## Network Requirements

### IP Address Planning

**Validator PC**: `192.168.1.100`
- Main Scanner Listener: Port 5000
- On-Demand Scanner Listener: Port 5100
- Output Sender: Auto-assigned port

**Main Scanner Device**: `192.168.1.50`
- Sends UDP packets to: `192.168.1.100:5000`

**On-Demand Scanner Device**: `192.168.1.51`
- Sends UDP packets to: `192.168.1.100:5100`

**PLC/Controller**: `192.168.1.200`
- Receives UDP packets on: Port 6000

### Firewall Configuration

**Windows Firewall Rules Required**:

1. **Inbound Rule for Main Scanner**:
   - Protocol: UDP
   - Local Port: 5000
   - Action: Allow

2. **Inbound Rule for On-Demand Scanner**:
   - Protocol: UDP
   - Local Port: 5100
   - Action: Allow

3. **Outbound Rule for PLC Output**:
   - Protocol: UDP
   - Remote IP: 192.168.1.200
   - Remote Port: 6000
   - Action: Allow

**PowerShell Commands** (Run as Administrator):
```powershell
# Allow inbound UDP on port 5000 (Main Scanner)
New-NetFirewallRule -DisplayName "Card Validator - Main Scanner" -Direction Inbound -Protocol UDP -LocalPort 5000 -Action Allow

# Allow inbound UDP on port 5100 (On-Demand Scanner)
New-NetFirewallRule -DisplayName "Card Validator - On-Demand Scanner" -Direction Inbound -Protocol UDP -LocalPort 5100 -Action Allow

# Allow outbound UDP to PLC
New-NetFirewallRule -DisplayName "Card Validator - PLC Output" -Direction Outbound -Protocol UDP -RemoteAddress 192.168.1.200 -RemotePort 6000 -Action Allow
```

---

## Scanner Device Configuration

### Configuring Network Scanners

Most modern barcode/QR scanners support UDP output. Configuration typically involves:

1. **Set Scanner to UDP Mode**
2. **Configure Target IP**: `192.168.1.100` (validator PC)
3. **Configure Target Port**: `5000` (main) or `5100` (on-demand)
4. **Set Scanner IP**: `192.168.1.50` or `192.168.1.51`
5. **Test Connection**: Scan a test QR code

### Example: Honeywell Scanner Configuration

```
Scanner Settings:
- Communication Mode: UDP
- Target IP: 192.168.1.100
- Target Port: 5000
- Scanner IP: 192.168.1.50
- Subnet Mask: 255.255.255.0
- Gateway: 192.168.1.1
```

### Example: Zebra Scanner Configuration

```
Scanner Settings:
- Interface: Ethernet/WiFi
- Protocol: UDP
- Destination IP: 192.168.1.100
- Destination Port: 5000
- Source IP: 192.168.1.50
```

---

## Testing UDP Communication

### Test Main Scanner Input

**Using PowerShell** (on another PC or same PC):
```powershell
# Send test QR code to main scanner port
$udpClient = New-Object System.Net.Sockets.UdpClient
$bytes = [System.Text.Encoding]::UTF8.GetBytes("TEST_QR_CODE_12345")
$udpClient.Send($bytes, $bytes.Length, "192.168.1.100", 5000)
$udpClient.Close()
```

**Using Python**:
```python
import socket

# Send test QR code
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
message = "TEST_QR_CODE_12345"
sock.sendto(message.encode(), ("192.168.1.100", 5000))
sock.close()
```

### Test Output to PLC

**Monitor on PLC side** (using Python):
```python
import socket

# Listen for output from validator
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("192.168.1.200", 6000))

print("Listening for validation results...")
while True:
    data, addr = sock.recvfrom(1024)
    print(f"Received from {addr}: {data.decode()}")
```

---

## Advantages of UDP over Serial

### Performance
- **No Baud Rate Limitations**: Network speed (100 Mbps+) vs serial (115200 bps max)
- **Parallel Processing**: Multiple scanners can send simultaneously
- **No Cable Length Limits**: Network cables can be 100m+ vs serial 15m max

### Flexibility
- **Remote Scanners**: Scanners can be anywhere on the network
- **Multiple Validators**: One scanner can send to multiple validators
- **Easy Expansion**: Add more scanners without physical ports

### Reliability
- **No COM Port Conflicts**: No need to manage COM port assignments
- **Hot-Swappable**: Scanners can be added/removed without restarting
- **Network Redundancy**: Can use multiple network paths

### Maintenance
- **Remote Configuration**: Configure scanners over network
- **Centralized Management**: All devices visible on network
- **Easier Troubleshooting**: Use network tools (ping, Wireshark)

---

## Troubleshooting

### Problem: "Not Connected" Status

**Check**:
1. Firewall rules are configured
2. IP addresses are correct
3. Ports are not in use by other applications
4. Network cable is connected

**Test**:
```powershell
# Check if port is listening
netstat -an | findstr "5000"
```

### Problem: No Data Received

**Check**:
1. Scanner is configured with correct target IP and port
2. Scanner and PC are on same network/subnet
3. Firewall is not blocking UDP packets
4. Scanner is sending data (check scanner logs)

**Test**:
```powershell
# Use Wireshark or tcpdump to monitor UDP traffic
# Filter: udp.port == 5000
```

### Problem: Output Not Reaching PLC

**Check**:
1. PLC IP and port are correct
2. PLC is listening on the configured port
3. Network route exists between PC and PLC
4. PLC firewall allows incoming UDP

**Test**:
```powershell
# Ping PLC
ping 192.168.1.200

# Check route
tracert 192.168.1.200
```

---

## Migration from Serial to UDP

### Step-by-Step Migration

1. **Document Current Serial Configuration**
   - Note COM port assignments
   - Note baud rates and settings
   - Note which scanner is which

2. **Configure Network Scanners**
   - Assign IP addresses to scanners
   - Configure UDP output mode
   - Set target IP (validator PC) and ports

3. **Configure Validator PC**
   - Open Network Setup window
   - Enter local IP and ports
   - Enter remote IPs (optional filters)
   - Configure output to PLC

4. **Configure Firewall**
   - Add inbound rules for scanner ports
   - Add outbound rule for PLC

5. **Test Each Component**
   - Test main scanner input
   - Test on-demand scanner input
   - Test output to PLC

6. **Verify Full Workflow**
   - Load a test file
   - Start validation
   - Scan cards
   - Verify output signals

### Rollback Plan

If you need to revert to serial communication:
1. Keep old serial cables and scanners
2. Backup current configuration
3. Reinstall previous version of software
4. Reconfigure COM ports

---

## Performance Comparison

### Serial (Before)

| Metric | Value |
|--------|-------|
| Max Baud Rate | 115,200 bps |
| Theoretical Speed | ~768 cards/second |
| Practical Speed | 2-10 cards/second |
| Cable Length | 15 meters max |
| Latency | 0.1-1 second |

### UDP (After)

| Metric | Value |
|--------|-------|
| Network Speed | 100 Mbps - 1 Gbps |
| Theoretical Speed | 10,000+ cards/second |
| Practical Speed | 2-15 cards/second (scanner limited) |
| Cable Length | 100 meters (copper), unlimited (fiber) |
| Latency | 0.001-0.01 seconds |

**Note**: Practical speed is still limited by scanner hardware, not communication protocol.

---

## Security Considerations

### Network Security

1. **Use Private Network**: Keep validator network isolated from internet
2. **VLAN Segmentation**: Separate validation network from corporate network
3. **IP Filtering**: Use remote IP filters to accept only from known scanners
4. **Firewall Rules**: Only allow necessary ports

### Access Control

1. **Physical Security**: Secure network equipment
2. **MAC Address Filtering**: Whitelist scanner MAC addresses on switches
3. **Network Monitoring**: Log all UDP traffic for audit

---

## Advanced Configuration

### Multiple Validators

**Scenario**: Two validator PCs on same network

**Validator 1**:
- IP: 192.168.1.100
- Main Scanner Port: 5000
- On-Demand Port: 5100

**Validator 2**:
- IP: 192.168.1.101
- Main Scanner Port: 5000
- On-Demand Port: 5100

**Scanners**: Configure to send to specific validator IP

### Load Balancing

**Scenario**: Distribute scans across multiple validators

**Implementation**:
- Use network load balancer
- Round-robin DNS
- Scanner-side logic to alternate targets

### Redundancy

**Scenario**: Backup validator for high availability

**Implementation**:
- Primary validator: 192.168.1.100
- Backup validator: 192.168.1.101
- Scanners configured with both IPs
- Automatic failover on primary failure

---

## Summary

The UDP migration provides:
- ✅ Faster communication
- ✅ Greater flexibility
- ✅ Easier expansion
- ✅ Better reliability
- ✅ Simplified maintenance

**Key Changes**:
- Serial COM ports → UDP IP:Port
- Baud rate settings → Network configuration
- Physical cables → Network infrastructure
- COM Port Setup → Network Setup

**Next Steps**:
1. Configure network infrastructure
2. Set up firewall rules
3. Configure scanners for UDP
4. Test thoroughly before production use

---

**Document Version**: 1.0  
**Last Updated**: February 8, 2026  
**Project**: Card Sequence Validator - UDP Migration
