# Multi-Instance UI Visual Guide

## Instance Toggle Button Design

### Dark Theme

**Inactive State:**
```
┌──────────────────┐
│  Instance 1      │  ← Gray background (#555c6b)
└──────────────────┘
```

**Active State:**
```
┌──────────────────┐
│  Instance 1      │  ← Blue background (#00aaff)
└──────────────────┘
```

**Hover State (Inactive):**
```
┌──────────────────┐
│  Instance 1      │  ← Lighter gray (#666e7f)
└──────────────────┘
```

**Hover State (Active):**
```
┌──────────────────┐
│  Instance 1      │  ← Lighter blue (#33bbff)
└──────────────────┘
```

### Light Theme

**Inactive State:**
```
┌──────────────────┐
│  Instance 1      │  ← Gray background (#6c757d)
└──────────────────┘
```

**Active State:**
```
┌──────────────────┐
│  Instance 1      │  ← Blue background (#007bff)
└──────────────────┘
```

## Home Page Header Layout

### Before (Old Design)
```
┌─────────────────────────────────────────────────────────────────┐
│ Logo │ Title │ Clock │ Instance 1 │ Instance 2 │ Theme Toggle   │
│      │       │       │ [Button]   │ [Button]   │ [Button]       │
└─────────────────────────────────────────────────────────────────┘
```

### After (New Design)
```
┌─────────────────────────────────────────────────────────────────┐
│ Logo │ Title │ Clock │ Instance │ Theme Toggle                  │
│      │       │       │ [1] [2]  │ [Button]                      │
│      │       │       │ Toggle   │                               │
└─────────────────────────────────────────────────────────────────┘
```

## Scanner Logging Window Header

### Before (No Instance Display)
```
┌─────────────────────────────────────────────────────────────────┐
│ Live Scanner Feed & Validation Log │ Clock │ Start │ Stop       │
└─────────────────────────────────────────────────────────────────┘
```

### After (With Instance Display)
```
┌─────────────────────────────────────────────────────────────────┐
│ Live Scanner Feed & Validation Log │ Instance 1 │ Clock │ Start │ Stop │
│                                    │ (Blue)     │       │       │      │
└─────────────────────────────────────────────────────────────────┘
```

## Log Table - Single Card Type

### Before (No Instance Column)
```
┌──────────────────────────────────────────────────────────────┐
│ Entry # │ Time     │ Scanned ID │ Expected ID │ Result       │
├──────────────────────────────────────────────────────────────┤
│    1    │ 10:30:45 │  ABC123    │   ABC123    │ OK (Green)   │
│    2    │ 10:31:12 │  DEF456    │   DEF456    │ OK (Green)   │
│    3    │ 10:31:45 │  GHI789    │   GHI789    │ OK (Green)   │
└──────────────────────────────────────────────────────────────┘
```

### After (With Instance Column)
```
┌────────────────────────────────────────────────────────────────────┐
│ Entry # │ Time     │ Scanned ID │ Expected ID │ Result       │ Instance    │
├────────────────────────────────────────────────────────────────────┤
│    1    │ 10:30:45 │  ABC123    │   ABC123    │ OK (Green)   │ Instance 1  │
│    2    │ 10:31:12 │  DEF456    │   DEF456    │ OK (Green)   │ Instance 1  │
│    3    │ 10:31:45 │  GHI789    │   GHI789    │ OK (Green)   │ Instance 2  │
│         │          │            │             │              │ (Blue)      │
└────────────────────────────────────────────────────────────────────┘
```

## Log Table - Half/Quarter Card Type

### Before (No Instance Column)
```
┌──────────────────────────────────────────────────────────────────────┐
│ Entry # │ Time     │ Scanned ID │ Expected ID │ Result │ Scan Side   │
├──────────────────────────────────────────────────────────────────────┤
│    1    │ 10:30:45 │  ABC123    │   ABC123    │ OK     │ Left        │
│    2    │ 10:31:12 │  DEF456    │   DEF456    │ OK     │ Right       │
│    3    │ 10:31:45 │  GHI789    │   GHI789    │ OK     │ Left        │
└──────────────────────────────────────────────────────────────────────┘
```

