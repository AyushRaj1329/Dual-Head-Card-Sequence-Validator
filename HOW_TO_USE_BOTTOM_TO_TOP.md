# How to Use Bottom-to-Top Scanning - Step by Step

## Quick Start Guide

### Step 1: Launch Application
```bash
python main.py
```

### Step 2: Go to File Management
Click the **"File & Log Management"** button on the home page.

### Step 3: Load Your File
1. Click **"Load Sequence File"**
2. Select your card type:
   - ○ Single Card (1 QR per card)
   - ● Half Card (2 QRs per card)
   - ○ Quarter Card (4 QRs per card)
3. Choose your file (.cpd, .txt, or .csv)
4. Wait for confirmation: "Loaded X cards"

### Step 4: Select Scan Direction
Look for the button that says **"🔄 Top → Bottom"**

Click it to toggle to **"🔄 Bottom → Top"**

You'll see a confirmation message:
```
✓ Scan Direction Changed

Scan direction changed to:
Bottom → Top (Last card first)

The first card you scan will be set as the start card.
Scanning will continue Bottom → Top from that card.

[OK]
```

### Step 5: Go to Scanner & Logging
The system will automatically navigate you to the Scanner & Logging window.

If not, click **"Scanner Control"** from the home page.

### Step 6: Start Validation
Click the **"Start Validation"** button.

The system is now ready and waiting for your first scan.

### Step 7: Scan Your First Card
Scan **any card** from your file. This will be your starting point.

**Example**: If you have 100 cards and scan Card 75:
```
✅ OK (Start card set)
Next expected: Card 74
```

### Step 8: Continue Scanning
Scan the **previous card** in the sequence.

**Example**: After scanning Card 75, scan Card 74:
```
✅ OK
Next expected: Card 73
```

### Step 9: Keep Going
Continue scanning backwards through your file:
```
Card 75 ✅ OK
Card 74 ✅ OK
Card 73 ✅ OK
Card 72 ✅ OK
Card 71 ✅ OK
...
```

## Complete Example

### Scenario: 100 Cards, Start from Card 80

```
┌─────────────────────────────────────────┐
│ Your File (100 cards)                   │
├─────────────────────────────────────────┤
│ Card 1                                  │
│ Card 2                                  │
│ ...                                     │
│ Card 79                                 │
│ Card 80  ← You scan this first         │
│ Card 81                                 │
│ ...                                     │
│ Card 99                                 │
│ Card 100                                │
└─────────────────────────────────────────┘

Scan Order (Bottom → Top):
1. Scan Card 80 → ✅ OK (Start card set)
2. Scan Card 79 → ✅ OK
3. Scan Card 78 → ✅ OK
4. Scan Card 77 → ✅ OK
5. Continue backwards...
```

## What If I Scan the Wrong Card?

### Scenario 1: Card Not in File
```
You scan: Card_XYZ (not in file)
System: ❌ NOT IN SEQUENCE
Action: Scan a valid card from your file
```

### Scenario 2: Card Out of Order
```
You scan: Card 75 (start)
Expected: Card 74
You scan: Card 72 (skipped Card 74)
System: Shows approval dialog
```

**Approval Dialog:**
```
┌─────────────────────────────────────────┐
│ Sequence Mismatch Detected              │
│                                         │
│ You skipped 1 card(s).                  │
│                                         │
│ Scanned: Card 72                        │
│ Expected: Card 74                       │
│                                         │
│ Do you want to jump to Card 72?        │
│                                         │
│ [Approve] [Reject]                      │
└─────────────────────────────────────────┘
```

**If you click Approve:**
- Card 74 logged as "SKIPPED"
- Card 72 logged as "OK (JUMPED)"
- Continue from Card 72 → 71 → 70...

**If you click Reject:**
- Card 72 logged as "NOT OK"
- Still expects Card 74
- Scan Card 74 next

## Common Use Cases

### Use Case 1: Inventory Check (Top of Stack)
```
Situation: Cards stacked, top card is last in file
Solution: Use Bottom → Top
Process:
1. Scan top card (e.g., Card 100)
2. Scan next card down (Card 99)
3. Continue through stack
```

### Use Case 2: Return Processing
```
Situation: Returned cards in reverse order
Solution: Use Bottom → Top
Process:
1. Scan first returned card
2. System validates in reverse
3. Process entire return batch
```

### Use Case 3: Partial Batch (End Section)
```
Situation: Only validating cards 70-100
Solution: Use Bottom → Top
Process:
1. Scan Card 100 first
2. Work backwards to Card 70
3. Stop when done
```

## Tips & Tricks

### Tip 1: Check Direction Before Starting
Always verify the button shows the correct direction:
- **"🔄 Top → Bottom"** = Normal order
- **"🔄 Bottom → Top"** = Reverse order

### Tip 2: Any Card Can Be First
You don't need to start at the last card. Start anywhere:
- Start at Card 100 → scan to Card 1
- Start at Card 75 → scan to Card 1
- Start at Card 50 → scan to Card 1

### Tip 3: Can't Change Mid-Scan
If you need to change direction after starting:
1. Stop validation
2. Clear logs
3. Toggle direction
4. Start again

### Tip 4: Watch the "Next Expected" Display
The scanner window shows what card to scan next:
```
┌─────────────────────────────────────────┐
│ Last Scanned: Card 75                   │
│ Current Card: Card 74                   │
│ Next Expected: Card 73                  │
└─────────────────────────────────────────┘
```

## Troubleshooting

### Problem: First card shows "NOT OK"
**Solution**: This was the bug that's now fixed! Update to the latest version.

### Problem: Direction button doesn't work
**Solution**: Make sure you haven't started scanning. Clear logs first.

### Problem: Cards validating in wrong order
**Solution**: Check the direction button before starting. It should show "🔄 Bottom → Top".

### Problem: Can't find the direction button
**Solution**: It's in the File Management window, in the "Scan Direction" section.

### Problem: System expects wrong card
**Solution**: 
1. Check scan direction is correct
2. Verify you're scanning the right card
3. Check the "Next Expected" display

## Visual Indicators

### Direction Button States
```
Top → Bottom Mode:
┌──────────────────────────┐
│ 🔄 Top → Bottom          │  ← Not checked
└──────────────────────────┘

Bottom → Top Mode:
┌──────────────────────────┐
│ 🔄 Bottom → Top          │  ← Checked (highlighted)
└──────────────────────────┘
```

### Validation Log Colors
```
✅ Green = OK (correct card)
❌ Red = NOT OK (wrong card)
🟠 Orange = SKIPPED (approved jump)
```

## Summary

Bottom-to-Top scanning is perfect for:
- ✅ Checking cards from the end of the file
- ✅ Processing returns in reverse order
- ✅ Validating stacked cards from top down
- ✅ Any scenario where reverse order makes sense

Just remember:
1. Load file
2. Toggle to "Bottom → Top"
3. Start scanning
4. Scan any card as first card
5. Continue backwards

**It's that simple!** 🎉
