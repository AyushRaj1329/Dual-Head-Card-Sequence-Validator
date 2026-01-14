# System Flow Diagram

## Complete Scanning Flow with Side Validation

```
┌─────────────────────────────────────────────────────────────────┐
│                    START SCANNING SESSION                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FIRST SCAN RECEIVED                           │
│  • Detect card type (Single/Half/Quarter)                       │
│  • Detect scan side (Left/Right/TL/TR/BL/BR)                    │
│  • Lock in the scan side for entire session                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   SUBSEQUENT SCANS                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────┴─────────┐
                    │  Scan QR Code     │
                    └─────────┬─────────┘
                              ↓
              ┌───────────────┴───────────────┐
              │   Is QR from correct side?    │
              └───────────────┬───────────────┘
                              ↓
                    ┌─────────┴─────────┐
                    │                   │
                   NO                  YES
                    │                   │
                    ↓                   ↓
        ┌───────────────────┐  ┌──────────────────┐
        │  Status: NOT OK   │  │  Check Position  │
        │  (Wrong Side)     │  └────────┬─────────┘
        └───────────────────┘           │
                                        ↓
                        ┌───────────────┴───────────────┐
                        │  Is it the expected card?     │
                        └───────────────┬───────────────┘
                                        ↓
                            ┌───────────┴───────────┐
                            │                       │
                           YES                     NO
                            │                       │
                            ↓                       ↓
                ┌───────────────────┐   ┌──────────────────────┐
                │  Status: OK       │   │  Is card in sequence?│
                │  Move to next     │   └──────────┬───────────┘
                └───────────────────┘              │
                                                   ↓
                                    ┌──────────────┴──────────────┐
                                    │                             │
                                   YES                           NO
                                    │                             │
                                    ↓                             ↓
                        ┌───────────────────────┐   ┌────────────────────┐
                        │  Is card ahead?       │   │  Status: NOT OK    │
                        └───────────┬───────────┘   │  (Not in sequence) │
                                    │               └────────────────────┘
                                    ↓
                        ┌───────────┴───────────┐
                        │                       │
                       YES                     NO
                        │                       │
                        ↓                       ↓
            ┌───────────────────────┐  ┌──────────────────┐
            │  PAUSE SCANNING       │  │  Status: NOT OK  │
            │  Show Skip Dialog     │  │  (Card behind)   │
            └───────────┬───────────┘  └──────────────────┘
                        │
                        ↓
            ┌───────────────────────┐
            │  User Decision        │
            └───────────┬───────────┘
                        │
            ┌───────────┴───────────┐
            │                       │
        APPROVE                  REJECT
            │                       │
            ↓                       ↓
┌───────────────────────┐  ┌──────────────────┐
│  SKIP RESOLUTION      │  │  Status: NOT OK  │
│  • Mark intermediate  │  │  Resume scanning │
│    cards as SKIPPED   │  └──────────────────┘
│    (correct side QR)  │
│  • Mark target as     │
│    OK (JUMPED)        │
│  • Move to next card  │
└───────────────────────┘
```

## Side Validation Logic

### Half Card Example
```
┌─────────────────────────────────────────────────────────────┐
│  HALF CARD - Each card has 2 QR codes                       │
│  ┌──────────────┐                                           │
│  │  Card #1     │                                           │
│  │  ┌────┬────┐ │                                           │
│  │  │ L  │ R  │ │  L = Left QR,  R = Right QR              │
│  │  └────┴────┘ │                                           │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘

First Scan: QR_1_LEFT
  ↓
Scan Side Locked: LEFT
  ↓
All subsequent scans MUST be LEFT QR codes

Scan QR_2_LEFT  → ✓ OK (correct side)
Scan QR_3_RIGHT → ✗ NOT OK (wrong side)
Scan QR_3_LEFT  → ✓ OK (correct side)
```

