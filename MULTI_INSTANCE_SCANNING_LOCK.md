# Multi-Instance Scanning Lock Feature

## Overview

Once scanning is started in an instance, the instance selector is locked and cannot be changed for the lifetime of that window instance. This prevents accidental instance switching during active scanning operations.

## Feature Details

### What Gets Locked

When scanning is active:
- Instance toggle buttons are **disabled** (grayed out)
- Clicking disabled buttons has no effect
- User cannot switch instances
- Visual feedback shows buttons are disabled

### When Buttons Are Unlocked

Instance buttons are re-enabled when:
- Scanning is stopped
- Validation is completed
- User clicks "Stop Validation" button
- Application window is closed and reopened

### User Experience

**Before Scanning:**
```
Instance Selector: [Instance 1] [Instance 2]
                   (Enabled)    (Enabled)
                   (Clickable)  (Clickable)
```

**During Scanning:**
```
Instance Selector: [Instance 1] [Instance 2]
                   (Disabled)   (Disabled)
                   (Grayed out) (Grayed out)
                   (Not clickable)
```

**After Stopping:**
```
Instance Selector: [Instance 1] [Instance 2]
                   (Enabled)    (Enabled)
                   (Clickable)  (Clickable)
```

## Implementation

### Code Changes

**File: src/ui/main_application.py**

1. **Updated switch_instance() method**
   - Checks if scanning is active
   - Shows warning message if user tries to switch during scanning
   - Reverts button to current instance
   - Prevents instance switch

2. **New update_instance_button_state() method**
   - Disables buttons when scanning is active
   - Enables buttons when scanning stops
   - Called whenever state changes

3. **Connected state_changed signal**
   - Calls update_instance_button_state() on state changes
   - Automatically updates button state

### Code Flow

```
User clicks instance button
        ↓
switch_instance() called
        ↓
Check: Is scanning active?
        ├─ YES: Show warning, revert button, return
        └─ NO: Proceed with switch
        ↓
Save current instance data
        ↓
Switch instance
        ↓
Load new instance data
        ↓
Update UI
        ↓
Show confirmation
```

### Button State Management

```
Scanning starts
        ↓
state_changed signal emitted
        ↓
update_instance_button_state() called
        ↓
is_scanning = True
        ↓
Disable all instance buttons
        ↓
Buttons appear grayed out

---

Scanning stops
        ↓
state_changed signal emitted
        ↓
update_instance_button_state() called
        ↓
is_scanning = False
        ↓
Enable all instance buttons
        ↓
Buttons appear normal
```

## User Scenarios

### Scenario 1: Normal Scanning

1. User starts app (Instance 1 selected)
2. User configures network and loads file
3. User clicks "Start Validation"
4. Instance buttons become disabled (grayed out)
5. User scans cards
6. User clicks "Stop Validation"
7. Instance buttons become enabled again
8. User can now switch instances

### Scenario 2: Attempted Switch During Scanning

1. User starts scanning with Instance 1
2. Instance buttons are disabled
3. User tries to click "Instance 2" button
4. Button click has no effect (disabled)
5. Warning message appears: "Cannot Switch Instance - Instance cannot be changed while scanning is active"
6. User must stop scanning first
7. After stopping, user can switch instances

### Scenario 3: Multiple Windows

1. Terminal 1: Start app with Instance 1, start scanning
   - Instance buttons disabled in Terminal 1
2. Terminal 2: Start app with Instance 2, start scanning
   - Instance buttons disabled in Terminal 2
3. Each window is independent
4. Stopping scanning in Terminal 1 enables buttons in Terminal 1
5. Stopping scanning in Terminal 2 enables buttons in Terminal 2

## Visual Feedback

### Disabled Button Appearance

**Dark Theme:**
```
Disabled Button:
┌──────────────────┐
│  Instance 1      │  ← Grayed out
│  (Disabled)      │  ← Reduced opacity
└──────────────────┘
```

**Light Theme:**
```
Disabled Button:
┌──────────────────┐
│  Instance 1      │  ← Grayed out
│  (Disabled)      │  ← Reduced opacity
└──────────────────┘
```

### Warning Message

