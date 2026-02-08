# PySerial Visual Diagrams - Card Sequence Validator

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Card Sequence Validator                      │
│                        (PyQt6 Application)                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │ComPortReader │ │ComPortReader │ │ComPortWriter │
        │  (Thread 1)  │ │  (Thread 2)  │ │ (Synchronous)│
        │              │ │              │ │              │
        │ Main Scanner │ │  On-Demand   │ │    Output    │
        └──────────────┘ └──────────────┘ └──────────────┘
                │               │               │
                │               │               │
                ▼               ▼               ▼
        ┌──────────────────────────────────────────────┐
        │            PySerial Library                   │
        │         (serial.Serial objects)               │
        └──────────────────────────────────────────────┘
                │               │               │
                │               │               │
                ▼               ▼               ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │   Scanner    │ │   Scanner    │ │     PLC/     │
        │   (COM3)     │ │   (COM5)     │ │  Controller  │
        │              │ │              │ │   (COM7)     │
        └──────────────┘ └──────────────┘ └──────────────┘
```

---

## ComPortReader Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Scanner Device                            │
│                  (Barcode Scanner)                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Scan QR Code
                            │ (Serial Data: "QR123456\r\n")
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  PySerial: serial.Serial                     │
│  Port: COM3, Baud: 115200, Data: 8, Parity: N, Stop: 1     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ in_waiting > 0?
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              read(256) → bytes object                        │
│         b'QR123456\r\n' (raw bytes)                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ decode('utf-8')
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                String: "QR123456\r\n"                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ .strip()
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                String: "QR123456"                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Clean non-printable chars
                            │ re.sub(r'[^\x20-\x7E]', '', data)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│            Cleaned String: "QR123456"                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ callback(decoded_data)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│         app_state.handle_main_scan("QR123456")              │
│                                                              │
│  1. Lookup in qr_to_index dictionary                        │
│  2. Compare with expected card                              │
│  3. Determine status (OK/NOT OK)                            │
│  4. Create log entry                                        │
│  5. Emit signals to UI                                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    UI Update                                 │
│  - Log table updated                                        │
│  - Status indicators changed                                │
│  - Next expected card displayed                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ComPortWriter Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│              Validation Result: "OK"                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ send_output_signal("OK")
                            ▼
┌─────────────────────────────────────────────────────────────┐
│         Lookup in output_formats.json                        │
│  Format: "Standard (OK/NOT OK)"                             │
│  Signal: "OK\r\n"                                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ output_com_writer.send("OK\r\n")
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              String: "OK\r\n"                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ .encode('utf-8')
                            ▼
┌─────────────────────────────────────────────────────────────┐
│         bytes: b'OK\r\n'                                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ serial_instance.write(bytes)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              PySerial: serial.Serial                         │
│         Port: COM7, Baud: 115200                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Serial transmission
                            ▼
┌─────────────────────────────────────────────────────────────┐
│           External Device (PLC/Controller)                   │
│         Receives: "OK\r\n"                                  │
│         Action: Trigger OK signal                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Threading Model

```
┌─────────────────────────────────────────────────────────────┐
│                    Main Thread                               │
│                  (PyQt6 UI Thread)                          │
│                                                              │
│  - Handle user interactions                                 │
│  - Update UI components                                     │
│  - Create ComPortReader instances                           │
│  - Process callbacks from readers                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Creates
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              ComPortReader Instance                          │
│                                                              │
│  self.thread = threading.Thread(target=self.read_loop)     │
│  self.thread.daemon = True                                  │
│  self.thread.start()                                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Spawns
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Background Thread 1                             │
│            (Main Scanner Reader)                            │
│                                                              │
│  while self.running:                                        │
│      self.paused.wait()  # Pause mechanism                 │
│      if in_waiting > 0:                                     │
│          data = read(256)                                   │
│          callback(data)  # Back to main thread             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Background Thread 2                             │
│          (On-Demand Scanner Reader)                         │
│                                                              │
│  while self.running:                                        │
│      self.paused.wait()                                     │
│      if in_waiting > 0:                                     │
│          data = read(256)                                   │
│          callback(data)                                     │
└─────────────────────────────────────────────────────────────┘

