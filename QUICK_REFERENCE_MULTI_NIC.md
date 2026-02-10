# Multi-NIC Fix - Quick Reference Card

## 🚀 Quick Start (3 Steps)

### Step 1: Install psutil
```bash
pip install psutil
```

### Step 2: Configure Interfaces
```
Main Scanner:  192.168.1.100 (Ethernet - UP) → Port 5000
Output PLC:    192.168.2.100 (Ethernet 2 - UP) → Port 6000
```

### Step 3: Test & Apply
```
Click "🔍 Test Connection" → Verify all ✓ → Click "Apply Configuration"
```

---

## 🎯 Key Features

| Feature | Status | Description |
|---------|--------|-------------|
| **Ethernet Detection** | ✅ | Auto-detect operational Ethernet interfaces |
| **Virtual Filter** | ✅ | Exclude VMware, VirtualBox, VPN adapters |
| **Status Display** | ✅ | Show UP/DOWN status for each interface |
| **Specific Binding** | ✅ | Bind to specific IP (not 0.0.0.0) |
| **Connection Test** | ✅ | Built-in ping + socket bind tests |
| **Dropdown Ports** | ✅ | Preset port values with custom input |
| **Styled Buttons** | ✅ | Refresh buttons with hover effects |

---

## 🔧 Configuration Examples

### Two Separate Networks
```
Ethernet 1: 192.168.1.100 → Scanner Network
Ethernet 2: 192.168.2.100 → PLC Network

Main Scanner Input:
  Local IP: 192.168.1.100 (Ethernet - UP)
  Local Port: 5000
  Remote IP: 192.168.1.50

Output Configuration:
  Local IP: 192.168.2.100 (Ethernet 2 - UP)
  Local Port: 0
  Remote IP: 192.168.2.50
  Remote Port: 6000
```

### Same Network
```
Ethernet: 192.168.1.100 → Industrial Network

Main Scanner Input:
  Local IP: 192.168.1.100 (Ethernet - UP)
  Local Port: 5000
  Remote IP: 192.168.1.50

Output Configuration:
  Local IP: 192.168.1.100 (Ethernet - UP)
  Local Port: 0
  Remote IP: 192.168.1.60
  Remote Port: 6000
```

---

## 🧪 Testing

### Run Test Script
```bash
python test_multi_nic_detection.py
```

### Expected Output
```
✓ Found 2 operational Ethernet interface(s)
✓ Socket Binding: 2/2 successful
✓ All tests passed!
```

### In-App Testing
```
1. Open "Network & COM Setup"
2. Click "🔍 Test Connection"
3. Check Connection Log for results:
   ✓ Ping successful: 192.168.1.100
   ✓ Can bind to 192.168.1.100:5000
   ✓ Scanner reachable: 192.168.1.50
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| **No interfaces shown** | `pip install psutil` |
| **Interface shows DOWN** | Check network cable, enable adapter |
| **Cannot bind to port** | `netstat -an \| findstr :5000` → Close other app |
| **Remote not reachable** | `ping 192.168.1.50` → Check device power/IP |
| **psutil not found** | `pip install psutil` → Restart app |

---

## 📋 Port Presets

### Main Scanner Ports
```
5000 (default), 5001, 5002, 5003, 5004, 5005
6000, 7000, 8000, 9000
```

### Output/PLC Ports
```
6000 (default), 6001, 6002
5000, 5001, 7000, 8000, 9000, 10000
```

### Timeout Values
```
0.5s, 1s (default), 1.5s, 2s, 3s, 5s, 10s
```

---

## 🎨 UI Elements

### Buttons
- **Apply Configuration** - Save and activate settings
- **🔍 Test Connection** - Test connectivity (ping + bind)
- **Disconnect All** - Stop all connections
- **🔄 Refresh Network** - Re-scan interfaces

### Dropdowns
- **Local IP** - Select Ethernet interface (editable)
- **Local Port** - Select port or type custom (editable)
- **Remote IP** - Select or type device IP (editable)
- **Remote Port** - Select port or type custom (editable)

### Status Colors
- 🟢 **Green** - Connected and working
- 🔴 **Red** - Error or not connected
- 🟠 **Orange** - Warning or partial connection
- 🔵 **Blue** - Information message

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `MULTI_NIC_UDP_BINDING_FIX.md` | Technical details |
| `QUICK_SETUP_MULTI_NIC.md` | Setup guide |
| `IMPLEMENTATION_SUMMARY_MULTI_NIC.md` | Implementation summary |
| `UI_IMPROVEMENTS_DROPDOWNS.md` | UI changes |
| `MULTI_NIC_VERIFICATION_COMPLETE.md` | Verification checklist |
| `test_multi_nic_detection.py` | Test script |

---

## ⚡ Quick Commands

```bash
# Install dependencies
pip install psutil

# Run test script
python test_multi_nic_detection.py

# Check network interfaces
ipconfig /all

# Test connectivity
ping 192.168.1.50

# Check port usage
netstat -an | findstr :5000

# Launch application
python main.py
```

---

## ✅ Verification Checklist

Before going live:
- [ ] psutil installed
- [ ] Interfaces detected correctly
- [ ] Virtual adapters filtered out
- [ ] Test Connection passes all tests
- [ ] Scanner receives on correct interface
- [ ] PLC sends on correct interface
- [ ] Configuration saves/loads correctly

---

## 🎯 Key Differences

| Aspect | Before (0.0.0.0) | After (Specific IP) |
|--------|------------------|---------------------|
| **Routing** | OS decides (unreliable) | User decides (reliable) |
| **Multi-NIC** | ❌ Fails | ✅ Works |
| **Testing** | Manual | Built-in |
| **Interface Info** | None | Name + Status |
| **Virtual Adapters** | Shown | Filtered |

---

## 💡 Pro Tips

1. **Always use specific IPs** on multi-NIC systems (not 0.0.0.0)
2. **Test before applying** - Use "🔍 Test Connection" button
3. **Check interface status** - Only use UP interfaces
4. **Verify subnet** - Local and remote IPs should match (e.g., 192.168.1.x)
5. **Use presets** - Click dropdown for common port values
6. **Refresh when needed** - Click 🔄 if network changes

---

## 🆘 Support

**Issue:** Something not working?

**Steps:**
1. Run `python test_multi_nic_detection.py`
2. Check Connection Log in app
3. Verify psutil installed: `pip show psutil`
4. Check network cables and device power
5. Review documentation files above

---

**Status:** ✅ READY FOR PRODUCTION

**Last Updated:** 2024

**Version:** 1.0.0
