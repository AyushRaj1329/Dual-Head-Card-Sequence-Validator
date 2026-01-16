# Quarter Card Side Logic - Detailed Explanation

## Overview
Your program uses a **quarter-based positioning system** to determine which QR code belongs to which side of a quarter card. The logic divides the file into 4 equal quarters and assigns each quarter to a specific corner.

## The Quarter System

### Visual Representation
```
Physical Card Layout:
┌─────────────┬─────────────┐
│             │             │
│  Top-Left   │  Top-Right  │
│     (TL)    │     (TR)    │
│             │             │
├─────────────┼─────────────┤
│             │             │
│ Bottom-Left │Bottom-Right │
│     (BL)    │     (BR)    │
│             │             │
└─────────────┴─────────────┘
```

### File Organization
The file is divided into 4 quarters, and each quarter is assigned to a corner:

```
File Structure (40 QR codes total):
┌──────────────────────────────────────────────────────────┐
│ Lines 1-10:   Bottom-Left (BL)   - 1st Quarter          │
│ Lines 11-20:  Top-Left (TL)      - 2nd Quarter          │
│ Lines 21-30:  Top-Right (TR)     - 3rd Quarter          │
│ Lines 31-40:  Bottom-Right (BR)  - 4th Quarter          │
└──────────────────────────────────────────────────────────┘
```

## The Logic Step-by-Step

### Step 1: Count Total QR Codes
```python
total_cards = len(lines)  # e.g., 40 QR codes
quarter_size = total_cards // 4  # 40 // 4 = 10
```

### Step 2: Divide into Quarters
```
Quarter 1 (BL): Lines 0-9    (indices 0 to 9)
Quarter 2 (TL): Lines 10-19  (indices 10 to 19)
Quarter 3 (TR): Lines 20-29  (indices 20 to 29)
Quarter 4 (BR): Lines 30-39  (indices 30 to 39)
```

### Step 3: Map to Cards
Each position `i` in a quarter corresponds to Card `i+1`:

```
For Card 1:
  BL = Line 0  (1st quarter, position 0)
  TL = Line 10 (2nd quarter, position 0)
  TR = Line 20 (3rd quarter, position 0)
  BR = Line 30 (4th quarter, position 0)

For Card 2:
  BL = Line 1  (1st quarter, position 1)
  TL = Line 11 (2nd quarter, position 1)
  TR = Line 21 (3rd quarter, position 1)
  BR = Line 31 (4th quarter, position 1)

For Card 3:
  BL = Line 2  (1st quarter, position 2)
  TL = Line 12 (2nd quarter, position 2)
  TR = Line 22 (3rd quarter, position 2)
  BR = Line 32 (4th quarter, position 2)
```

## Code Walkthrough

### For TXT Files
```python
elif card_type == CardType.QUARTER:
    # Quarter card logic: 1st->BL, 2nd->TL, 3rd->TR, 4th->BR
    quarter_size = total_cards // 4
    
    for i in range(quarter_size):
        bl_qr = lines[i]                          # 1st quarter -> BL
        tl_qr = lines[i + quarter_size]           # 2nd quarter -> TL
        tr_qr = lines[i + 2 * quarter_size]       # 3rd quarter -> TR
        br_qr = lines[i + 3 * quarter_size]       # 4th quarter -> BR
        
        card_data.append((f"Card_{i+1}", bl_qr, tl_qr, tr_qr, br_qr))
```

### For CPD/CSV Files (Single ICCID Column)
```python
elif card_type == CardType.QUARTER:
    quarter_size = total_cards // 4
    
    if card_index <= quarter_size:
        # First quarter -> Bottom-Left
        position = "BL"
        base_card = card_index
    elif card_index <= 2 * quarter_size:
        # Second quarter -> Top-Left
        position = "TL"
        base_card = card_index - quarter_size
    elif card_index <= 3 * quarter_size:
        # Third quarter -> Top-Right
        position = "TR"
        base_card = card_index - 2 * quarter_size
    else:
        # Fourth quarter -> Bottom-Right
        position = "BR"
        base_card = card_index - 3 * quarter_size
    
    card_data.append((str(base_card), qr_code, position))
```

