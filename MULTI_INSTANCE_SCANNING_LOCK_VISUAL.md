# Multi-Instance Scanning Lock - Visual Guide

## Button States

### State 1: Not Scanning (Enabled)

```
┌─────────────────────────────────────────────────────────────┐
│ Instance Selector                                           │
│                                                             │
│ ┌──────────────────┐  ┌──────────────────┐                │
│ │  Instance 1      │  │  Instance 2      │                │
│ │  [Active]        │  │  [Inactive]      │                │
│ │  (Blue)          │  │  (Gray)          │                │
│ │  ✓ Enabled       │  │  ✓ Enabled       │                │
│ │  ✓ Clickable     │  │  ✓ Clickable     │                │
│ └──────────────────┘  └──────────────────┘                │
│                                                             │
│ Status: Ready to switch instances                          │
└─────────────────────────────────────────────────────────────┘
```

### State 2: Scanning Active (Disabled)

```
┌─────────────────────────────────────────────────────────────┐
│ Instance Selector                                           │
│                                                             │
│ ┌──────────────────┐  ┌──────────────────┐                │
│ │  Instance 1      │  │  Instance 2      │                │
│ │  [Disabled]      │  │  [Disabled]      │                │
│ │  (Grayed out)    │  │  (Grayed out)    │                │
│ │  ✗ Disabled      │  │  ✗ Disabled      │                │
│ │  ✗ Not clickable │  │  ✗ Not clickable │                │
│ └──────────────────┘  └──────────────────┘                │
│                                                             │
│ Status: Scanning in progress - Cannot switch               │
└─────────────────────────────────────────────────────────────┘
```

## User Interaction Flow

### Successful Switch (Not Scanning)

```
User clicks Instance 2
        ↓
┌─────────────────────────────────────────┐
│ Button is ENABLED                       │
│ Click is processed                      │
└─────────────────────────────────────────┘
        ↓
Save Instance 1 data
        ↓
Switch to Instance 2
        ↓
Load Instance 2 data
        ↓
Update UI
        ↓
┌─────────────────────────────────────────┐
│ Instance Switched                       │
│ Switched to Instance 2                  │
│                                [OK]     │
└─────────────────────────────────────────┘
        ↓
Instance 2 is now active
```

### Failed Switch (Scanning Active)

```
User clicks Instance 2
        ↓
┌─────────────────────────────────────────┐
│ Button is DISABLED                      │
│ Click is ignored                        │
└─────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────┐
│ Cannot Switch Instance                  │
│                                         │
│ Instance cannot be changed while        │
│ scanning is active.                     │
│                                         │
│ Stop the validation first to switch     │
│ instances.                              │
│                                [OK]     │
└─────────────────────────────────────────┘
        ↓
Button reverts to Instance 1
        ↓
Still on Instance 1
```