Thread Communication:
Main Thread ←─ callback() ─← Background Threads
Main Thread ─→ pause() ────→ Background Threads
Main Thread ─→ resume() ───→ Background Threads
Main Thread ─→ stop() ─────→ Background Threads
```

---

## Pause/Resume Mechanism

```
Normal Operation:
┌─────────────────────────────────────────────────────────────┐
│  self.paused = threading.Event()                            │
│  self.paused.set()  # Event is SET                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  while self.running:                                        │
│      self.paused.wait()  # Passes immediately (SET)        │
│      # Continue reading...                                  │
└─────────────────────────────────────────────────────────────┘

Paused State:
┌─────────────────────────────────────────────────────────────┐
│  User clicks "Approve" dialog                               │
│  app_state.pause_scanning()                                 │
│  self.paused.clear()  # Event is CLEARED                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  while self.running:                                        │
│      self.paused.wait()  # BLOCKS here (CLEARED)           │
│      # Thread is paused, not reading                        │
└─────────────────────────────────────────────────────────────┘

Resume:
┌─────────────────────────────────────────────────────────────┐
│  User approves/rejects                                      │
│  app_state.resume_scanning()                                │
│  self.paused.set()  # Event is SET again                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  while self.running:                                        │
│      self.paused.wait()  # Unblocks, continues            │
│      # Resume reading...                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Port Enumeration Flow

```
┌─────────────────────────────────────────────────────────────┐
│         User clicks "Refresh Ports" button                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  import serial.tools.list_ports                             │
│  ports = serial.tools.list_ports.comports()                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Returns list of ListPortInfo objects:                      │
│                                                              │
│  [                                                           │
│    ListPortInfo(                                            │
│      device='COM3',                                         │
│      name='COM3',                                           │
│      description='USB Serial Port',                         │
│      hwid='USB VID:PID=0403:6001',                         │
│      vid=0x0403,                                            │
│      pid=0x6001                                             │
│    ),                                                        │
│    ListPortInfo(device='COM5', ...),                        │
│    ListPortInfo(device='COM7', ...)                         │
│  ]                                                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Extract device names
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  port_list = [port.device for port in ports]               │
│  Result: ['COM3', 'COM5', 'COM7']                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Update UI dropdowns:                                       │
│  - Input Port Combo                                         │
│  - Output Port Combo                                        │
│  - On-Demand Port Combo                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────┐
│  Attempt to open serial port                                │
│  serial.Serial(port='COM3', baudrate=115200, ...)          │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
        ┌──────────────┐        ┌──────────────┐
        │   Success    │        │    Error     │
        └──────────────┘        └──────────────┘
                │                       │
                │                       │
                ▼                       ▼
┌──────────────────────┐    ┌──────────────────────┐
│ Port opened          │    │ SerialException      │
│ Start reading        │    │ raised               │
│ Notify success       │    └──────────────────────┘
└──────────────────────┘                │
                                        │
                        ┌───────────────┼───────────────┐
                        │               │               │
                        ▼               ▼               ▼
            ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
            │Port not found│ │Port in use   │ │Access denied │
            └──────────────┘ └──────────────┘ └──────────────┘
                        │               │               │
                        └───────────────┼───────────────┘
                                        │
                                        ▼
                        ┌──────────────────────────────┐
                        │ error_callback(msg, "red")   │
                        │ Display error to user        │
                        │ Set status: "Not Connected"  │
                        └──────────────────────────────┘
```

---

## Complete Scanning Cycle

