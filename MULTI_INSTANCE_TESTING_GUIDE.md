# Multi-Instance Testing Guide

## Pre-Testing Setup

### 1. Clean Environment
Before testing, ensure a clean state:
```bash
# Remove existing cache files (optional, for fresh start)
# Windows: Delete C:\Users\[Username]\AppData\Local\CardSequenceValidator\CardSequenceValidator\
```

### 2. Prepare Test Data
- Have at least one sequence file (.cpd, .txt, or .csv) ready
- Have network configuration details for testing

## Test Cases

### Test 1: Basic Instance Selection

**Objective**: Verify that instance buttons work and switch instances

**Steps**:
1. Start the application
2. Observe the header - "Instance 1" should be selected (highlighted)
3. Click "Instance 2" button
4. Verify confirmation message appears: "Switched to Instance 2"
5. Observe "Instance 2" button is now selected
6. Click "Instance 1" button
7. Verify confirmation message appears: "Switched to Instance 1"
8. Observe "Instance 1" button is now selected

**Expected Result**: ✅ Instance buttons toggle correctly and show confirmation messages

---

### Test 2: Separate Configuration Storage

**Objective**: Verify each instance stores its own configuration

**Steps**:
1. Start with Instance 1 (default)
2. Go to "Network & COM Setup"
3. Configure network settings:
   - Local IP: 192.168.1.100
   - Local Port: 5000
4. Go to "File Management"
5. Load a sequence file (e.g., HESH1355.CPD)
6. Switch to Instance 2
7. Go to "Network & COM Setup"
8. Verify network settings are empty/different
9. Configure different settings:
   - Local IP: 192.168.2.100
   - Local Port: 5001
10. Go to "File Management"
11. Load a different sequence file
12. Switch back to Instance 1
13. Go to "Network & COM Setup"
14. Verify original settings are restored (192.168.1.100:5000)
15. Go to "File Management"
16. Verify original file is still loaded

**Expected Result**: ✅ Each instance maintains separate configurations

---

### Test 3: Separate Logs

**Objective**: Verify each instance maintains separate logs

**Steps**:
1. Start with Instance 1
2. Go to "Scanner & Logging"
3. Manually add some test entries to the log (or perform scans)
4. Note the number of log entries
5. Switch to Instance 2
6. Go to "Scanner & Logging"
7. Verify logs are empty (or different from Instance 1)
8. Add different test entries
9. Switch back to Instance 1
10. Go to "Scanner & Logging"
11. Verify original logs are restored

**Expected Result**: ✅ Each instance has separate logs

---

### Test 4: Theme Persistence Per Instance

**Objective**: Verify each instance can have different themes

**Steps**:
1. Start with Instance 1
2. Click "Light Mode" button to switch to light theme
3. Verify UI changes to light theme
4. Switch to Instance 2
5. Verify theme is still dark (default)
6. Click "Dark Mode" button to switch to dark theme
7. Switch back to Instance 1
8. Verify light theme is still active
9. Switch to Instance 2
10. Verify dark theme is still active

**Expected Result**: ✅ Each instance remembers its theme preference

---

### Test 5: Application Restart - Instance Persistence

**Objective**: Verify last selected instance loads on restart

**Steps**:
1. Start application (Instance 1 loads by default)
2. Switch to Instance 2
3. Configure some settings (network, file, etc.)
4. Close the application
5. Restart the application
6. Verify Instance 2 is automatically selected
7. Go to "Network & COM Setup"
8. Verify Instance 2 settings are restored
9. Close application
10. Restart application
11. Switch to Instance 1
12. Close application
13. Restart application
14. Verify Instance 1 is now selected

**Expected Result**: ✅ Last selected instance loads on restart

---

### Test 6: Auto-Save Functionality

**Objective**: Verify data is automatically saved

**Steps**:
1. Start with Instance 1
2. Configure network settings
3. Load a sequence file
4. Wait 5 minutes (or perform 1000 scans)
5. Check cache file timestamp:
   - Windows: `C:\Users\[Username]\AppData\Local\CardSequenceValidator\CardSequenceValidator\app_cache_instance_1.json`
   - Right-click → Properties → Modified date
6. Verify timestamp is recent
7. Switch to Instance 2
8. Verify Instance 1 cache file timestamp updated (save on switch)

**Expected Result**: ✅ Cache files are updated regularly

---

### Test 7: Power Failure Simulation

**Objective**: Verify data recovery after unexpected shutdown

**Steps**:
1. Start with Instance 1
2. Configure network settings
3. Load a sequence file
4. Add some log entries (perform scans or manual entries)
5. Note the configuration and log count
6. Force close the application (kill process):
   - Windows: Task Manager → End Task
   - Or: `taskkill /IM python.exe /F` in terminal
7. Restart the application
8. Verify Instance 1 is still selected
9. Go to "Network & COM Setup"
10. Verify settings are restored
11. Go to "File Management"
12. Verify file is still loaded
13. Go to "Scanner & Logging"
14. Verify logs are restored

