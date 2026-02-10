# Simple Network Guide - IP & Port Explained

## 🏠 Think of it Like a Building

```
IP Address = Street Address (which building)
Port = Apartment Number (which door in the building)
```

---

## 📥 INPUT (Main Scanner) - You RECEIVE Data

### What You Configure

```
┌─────────────────────────────────────────┐
│ YOUR PC (Listening for scanner data)   │
├─────────────────────────────────────────┤
│ Local IP:   192.168.1.100              │ ← Your building address
│ Local Port: 5000                        │ ← Your apartment number
└─────────────────────────────────────────┘
```

### Simple Explanation

**Local IP (Your PC):**
- This is YOUR computer's address
- Like: "123 Main Street" (your building)
- Example: 192.168.1.100

**Local Port (Your PC):**
- This is the "door number" on your computer
- Like: "Apartment #5000" (your door)
- Example: 5000

**Together:** Your PC listens at "192.168.1.100:5000"
- Like: "123 Main Street, Apartment #5000"

### Visual

```
SCANNER                          YOUR PC
(Sends QR Code)                  (Receives QR Code)

192.168.1.50                     192.168.1.100:5000
┌──────────┐                     ┌──────────┐
│          │  ───QR Code───>     │          │
│ Scanner  │     "ABC123"        │ Your PC  │
│          │                     │ Listening│
└──────────┘                     └──────────┘

Scanner sends TO: 192.168.1.100:5000
Your PC listens ON: 192.168.1.100:5000
✓ Match! Data received!
```

---

## 📤 OUTPUT (PLC) - You SEND Data

### What You Configure

```
┌─────────────────────────────────────────┐
│ PLC (Waiting for your validation)      │
├─────────────────────────────────────────┤
│ Remote IP:   192.168.2.50              │ ← PLC's building address
│ Remote Port: 6000                       │ ← PLC's apartment number
└─────────────────────────────────────────┘
```

### Simple Explanation

