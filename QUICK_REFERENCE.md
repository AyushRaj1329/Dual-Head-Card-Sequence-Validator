# Quick Reference Guide

## What Changed?

### 1. Side Validation (NEW)
- **What**: System locks to one side after first scan
- **Why**: Prevents operator confusion and errors
- **How**: First scan determines side (Left/Right/TL/TR/BL/BR)

### 2. Fixed Skipping Logic
- **What**: Skip feature now jumps to correct card
- **Why**: Was jumping to random positions before
- **How**: Fixed index calculations for both scan directions

### 3. Simplified Status Messages
- **What**: All mismatches show "NOT OK"
- **Why**: Cleaner, simpler logs
- **How**: Removed complex messages like "NOT OK (Wrong Side: X)"

### 4. Correct Side in Skipped Cards
- **What**: Skipped cards show QR from scanned side
- **Why**: Consistency and clarity in logs
- **How**: Uses same `qr_position` for all log entries

## How to Use

### Starting a Scan Session

1. **Load File**: Select your card file (CPD, CSV, or TXT)
2. **Choose Card Type**: Single, Half, or Quarter
3. **Start Scanning**: Scan the first card
4. **Side Locked**: System detects and locks the side

### During Scanning

**Normal Scan:**
```
Scan correct card → Status: OK
```

**Wrong Card:**
```
Scan wrong card → Status: NOT OK
```

**Wrong Side:**
```
Scan different side → Status: NOT OK
```

**Skip Ahead:**
```
Scan card ahead → Dialog appears
  → Approve: Cards marked SKIPPED, continue from new position
  → Reject: Status NOT OK, stay at current position
```

## Card Type Behaviors

### Single Card
- **QR Codes per Card**: 1
- **Side Validation**: None (not needed)
- **Example**: `QR_1`, `QR_2`, `QR_3`

### Half Card
- **QR Codes per Card**: 2 (Left, Right)
- **Side Validation**: Yes (Left OR Right)
- **Example**: 
  - Left: `QR_1_LEFT`, `QR_2_LEFT`, `QR_3_LEFT`
  - Right: `QR_1_RIGHT`, `QR_2_RIGHT`, `QR_3_RIGHT`

### Quarter Card
- **QR Codes per Card**: 4 (TL, TR, BL, BR)
- **Side Validation**: Yes (one of four sides)
- **Example**:
  - Top-Left: `QR_1_TL`, `QR_2_TL`, `QR_3_TL`
  - Top-Right: `QR_1_TR`, `QR_2_TR`, `QR_3_TR`
  - Bottom-Left: `QR_1_BL`, `QR_2_BL`, `QR_3_BL`
  - Bottom-Right: `QR_1_BR`, `QR_2_BR`, `QR_3_BR`

## Status Messages

| Status | What It Means |
|--------|---------------|
| `OK` | ✓ Correct card scanned |
| `NOT OK` | ✗ Wrong card, wrong side, or card behind |
| `OK (JUMPED)` | ⚠ Skip approved, jumped to this card |
| `SKIPPED` | ⊘ Card was skipped (missing) |
| `EXTRA SCAN` | ⚠ Scanned after sequence complete |
| `NOT IN SEQUENCE` | ✗ Card not found in file |
| `NO FILE` | ✗ No file loaded |

## Common Scenarios

### Scenario 1: Operator Flips Card
```
Problem: Accidentally scanned wrong side
Solution: System shows "NOT OK", operator flips card back
Result: Next scan with correct side shows "OK"
```

### Scenario 2: Missing Cards
```
Problem: Cards 5-7 are missing from stack
Solution: Scan card 8, system detects gap, shows skip dialog
Result: Approve skip, cards 5-7 marked as SKIPPED
```

### Scenario 3: Scanning Same Card Twice
```
Problem: Accidentally scanned same card again
Solution: System shows "NOT OK" (card is behind)
Result: Continue with next card
```

### Scenario 4: Wrong Side During Skip
```
Problem: Try to skip with wrong side QR
Solution: System shows "NOT OK" (no skip dialog)
Result: Must scan correct side to trigger skip
```

## Troubleshooting

### "NOT OK" appears but card looks correct
- **Check**: Are you scanning the correct side?
- **Fix**: Flip card to match the side you started with

### Skip dialog doesn't appear
- **Check**: Are you scanning the correct side?
- **Fix**: Scan the same side QR code to trigger skip

### Skipped cards show wrong QR codes
- **This is fixed**: Skipped cards now always show correct side
- **Verify**: Check that logs show QR codes matching your scan side

## Testing

Run these test files to verify everything works:

```bash
python test_final_validation.py        # Complete test suite
python test_side_validation.py         # Side validation tests
python test_complete_matching_logic.py # Matching and skipping tests
```

All tests should pass with green checkmarks ✓

## Key Benefits

1. ✓ **No More Random Jumps**: Skip feature works correctly
2. ✓ **Consistent Scanning**: Can't accidentally mix sides
3. ✓ **Clear Feedback**: Simple "NOT OK" for any error
4. ✓ **Accurate Logs**: Skipped cards show correct side
5. ✓ **Works Everywhere**: All card types, both directions

## Need Help?

- **Documentation**: See `FINAL_IMPLEMENTATION_SUMMARY.md`
- **Flow Diagram**: See `SYSTEM_FLOW_DIAGRAM.md`
- **Side Validation**: See `SIDE_VALIDATION_IMPLEMENTATION.md`