```
1. Application Start
   │
   ├─ Load cached configuration
   ├─ Enumerate available ports
   └─ Validate cached ports still exist
   
2. User Configuration
   │
   ├─ Select COM ports (Main, On-Demand, Output)
   ├─ Configure serial settings (baud, parity, etc.)
   └─ Click "Apply Configuration"
   
3. Port Connection
   │
   ├─ Create ComPortReader for Main Scanner
   │  └─ Start background thread
   │
   ├─ Create ComPortReader for On-Demand Scanner
   │  └─ Start background thread
   │
   └─ Create ComPortWriter for Output
      └─ Open port (synchronous)
   
4. File Loading
   │
   ├─ User selects file
   ├─ Choose card type
   ├─ Parse file
   └─ Build QR lookup dictionary
   
5. Start Scanning
   │
   ├─ User clicks "Start Validation"
   ├─ Main scanner thread begins reading
   └─ Wait for first scan
   
6. Scan Processing (Loop)
   │
   ├─ Scanner sends QR code
   │  └─ PySerial: read(256)
   │
   ├─ Decode and clean data
   │  └─ bytes → string → cleaned
   │
   ├─ Callback to handle_main_scan()
   │  ├─ Lookup QR in dictionary
   │  ├─ Compare with expected
   │  └─ Determine status
   │
   ├─ Create log entry
   │  └─ Timestamp, codes, status
   │
   ├─ Send output signal
   │  └─ PySerial: write(signal)
   │
   └─ Update UI
      └─ Emit PyQt signals
   
7. Stop Scanning
   │
   ├─ User clicks "Stop Validation"
   ├─ Set running = False
   ├─ Wait for threads to finish
   └─ Close all ports
   
8. Application Exit
   │
   ├─ Stop all readers
   ├─ Close all ports
   ├─ Save configuration
   └─ Exit cleanly
```

---

## Serial Communication Timing

```
Timeline of a Single Scan:

T=0ms     Scanner trigger pressed
          │
T=50ms    Scanner reads QR code
          │
T=100ms   Scanner sends data to COM port
          │         "QR123456\r\n"
          ▼
T=101ms   PySerial receives data
          │ in_waiting = 10 bytes
          │
T=102ms   read(256) called
          │ Returns: b'QR123456\r\n'
          │
T=103ms   decode('utf-8')
          │ Returns: "QR123456\r\n"
          │
T=104ms   strip() and clean
          │ Returns: "QR123456"
          │
T=105ms   callback(decoded_data)
          │ → handle_main_scan("QR123456")
          │
T=106ms   Dictionary lookup
          │ qr_to_index["QR123456"] → (index, position)
          │
T=107ms   Validation logic
          │ Compare with expected
          │ Status: "OK"
          │
T=108ms   Create log entry
          │ {timestamp, scanned, expected, status}
          │
T=109ms   Send output signal
          │ output_com_writer.send("OK\r\n")
          │
T=110ms   PySerial write
          │ Transmit to external device
          │
T=111ms   Update UI
          │ Emit PyQt signals
          │ Update log table
          │
T=115ms   UI refresh complete
          │
T=120ms   Ready for next scan

Total Processing Time: ~20ms
Bottleneck: Scanner hardware (50-100ms)
```

---

## Memory Layout

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Memory                        │
│                      (~50-200 MB)                           │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  PyQt6 UI    │   │  App State   │   │  PySerial    │
│   (~30 MB)   │   │   (~20 MB)   │   │   (~1 MB)    │
└──────────────┘   └──────────────┘   └──────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│expected_cards│   │qr_to_index   │   │  log_data    │
│ (list)       │   │ (dict)       │   │  (list)      │
│              │   │              │   │              │
│ 10K cards:   │   │ O(1) lookup  │   │ Grows with   │
│ ~15 MB       │   │ ~15 MB       │   │ scans        │
└──────────────┘   └──────────────┘   └──────────────┘

Serial Buffers (per port):
┌──────────────────────────────────────┐
│ Input Buffer:  256 bytes (read size) │
│ Output Buffer: OS managed (~4KB)     │
└──────────────────────────────────────┘
```

---

**Document Version**: 1.0  
**Last Updated**: January 19, 2026  
**Project**: Card Sequence Validator
