# Multi-Instance Scanning Lock - Quick Reference

## What Changed

Instance selector buttons are now **locked during scanning** to prevent accidental instance switches.

## How It Works

### Before Scanning
```
Instance Selector: [Instance 1] [Instance 2]
                   ✓ Enabled    ✓ Enabled
                   ✓ Clickable  ✓ Clickable
```

### During Scanning
```
Instance Selector: [Instance 1] [Instance 2]
                   ✗ Disabled   ✗ Disabled
                   ✗ Grayed out ✗ Grayed out
                   ✗ Not clickable
```

### After Stopping
```
Instance Selector: [Instance 1] [Instance 2]
                   ✓ Enabled    ✓ Enabled
                   ✓ Clickable  ✓ Clickable
```

## User Actions

### To Switch Instances

1. **Before Scanning:**
   - Click instance button → Switch immediately ✓

2. **During Scanning:**
   - Click instance button → Button disabled, warning appears ✗
   - Message: "Instance cannot be changed while scanning is active"

3. **After Stopping:**
   - Click instance button → Switch immediately ✓

## Warning Message

When trying to switch during scanning:
```
Cannot Switch Instance

Instance cannot be changed while scanning is active.

Stop the validation first to switch instances.

[OK]
```

## Benefits

✅ Prevents accidental instance switches
✅ Protects data integrity
✅ Clear visual feedback
✅ Intuitive behavior

## Implementation Details

**File Modified:** `src/ui/main_application.py`

**Methods Added:**
- `update_instance_button_state()` - Enables/disables buttons
- Updated `switch_instance()` - Checks scanning status

**Signal Connected:**
- `state_changed` → `update_instance_button_state()`

## Testing

### Quick Test
1. Start app
2. Click "Start Validation"
3. Try to click instance button → Should be disabled
4. Click "Stop Validation"
5. Click instance button → Should work

## Scenarios

### Scenario 1: Normal Use
```
Start app → Configure → Start scanning → Buttons disabled
→ Scan cards → Stop scanning → Buttons enabled → Switch instance
```

### Scenario 2: Attempted Switch
```
Start scanning → Try to switch instance → Warning appears
→ Button reverts to current instance → Stop scanning → Switch instance
```

### Scenario 3: Multiple Windows
```
Window 1: Scanning (buttons disabled)
Window 2: Not scanning (buttons enabled)
Each window independent
```

## FAQ

**Q: Can I switch instances while scanning?**
A: No. Buttons are disabled during scanning to prevent accidental switches.

**Q: What if I try to click a disabled button?**
A: The button won't respond, and a warning message will appear.

**Q: How do I switch instances?**
A: Stop scanning first, then click the instance button.

**Q: Does this affect multiple windows?**
A: No. Each window manages its own button state independently.

**Q: Is this permanent?**
A: No. Buttons are re-enabled when scanning stops.

## Visual Indicators

### Disabled Button (Dark Theme)
- Grayed out appearance
- Reduced opacity
- No hover effect
- Not clickable

### Disabled Button (Light Theme)
- Grayed out appearance
- Reduced opacity
- No hover effect
- Not clickable

## Backward Compatibility

✅ No breaking changes
✅ Existing functionality preserved
✅ Only adds safety feature

## Performance

- No performance impact
- Minimal memory overhead
- Smooth UI response

---

**Status**: ✅ Ready to Use
**Compatibility**: Backward compatible
**Performance**: No impact
