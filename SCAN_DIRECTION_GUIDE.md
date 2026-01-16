# Scan Direction Feature - User Guide

## Overview
The Card Sequence Validator supports two scanning directions:
- **Top → Bottom**: Scan cards in normal order (Card 1, 2, 3...)
- **Bottom → Top**: Scan cards in reverse order (Last card first)

## How to Use

### Step 1: Load Your File
1. Open the application
2. Go to **File Management** window
3. Click **"Load Sequence File"**
4. Select your card type (Single, Half, or Quarter)
5. Choose your file (.cpd, .txt, or .csv)

### Step 2: Select Scan Direction
In the **File Management** window, you'll see a button labeled:
- **🔄 Top → Bottom** (default) - Click to switch to Bottom → Top
- **🔄 Bottom → Top** - Click to switch back to Top → Bottom

### Step 3: Start Scanning
1. Go to **Scanner & Logging** window
2. Click **"Start Validation"**
3. Scan your first card

### How It Works

#### Top → Bottom Mode (Default)
- Scan cards in normal file order
- First card you scan becomes the start position
- Continue scanning: Card 1 → Card 2 → Card 3...
- Example: If you scan Card 5 first, continue with 6, 7, 8...

#### Bottom → Top Mode
- Scan cards in reverse file order
- First card you scan becomes the start position
- Continue scanning: Last Card → Second-to-Last → ...
- Example: If you scan Card 95 first, continue with 94, 93, 92...

### Important Notes

⚠️ **Cannot Change During Scanning**
- You cannot change scan direction after scanning has started
- To change direction mid-scan:
  1. Clear the logs
  2. Toggle the direction
  3. Restart scanning

✅ **Automatic Start Card Detection**
- The first card you scan sets the starting position
- No need to manually configure start position
- Works in both directions

✅ **Sequence Jump Detection**
- If you skip cards, the system detects it
- Shows approval dialog
- Logs skipped cards if approved

## Examples

### Example 1: Normal Scanning (Top → Bottom)
```
File has 100 cards
Direction: Top → Bottom
First scan: Card 10
Expected sequence: 10 → 11 → 12 → 13 → ... → 100
```

### Example 2: Reverse Scanning (Bottom → Top)
```
File has 100 cards
Direction: Bottom → Top
First scan: Card 90
Expected sequence: 90 → 89 → 88 → 87 → ... → 1
```

### Example 3: Starting from Middle (Bottom → Top)
```
File has 100 cards
Direction: Bottom → Top
First scan: Card 50
Expected sequence: 50 → 49 → 48 → 47 → ... → 1
```

## Troubleshooting

### Q: The direction button doesn't work
**A:** Make sure you haven't started scanning yet. Clear logs first.

### Q: Cards are validating in wrong order
**A:** Check the scan direction button shows the correct mode before starting.

### Q: I want to scan from the end of the file
**A:** 
1. Set direction to "Bottom → Top"
2. Scan the last card in your file first
3. Continue scanning backwards

### Q: Can I change direction mid-scan?
**A:** No. You must:
1. Stop scanning
2. Clear logs
3. Toggle direction
4. Restart scanning

## Technical Details

### How Direction Affects Validation
- **Top → Bottom**: `current_card_index` increments normally (0, 1, 2...)
- **Bottom → Top**: `current_card_index` maps to reverse array position

### Persistence
- Scan direction is saved to cache
- Restored when you restart the application
- Saved with other settings

### Integration with Other Features
- ✅ Works with all card types (Single, Half, Quarter)
- ✅ Works with sequence jump detection
- ✅ Works with start card auto-detection
- ✅ Works with on-demand scanning features

## Summary

The scan direction feature gives you flexibility in how you validate card sequences:
- **Top → Bottom**: Traditional forward scanning
- **Bottom → Top**: Reverse scanning from end of file

Simply toggle the button in File Management before starting your scan!
