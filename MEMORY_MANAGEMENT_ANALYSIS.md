# Memory Management Analysis - Card Sequence Validator

## Executive Summary

The Card Sequence Validator uses **in-memory storage** for active data with **persistent cache** for configuration and logs. Memory usage is efficient, typically **50-200MB** depending on file size and log volume.

**Key Points:**
- **Single Instance**: One AppState object manages all memory
- **In-Memory Logs**: Stored in Python list, grows with scans
- **Persistent Cache**: JSON file on disk for session persistence
- **Efficient Lookups**: Dictionary-based O(1) QR code lookups
- **No Database**: All data in RAM for maximum speed

---

## Memory Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Process                       │
│                  (Python + PyQt6 Runtime)                   │
│                     Total: 50-200 MB                        │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   PyQt6 UI   │   │  AppState    │   │  PySerial    │
│   (~30 MB)   │   │  (Main Data) │   │   (~1 MB)    │
│              │   │  (~20-150MB) │   │              │
└──────────────┘   └──────────────┘   └──────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│expected_cards│   │qr_to_index   │   │  log_data    │
│   (list)     │   │   (dict)     │   │   (list)     │
└──────────────┘   └──────────────┘   └──────────────┘
```

---

## AppState Instance - Single Source of Truth

### Instance Creation
```python
# In main.py - Only ONE instance created
app_state = AppState(card_type=CardType.HALF)
```

**Critical**: Only **ONE AppState instance** exists for the entire application.

### Instance Sharing
```python
# All windows share the SAME instance
window = HomePage(app_state)           # Main window
com_port_window = ComPortSetupWindow(app_state)
file_window = FileManagementWindow(app_state)
scanner_window = ScannerLoggingWindow(app_state)
```

**Memory Implication**: All windows reference the **same memory**, not separate copies.

---

## Memory Components Breakdown

### 1. Log Data (log_data)

#### Location in Code
```python
# src/app_state.py line 140
self.log_data = []  # Python list in RAM
```

#### Structure
```python
log_entry = {
    "timestamp": "10:30:45.123",      # ~15 bytes
    "scanned_code": "QR123456789",    # ~20 bytes
    "expected_code": "QR123456789",   # ~20 bytes
    "status": "OK",                   # ~10 bytes
    "scanned_side": "Left"            # ~10 bytes
}
# Total per entry: ~75 bytes + Python overhead (~150 bytes)
# Actual per entry: ~225 bytes
```

#### Memory Calculation
```
1 log entry     = ~225 bytes
100 entries     = ~22 KB
1,000 entries   = ~220 KB
10,000 entries  = ~2.2 MB
100,000 entries = ~22 MB
```

#### Growth Pattern
```
Start:          log_data = []           (0 bytes)
After 1 scan:   log_data = [entry1]    (225 bytes)
After 100:      log_data = [e1...e100] (22 KB)
After 1000:     log_data = [e1...e1000](220 KB)
```

#### Memory Location
- **Type**: Python list object
- **Storage**: RAM (heap memory)
- **Scope**: AppState instance attribute
- **Lifetime**: Until cleared or app closes
- **Shared**: All windows see same list

#### Operations
```python
# Add entry (O(1) operation)
self.log_data.append(log_entry)

# Clear logs (frees memory)
self.log_data = []  # Old list garbage collected

# Access (O(1) by index)
entry = self.log_data[0]

# Iterate (O(n))
for entry in self.log_data:
    process(entry)
```

---

### 2. Expected Cards (expected_cards)

#### Location in Code
```python
# src/app_state.py line 130
self.expected_cards = []  # Python list in RAM
```

#### Structure
```python
# Single Card Type
card = ("Card_123", "QR_123456789")
# Size: ~50 bytes + overhead = ~100 bytes per card

# Half Card Type
card = ("Card_123", "QR_LEFT_123", "QR_RIGHT_123")
# Size: ~70 bytes + overhead = ~150 bytes per card

# Quarter Card Type
card = ("Card_123", "QR_BL_123", "QR_TL_123", "QR_TR_123", "QR_BR_123")
# Size: ~110 bytes + overhead = ~250 bytes per card
```

#### Memory Calculation by Card Type
```
Single Cards:
  1,000 cards   = ~100 KB
  10,000 cards  = ~1 MB
  100,000 cards = ~10 MB

Half Cards:
  1,000 cards   = ~150 KB
  10,000 cards  = ~1.5 MB
  100,000 cards = ~15 MB

Quarter Cards:
  1,000 cards   = ~250 KB
  10,000 cards  = ~2.5 MB
  100,000 cards = ~25 MB