### After (With Instance Column)
```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Entry # │ Time     │ Scanned ID │ Expected ID │ Result │ Scan Side │ Instance   │
├──────────────────────────────────────────────────────────────────────────────┤
│    1    │ 10:30:45 │  ABC123    │   ABC123    │ OK     │ Left      │ Instance 1 │
│    2    │ 10:31:12 │  DEF456    │   DEF456    │ OK     │ Right     │ Instance 1 │
│    3    │ 10:31:45 │  GHI789    │   GHI789    │ OK     │ Left      │ Instance 2 │
│         │          │            │             │        │           │ (Blue)     │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Color Scheme

### Dark Theme
```
Inactive Button:    #555c6b (Gray)
Active Button:      #00aaff (Bright Blue)
Hover Inactive:     #666e7f (Lighter Gray)
Hover Active:       #33bbff (Lighter Blue)
Instance Text:      #00aaff (Bright Blue)
```

### Light Theme
```
Inactive Button:    #6c757d (Gray)
Active Button:      #007bff (Blue)
Hover Inactive:     #5a6268 (Darker Gray)
Hover Active:       #0056b3 (Darker Blue)
Instance Text:      #007bff (Blue)
```

## Interaction Flow

### Switching Instances

```
User clicks Instance 2 button
        ↓
Instance 2 button becomes active (blue)
Instance 1 button becomes inactive (gray)
        ↓
Current instance data is saved
        ↓
New instance data is loaded
        ↓
Scanner logging window updates:
  - Instance display shows "Instance 2"
  - Log table shows logs from Instance 2
        ↓
Confirmation message appears
```

## Responsive Design

### Full Screen
```
┌─────────────────────────────────────────────────────────────────┐
│ Logo │ Title │ Clock │ Instance │ Theme │ Extra Space           │
└─────────────────────────────────────────────────────────────────┘
```

### Compact Screen
```
┌──────────────────────────────────────────────────────────────┐
│ Logo │ Title │ Clock │ Instance │ Theme                      │
└──────────────────────────────────────────────────────────────┘
```

## Accessibility Features

### Visual Indicators
- ✅ Color contrast meets WCAG standards
- ✅ Active state clearly distinguished
- ✅ Hover effects provide feedback
- ✅ Text labels are clear and readable

### Keyboard Navigation
- ✅ Buttons are keyboard accessible
- ✅ Tab order is logical
- ✅ Enter/Space to activate buttons
- ✅ Focus indicators visible

### Screen Reader Support
- ✅ Button labels are descriptive
- ✅ Instance information is announced
- ✅ Table headers are properly marked
- ✅ Status changes are announced

## Animation & Transitions

### Button State Changes
```
Inactive → Hover:     Smooth color transition (200ms)
Hover → Active:       Smooth color transition (200ms)
Active → Inactive:    Smooth color transition (200ms)
```

### Instance Display Update
```
Old Instance → New Instance:  Instant update
Log table refresh:            Smooth scroll to bottom
```

## Summary

The UI improvements provide:

1. **Professional Toggle Design**
   - Matches app aesthetic
   - Clear active/inactive states
   - Smooth transitions

2. **Instance Tracking in Logs**
   - Every log entry shows instance
   - Blue highlight for visibility
   - Single dedicated column

3. **Instance Display**
   - Prominent in scanner logging header
   - Always visible
   - Updates automatically

4. **Consistent Theming**
   - Works with dark and light themes
   - Color scheme matches app
   - Professional appearance

5. **Better User Experience**
   - Clear indication of active instance
   - Easy to track which instance generated logs
   - Professional and polished design
