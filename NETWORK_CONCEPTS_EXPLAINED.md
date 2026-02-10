# Network Concepts Explained - IP Addresses & Ports

## 🎯 Simple Explanation

Think of your network setup like a **postal system**:

- **IP Address** = Street Address (where to send/receive)
- **Port** = Apartment Number (which specific door)
- **Local** = Your building (this PC)
- **Remote** = Another building (scanner/PLC)

---

## 📥 Main Scanner Input (UDP) - RECEIVING Data

### Purpose
Your PC **listens** for QR code data coming FROM the scanner.

### Configuration Fields

```
┌─────────────────────────────────────────────────────┐
│ Main Scanner Input (UDP)                            │
├─────────────────────────────────────────────────────┤
│ Local IP (this PC):      192.168.1.100 (Ethernet)  │ ← YOUR PC's address
│ Local Port (listen):     5000                       │ ← YOUR PC's door number
│ Remote IP (scanner):     192.168.1.50               │ ← Scanner's address (optional)
│ Remote Port (scanner):   5001                       │ ← Scanner's door number (optional)
└─────────────────────────────────────────────────────┘
```

### What Each Field Means

#### 1. **Local IP (this PC)** - WHERE your PC listens
```
Example: 192.168.1.100

What it means:
- This is YOUR PC's network address
- The Ethernet adapter that will RECEIVE scanner data
- Like your building's street address

Why it matters:
- If you have multiple Ethernet ports, this tells the PC
  which one to use for receiving scanner data
- Must be on the same network as the scanner
```

#### 2. **Local Port (listen)** - WHICH door your PC listens on
```
Example: 5000

What it means:
- This is the "door number" on your PC
- Your PC will LISTEN on this port for incoming data
- Like an apartment number in your building

Why it matters:
- Multiple programs can use the same IP but different ports
- Scanner must send data to THIS port number
- Common ports: 5000, 5001, 5002, etc.
```

#### 3. **Remote IP (scanner)** - WHO can send to you (OPTIONAL)
```
Example: 192.168.1.50

What it means:
- This is the SCANNER's network address
- If specified, ONLY accept data from this IP
- Like saying "only accept mail from this address"

Why it matters:
- Security: Ignore data from other devices
- If left empty: Accept data from ANY device
- Useful when you have multiple scanners
```

#### 4. **Remote Port (scanner)** - WHICH door scanner sends from (OPTIONAL)
```
Example: 5001

What it means:
- This is the port the SCANNER sends from
- If specified, ONLY accept data from this port
- Like saying "only accept mail from apartment #5001"

Why it matters:
- Additional filtering
- Usually left empty (accept from any port)
- Rarely needed unless very specific setup
```

### Visual Flow - Main Scanner Input

```
SCANNER (Remote)                    YOUR PC (Local)
192.168.1.50:5001                   192.168.1.100:5000
┌──────────────┐                    ┌──────────────┐
│              │                    │              │
│   Scanner    │  ─────────────>   │   Your PC    │
│              │   QR Code Data     │              │
│  Sends from  │                    │  Listens on  │
│  Port 5001   │                    │  Port 5000   │
└──────────────┘                    └──────────────┘

Flow:
1. Scanner scans QR code
2. Scanner sends data FROM 192.168.1.50:5001
3. Data travels over network
4. Your PC receives data ON 192.168.1.100:5000
5. Your application processes the QR code
```

### Real-World Example

```
Scenario: Scanner sends QR code "ABC123"

Scanner Configuration:
- Scanner IP: 192.168.1.50
- Send to IP: 192.168.1.100
- Send to Port: 5000

Your PC Configuration:
- Local IP: 192.168.1.100 ✓ (matches scanner's target)
- Local Port: 5000 ✓ (matches scanner's target port)
- Remote IP: 192.168.1.50 (optional - only accept from scanner)
- Remote Port: (empty - accept from any port)

Result: ✓ QR code received successfully!
```

---

## 📤 Output Configuration (UDP) - SENDING Data

### Purpose
Your PC **sends** validation results TO the PLC/controller.

### Configuration Fields

```
┌─────────────────────────────────────────────────────┐
│ Output Configuration (UDP)                          │
├─────────────────────────────────────────────────────┤
│ Local IP (this PC):      192.168.2.100 (Ethernet 2)│ ← YOUR PC's address
│ Local Port (send from):  0 (auto-assign)           │ ← YOUR PC's door number
│ Remote IP (PLC):         192.168.2.50               │ ← PLC's address
│ Remote Port (PLC):       6000                       │ ← PLC's door number
└─────────────────────────────────────────────────────┘
```

### What Each Field Means

#### 1. **Local IP (this PC)** - WHERE your PC sends from
```
Example: 192.168.2.100

What it means:
- This is YOUR PC's network address
- The Ethernet adapter that will SEND to PLC
- Like your building's return address

Why it matters:
- If you have multiple Ethernet ports, this tells the PC
  which one to use for sending to PLC
- Must be on the same network as the PLC
- Can be same or different from scanner input IP
```