```

#### Memory Location
- **Type**: Python list of tuples
- **Storage**: RAM (heap memory)
- **Scope**: AppState instance attribute
- **Lifetime**: Until file cleared or new file loaded
- **Shared**: All windows see same list

#### Loading Process
```python
# File loaded
self.expected_cards, _ = parse_file(file_path, card_type)

# Memory allocated for entire file at once
# Example: 10,000 half cards = ~1.5 MB allocated
```

---

### 3. QR Code Lookup Dictionaries

#### qr_to_index Dictionary

**Location in Code:**
```python
# src/app_state.py line 133
self.qr_to_index = {}  # Python dict in RAM
```

**Structure:**
```python
self.qr_to_index = {
    "QR_123456789": (card_index, position),
    "QR_987654321": (card_index, position),
    # ...
}
# Key: ~20 bytes
# Value: tuple (2 integers) = ~28 bytes
# Entry: ~48 bytes + dict overhead = ~100 bytes per QR code
```

**Memory Calculation:**
```
Single Cards (1 QR per card):
  1,000 cards   = 1,000 QRs   = ~100 KB
  10,000 cards  = 10,000 QRs  = ~1 MB
  100,000 cards = 100,000 QRs = ~10 MB

Half Cards (2 QRs per card):
  1,000 cards   = 2,000 QRs   = ~200 KB
  10,000 cards  = 20,000 QRs  = ~2 MB
  100,000 cards = 200,000 QRs = ~20 MB

Quarter Cards (4 QRs per card):
  1,000 cards   = 4,000 QRs   = ~400 KB
  10,000 cards  = 40,000 QRs  = ~4 MB
  100,000 cards = 400,000 QRs = ~40 MB
```

**Purpose**: O(1) lookup for QR code validation

#### numcard_to_qrs Dictionary

**Location in Code:**
```python
# src/app_state.py line 134
self.numcard_to_qrs = {}  # Python dict in RAM
```

**Structure:**
```python
self.numcard_to_qrs = {
    "Card_123": ("QR_LEFT_123", "QR_RIGHT_123"),
    "Card_456": ("QR_LEFT_456", "QR_RIGHT_456"),
    # ...
}
# Similar size to qr_to_index
```

**Memory**: Same as qr_to_index (~100 bytes per card)

---

### 4. Cache File (Persistent Storage)

#### Location on Disk
```python
# Windows path (typical):
C:\Users\<username>\AppData\Local\YourCompany\CardSequenceValidator\app_cache.json

# Determined by:
from appdirs import user_data_dir
cache_dir = user_data_dir("CardSequenceValidator", "YourCompany")
cache_file = os.path.join(cache_dir, "app_cache.json")
```

#### Structure
```json
{
  "card_type": "half",
  "selected_com_port": "COM3",
  "start_card_scan_port": "COM5",
  "selected_output_port": "COM7",
  "baud_rate": 115200,
  "data_bits": 8,
  "parity": "N",
  "stop_bits": 1,
  "timeout": 0.1,
  "selected_output_format": "Standard (OK/NOT OK)",
  "selected_file_path": "C:\\path\\to\\file.csv",
  "start_card_code": "QR_123456",
  "scan_direction": "top_to_bottom",
  "log_data": [
    {
      "timestamp": "10:30:45.123",
      "scanned_code": "QR_123456",
      "expected_code": "QR_123456",
      "status": "OK",
      "scanned_side": "Left"
    }
    // ... more log entries
  ],
  "current_theme": "dark"
}
```

#### File Size Calculation
```
Configuration data: ~500 bytes
Log data: ~225 bytes per entry

Examples:
  0 logs:       ~0.5 KB
  100 logs:     ~22 KB
  1,000 logs:   ~220 KB
  10,000 logs:  ~2.2 MB
  100,000 logs: ~22 MB
```

#### Cache Operations

**Save to Disk:**
```python
def save_cache(self):
    cache_data = {
        'card_type': self.card_type.value,
        'selected_com_port': self.selected_com_port,
        # ... all configuration
        'log_data': self.log_data,  # Entire log list
    }
    with open(get_cache_file_path(), 'w') as f:
        json.dump(cache_data, f, indent=4)
```

**Load from Disk:**
```python
def load_cache(self):
    with open(get_cache_file_path(), 'r') as f:
        cache = json.load(f)
        self.log_data = cache.get('log_data', [])
        # ... restore all configuration
```

**When Cache is Saved:**
- Configuration changes (COM ports, settings)
- File loaded/cleared
- Logs cleared
- Application exit
- Manual save operations

**When Cache is Loaded:**
- Application startup (once)

---

## Memory Lifecycle

### Application Startup

```
1. Python Process Starts
   └─ Base memory: ~30 MB (Python + PyQt6)

2. AppState Created (ONE instance)
   ├─ log_data = []              (0 bytes)
   ├─ expected_cards = []        (0 bytes)
   ├─ qr_to_index = {}           (0 bytes)
   └─ numcard_to_qrs = {}        (0 bytes)
   Total: ~50 MB

