# Multi-Instance Feature Documentation

## Overview

The Card Sequence Validator now supports running two independent instances simultaneously with completely separate configurations, logs, and cache. This allows you to run Instance 1 and Instance 2 with different network settings, and all data is preserved independently.

## Features

### 1. Instance Selection Toggle
- Located in the home page header next to the theme toggle
- Two buttons: "Instance 1" and "Instance 2"
- Only one instance can be active at a time
- Visual indicator shows which instance is currently selected

### 2. Separate Data Storage
Each instance maintains its own:
- **Logs**: Separate log files for each instance
- **Cache**: Instance-specific configuration cache
- **Settings**: Network settings, COM ports, output formats, etc.
- **Theme**: Each instance can have its own theme preference
- **Card Type**: Each instance remembers its own card type selection
- **Scan Direction**: Each instance maintains its own scan direction

### 3. Power Loss Protection
- All settings and logs are automatically saved to instance-specific cache files
- Auto-save occurs every 5 minutes or after 1000 scans
- On application restart, the last selected instance is automatically loaded
- All data is restored exactly as it was before the power failure

## How It Works

### File Structure

Instance-specific cache files are stored in the user data directory:
```
Windows: C:\Users\[Username]\AppData\Local\CardSequenceValidator\CardSequenceValidator\
├── app_cache_instance_1.json    # Instance 1 cache
├── app_cache_instance_2.json    # Instance 2 cache
└── instance_config.json         # Global instance selection
```

### Instance Switching Process

1. **Click Instance Button**: Click "Instance 1" or "Instance 2" in the header
2. **Save Current Data**: Current instance data is automatically saved
3. **Switch Instance**: The global instance selector switches to the new instance
4. **Load New Data**: All settings, logs, and configurations for the new instance are loaded
5. **Update UI**: The interface updates to reflect the new instance's data
6. **Confirmation**: A message confirms the instance switch

### Data Persistence

**On Application Start:**
- The app reads `instance_config.json` to determine the last selected instance
- That instance's cache file (`app_cache_instance_1.json` or `app_cache_instance_2.json`) is loaded
- All settings, logs, and configurations are restored

**During Operation:**
- Every 5 minutes, the current instance's data is automatically saved
- After every 1000 scans, data is saved
- When switching instances, the current instance is saved before switching
- When closing the application, the current instance is saved

**On Power Failure:**
- The last saved state of each instance is preserved
- When the app restarts, it loads the last selected instance
- All data is restored to the last saved state

## Usage Examples

### Example 1: Running Two Different Network Configurations

**Instance 1:**
- Network: 192.168.1.100:5000
- Card Type: Half
- Scan Direction: Top to Bottom

**Instance 2:**
- Network: 192.168.2.100:5001
- Card Type: Quarter
- Scan Direction: Bottom to Top

You can switch between these instances at any time, and each will maintain its own configuration.

### Example 2: Power Failure Recovery

1. You're running Instance 1 with 500 scans logged
2. Power fails unexpectedly
3. Application restarts
4. Instance 1 is automatically selected (last selected instance)
5. All 500 scans are restored from the cache
6. You can continue scanning from where you left off

### Example 3: Switching Instances During Operation

1. You're scanning with Instance 1
2. You click "Instance 2" button
3. Instance 1 data is saved
4. Instance 2 loads with its own configuration
5. You can now scan with different network settings
6. Click "Instance 1" to switch back anytime

## Technical Details

### Cache File Format

Each instance cache file (`app_cache_instance_1.json` or `app_cache_instance_2.json`) contains:

```json
{
  "card_type": "half",
  "main_scanner_config": {
    "local_ip": "192.168.1.100",
    "local_port": 5000,
    "remote_ip": "192.168.1.50",
    "remote_port": 5001
  },
  "ondemand_scanner_config": {...},
  "output_config": {...},
  "selected_output_format": "format_name",
  "selected_file_path": "/path/to/file.cpd",
  "start_card_code": "ABC123",
  "scan_direction": "top_to_bottom",
  "log_data": [...],
  "current_theme": "dark",
  "baud_rate": 115200,
  "data_bits": 8,
  "parity": "N",
  "stop_bits": 1,
  "timeout": 1
}
```

### Instance Config File

The global instance selection is stored in `instance_config.json`:

```json
{
  "current_instance": 1
}
```

This file is updated whenever you switch instances or close the application.

### Atomic Write Protection

Cache files are written atomically using a temp file + rename pattern:
1. Data is written to a temporary file
2. The temporary file is flushed to disk
3. The temporary file is atomically renamed to the final name
4. This ensures that either the old or new data exists, never partial/corrupted data

## Implementation Details

### Key Functions

**In `src/app_state.py`:**
- `set_current_instance(instance_num)`: Sets the global instance number
- `get_current_instance()`: Gets the current instance number
- `get_cache_file_path()`: Returns the instance-specific cache file path
- `save_instance_selection()`: Saves the current instance to global config
- `load_instance_selection()`: Loads the last selected instance from global config

**In `src/ui/main_application.py`:**
- `switch_instance(instance_num)`: Handles instance switching in the UI
- Instance toggle buttons in the header

### Signal Flow

1. User clicks instance button
2. `switch_instance()` is called
3. Current instance data is saved via `save_cache()`
4. Global instance is switched via `set_current_instance()`
5. New instance data is loaded via `load_cache()`
6. UI is updated via `state_changed` signal
7. Confirmation message is shown

## Troubleshooting

### Instance Data Not Persisting

**Problem:** After switching instances, data is lost.

**Solution:** 
- Check that the cache directory exists: `C:\Users\[Username]\AppData\Local\CardSequenceValidator\CardSequenceValidator\`
- Ensure the application has write permissions to this directory
- Check the console for any error messages about cache saving

### Wrong Instance Loads on Startup

**Problem:** The wrong instance loads when the app starts.

**Solution:**
- Check `instance_config.json` to see which instance is marked as current
- Manually edit the file if needed (change `"current_instance": 1` or `2`)
- Restart the application

### Logs Not Showing After Switch

**Problem:** Logs disappear after switching instances.

**Solution:**
- This is expected behavior - each instance has its own logs
- Switch back to the previous instance to see its logs
- Logs are stored separately in each instance's cache file

## Best Practices

1. **Always switch instances properly**: Use the toggle buttons in the header, don't just close and restart
2. **Monitor auto-save**: The app auto-saves every 5 minutes, so your data is protected
3. **Backup important data**: Periodically backup the cache directory if you have critical data
4. **Check instance before scanning**: Always verify which instance is selected before starting a scan
5. **Use consistent naming**: Keep track of which instance uses which network configuration

## Future Enhancements

Potential improvements for the multi-instance feature:
- Instance naming (e.g., "Production", "Testing")
- Instance profiles with preset configurations
- Instance synchronization options
- Instance-specific logging levels
- Instance performance metrics