When user tries to switch during scanning:
```
┌─────────────────────────────────────────────────────┐
│ Cannot Switch Instance                              │
├─────────────────────────────────────────────────────┤
│ Instance cannot be changed while scanning is active.│
│                                                     │
│ Stop the validation first to switch instances.      │
│                                                     │
│                                          [OK]       │
└─────────────────────────────────────────────────────┘
```

## Benefits

✅ **Prevents Accidental Switches**
- User cannot accidentally switch instances during scanning
- Protects data integrity

✅ **Clear Visual Feedback**
- Disabled buttons show they're not clickable
- Warning message explains why

✅ **Intuitive Behavior**
- Buttons are disabled when action is not allowed
- Standard UI pattern

✅ **Data Protection**
- Prevents mixing logs from different instances
- Ensures clean separation of data

✅ **Better User Experience**
- No confusion about which instance is active
- Clear indication of what's allowed

## Technical Details

### State Management

```python
# In app_state.py
self.is_scanning = False  # Tracks scanning status

# When scanning starts
self.is_scanning = True
self.state_changed.emit()  # Triggers button update

# When scanning stops
self.is_scanning = False
self.state_changed.emit()  # Triggers button update
```

### Button Disabling

```python
# In main_application.py
def update_instance_button_state(self):
    """Enable/disable instance buttons based on scanning status"""
    is_scanning = self.app_state.is_scanning
    for btn in self.instance_button_group.buttons():
        btn.setEnabled(not is_scanning)
```

### Switch Prevention

```python
def switch_instance(self, instance_num):
    # Prevent switching if scanning is active
    if self.app_state.is_scanning:
        QMessageBox.warning(
            self,
            "Cannot Switch Instance",
            "Instance cannot be changed while scanning is active.\n\n"
            "Stop the validation first to switch instances."
        )
        # Revert button to current instance
        current_btn = self.instance_button_group.button(
            self.app_state.current_instance
        )
        if current_btn:
            current_btn.setChecked(True)
        return
    
    # Proceed with switch...
```

## Testing

### Test Case 1: Button Disabling

1. Start app
2. Instance buttons should be enabled
3. Click "Start Validation"
4. Instance buttons should be disabled (grayed out)
5. Click "Stop Validation"
6. Instance buttons should be enabled again

**Expected Result:** ✅ Buttons enable/disable correctly

### Test Case 2: Switch Prevention

1. Start app
2. Click "Start Validation"
3. Try to click "Instance 2" button
4. Button should not respond
5. Warning message should appear
6. Click "Stop Validation"
7. Try to click "Instance 2" button
8. Button should respond and switch instance

**Expected Result:** ✅ Switch prevented during scanning

### Test Case 3: Button State Persistence

1. Start app with Instance 1
2. Click "Start Validation"
3. Buttons are disabled
4. Open another window (Terminal 2)
5. Start app with Instance 2
6. Buttons in Terminal 2 should be enabled
7. Click "Start Validation" in Terminal 2
8. Buttons in Terminal 2 should be disabled
9. Buttons in Terminal 1 should still be disabled

**Expected Result:** ✅ Each window manages its own button state

### Test Case 4: Visual Feedback

1. Start app
2. Observe instance buttons (normal appearance)
3. Click "Start Validation"
4. Observe instance buttons (grayed out)
5. Hover over disabled button
6. Button should not respond to hover
7. Click "Stop Validation"
8. Observe instance buttons (normal appearance again)

**Expected Result:** ✅ Visual feedback is clear

## Backward Compatibility

✅ No breaking changes
✅ Existing functionality preserved
✅ Only adds safety feature
✅ No impact on data or logs

## Performance Impact

- **Minimal**: Only adds button state check
- **Memory**: No additional overhead
- **UI**: No performance impact
- **Rendering**: Smooth and responsive

## Summary

The scanning lock feature provides:

1. **Safety** - Prevents accidental instance switches during scanning
2. **Clarity** - Clear visual indication of what's allowed
3. **Protection** - Ensures data integrity
4. **Usability** - Intuitive behavior
5. **Feedback** - Warning message explains why action is blocked

This feature enhances the multi-instance system by preventing user errors and protecting data integrity during active scanning operations.

---

**Status**: ✅ Implemented and Ready
**Compatibility**: Backward compatible
**Performance**: No impact
**Testing**: Ready for QA