#### 2. **Local Port (send from)** - WHICH door your PC sends from
```
Example: 0 (auto-assign) or 5000

What it means:
- This is the "door number" your PC sends from
- 0 = Let the system choose automatically (recommended)
- Like which mailbox you use to send mail

Why it matters:
- Usually set to 0 (auto-assign)
- System picks an available port automatically
- Rarely needs to be changed
```

#### 3. **Remote IP (PLC)** - WHERE to send data (REQUIRED)
```
Example: 192.168.2.50

What it means:
- This is the PLC's network address
- Your PC will SEND validation results to this IP
- Like the destination address on an envelope

Why it matters:
- REQUIRED - must specify where to send
- Must be the actual PLC's IP address
- Must be reachable from your PC
```

#### 4. **Remote Port (PLC)** - WHICH door on PLC to send to (REQUIRED)
```
Example: 6000

What it means:
- This is the port the PLC is LISTENING on
- Your PC will SEND data to this port
- Like the apartment number at destination

Why it matters:
- REQUIRED - must specify which port
- Must match what PLC is configured to listen on
- Common PLC ports: 6000, 6001, 6002, etc.
```

### Visual Flow - Output Configuration

```
YOUR PC (Local)                     PLC (Remote)
192.168.2.100:0                     192.168.2.50:6000
┌──────────────┐                    ┌──────────────┐
│              │                    │              │
│   Your PC    │  ─────────────>    │     PLC      │
│              │  Validation Result │              │
│  Sends from  │                    │  Listens on  │
│  Port (auto) │                    │  Port 6000   │
└──────────────┘                    └──────────────┘

Flow:
1. Your PC validates QR code
2. Your PC sends result FROM 192.168.2.100:(auto)
3. Data travels over network
4. PLC receives data ON 192.168.2.50:6000
5. PLC processes the validation result
```

### Real-World Example

```
Scenario: Send "PASS" signal to PLC

Your PC Configuration:
- Local IP: 192.168.2.100
- Local Port: 0 (auto-assign)
- Remote IP: 192.168.2.50 ✓ (PLC's address)
- Remote Port: 6000 ✓ (PLC's listening port)

PLC Configuration:
- PLC IP: 192.168.2.50
- Listen on Port: 6000

Result: ✓ PLC receives "PASS" signal successfully!
```

---

## 🔄 Complete System Flow

### Scenario: Two Separate Networks

```
SCANNER NETWORK (192.168.1.x)          PLC NETWORK (192.168.2.x)
┌─────────────────────────┐            ┌─────────────────────────┐
│                         │            │                         │
│  Scanner                │            │  PLC                    │
│  192.168.1.50:5001      │            │  192.168.2.50:6000      │
│  ┌──────────┐           │            │  ┌──────────┐           │
│  │ Sends QR │           │            │  │ Receives │           │
│  │   Code   │           │            │  │  Result  │           │
│  └────┬─────┘           │            │  └────▲─────┘           │
│       │                 │            │       │                 │
│       │ QR: "ABC123"    │            │       │ Result: "PASS"  │
│       │                 │            │       │                 │
│       ▼                 │            │       │                 │
│  ┌─────────────────┐   │            │  ┌─────────────────┐   │
│  │  Ethernet 1     │   │            │  │  Ethernet 2     │   │
│  │  192.168.1.100  │   │            │  │  192.168.2.100  │   │
│  │  Port 5000      │◄──┼────────────┼──┤  Port (auto)    │   │
│  └────────┬────────┘   │            │  └────────▲────────┘   │
│           │            │            │           │            │
└───────────┼────────────┘            └───────────┼────────────┘
            │                                     │
            │         YOUR PC                     │
            │    ┌─────────────────┐             │
            └────┤  1. Receive QR  │             │
                 │  2. Validate    │             │
                 │  3. Send Result ├─────────────┘
                 └─────────────────┘
```

### Step-by-Step Flow

**Step 1: Scanner Sends QR Code**
```
Scanner (192.168.1.50:5001)
    ↓ Sends "ABC123"
Your PC Ethernet 1 (192.168.1.100:5000)
    ↓ Receives
Your Application
```

**Step 2: Your PC Validates**
```
Your Application
    ↓ Validates "ABC123"
    ↓ Result: "PASS"
```

**Step 3: Your PC Sends to PLC**
```
Your Application
    ↓ Sends "PASS"
Your PC Ethernet 2 (192.168.2.100:auto)
    ↓ Sends
PLC (192.168.2.50:6000)
    ↓ Receives
PLC Processes Result
```

---

## 🎓 Key Concepts

### Local vs Remote

| Term | Meaning | Example |
|------|---------|---------|
| **Local** | Your PC | 192.168.1.100 |
| **Remote** | Other device | 192.168.1.50 (scanner) |

### IP Address vs Port

| Concept | Analogy | Example |
|---------|---------|---------|
| **IP Address** | Building address | 192.168.1.100 |
| **Port** | Apartment number | 5000 |
| **Together** | Complete address | 192.168.1.100:5000 |

### Input vs Output

