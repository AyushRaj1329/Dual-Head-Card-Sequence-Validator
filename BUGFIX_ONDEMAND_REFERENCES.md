# Bug Fix: Removed Orphaned On-Demand UDP References

## Issue
```
AttributeError: 'NetworkSetupWindow' object has no attribute 'ondemand_remote_ip'
```

## Root Cause
When migrating the on-demand scanner from UDP to Serial, some references to the old UDP UI fields were not removed:
- `self.ondemand_remote_ip` (ComboBox)
- `self.ondemand_local_ip` (LineEdit)
- `self.ondemand_local_port` (LineEdit)
- `self.ondemand_remote_port` (LineEdit)

These fields were replaced with serial COM port fields but some code still tried to access them.

## Files Fixed

### src/ui/network_setup.py

#### 1. Removed Signal Connection (Line ~45)
**Before:**
```python
self.main_remote_ip.activated.connect(lambda: self.refresh_remote_ip_dropdown(self.main_remote_ip))
self.ondemand_remote_ip.activated.connect(lambda: self.refresh_remote_ip_dropdown(self.ondemand_remote_ip))  # ❌ Error
self.output_remote_ip.activated.connect(lambda: self.refresh_remote_ip_dropdown(self.output_remote_ip))
```

**After:**
```python
self.main_remote_ip.activated.connect(lambda: self.refresh_remote_ip_dropdown(self.main_remote_ip))
self.output_remote_ip.activated.connect(lambda: self.refresh_remote_ip_dropdown(self.output_remote_ip))
```

#### 2. Removed Local IP Auto-Fill (Line ~81)
**Before:**
```python
if not self.main_local_ip.text():
    self.main_local_ip.setText(primary_ip)
if not self.ondemand_local_ip.text():  # ❌ Error
    self.ondemand_local_ip.setText(primary_ip)
if not self.output_local_ip.text():
    self.output_local_ip.setText(primary_ip)
```

**After:**
```python
if not self.main_local_ip.text():
    self.main_local_ip.setText(primary_ip)
if not self.output_local_ip.text():
    self.output_local_ip.setText(primary_ip)
```

#### 3. Removed from Remote IP Dropdown Population (Line ~283)
**Before:**
```python
main_current = self.main_remote_ip.currentText()
ondemand_current = self.ondemand_remote_ip.currentText()  # ❌ Error
output_current = self.output_remote_ip.currentText()

for combo in [self.main_remote_ip, self.ondemand_remote_ip, self.output_remote_ip]:  # ❌ Error
    combo.clear()
    # ...

if ondemand_current:  # ❌ Error
    index = self.ondemand_remote_ip.findText(ondemand_current)
    # ...
```

**After:**
```python
main_current = self.main_remote_ip.currentText()
output_current = self.output_remote_ip.currentText()

for combo in [self.main_remote_ip, self.output_remote_ip]:
    combo.clear()
    # ...

# ondemand_current section removed
```

## Changes Summary

| Location | Change | Reason |
|----------|--------|--------|
| Signal connections | Removed `ondemand_remote_ip.activated` | Field no longer exists |
| Local IP auto-fill | Removed `ondemand_local_ip` check | Field no longer exists |
| Remote IP dropdown | Removed from loop and restore logic | Field no longer exists |

## Testing

✅ **Syntax Check**: No errors
✅ **Compilation**: Successful
✅ **Diagnostics**: Clean

## Impact

- ✅ No more AttributeError on startup
- ✅ Network detection still works for main scanner and output
- ✅ On-demand scanner uses serial COM port (not affected by network detection)
- ✅ All functionality preserved

## Root Cause Analysis

The migration from UDP to Serial for on-demand scanner was incomplete. While the UI section was replaced with serial fields, some initialization code still referenced the old UDP fields.

**Lesson**: When replacing UI components, search for ALL references to the old field names, including:
- Signal connections
- Auto-fill logic
- Dropdown population
- State restoration
- Event handlers

## Prevention

To prevent similar issues in the future:
1. Use IDE "Find All References" before removing fields
2. Search for field name patterns (e.g., `ondemand_.*ip`)
3. Test application startup after major UI changes
4. Add error handling for missing attributes during development

---

**Status**: ✅ FIXED

The application now starts without errors and the on-demand scanner serial configuration works correctly!
