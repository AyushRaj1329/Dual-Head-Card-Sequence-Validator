# Power Loss & Data Recovery Analysis - Card Sequence Validator

## Critical Question: What Happens During Sudden Power Loss?

**Short Answer**: Logs generated during active scanning will be **LOST** if power is cut before the cache is saved.

---

## Power Loss Scenario Analysis

### Scenario: Mid-Validation Power Loss

```
Timeline:
─────────────────────────────────────────────────────────────
T=0:00    Application starts
          └─ Loads cache from disk (previous session logs restored)

T=0:30    User loads file (10,000 cards)
          └─ Cache saved ✅ (file path saved)

T=1:00    User starts validation
          └─ No cache save (scanning begins)

T=1:05    Scan card 1 → OK
          └─ Log added to RAM only ⚠️ (NOT saved to disk)

T=1:10    Scan card 2 → OK
          └─ Log added to RAM only ⚠️ (NOT saved to disk)

T=1:15    Scan card 3 → OK
          └─ Log added to RAM only ⚠️ (NOT saved to disk)

T=1:20    ⚡ POWER LOSS ⚡
          └─ Application crashes immediately

T=1:21    All RAM cleared
          └─ Logs for cards 1, 2, 3 are LOST ❌

T=2:00    Power restored, application restarted
          └─ Loads cache from disk
          └─ Only logs from BEFORE T=1:00 are restored
          └─ Logs from T=1:05 to T=1:20 are GONE ❌
```

---

## When Cache is Saved (Data Persisted to Disk)

### Current Save Points

```python
# src/app_state.py - save_cache() is called at:

1. Configuration Changes
   - COM port selection changed
   - Serial settings changed
   - Output format changed
   └─ save_cache() ✅

2. File Operations
   - File loaded
   - File cleared
   └─ save_cache() ✅

3. Log Management
   - Logs cleared
   └─ save_cache() ✅

4. Theme Changes
   - Theme switched
   └─ save_cache() ✅

5. Application Exit
   - Window closed normally
   └─ save_cache() ✅

6. Port Disconnection
   - Disconnect all ports
   └─ save_cache() ✅
```

### When Cache is NOT Saved

```python
❌ During Active Scanning
   - Each scan adds log to RAM
   - NO save_cache() called
   - Logs accumulate in memory only

❌ During Validation
   - handle_main_scan() adds logs
   - NO save_cache() called
   - Data only in RAM

❌ During Sequence Jumps
   - Skipped cards logged
   - NO save_cache() called
   - Data only in RAM
```

---

## Data Loss Analysis

### What is Lost During Power Failure

```
┌─────────────────────────────────────────────────────────────┐
│                    LOST (In RAM Only)                        │
├─────────────────────────────────────────────────────────────┤
│ ❌ All logs generated during current scanning session       │
│ ❌ Current scan position (current_card_index)               │
│ ❌ Start card detection state                               │
│ ❌ Any unsaved validation results                           │
│ ❌ Temporary scanning state                                 │
└─────────────────────────────────────────────────────────────┘
```

### What is Preserved (On Disk)

```
┌─────────────────────────────────────────────────────────────┐
│                PRESERVED (In Cache File)                     │
├─────────────────────────────────────────────────────────────┤
│ ✅ Logs from previous sessions                              │
│ ✅ Logs saved before current scanning session               │
│ ✅ COM port configuration                                   │
│ ✅ Serial settings                                          │
│ ✅ Selected file path                                       │
│ ✅ Output format selection                                  │
│ ✅ Theme preference                                         │
│ ✅ Scan direction setting                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Detailed Example

### Example: 1000 Card Validation with Power Loss

```
Initial State (Application Start):
├─ Cache loaded from disk
├─ Previous logs: 500 entries (from yesterday)
└─ RAM: 500 logs loaded

User Actions:
├─ Loads new file (10,000 cards)
│  └─ save_cache() called ✅
│  └─ Disk: 500 logs + new file path
│
├─ Starts validation
│  └─ No save_cache() ⚠️
│
├─ Scans 100 cards (T=0 to T=5 minutes)
│  ├─ RAM: 500 old + 100 new = 600 logs
│  └─ Disk: Still only 500 logs ⚠️
│
└─ ⚡ Power Loss at T=5 minutes ⚡

After Power Restored:
├─ Application restarts
├─ Cache loaded from disk
├─ RAM: 500 logs (from yesterday)
└─ Lost: 100 logs from today ❌

