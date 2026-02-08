# PySerial Quick Reference - Card Sequence Validator

## Quick Facts

**Library**: PySerial 3.5+  
**Purpose**: Serial communication with barcode scanners and external devices  
**Components**: 2 readers (input) + 1 writer (output)  
**Threading**: Non-blocking background threads for reading  
**Performance**: <5% CPU, handles 10+ cards/second  

---

## Key Classes

### ComPortReader (Input)
```python
# Location: src/app_state.py lines 41-97
# Purpose: Read from scanners
# Method: Threaded, non-blocking
# Instances: 2 (Main + On-Demand)
```

### ComPortWriter (Output)
```python
# Location: src/services/com_writer.py
# Purpose: Send signals to devices
# Method: Synchronous
# Instances: 1 (Output port)
```

---

## Essential PySerial Methods

### Opening a Port
```python
import serial

ser = serial.Serial(
    port='COM3',
    baudrate=115200,
    bytesize=8,
    parity='N',
    stopbits=1,
    timeout=0.1
)
```

### Reading Data
```python
# Check if data available
if ser.in_waiting > 0:
    # Read up to 256 bytes
    data = ser.read(256)
    # Decode to string
    text = data.decode('utf-8')
```

### Writing Data
```python
# Encode string to bytes
message = "OK\r\n".encode('utf-8')
# Write to port
ser.write(message)
```

### Closing Port
```python
if ser.is_open:
    ser.close()
```

### Listing Ports
```python
import serial.tools.list_ports

ports = [port.device for port in serial.tools.list_ports.comports()]
# Returns: ['COM1', 'COM3', 'COM5']
```

---

## Configuration Parameters

| Parameter | Default | Options | Purpose |
|-----------|---------|---------|---------|
| baudrate | 115200 | 9600-115200 | Communication speed |
| bytesize | 8 | 5,6,7,8 | Character size |
| parity | 'N' | N,E,O | Error detection |
| stopbits | 1 | 1,1.5,2 | Frame ending |
| timeout | 0.1 | 0.02-5.0 | Read timeout (seconds) |

---

## Threading Model

```
Main Thread (UI)
    └─ Creates ComPortReader
           └─ Background Thread
                  └─ Continuous read_loop()
                         └─ callback() → Main Thread
```

**Key Features:**
- Daemon threads (auto-cleanup)
- Pause/resume mechanism
- Thread-safe callbacks

---

## Data Flow

### Reading
```
Scanner → PySerial.read() → bytes → decode() → string
    → clean() → callback() → validate() → log → UI
```

### Writing
```
Result → lookup signal → encode() → bytes
    → PySerial.write() → External Device
```

---

## Common Patterns

### Start Reading
```python
reader = ComPortReader(
    port='COM3',
    baudrate=115200,
    callback=self.handle_data
)
reader.start_reading()
```

### Stop Reading
```python
reader.stop_reading()  # Closes port and stops thread
```

### Pause/Resume
```python
reader.pause()   # Temporarily stop reading
reader.resume()  # Continue reading
```

### Send Output
```python
writer = ComPortWriter()
writer.connect('COM5', 115200)
writer.send("OK\r\n")
writer.disconnect()
```

---

## Error Handling

```python
try:
    ser = serial.Serial('COM3', 115200)
except serial.SerialException as e:
    print(f"Error: {e}")
    # Common errors:
    # - Port doesn't exist
    # - Port in use
    # - Permission denied
```

---

## Performance Tips

1. **Buffer Size**: Read 256 bytes at once
2. **Timeout**: Use 0.05-0.1s for best balance
3. **Threading**: Always use background threads for reading
4. **Cleanup**: Always close ports in finally blocks

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port not found | Check Device Manager, verify port name |
| Access denied | Close other apps, run as admin |
| Garbled data | Check baud rate matches device |
| No data | Increase timeout, verify device sending |

---

## File Locations

- **ComPortReader**: `src/app_state.py` lines 41-97
- **ComPortWriter**: `src/services/com_writer.py`
- **Port Enumeration**: `src/app_state.py` line 158, `src/ui/com_port_setup.py` line 92

---

## Complete Documentation

- **Full Guide**: `PYSERIAL_IMPLEMENTATION_GUIDE.md` (800+ lines)
- **Visual Diagrams**: `PYSERIAL_VISUAL_DIAGRAMS.md`
- **Q&A**: `PROJECT_QA.md` (PySerial section)

---

**Quick Start**: Import `serial`, open port with `Serial()`, read with `read()`, write with `write()`, close with `close()`.

**Remember**: Always close ports, use threads for reading, handle exceptions gracefully!