## Timeline: Scanning Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│ Application Start                                           │
│ Instance 1 selected                                         │
│ Buttons: ENABLED                                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ User configures network and loads file                      │
│ Buttons: ENABLED                                            │
│ User can switch instances                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ User clicks "Start Validation"                              │
│ Scanning starts                                             │
│ is_scanning = True                                          │
│ state_changed signal emitted                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ update_instance_button_state() called                       │
│ Buttons: DISABLED (grayed out)                              │
│ User cannot switch instances                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ User scans cards                                            │
│ Buttons: DISABLED                                           │
│ Logs generated with Instance 1 marker                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ User clicks "Stop Validation"                               │
│ Scanning stops                                              │
│ is_scanning = False                                         │
│ state_changed signal emitted                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ update_instance_button_state() called                       │
│ Buttons: ENABLED                                            │
│ User can now switch instances                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ User clicks "Instance 2"                                    │
│ Switch succeeds                                             │
│ Instance 2 selected                                         │
│ Buttons: ENABLED                                            │
└─────────────────────────────────────────────────────────────┘
```

## Multiple Windows Scenario

```
┌──────────────────────────────────────────────────────────────┐
│ Terminal 1                    │ Terminal 2                   │
├──────────────────────────────────────────────────────────────┤
│ Instance 1 selected           │ Instance 2 selected          │
│ Buttons: ENABLED              │ Buttons: ENABLED             │
│                               │                              │
│ Click "Start Validation"      │ Not scanning                 │
│ Scanning starts               │                              │
│ Buttons: DISABLED             │ Buttons: ENABLED             │
│ (grayed out)                  │                              │
│                               │                              │
│ Scanning in progress          │ Can switch instances         │
│ Buttons: DISABLED             │ Buttons: ENABLED             │
│                               │                              │
│ Click "Stop Validation"       │ Click "Instance 1"           │
│ Scanning stops                │ Switch succeeds              │
│ Buttons: ENABLED              │ Instance 1 selected          │
│                               │ Buttons: ENABLED             │
│                               │                              │
│ Can switch instances          │ Can switch instances         │
│ Buttons: ENABLED              │ Buttons: ENABLED             │
└──────────────────────────────────────────────────────────────┘
```

## Button Appearance

### Dark Theme

**Enabled (Active):**
```
┌──────────────────┐
│  Instance 1      │  ← Blue (#00aaff)
│                  │  ← Bright, clickable
└──────────────────┘
```

**Enabled (Inactive):**
```
┌──────────────────┐
│  Instance 2      │  ← Gray (#555c6b)
│                  │  ← Clickable
└──────────────────┘
```

**Disabled:**
```
┌──────────────────┐
│  Instance 1      │  ← Grayed out
│                  │  ← Reduced opacity
│  (Disabled)      │  ← Not clickable
└──────────────────┘
```

### Light Theme

**Enabled (Active):**
```
┌──────────────────┐
│  Instance 1      │  ← Blue (#007bff)
│                  │  ← Bright, clickable
└──────────────────┘
```

**Enabled (Inactive):**
```
┌──────────────────┐
│  Instance 2      │  ← Gray (#6c757d)
│                  │  ← Clickable
└──────────────────┘
```

**Disabled:**
```
┌──────────────────┐
│  Instance 1      │  ← Grayed out
│                  │  ← Reduced opacity
│  (Disabled)      │  ← Not clickable
└──────────────────┘
```

## Warning Message

```
┌─────────────────────────────────────────────────────────────┐
│ ⚠ Cannot Switch Instance                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Instance cannot be changed while scanning is active.       │
│                                                             │
│ Stop the validation first to switch instances.             │
│                                                             │
│                                              [OK]           │
└─────────────────────────────────────────────────────────────┘
```

## State Diagram

```
                    ┌─────────────────┐
                    │   Application   │
                    │     Started     │
                    └────────┬────────┘
                             │
                             ↓
                    ┌─────────────────┐
                    │  Buttons        │
                    │  ENABLED        │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ↓                 ↓
          ┌──────────────────┐  ┌──────────────────┐
          │ User clicks      │  │ User clicks      │
          │ "Start"          │  │ Instance button  │
          └────────┬─────────┘  └──────────────────┘
                   │                    │
                   ↓                    ↓
          ┌──────────────────┐  ┌──────────────────┐
          │ Scanning starts  │  │ Switch instance  │
          │ is_scanning=True │  │ (succeeds)       │
          └────────┬─────────┘  └──────────────────┘
                   │
                   ↓
          ┌──────────────────┐
          │ Buttons          │
          │ DISABLED         │
          └────────┬─────────┘
                   │
          ┌────────┴────────┐
          │                 │
          ↓                 ↓
┌──────────────────┐  ┌──────────────────┐
│ User scans       │  │ User clicks      │
│ (buttons stay    │  │ Instance button  │
│  disabled)       │  │ (warning shown)  │
└────────┬─────────┘  └──────────────────┘
         │                    │
         └────────┬───────────┘
                  │
                  ↓
         ┌──────────────────┐
         │ User clicks      │
         │ "Stop"           │
         └────────┬─────────┘
                  │
                  ↓
         ┌──────────────────┐
         │ Scanning stops   │
         │ is_scanning=False│
         └────────┬─────────┘
                  │
                  ↓
         ┌──────────────────┐
         │ Buttons          │
         │ ENABLED          │
         └────────┬─────────┘
                  │
                  ↓
         ┌──────────────────┐
         │ User can switch  │
         │ instances again  │
         └──────────────────┘
```

## Summary

The scanning lock feature provides:

1. **Clear Visual States**
   - Enabled buttons: Normal appearance, clickable
   - Disabled buttons: Grayed out, not clickable

2. **User Feedback**
   - Warning message when trying to switch
   - Button reverts to current instance
   - Clear explanation provided

3. **Data Protection**
   - Prevents accidental switches
   - Ensures clean data separation
   - Protects ongoing operations

4. **Intuitive Behavior**
   - Standard UI pattern
   - Users understand immediately
   - No confusion about state