Result:
✅ Preserved: 500 logs from previous session
❌ Lost: 100 logs from current session
```

---

## Memory vs Disk State

### During Active Scanning

```
┌─────────────────────────────────────────────────────────────┐
│                         RAM State                            │
│                    (Volatile - Lost on Power Loss)           │
├─────────────────────────────────────────────────────────────┤
│ log_data = [                                                │
│   {timestamp: "10:00:01", scanned: "QR1", status: "OK"},   │
│   {timestamp: "10:00:02", scanned: "QR2", status: "OK"},   │
│   {timestamp: "10:00:03", scanned: "QR3", status: "OK"},   │
│   ... (100 new entries)                                     │
│ ]                                                            │
│                                                              │
│ Total in RAM: 600 entries                                   │
└─────────────────────────────────────────────────────────────┘
                            ↕
                    NOT SYNCHRONIZED
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                        Disk State                            │
│                  (Persistent - Survives Power Loss)          │
├─────────────────────────────────────────────────────────────┤
│ app_cache.json:                                             │
│ {                                                            │
│   "log_data": [                                             │
│     {timestamp: "09:00:01", scanned: "QR1", status: "OK"}, │
│     {timestamp: "09:00:02", scanned: "QR2", status: "OK"}, │
│     ... (500 old entries)                                   │
│   ]                                                          │
│ }                                                            │
│                                                              │
│ Total on Disk: 500 entries (outdated)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Risk Assessment

### High Risk Scenarios

```
1. Long Validation Sessions
   Risk: Hours of scanning without save
   Impact: All session data lost
   Example: 10,000 card validation over 2 hours

2. Unstable Power Supply
   Risk: Frequent power interruptions
   Impact: Repeated data loss
   Example: Factory with power fluctuations

3. Large Batch Operations
   Risk: Thousands of scans between saves
   Impact: Significant data loss
   Example: 50,000 card validation

4. No UPS Protection
   Risk: Immediate power loss
   Impact: No graceful shutdown
   Example: Power outage without warning
```

### Low Risk Scenarios

```
1. Frequent Configuration Changes
   Risk: Low (saves trigger often)
   Impact: Minimal data loss
   Example: Adjusting settings between batches

2. Small Batch Operations
   Risk: Low (less data at risk)
   Impact: Limited loss
   Example: 100 cards per session

3. UPS Protected System
   Risk: Low (time for graceful shutdown)
   Impact: Can save before shutdown
   Example: System with 30-minute UPS backup
```

---

## Current Behavior Summary

### Save Triggers (Data Persisted)

| Event | Saves Logs? | Saves Config? |
|-------|-------------|---------------|
| Application Start | No | No (loads) |
| File Loaded | ✅ Yes | ✅ Yes |
| File Cleared | ✅ Yes | ✅ Yes |
| COM Port Changed | ✅ Yes | ✅ Yes |
| Settings Changed | ✅ Yes | ✅ Yes |
| **Scanning Active** | ❌ **No** | ❌ **No** |
| **Each Scan** | ❌ **No** | ❌ **No** |
| Logs Cleared | ✅ Yes | ✅ Yes |
| Theme Changed | ✅ Yes | ✅ Yes |
| Normal Exit | ✅ Yes | ✅ Yes |
| **Power Loss** | ❌ **No** | ❌ **No** |
| **Crash** | ❌ **No** | ❌ **No** |

---

## Mitigation Strategies

### 1. Auto-Save Implementation (Recommended)

```python
# Add periodic auto-save during scanning
class AppState:
    def __init__(self):
        # ... existing code ...
        self.last_save_time = time.time()
        self.save_interval = 60  # Save every 60 seconds
    
    def handle_main_scan(self, scanned_code):
        # ... existing validation logic ...
        
        # Add auto-save check
        current_time = time.time()
        if current_time - self.last_save_time > self.save_interval:
            self.save_cache()
            self.last_save_time = current_time
```

**Benefits:**
- ✅ Maximum 60 seconds of data loss
- ✅ Automatic, no user action needed
- ✅ Configurable interval

**Drawbacks:**
- ⚠️ Disk I/O during scanning
- ⚠️ Slight performance impact

### 2. Batch Save Implementation

```python
# Save after every N scans
class AppState:
    def __init__(self):
        # ... existing code ...
        self.scans_since_save = 0
        self.save_batch_size = 100  # Save every 100 scans
    
    def handle_main_scan(self, scanned_code):
        # ... existing validation logic ...
        
        self.scans_since_save += 1
        if self.scans_since_save >= self.save_batch_size:
            self.save_cache()
            self.scans_since_save = 0
```

**Benefits:**
- ✅ Predictable save points
- ✅ Maximum N scans lost
- ✅ Less frequent disk writes

**Drawbacks:**
- ⚠️ Still potential for data loss
- ⚠️ Batch size needs tuning

### 3. UPS Integration (Hardware Solution)

```python
# Detect UPS power loss and save immediately
import psutil

def monitor_power_status():
    battery = psutil.sensors_battery()
    if battery:
        if not battery.power_plugged:
            # On battery power - save immediately
            app_state.save_cache()
            # Optionally: graceful shutdown
```

