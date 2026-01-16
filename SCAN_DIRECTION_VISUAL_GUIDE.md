# Scan Direction - Visual Guide

## 🎯 Feature Location

```
Main Window
    ↓
[File Management] Button
    ↓
File Management Window
    ↓
[🔄 Top → Bottom] Button ← HERE!
```

## 📋 Complete Workflow

### Scenario 1: Top → Bottom (Normal Order)

```
┌─────────────────────────────────────────┐
│  File Management Window                 │
├─────────────────────────────────────────┤
│                                         │
│  📁 Load Sequence File                  │
│     ✓ File loaded: test_cards.csv      │
│     ✓ 100 cards loaded                 │
│                                         │
│  🔄 [Top → Bottom] ← Click to toggle   │
│                                         │
└─────────────────────────────────────────┘

Your file order:
Card 1  ─┐
Card 2   │
Card 3   │
Card 4   │
...      │ Scan Direction: ↓
Card 97  │
Card 98  │
Card 99  │
Card 100─┘

You scan Card 25 first:
Expected sequence: 25 → 26 → 27 → 28 → ... → 100
```

### Scenario 2: Bottom → Top (Reverse Order)

```
┌─────────────────────────────────────────┐
│  File Management Window                 │
├─────────────────────────────────────────┤
│                                         │
│  📁 Load Sequence File                  │
│     ✓ File loaded: test_cards.csv      │
│     ✓ 100 cards loaded                 │
│                                         │
│  🔄 [Bottom → Top] ← Currently active  │
│                                         │
└─────────────────────────────────────────┘

Your file order:
Card 1  ─┐
Card 2   │
Card 3   │
Card 4   │
...      │ Scan Direction: ↑
Card 97  │
Card 98  │
Card 99  │
Card 100─┘

You scan Card 75 first:
Expected sequence: 75 → 74 → 73 → 72 → ... → 1
```

## 🎬 Step-by-Step Animation

### Step 1: Load Your File
```
┌──────────────────────────┐
│ [Load Sequence File]     │ ← Click
└──────────────────────────┘
         ↓
┌──────────────────────────┐
│ Select Card Type:        │
│ ○ Single Card            │
│ ● Half Card              │ ← Select
│ ○ Quarter Card           │
└──────────────────────────┘
         ↓
┌──────────────────────────┐
│ Choose file...           │
│ test_cards.csv           │ ← Select
└──────────────────────────┘
         ↓
✅ File loaded: 100 cards
```

### Step 2: Choose Direction
```
Before clicking:
┌──────────────────────────┐
│ 🔄 Top → Bottom          │ ← Default
└──────────────────────────┘

After clicking:
┌──────────────────────────┐
│ 🔄 Bottom → Top          │ ← Changed!
└──────────────────────────┘

Confirmation message:
┌─────────────────────────────────────┐
│ ✓ Scan Direction Changed            │
│                                     │
│ Scan direction changed to:          │
│ Bottom → Top (Last card first)      │
│                                     │
│ The first card you scan will be     │
│ set as the start card.              │
│                                     │
│ [OK]                                │
└─────────────────────────────────────┘
```

### Step 3: Start Scanning
```
┌──────────────────────────┐
│ Scanner & Logging        │ ← Navigate here
└──────────────────────────┘
         ↓
┌──────────────────────────┐
│ [Start Validation]       │ ← Click
└──────────────────────────┘
         ↓
Scanner ready! Scan first card...
```

### Step 4: Scan Cards
```
Top → Bottom Mode:
─────────────────────────────
Scan #1: Card 50
  Status: ✓ OK (Start card set)
  Next expected: Card 51

Scan #2: Card 51
  Status: ✓ OK
  Next expected: Card 52

Scan #3: Card 52
  Status: ✓ OK
  Next expected: Card 53


Bottom → Top Mode:
─────────────────────────────
Scan #1: Card 50
  Status: ✓ OK (Start card set)
  Next expected: Card 49

Scan #2: Card 49
  Status: ✓ OK
  Next expected: Card 48

Scan #3: Card 48
  Status: ✓ OK
  Next expected: Card 47
```

## ⚠️ Important Rules

### ❌ Cannot Change During Scanning
```
Scanning in progress...
         ↓
Click [🔄 Bottom → Top]
         ↓
┌─────────────────────────────────────┐
│ ⚠ Cannot Toggle Direction           │
│                                     │
│ Scan direction cannot be changed    │
│ after scanning has started.         │
│                                     │
│ Please clear the logs and restart   │
│ scanning to change direction.       │
│                                     │
│ [OK]                                │
└─────────────────────────────────────┘
```