**Remote IP (PLC):**
- This is the PLC's address
- Like: "456 Industrial Ave" (PLC's building)
- Example: 192.168.2.50

**Remote Port (PLC):**
- This is the "door number" on the PLC
- Like: "Apartment #6000" (PLC's door)
- Example: 6000

**Together:** You send to "192.168.2.50:6000"
- Like: Sending mail to "456 Industrial Ave, Apartment #6000"

### Visual

```
YOUR PC                          PLC
(Sends Result)                   (Receives Result)

192.168.2.100                    192.168.2.50:6000
┌──────────┐                     ┌──────────┐
│          │  ───Result───>      │          │
│ Your PC  │     "PASS"          │   PLC    │
│ Sending  │                     │ Listening│
└──────────┘                     └──────────┘

Your PC sends TO: 192.168.2.50:6000
PLC listens ON: 192.168.2.50:6000
✓ Match! Data received!
```

---

## 🔄 Complete Flow (Simple)

```
Step 1: Scanner sends QR code to YOUR PC
   Scanner (192.168.1.50)
      ↓ Sends "ABC123"
   Your PC (192.168.1.100:5000)
      ↓ Receives

Step 2: Your PC validates the QR code
   Your PC
      ↓ Checks "ABC123"
      ↓ Result: "PASS"

Step 3: Your PC sends result to PLC
   Your PC (192.168.2.100)
      ↓ Sends "PASS"
   PLC (192.168.2.50:6000)
      ↓ Receives
```

---

## 🎯 Key Rules

### Rule 1: Local = Your PC
```
Local IP:   YOUR computer's address
Local Port: YOUR computer's door number
```

### Rule 2: Remote = Other Device
```
Remote IP:   OTHER device's address (scanner or PLC)
Remote Port: OTHER device's door number
```

### Rule 3: Input = Receive
```
Main Scanner Input:
- You LISTEN for data coming IN
- Configure YOUR address (Local IP:Port)
```

### Rule 4: Output = Send
```
Output Configuration:
- You SEND data going OUT
- Configure PLC's address (Remote IP:Port)
```

---

## 📋 Configuration Checklist

### For Scanner Input (Receiving)

**What you need to know:**
1. ✓ Your PC's IP address (e.g., 192.168.1.100)
2. ✓ Which port to listen on (e.g., 5000)
3. ✓ Scanner's IP address (optional, e.g., 192.168.1.50)

**Configuration:**
```
Local IP:   192.168.1.100  ← Your PC
Local Port: 5000           ← Your listening port
Remote IP:  192.168.1.50   ← Scanner (optional filter)
```

### For PLC Output (Sending)

**What you need to know:**
1. ✓ PLC's IP address (e.g., 192.168.2.50)
2. ✓ PLC's listening port (e.g., 6000)
3. ✓ Your PC's IP address (e.g., 192.168.2.100)

**Configuration:**
```
Local IP:   192.168.2.100  ← Your PC
Remote IP:  192.168.2.50   ← PLC
Remote Port: 6000          ← PLC's listening port
```

---

## 🔍 Common Questions

### Q: What is 0.0.0.0?
```
A: "All interfaces" - means listen on ALL network adapters
   ❌ Don't use on multi-NIC systems (causes problems)
   ✓ Use specific IP like 192.168.1.100
```

### Q: What is port 0?
```
A: "Auto-assign" - let system choose an available port
   ✓ Good for Local Port when sending (Output)
   ❌ Don't use for Local Port when receiving (Input)
```

### Q: Why two different IPs?
```
A: If you have two Ethernet ports:
   - Ethernet 1: 192.168.1.100 (for scanner)
   - Ethernet 2: 192.168.2.100 (for PLC)
   
   This keeps networks separate and organized
```

### Q: What if scanner and PLC are on same network?
```
A: Use same Local IP for both:
   
   Scanner Input:
     Local IP: 192.168.1.100
   
   PLC Output:
     Local IP: 192.168.1.100 (same!)
```

---

## 🎨 Visual Summary

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR PC                              │
│                                                         │
│  INPUT (Receive from Scanner)                          │
│  ┌─────────────────────────────┐                       │
│  │ Local IP:   192.168.1.100   │ ← Your address       │
│  │ Local Port: 5000            │ ← Your door          │
│  └─────────────────────────────┘                       │
│              ▲                                          │
│              │ QR Code Data                            │
│              │                                          │
│  ┌───────────┴──────────┐                              │
│  │   Process & Validate │                              │
│  └───────────┬──────────┘                              │
│              │                                          │
│              │ Validation Result                        │
│              ▼                                          │
│  OUTPUT (Send to PLC)                                  │
│  ┌─────────────────────────────┐                       │
│  │ Remote IP:   192.168.2.50   │ ← PLC's address      │
│  │ Remote Port: 6000           │ ← PLC's door         │
│  └─────────────────────────────┘                       │
└─────────────────────────────────────────────────────────┘
```

---

## 💡 Quick Tips

1. **Always test first**
   - Click "🔍 Test Connection" button
   - Make sure all tests pass (✓)

2. **Use specific IPs**
   - Don't use 0.0.0.0 on multi-NIC systems
   - Select actual Ethernet adapter IP

3. **Write it down**
   - Document your IP addresses
   - Keep a note of port numbers

4. **Same subnet**
   - Scanner and your PC should be 192.168.1.x
   - PLC and your PC should be 192.168.2.x
   - First three numbers should match!

5. **Check cables**
   - Make sure network cables are plugged in
   - Check that devices are powered on

---

## 🚀 Quick Start Example

### Scenario: Simple Setup

**Your Equipment:**
- Scanner IP: 192.168.1.50
- Your PC IP: 192.168.1.100
- PLC IP: 192.168.1.60
- All on same network (192.168.1.x)

**Configuration:**

```
Main Scanner Input:
  Local IP:   192.168.1.100  ← Your PC
  Local Port: 5000           ← Listen here
  Remote IP:  192.168.1.50   ← Scanner

Output Configuration:
  Local IP:   192.168.1.100  ← Your PC (same)
  Local Port: 0              ← Auto
  Remote IP:  192.168.1.60   ← PLC
  Remote Port: 6000          ← PLC listens here
```

**Test:**
1. Click "🔍 Test Connection"
2. Should see:
   - ✓ Ping successful: 192.168.1.100
   - ✓ Can bind to 192.168.1.100:5000
   - ✓ Scanner reachable: 192.168.1.50
   - ✓ PLC reachable: 192.168.1.60

3. Click "Apply Configuration"
4. Start scanning!

---

## 📞 Need Help?

**If scanner not working:**
- Check Local IP matches your PC
- Check Local Port matches scanner's target
- Click "🔍 Test Connection"

**If PLC not working:**
- Check Remote IP matches PLC
- Check Remote Port matches PLC's listening port
- Click "🔍 Test Connection"

**Still stuck?**
- Check network cables
- Verify device power
- Ping devices: `ping 192.168.1.50`

---

## ✅ Remember

```
INPUT (Scanner):
  Local = YOUR PC (where you listen)
  
OUTPUT (PLC):
  Remote = PLC (where you send)

IP = Building Address
Port = Apartment Number

Test before you start!
```

---

**That's it! You're ready to configure your network!** 🎉