**Benefits:**
- ✅ No data loss with proper UPS
- ✅ Time for graceful shutdown
- ✅ No performance impact during normal operation

**Drawbacks:**
- ⚠️ Requires UPS hardware
- ⚠️ Additional cost

### 4. Manual Save Button (User Control)

```python
# Add "Save Progress" button in UI
def save_progress_clicked(self):
    self.app_state.save_cache()
    QMessageBox.information(self, "Saved", 
        f"Progress saved: {len(self.app_state.log_data)} logs")
```

**Benefits:**
- ✅ User control over saves
- ✅ No automatic overhead
- ✅ Simple implementation

**Drawbacks:**
- ⚠️ Requires user action
- ⚠️ Easy to forget

---

## Recommended Solution

### Hybrid Approach (Best Practice)

```python
class AppState:
    def __init__(self):
        # ... existing code ...
        self.last_save_time = time.time()
        self.save_interval = 300  # 5 minutes
        self.scans_since_save = 0
        self.save_batch_size = 1000  # 1000 scans
    
    def handle_main_scan(self, scanned_code):
        # ... existing validation logic ...
        
        # Auto-save logic
        self.scans_since_save += 1
        current_time = time.time()
        
        # Save if either condition met:
        # 1. Time-based: 5 minutes elapsed
        # 2. Count-based: 1000 scans completed
        if (current_time - self.last_save_time > self.save_interval or
            self.scans_since_save >= self.save_batch_size):
            self.save_cache()
            self.last_save_time = current_time
            self.scans_since_save = 0
```

**Configuration:**
- Time interval: 5 minutes (300 seconds)
- Batch size: 1000 scans
- Whichever comes first triggers save

**Maximum Data Loss:**
- Time-based: 5 minutes of scans
- Count-based: 1000 scans
- Typical: 50-500 scans (depending on speed)

---

## User Recommendations

### For Current Version (No Auto-Save)

**Best Practices:**
1. **Use UPS**: Invest in uninterruptible power supply
2. **Save Frequently**: Export logs periodically
3. **Small Batches**: Validate in smaller batches
4. **Stable Power**: Ensure reliable power source
5. **Regular Exports**: Export logs before long sessions

**Workflow:**
```
1. Start validation session
2. Scan 500-1000 cards
3. Stop validation
4. Export logs to CSV
5. Clear logs (triggers save)
6. Resume validation
7. Repeat
```

### For Future Version (With Auto-Save)

**Automatic Protection:**
- Logs saved every 5 minutes
- Logs saved every 1000 scans
- Maximum loss: 5 minutes or 1000 scans
- No user action required

---

## Recovery Procedures

### After Power Loss

```
1. Restart Computer
   └─ Wait for system to boot

2. Launch Application
   └─ Cache automatically loaded
   └─ Previous logs restored

3. Check Log Count
   └─ Compare with expected
   └─ Identify missing scans

4. Resume Validation
   └─ Load same file
   └─ Continue from last saved position
   └─ Re-scan missing cards

5. Export Logs
   └─ Save to CSV immediately
   └─ Backup important data
```

### Identifying Lost Data

```python
# Check last log timestamp
last_log = app_state.log_data[-1]
print(f"Last saved scan: {last_log['timestamp']}")

# Compare with expected
expected_scans = 1000
actual_scans = len(app_state.log_data)
lost_scans = expected_scans - actual_scans
print(f"Lost scans: {lost_scans}")
```

---

## Summary

### Current Behavior

**During Scanning:**
- ❌ Logs stored in RAM only
- ❌ No automatic saves
- ❌ Power loss = data loss

**On Normal Exit:**
- ✅ Cache saved to disk
- ✅ All logs preserved
- ✅ Configuration saved

### Data Loss Risk

**High Risk:**
- Long validation sessions
- Unstable power
- No UPS protection

**Mitigation:**
- Use UPS (hardware)
- Implement auto-save (software)
- Export logs frequently (user)
- Small batch operations (workflow)

### Recommended Actions

**Immediate (Current Version):**
1. Install UPS on validation machines
2. Export logs frequently
3. Validate in smaller batches
4. Ensure stable power supply

**Future Enhancement:**
1. Implement auto-save (5 min / 1000 scans)
2. Add manual "Save Progress" button
3. Add UPS detection and emergency save
4. Display "Last Saved" timestamp in UI

---

**Critical Takeaway**: In the current version, **logs are NOT saved during active scanning**. Power loss will result in loss of all scans since the last save event. Use UPS protection and frequent exports to mitigate risk.

---

**Document Version**: 1.0  
**Last Updated**: January 19, 2026  
**Project**: Card Sequence Validator  
**Status**: Current Behavior Documented + Mitigation Strategies Provided