Then merge all positions for each card:
```python
merged_cards = {}
for numcard, qr_code, position in card_data:
    if numcard not in merged_cards:
        merged_cards[numcard] = {"BL": "", "TL": "", "TR": "", "BR": ""}
    merged_cards[numcard][position] = qr_code

# Convert to final format: (numcard, BL, TL, TR, BR)
card_data = []
for numcard in sorted(merged_cards.keys(), key=int):
    card = merged_cards[numcard]
    card_data.append((numcard, card["BL"], card["TL"], card["TR"], card["BR"]))
```

## Concrete Example

### Example File (40 QR codes)
```
Line 0:  QR_BL_1    ← Card 1, Bottom-Left
Line 1:  QR_BL_2    ← Card 2, Bottom-Left
Line 2:  QR_BL_3    ← Card 3, Bottom-Left
...
Line 9:  QR_BL_10   ← Card 10, Bottom-Left
Line 10: QR_TL_1    ← Card 1, Top-Left
Line 11: QR_TL_2    ← Card 2, Top-Left
Line 12: QR_TL_3    ← Card 3, Top-Left
...
Line 19: QR_TL_10   ← Card 10, Top-Left
Line 20: QR_TR_1    ← Card 1, Top-Right
Line 21: QR_TR_2    ← Card 2, Top-Right
Line 22: QR_TR_3    ← Card 3, Top-Right
...
Line 29: QR_TR_10   ← Card 10, Top-Right
Line 30: QR_BR_1    ← Card 1, Bottom-Right
Line 31: QR_BR_2    ← Card 2, Bottom-Right
Line 32: QR_BR_3    ← Card 3, Bottom-Right
...
Line 39: QR_BR_10   ← Card 10, Bottom-Right
```

### Resulting Card Data
```python
[
    ("Card_1", "QR_BL_1", "QR_TL_1", "QR_TR_1", "QR_BR_1"),
    ("Card_2", "QR_BL_2", "QR_TL_2", "QR_TR_2", "QR_BR_2"),
    ("Card_3", "QR_BL_3", "QR_TL_3", "QR_TR_3", "QR_BR_3"),
    ...
    ("Card_10", "QR_BL_10", "QR_TL_10", "QR_TR_10", "QR_BR_10")
]
```

### Data Structure
Each card tuple contains:
```
Position 0: Card Number (e.g., "Card_1")
Position 1: Bottom-Left QR code
Position 2: Top-Left QR code
Position 3: Top-Right QR code
Position 4: Bottom-Right QR code
```

## Position Mapping in Code

When the program needs to access a specific side:

```python
# In app_state.py - CORRECTED
if self.card_type == CardType.QUARTER:
    position_map = {
        "bottom_left": 1,   # Index 1 in tuple → BL
        "top_left": 2,      # Index 2 in tuple → TL
        "top_right": 3,     # Index 3 in tuple → TR
        "bottom_right": 4   # Index 4 in tuple → BR
    }
    qr_position = position_map.get(self.scan_side, 1)
    expected_qr = self.expected_cards[actual_card_index][qr_position]
```

This correctly maps the scan side to the tuple position:
- `bottom_left` → Index 1 → Bottom-Left QR ✓
- `top_left` → Index 2 → Top-Left QR ✓
- `top_right` → Index 3 → Top-Right QR ✓
- `bottom_right` → Index 4 → Bottom-Right QR ✓

## Summary

### File Format
```
Quarter 1 (Lines 0-9):    Bottom-Left QR codes
Quarter 2 (Lines 10-19):  Top-Left QR codes
Quarter 3 (Lines 20-29):  Top-Right QR codes
Quarter 4 (Lines 30-39):  Bottom-Right QR codes
```

### Tuple Structure
```python
(Card_Number, BL_QR, TL_QR, TR_QR, BR_QR)
```

### Index Mapping
```
Index 0: Card Number
Index 1: Bottom-Left (BL)
Index 2: Top-Left (TL)
Index 3: Top-Right (TR)
Index 4: Bottom-Right (BR)
```

### Position Map (Corrected)
```python
{
    "bottom_left": 1,   # Maps to BL (index 1)
    "top_left": 2,      # Maps to TL (index 2)
    "top_right": 3,     # Maps to TR (index 3)
    "bottom_right": 4   # Maps to BR (index 4)
}
```

### Key Points
1. **Quarter-based**: File divided into 4 equal parts
2. **Position assignment**: 1st→BL, 2nd→TL, 3rd→TR, 4th→BR
3. **Card grouping**: Same position in each quarter = same card
4. **Tuple order**: (numcard, BL, TL, TR, BR)
5. **Position mapping**: Correctly maps scan_side to tuple index