### Quarter Card Example
```
┌─────────────────────────────────────────────────────────────┐
│  QUARTER CARD - Each card has 4 QR codes                    │
│  ┌──────────────┐                                           │
│  │  Card #1     │                                           │
│  │  ┌────┬────┐ │                                           │
│  │  │ TL │ TR │ │  TL = Top-Left,    TR = Top-Right        │
│  │  ├────┼────┤ │  BL = Bottom-Left, BR = Bottom-Right     │
│  │  │ BL │ BR │ │                                           │
│  │  └────┴────┘ │                                           │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘

First Scan: QR_1_TL
  ↓
Scan Side Locked: TOP-LEFT
  ↓
All subsequent scans MUST be TOP-LEFT QR codes

Scan QR_2_TL → ✓ OK (correct side)
Scan QR_3_TR → ✗ NOT OK (wrong side)
Scan QR_3_BL → ✗ NOT OK (wrong side)
Scan QR_3_BR → ✗ NOT OK (wrong side)
Scan QR_3_TL → ✓ OK (correct side)
```

## Skip Resolution Flow

### Example: Skipping Cards 3-5 (Half Card, Left Side)
```
Current Position: Card 2
Scanned: QR_6_LEFT (Card 6)

┌─────────────────────────────────────────────────────────────┐
│  SKIP DETECTION                                              │
│  • Current: Card 2                                           │
│  • Scanned: Card 6                                           │
│  • Gap: 3 cards (Cards 3, 4, 5)                             │
│  • Side: LEFT (correct)                                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  SHOW DIALOG                                                 │
│  "Found card 3 positions ahead. Skip?"                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────┴─────────┐
                    │  User Approves    │
                    └─────────┬─────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  SKIP RESOLUTION                                             │
│                                                              │
│  Log Entry 1: MISSING → QR_3_LEFT (SKIPPED)                 │
│  Log Entry 2: MISSING → QR_4_LEFT (SKIPPED)                 │
│  Log Entry 3: MISSING → QR_5_LEFT (SKIPPED)                 │
│  Log Entry 4: QR_6_LEFT → QR_6_LEFT (OK JUMPED)             │
│                                                              │
│  ✓ All skipped cards show LEFT QR codes                     │
│  ✓ Target card marked as OK (JUMPED)                        │
│  ✓ Next expected: Card 7                                    │
└─────────────────────────────────────────────────────────────┘
```

## Direction Independence

### Top-to-Bottom
```
Scan Order: Card 1 → Card 2 → Card 3 → ... → Card N
Array Index: 0 → 1 → 2 → ... → N-1
current_card_index = array_index
```

### Bottom-to-Top
```
Scan Order: Card N → Card N-1 → ... → Card 2 → Card 1
Array Index: N-1 → N-2 → ... → 1 → 0
current_card_index = scan_position
array_index = (N - 1) - current_card_index
```

**Key Point:** Side validation works the SAME in both directions!

## Status Messages Reference

| Status | Meaning | When It Appears |
|--------|---------|-----------------|
| `OK` | Correct card, correct side | Normal sequential scan |
| `NOT OK` | Any mismatch | Wrong card, wrong side, card behind, etc. |
| `OK (JUMPED)` | Skip approved | After user approves skip |
| `SKIPPED` | Card was skipped | Intermediate cards in skip range |
| `EXTRA SCAN` | Scan after completion | Scanning after all cards done |
| `NOT IN SEQUENCE` | Card not in file | QR code not found in loaded file |
| `NO FILE` | No file loaded | Scanning without loading a file |

## Complete Feature Set

✓ **Matching**: Detects correct/incorrect cards
✓ **Skipping**: Allows jumping ahead with approval
✓ **Side Validation**: Enforces consistent side scanning
✓ **Direction Support**: Works top-to-bottom and bottom-to-top
✓ **All Card Types**: Single, Half, and Quarter cards
✓ **Clean Status**: Simple, clear status messages
✓ **Correct Side in Logs**: Skipped cards show correct side QR
