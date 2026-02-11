# Card-Type Specific Output Formats

## Overview
Your application now supports **card-type-specific output signals**. Instead of sending the same "OK" or "NOT OK" signal regardless of card type, you can now configure different outputs for Single, Half, and Quarter cards.

## How It Works

### Output Format Structure
Each output format now has three card-type sections:

```json
{
  "Format Name": {
    "single": {
      "OK": "signal_for_single_ok",
      "NOT OK": "signal_for_single_not_ok",
      "SKIPPED": "signal_for_single_skipped",
      "OK (JUMPED)": "signal_for_single_jumped"
    },
    "half": {
      "OK": "signal_for_half_ok",
      "NOT OK": "signal_for_half_not_ok",
      "SKIPPED": "signal_for_half_skipped",
      "OK (JUMPED)": "signal_for_half_jumped"
    },
    "quarter": {
      "OK": "signal_for_quarter_ok",
      "NOT OK": "signal_for_quarter_not_ok",
      "SKIPPED": "signal_for_quarter_skipped",
      "OK (JUMPED)": "signal_for_quarter_jumped"
    }
  }
}
```

### Available Formats

#### 1. Standard (OK/NOT OK)
Same output for all card types:
- Single: `OK` / `NOT OK`
- Half: `OK` / `NOT OK`
- Quarter: `OK` / `NOT OK`

#### 2. Numeric (1/0)
Numeric signals for all card types:
- Single: `1` (OK) / `0` (NOT OK)
- Half: `1` (OK) / `0` (NOT OK)
- Quarter: `1` (OK) / `0` (NOT OK)

#### 3. PLC Signals
Different PLC signals per card type:
- Single: `SIG_A_HIGH` (OK) / `SIG_B_HIGH` (NOT OK)
- Half: `SIG_D_HIGH` (OK) / `SIG_E_HIGH` (NOT OK)
- Quarter: `SIG_G_HIGH` (OK) / `SIG_H_HIGH` (NOT OK)

#### 4. Card-Type Specific
Explicit card-type labels:
- Single: `SINGLE_OK` / `SINGLE_FAIL`
- Half: `HALF_OK` / `HALF_FAIL`
- Quarter: `QUARTER_OK` / `QUARTER_FAIL`

## How to Use

### 1. Select Output Format
In the **Network Setup** or **COM Port Setup** window:
- Choose your desired format from the "Format:" dropdown
- The format applies to all card types

### 2. Automatic Card-Type Detection
When you scan:
1. The app detects your current card type (Single/Half/Quarter)
2. Automatically sends the appropriate signal for that card type
3. No manual configuration needed per card type

### 3. Example Workflow
```
Scenario: Using "Card-Type Specific" format

Step 1: Load a Half Card file
Step 2: Start scanning
Step 3: Scan a card → App sends "HALF_OK" or "HALF_FAIL"

Step 4: Load a Quarter Card file
Step 5: Start scanning
Step 6: Scan a card → App sends "QUARTER_OK" or "QUARTER_FAIL"
```

## Customizing Output Formats

### Edit output_formats.json
To add your own format or modify existing ones:

```json
{
  "My Custom Format": {
    "single": {
      "OK": "SINGLE_PASS\r\n",
      "NOT OK": "SINGLE_FAIL\r\n",
      "SKIPPED": "SINGLE_SKIP\r\n",
      "OK (JUMPED)": "SINGLE_PASS\r\n"
    },
    "half": {
      "OK": "HALF_PASS\r\n",
      "NOT OK": "HALF_FAIL\r\n",
      "SKIPPED": "HALF_SKIP\r\n",
      "OK (JUMPED)": "HALF_PASS\r\n"
    },
    "quarter": {
      "OK": "QUARTER_PASS\r\n",
      "NOT OK": "QUARTER_FAIL\r\n",
      "SKIPPED": "QUARTER_SKIP\r\n",
      "OK (JUMPED)": "QUARTER_PASS\r\n"
    }
  }
}
```

### Steps to Add Custom Format
1. Open `output_formats.json`
2. Add a new format object with all three card types
3. Save the file
4. Restart the application
5. Your new format appears in the dropdown

## Signal Types

### OK
Sent when a scanned QR code matches the expected code for the current position.

### NOT OK
Sent when a scanned QR code doesn't match the expected code.

### SKIPPED
Sent for each card that was skipped when a mismatch is resolved.

### OK (JUMPED)
Sent when a mismatch is approved and the scanner jumps to the correct card.

## Technical Implementation

### Code Changes
The `send_output_signal()` method now:
1. Gets the current card type (single/half/quarter)
2. Looks up the format for that card type
3. Sends the appropriate signal

```python
def send_output_signal(self, status):
    card_type_key = self.card_type.value  # "single", "half", or "quarter"
    format_config = self.output_formats.get(self.selected_output_format, {})
    card_type_config = format_config.get(card_type_key, {})
    output_signal = card_type_config.get(status)
    if output_signal:
        self.output_udp_writer.send(output_signal)
```

## Benefits

✅ **Flexibility**: Different signals for different card types
✅ **Automation**: No manual switching between formats
✅ **Clarity**: Explicit card-type labels in signals
✅ **Integration**: Easy to integrate with PLC/external systems
✅ **Backward Compatible**: Existing formats still work

## File Location
- **Configuration**: `output_formats.json` (in project root)
- **Code**: `src/app_state.py` - `send_output_signal()` method

## Troubleshooting

### Format not appearing in dropdown
- Restart the application
- Check `output_formats.json` for syntax errors
- Ensure all three card types (single, half, quarter) are defined

### Wrong signal being sent
- Verify the correct format is selected
- Check that the card type is correct (shown in UI)
- Confirm the output UDP connection is active

### Custom format not working
- Ensure JSON syntax is valid
- Include all four status types: OK, NOT OK, SKIPPED, OK (JUMPED)
- Include all three card types: single, half, quarter