**Expected Result**: ✅ All data is recovered after power failure

---

### Test 8: Concurrent Instance Execution

**Objective**: Verify two instances can run simultaneously

**Steps**:
1. Open Terminal 1
2. Run: `python main.py`
3. Wait for app to load (Instance 1)
4. Configure Instance 1 with network settings
5. Open Terminal 2
6. Run: `python main.py`
7. Wait for app to load (Instance 2)
8. Configure Instance 2 with different network settings
9. In Terminal 1 app: Go to "Network & COM Setup"
10. Verify Instance 1 settings are correct
11. In Terminal 2 app: Go to "Network & COM Setup"
12. Verify Instance 2 settings are different
13. Perform scans in both instances simultaneously
14. Verify logs are separate in each instance
15. Close both applications
16. Restart one instance
17. Verify correct data loads

**Expected Result**: ✅ Two instances can run simultaneously with separate data

---

### Test 9: Cache File Integrity

**Objective**: Verify cache files are created correctly

**Steps**:
1. Start application
2. Navigate to cache directory:
   - Windows: `C:\Users\[Username]\AppData\Local\CardSequenceValidator\CardSequenceValidator\`
3. Verify files exist:
   - `instance_config.json` (global config)
   - `app_cache_instance_1.json` (Instance 1 data)
   - `app_cache_instance_2.json` (Instance 2 data)
4. Open `instance_config.json` in text editor
5. Verify content: `{"current_instance": 1}`
6. Switch to Instance 2
7. Verify `instance_config.json` now shows: `{"current_instance": 2}`
8. Open `app_cache_instance_1.json`
9. Verify JSON is valid and contains expected fields
10. Open `app_cache_instance_2.json`
11. Verify JSON is valid and contains expected fields

**Expected Result**: ✅ Cache files are created and updated correctly

---

### Test 10: UI Update on Switch

**Objective**: Verify UI updates correctly when switching instances

**Steps**:
1. Start with Instance 1
2. Configure network settings
3. Load a sequence file
4. Observe status indicators in home page
5. Switch to Instance 2
6. Observe status indicators update
7. Verify "File Loaded" shows "No File" (Instance 2 has no file)
8. Verify "Input Port" shows "Not Set" (Instance 2 has no network config)
9. Load a file in Instance 2
10. Switch back to Instance 1
11. Verify status indicators show Instance 1 data again

**Expected Result**: ✅ UI updates correctly on instance switch

---

## Stress Testing

### Test 11: Rapid Instance Switching

**Objective**: Verify system handles rapid switching

**Steps**:
1. Start application
2. Rapidly click between Instance 1 and Instance 2 buttons (10+ times)
3. Verify no crashes or errors
4. Verify data is still correct after rapid switching
5. Check console for any error messages

**Expected Result**: ✅ System handles rapid switching without issues

---

### Test 12: Large Log Data

**Objective**: Verify system handles large logs

**Steps**:
1. Start with Instance 1
2. Perform 5000+ scans (or manually add many log entries)
3. Verify logs display correctly with pagination
4. Switch to Instance 2
5. Perform 5000+ scans
6. Switch back to Instance 1
7. Verify all 5000+ logs are still there
8. Check cache file size (should be reasonable)

**Expected Result**: ✅ System handles large logs efficiently

---

## Regression Testing

### Test 13: Existing Features Still Work

**Objective**: Verify multi-instance doesn't break existing features

**Steps**:
1. Test scanner functionality in both instances
2. Test file loading in both instances
3. Test network configuration in both instances
4. Test theme switching in both instances
5. Test log viewing and pagination in both instances
6. Test all buttons and UI elements

**Expected Result**: ✅ All existing features work correctly

---

## Test Results Template

```
Test Case: [Test Name]
Date: [Date]
Tester: [Name]
Environment: [OS, Python version, etc.]

Steps Performed:
1. [Step 1]
2. [Step 2]
...

Expected Result:
[Expected outcome]

Actual Result:
[What actually happened]

Status: ✅ PASS / ❌ FAIL

Notes:
[Any additional observations]
```

## Checklist

- [ ] Test 1: Basic Instance Selection
- [ ] Test 2: Separate Configuration Storage
- [ ] Test 3: Separate Logs
- [ ] Test 4: Theme Persistence Per Instance
- [ ] Test 5: Application Restart - Instance Persistence
- [ ] Test 6: Auto-Save Functionality
- [ ] Test 7: Power Failure Simulation
- [ ] Test 8: Concurrent Instance Execution
- [ ] Test 9: Cache File Integrity
- [ ] Test 10: UI Update on Switch
- [ ] Test 11: Rapid Instance Switching
- [ ] Test 12: Large Log Data
- [ ] Test 13: Existing Features Still Work

## Known Issues / Limitations

(To be filled in after testing)

## Sign-Off

- [ ] All tests passed
- [ ] No critical issues found
- [ ] Ready for production

Tested by: ________________
Date: ________________