3. Load Cache from Disk
   ├─ Read app_cache.json
   ├─ Restore log_data           (+X MB depending on logs)
   └─ Restore configuration      (+1 KB)
   Total: ~50 MB + log size

4. UI Windows Created
   ├─ All share same AppState
   └─ UI elements: +10-20 MB
   Total: ~60-70 MB + log size
```

### File Loading

```
1. User Selects File
   └─ File path stored (string, ~100 bytes)

2. Parse File
   ├─ Read file from disk
   ├─ Parse into card tuples
   └─ Temporary memory during parsing

3. Store in Memory
   ├─ expected_cards = [...]     (+X MB, see calculations)
   ├─ Build qr_to_index          (+X MB, see calculations)
   └─ Build numcard_to_qrs       (+X MB, see calculations)

4. Total Memory Increase
   Single Cards (10K):   ~1 MB + 1 MB + 1 MB = ~3 MB
   Half Cards (10K):     ~1.5 MB + 2 MB + 1.5 MB = ~5 MB
   Quarter Cards (10K):  ~2.5 MB + 4 MB + 2.5 MB = ~9 MB
```

### Scanning Operation

```
1. Each Scan
   ├─ Read from serial port      (256 bytes buffer)
   ├─ Decode string              (~50 bytes)
   ├─ Lookup in qr_to_index      (O(1), no new memory)
   ├─ Create log entry           (+225 bytes)
   └─ Append to log_data         (+225 bytes)

2. After 1,000 Scans
   └─ log_data grows by ~220 KB

3. After 10,000 Scans
   └─ log_data grows by ~2.2 MB

4. After 100,000 Scans
   └─ log_data grows by ~22 MB
```

### Clear Logs

```
1. User Clicks "Clear Logs"
   └─ self.log_data = []

2. Python Garbage Collection
   └─ Old list freed (~X MB released)

3. Memory Reduced
   └─ Back to base + file data
```

### Application Exit

```
1. Save Cache
   ├─ Write log_data to disk
   ├─ Write configuration to disk
   └─ Cache file size: ~X MB

2. Close Ports
   └─ Release serial port resources

3. Destroy Windows
   └─ UI memory freed

4. Python Process Exits
   └─ All memory released to OS
```

---

## Memory Locations Summary

### RAM (Volatile Memory)

| Component | Location | Type | Size | Lifetime |
|-----------|----------|------|------|----------|
| **log_data** | AppState.log_data | Python list | ~225 bytes/entry | Until cleared |
| **expected_cards** | AppState.expected_cards | Python list | ~100-250 bytes/card | Until file cleared |
| **qr_to_index** | AppState.qr_to_index | Python dict | ~100 bytes/QR | Until file cleared |
| **numcard_to_qrs** | AppState.numcard_to_qrs | Python dict | ~100 bytes/card | Until file cleared |
| **Serial buffers** | PySerial | bytes | 256 bytes/port | While connected |
| **UI elements** | PyQt6 | Various | ~30 MB | While app running |

### Disk (Persistent Storage)

| Component | Location | Type | Size | Lifetime |
|-----------|----------|------|------|----------|
| **Cache file** | app_cache.json | JSON | ~0.5 KB + logs | Permanent |
| **Log exports** | User-selected | CSV | ~X MB | Permanent |

---

## Instance Separation Analysis

### Question: Are Two Instances Separate?

**Answer: There is only ONE AppState instance.**

```python
# In main.py - Single instance created
app_state = AppState(card_type=CardType.HALF)

# All windows share this SAME instance
window1 = HomePage(app_state)
window2 = ComPortSetupWindow(app_state)
window3 = FileManagementWindow(app_state)
window4 = ScannerLoggingWindow(app_state)
```

**Memory Implications:**
- ✅ **Shared Memory**: All windows see same log_data
- ✅ **Synchronized**: Changes in one window visible in all
- ✅ **Efficient**: No duplication of data
- ✅ **Consistent**: Single source of truth

**Example:**
```python
# Window 1 adds log entry
app_state.log_data.append(entry)

# Window 2 immediately sees it
print(len(app_state.log_data))  # Includes new entry

# Same memory address
print(id(window1.app_state.log_data))  # 0x12345678
print(id(window2.app_state.log_data))  # 0x12345678 (SAME!)
```

---

## Memory Usage Examples

### Example 1: Small Operation (1,000 cards, 1,000 scans)

```
Base Application:        50 MB
Half Card File (1K):     5 MB
  - expected_cards:      1.5 MB
  - qr_to_index:         2 MB
  - numcard_to_qrs:      1.5 MB
