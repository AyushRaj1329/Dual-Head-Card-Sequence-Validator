# UI Layout Changes - File Management Window

## Before (Old Layout)

```
┌─────────────────────────────────────────────────────────┐
│ Sequence Control Tools                                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [Scan Start Card]  [Cancel Scan]                       │
│                                                          │
│  Current Start Card:  [None________________]            │
│                                                          │
├─────────────────────────────────────────────────────────┤
│  Count Card Range Section...                            │
└─────────────────────────────────────────────────────────┘
```

## After (New Layout)

```
┌─────────────────────────────────────────────────────────┐
│ Sequence Control Tools                                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Card Details Panel (Accent Background)              │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │                                                      │ │
│ │  [Scan Card Details]  [Cancel Scan]                 │ │
│ │                                                      │ │
│ │  Click 'Scan Card Details' to view card info...     │ │
│ │                                                      │ │
│ │  Card Number:      [________________]               │ │
│ │  Left QR (ICCID):  [________________]               │ │
│ │  Right QR (IMSI):  [________________]               │ │
│ │  Position:         [________________]               │ │
│ │                                                      │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Count Card Range Panel (Accent Background)          │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │                                                      │ │
│ │  [Count Card Range]  [Cancel Scan]                  │ │
│ │                                                      │ │
│ │  Click 'Count Card Range' to begin...               │ │
│ │                                                      │ │
│ │  First Card:  [________________]                    │ │
│ │  Last Card:   [________________]                    │ │
│ │  Total:       [________________]                    │ │
│ │                                                      │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Key Improvements

1. **Dedicated Card Details Panel**: 
   - Replaces the single "Start Card" display field
   - Shows comprehensive card information
   - Visually distinct with accent panel styling

2. **Consistent Layout**:
   - Both "Card Details" and "Count Card Range" now have similar panel designs
   - Both have action buttons, status labels, and data fields
   - Easier to understand and use

3. **Better Information Display**:
   - All card information visible at once
   - No need for popup message boxes
   - Information persists until next scan

4. **Improved User Flow**:
   - Start card is now set automatically on first scan
   - Card details feature is separate and non-intrusive
   - Clear visual separation between different tools
