# Output Format Removal - Change Summary

## Change Description
Removed the output format selection dropdown from the Network Setup window since both Head A and Head B use the same output format.

## Rationale
- Both heads share a single output format configuration
- No need for separate format selection per head
- Simplifies the UI
- Reduces configuration complexity

## Changes Made

### File: `src/ui/network_setup_dual.py`

#### 1. Removed Format Field from Output Section
**Before:**
```python
# Format
form.addWidget(QLabel("Format:"), 4, 0, Qt.AlignmentFlag.AlignRight)
format_combo = QComboBox()
setattr(self, f'output_format_{head_id}', format_combo)
form.addWidget(format_combo, 4, 1)
```

**After:**
```python
# Format field removed - both heads use same format
```

#### 2. Removed Format Dropdown Population
**Before:**
```python
def populate_all_dropdowns(self):
    for head_id in ['A', 'B']:
        self.populate_local_ip_dropdown(head_id)
        self.populate_com_ports(head_id)
        self.populate_format_dropdown(head_id)  # REMOVED
```

**After:**
```python
def populate_all_dropdowns(self):
    for head_id in ['A', 'B']:
        self.populate_local_ip_dropdown(head_id)
        self.populate_com_ports(head_id)
```

#### 3. Removed populate_format_dropdown Method
Entire method removed (no longer needed):
```python
def populate_format_dropdown(self, head_id):
    # Method removed
```

#### 4. Removed Format Update from apply_output
**Before:**
```python
# Update format
format_combo = getattr(self, f'output_format_{head_id}')
head.selected_output_format = format_combo.currentText()
```

**After:**
```python
# Format update removed - uses default format
```

## Updated UI Layout

### Output Configuration Section (Per Head)
```
Output Configuration (UDP)
┌─────────────────────────┐
│ Local IP:    [______]   │
│ Local Port:  [0     ]   │
│ Remote IP:   [______]   │  ← PLC IP address
│ Remote Port: [6000  ]   │  ← PLC port
│ Status: Not Connected   │
│ [Apply Output]          │
└─────────────────────────┘
```

**Removed:** Format dropdown field

## Output Format Configuration

### Where is Output Format Configured?
The output format is configured globally in `output_formats.json` and loaded by AppState. Both heads use the same format configuration.

### How to Change Output Format?
1. Edit `output_formats.json` file
2. Restart application
3. Both heads will use the updated format

### Example output_formats.json:
```json
{
  "default_format": {
    "single": {
      "OK": "1",
      "NOT OK": "0",
      "OK (JUMPED)": "1",
      "SKIPPED": "2"
    },
    "half": {
      "OK": "1",
      "NOT OK": "0",
      "OK (JUMPED)": "1",
      "SKIPPED": "2"
    },
    "quarter": {
      "OK": "1",
      "NOT OK": "0",
      "OK (JUMPED)": "1",
      "SKIPPED": "2"
    }
  }
}
```

## Benefits

1. **Simplified UI**: Less clutter in Network Setup window
2. **Consistency**: Both heads always use the same output format
3. **Easier Configuration**: One less field to configure per head
4. **Reduced Errors**: No risk of mismatched formats between heads
5. **Cleaner Code**: Removed unnecessary format handling logic

## Impact

### No Impact On:
- ✅ Output UDP functionality
- ✅ Validation signal sending
- ✅ PLC communication
- ✅ Head independence
- ✅ Network configuration

### Changed:
- ❌ Cannot select different output formats per head (by design)
- ✅ Both heads use global output format from `output_formats.json`

## Testing

- [x] Network Setup window opens without errors
- [x] Output section displays correctly (no format field)
- [x] Apply Output button works
- [x] Output signals sent correctly
- [x] Both heads use same format
- [x] No compilation errors

## Notes

- If per-head format selection is needed in the future, this change can be easily reverted
- Current design assumes both heads always use the same output format
- Format is still configurable globally via `output_formats.json`