| Direction | Purpose | Configuration |
|-----------|---------|---------------|
| **Input** | Receive from scanner | Local IP + Port (where to listen) |
| **Output** | Send to PLC | Remote IP + Port (where to send) |

---

## 📊 Common Configurations

### Configuration 1: Same Network

**Scenario:** Scanner and PLC on same network

```
Network: 192.168.1.x

Scanner:     192.168.1.50
Your PC:     192.168.1.100
PLC:         192.168.1.60

Main Scanner Input:
  Local IP: 192.168.1.100 (Ethernet)
  Local Port: 5000
  Remote IP: 192.168.1.50 (scanner)

Output Configuration:
  Local IP: 192.168.1.100 (same Ethernet)
  Local Port: 0
  Remote IP: 192.168.1.60 (PLC)
  Remote Port: 6000
```

### Configuration 2: Separate Networks

**Scenario:** Scanner on one network, PLC on another

```
Scanner Network: 192.168.1.x
PLC Network:     192.168.2.x

Scanner:     192.168.1.50
Your PC:     192.168.1.100 (Ethernet 1)
             192.168.2.100 (Ethernet 2)
PLC:         192.168.2.50

Main Scanner Input:
  Local IP: 192.168.1.100 (Ethernet 1)
  Local Port: 5000
  Remote IP: 192.168.1.50 (scanner)

Output Configuration:
  Local IP: 192.168.2.100 (Ethernet 2)
  Local Port: 0
  Remote IP: 192.168.2.50 (PLC)
  Remote Port: 6000
```

---

## 🔍 Troubleshooting Guide

### Problem: Not Receiving Scanner Data

**Check:**
1. ✓ Local IP matches your PC's Ethernet adapter
2. ✓ Local Port matches scanner's target port
3. ✓ Scanner is sending to correct IP:Port
4. ✓ Network cable connected
5. ✓ Firewall not blocking port

**Test:**
```
Click "🔍 Test Connection"
Look for:
  ✓ Ping successful: 192.168.1.100
  ✓ Can bind to 192.168.1.100:5000
  ✓ Scanner reachable: 192.168.1.50
```

### Problem: PLC Not Receiving Data

**Check:**
1. ✓ Remote IP matches PLC's actual IP
2. ✓ Remote Port matches PLC's listening port
3. ✓ PLC is powered on and connected
4. ✓ Network cable connected
5. ✓ Same subnet (e.g., both 192.168.2.x)

**Test:**
```
Click "🔍 Test Connection"
Look for:
  ✓ Ping successful: 192.168.2.100
  ✓ Can bind to 192.168.2.100:0
  ✓ PLC reachable: 192.168.2.50
```

---

## 💡 Pro Tips

### Tip 1: Use Specific IPs (Not 0.0.0.0)
```
❌ Bad:  Local IP: 0.0.0.0 (All interfaces)
✓ Good: Local IP: 192.168.1.100 (Ethernet)

Why: On multi-NIC systems, 0.0.0.0 causes routing ambiguity
```

### Tip 2: Keep Networks Separate
```
✓ Good Setup:
  Scanner Network: 192.168.1.x (Ethernet 1)
  PLC Network:     192.168.2.x (Ethernet 2)

Why: Clear separation, no interference
```

### Tip 3: Use Standard Ports
```
Scanner Input:  5000, 5001, 5002
PLC Output:     6000, 6001, 6002

Why: Easy to remember, avoid conflicts
```

### Tip 4: Test Before Operating
```
Always click "🔍 Test Connection" before starting
Verify all tests pass (✓)
```

### Tip 5: Document Your Setup
```
Write down:
- Scanner IP and port
- Your PC IPs (both Ethernet adapters)
- PLC IP and port
- Which Ethernet connects to what
```

---

## 📝 Quick Reference

### Main Scanner Input (Receiving)
```
Local IP:     YOUR PC's address (which Ethernet to use)
Local Port:   YOUR PC's door (where to listen)
Remote IP:    Scanner's address (optional filter)
Remote Port:  Scanner's door (optional filter)
```

### Output Configuration (Sending)
```
Local IP:     YOUR PC's address (which Ethernet to use)
Local Port:   YOUR PC's door (usually 0 = auto)
Remote IP:    PLC's address (where to send) ← REQUIRED
Remote Port:  PLC's door (where to send) ← REQUIRED
```

### Remember
- **Local** = Your PC
- **Remote** = Other device
- **IP** = Building address
- **Port** = Apartment number
- **Input** = Receive (listen)
- **Output** = Send (transmit)

---

## 🎯 Summary

**Main Scanner Input:**
- Your PC **LISTENS** for QR codes
- Configure: Where YOUR PC listens (Local IP:Port)
- Optional: Filter who can send (Remote IP:Port)

**Output Configuration:**
- Your PC **SENDS** validation results
- Configure: Where PLC listens (Remote IP:Port)
- Optional: Which Ethernet to use (Local IP)

**Key Rule:**
Always use **specific Ethernet IPs** (not 0.0.0.0) on multi-NIC systems for reliable communication!

---

Need help? Click "🔍 Test Connection" to diagnose issues!