Logs (1K entries):       0.22 MB
Cache File on Disk:      0.22 MB

Total RAM:               ~55 MB
Total Disk:              ~0.22 MB
```

### Example 2: Medium Operation (10,000 cards, 10,000 scans)

```
Base Application:        50 MB
Half Card File (10K):    5 MB
  - expected_cards:      1.5 MB
  - qr_to_index:         2 MB
  - numcard_to_qrs:      1.5 MB
Logs (10K entries):      2.2 MB
Cache File on Disk:      2.2 MB

Total RAM:               ~57 MB
Total Disk:              ~2.2 MB
```

### Example 3: Large Operation (100,000 cards, 100,000 scans)

```
Base Application:        50 MB
Quarter Card File (100K): 90 MB
  - expected_cards:      25 MB
  - qr_to_index:         40 MB
  - numcard_to_qrs:      25 MB
Logs (100K entries):     22 MB
Cache File on Disk:      22 MB

Total RAM:               ~162 MB
Total Disk:              ~22 MB
```

---

## Memory Optimization Strategies

### Current Optimizations

1. **Dictionary Lookups**: O(1) QR code validation (no linear search)
2. **Single Instance**: No data duplication across windows
3. **Lazy Loading**: Files loaded only when selected
4. **Efficient Storage**: Python's native data structures
5. **Garbage Collection**: Automatic memory cleanup

### Potential Improvements

1. **Log Pagination**: Keep only recent N entries in memory
2. **Database Storage**: Use SQLite for large log volumes
3. **Streaming Parsing**: Load files in chunks for very large files
4. **Compression**: Compress cache file on disk
5. **Memory Limits**: Implement max log size with rotation

---

## Memory Monitoring

### Check Memory Usage (Windows)

```python
import psutil
import os

process = psutil.Process(os.getpid())
memory_info = process.memory_info()

print(f"RSS (Resident Set Size): {memory_info.rss / 1024 / 1024:.2f} MB")
print(f"VMS (Virtual Memory Size): {memory_info.vms / 1024 / 1024:.2f} MB")
```

### Typical Values

```
Application Start:       50-60 MB
After Loading 10K File:  55-65 MB
After 10K Scans:         57-67 MB
After 100K Scans:        75-85 MB
```

---

## Cache File Management

### Cache File Operations

**Read Operations:**
- Application startup (once)
- Restore configuration
- Restore logs

**Write Operations:**
- Configuration changes
- File loaded/cleared
- Logs cleared
- Application exit

**File Size Growth:**
```
Initial:           ~0.5 KB (config only)
After 100 scans:   ~22 KB
After 1K scans:    ~220 KB
After 10K scans:   ~2.2 MB
After 100K scans:  ~22 MB
```

### Cache File Location by OS

**Windows:**
```
C:\Users\<username>\AppData\Local\YourCompany\CardSequenceValidator\app_cache.json
```

**Linux:**
```
~/.local/share/CardSequenceValidator/app_cache.json
```

**macOS:**
```
~/Library/Application Support/CardSequenceValidator/app_cache.json
```

---

## Memory Safety

### Protections

1. **No Memory Leaks**: Python garbage collection handles cleanup
2. **Bounded Growth**: Logs grow linearly with scans
3. **Clear Operation**: Frees memory immediately
4. **No Dangling Pointers**: Python manages references
5. **Thread Safety**: PyQt signals handle cross-thread communication

### Risks

1. **Unbounded Log Growth**: Logs can grow indefinitely
2. **Large Files**: 1M+ card files may use significant RAM
3. **Cache File Size**: Large logs increase disk usage

### Mitigations

1. **Clear Logs Regularly**: User can clear anytime
2. **Export and Clear**: Export logs, then clear
3. **File Size Warnings**: Could add warnings for large files
4. **Log Rotation**: Could implement automatic rotation

---

## Summary

### Memory Architecture
- **Single Instance**: One AppState for entire application
- **Shared Memory**: All windows reference same data
- **In-Memory**: Active data in RAM for speed
- **Persistent Cache**: JSON file for session persistence

### Memory Usage
- **Base**: ~50 MB (Python + PyQt6)
- **File Data**: ~3-9 MB per 10,000 cards
- **Logs**: ~225 bytes per scan
- **Total**: Typically 50-200 MB

### Storage Locations
- **RAM**: log_data, expected_cards, dictionaries
- **Disk**: app_cache.json (persistent)
- **Lifetime**: RAM cleared on exit, disk persists

### Key Characteristics
- ✅ Efficient O(1) lookups
- ✅ No data duplication
- ✅ Automatic garbage collection
- ✅ Linear memory growth
- ✅ User-controlled cleanup

---

**Document Version**: 1.0  
**Last Updated**: January 19, 2026  
**Project**: Card Sequence Validator