### ✅ How to Change Mid-Scan
```
Step 1: Stop scanning
┌──────────────────────────┐
│ [Stop Validation]        │ ← Click
└──────────────────────────┘

Step 2: Clear logs
┌──────────────────────────┐
│ [Clear Logs]             │ ← Click
└──────────────────────────┘

Step 3: Toggle direction
┌──────────────────────────┐
│ 🔄 [Top → Bottom]        │ ← Click to change
└──────────────────────────┘

Step 4: Restart scanning
┌──────────────────────────┐
│ [Start Validation]       │ ← Click
└──────────────────────────┘
```

## 📊 Validation Log Display

### Top → Bottom
```
┌────────────────────────────────────────────────────┐
│ Validation Log                                     │
├────────────────────────────────────────────────────┤
│ Time     │ Scanned  │ Expected │ Status │ Side    │
├──────────┼──────────┼──────────┼────────┼─────────┤
│ 10:30:01 │ QR_050   │ QR_050   │ ✓ OK   │ Left    │
│ 10:30:02 │ QR_051   │ QR_051   │ ✓ OK   │ Left    │
│ 10:30:03 │ QR_052   │ QR_052   │ ✓ OK   │ Left    │
│ 10:30:04 │ QR_053   │ QR_053   │ ✓ OK   │ Left    │
└────────────────────────────────────────────────────┘
Direction: Top → Bottom (Card 50 → 51 → 52 → 53...)
```

### Bottom → Top
```
┌────────────────────────────────────────────────────┐
│ Validation Log                                     │
├────────────────────────────────────────────────────┤
│ Time     │ Scanned  │ Expected │ Status │ Side    │
├──────────┼──────────┼──────────┼────────┼─────────┤
│ 10:30:01 │ QR_050   │ QR_050   │ ✓ OK   │ Left    │
│ 10:30:02 │ QR_049   │ QR_049   │ ✓ OK   │ Left    │
│ 10:30:03 │ QR_048   │ QR_048   │ ✓ OK   │ Left    │
│ 10:30:04 │ QR_047   │ QR_047   │ ✓ OK   │ Left    │
└────────────────────────────────────────────────────┘
Direction: Bottom → Top (Card 50 → 49 → 48 → 47...)
```

## 🎯 Use Cases

### Use Case 1: Quality Control Line
```
Production line: Cards come out in order
Direction: Top → Bottom ✓
Start: Scan first card from production
Continue: Validate each card in sequence
```

### Use Case 2: Inventory Check (Reverse)
```
Inventory: Cards stacked, need to check from top
Direction: Bottom → Top ✓
Start: Scan top card (last in file)
Continue: Work through stack backwards
```

### Use Case 3: Partial Batch
```
Batch: Cards 50-100 only
Direction: Top → Bottom ✓
Start: Scan Card 50
Continue: Validate 50 → 51 → ... → 100
```

### Use Case 4: Return Processing
```
Returns: Cards come back in reverse order
Direction: Bottom → Top ✓
Start: Scan first returned card
Continue: Process in reverse sequence
```

## 💡 Pro Tips

### Tip 1: Check Direction Before Starting
```
✓ Always verify the button shows correct direction
✓ Button text clearly shows: "Top → Bottom" or "Bottom → Top"
✓ Toggle if needed BEFORE starting scan
```

### Tip 2: Use Start Card Detection
```
✓ No need to manually set start position
✓ First card scanned = start position
✓ Works in both directions
✓ Flexible starting point
```

### Tip 3: Direction Persists
```
✓ Direction saved to cache
✓ Restored when app restarts
✓ No need to set every time
✓ Change only when needed
```

### Tip 4: Clear Logs to Reset
```
✓ Want to change direction mid-scan?
✓ Clear logs first
✓ Toggle direction
✓ Start fresh
```

## 🔍 Troubleshooting

### Problem: Button doesn't toggle
**Solution**: Make sure scanning hasn't started. Clear logs first.

### Problem: Cards validating wrong
**Solution**: Check button shows correct direction before starting.

### Problem: Can't find the button
**Solution**: It's in File Management window, below the file load section.

### Problem: Direction resets
**Solution**: Direction is saved. Check if you cleared cache or reinstalled.

## ✅ Quick Reference

| Action | Location | Button |
|--------|----------|--------|
| Load File | File Management | 📁 Load Sequence File |
| Toggle Direction | File Management | 🔄 Top → Bottom / Bottom → Top |
| Start Scanning | Scanner & Logging | ▶ Start Validation |
| Stop Scanning | Scanner & Logging | ⏸ Stop Validation |
| Clear Logs | File Management | 🗑 Clear Logs |

---

**Remember**: The scan direction feature is fully working and ready to use!
