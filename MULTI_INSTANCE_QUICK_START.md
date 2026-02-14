# Multi-Instance Quick Start Guide

## What's New?

Your application now supports running two independent instances with separate logs, cache, and settings. Perfect for running different network configurations simultaneously.

## Getting Started

### 1. Start the Application
```bash
python main.py
```

### 2. Look for Instance Selector
In the home page header, you'll see two buttons:
- **Instance 1** (default, selected on first run)
- **Instance 2**

### 3. Configure Instance 1
1. Click "Instance 1" (it's already selected)
2. Go to "Network & COM Setup"
3. Configure your network settings for Instance 1
4. Go to "File Management" and load your sequence file
5. Start scanning

### 4. Switch to Instance 2
1. Click the "Instance 2" button in the header
2. A confirmation message appears
3. Instance 1 data is automatically saved
4. Instance 2 loads (it will be empty on first use)

### 5. Configure Instance 2
1. Go to "Network & COM Setup"
2. Configure different network settings for Instance 2
3. Go to "File Management" and load a sequence file
4. Start scanning

### 6. Switch Back to Instance 1
1. Click "Instance 1" button
2. All your Instance 1 settings and logs are restored
3. Continue scanning where you left off

## Key Points

✅ **Each instance has its own:**
- Network configuration
- Logs and scan history
- Card type selection
- Theme preference
- All settings

✅ **Data is automatically saved:**
- Every 5 minutes
- After every 1000 scans
- When switching instances
- When closing the app

✅ **Power failure protection:**
- All data is saved atomically
- On restart, the last selected instance loads automatically
- All logs and settings are restored

## Common Tasks

### Run Two Instances Simultaneously

You can run the application twice with different instances:
1. Start the app normally (Instance 1)
2. Open another terminal and start the app again
3. Each instance will load its own configuration
4. You can now run both instances side-by-side

### Check Which Instance is Active

Look at the header - the selected button shows the active instance.

### Reset an Instance

To reset an instance to default:
1. Switch to that instance
2. Go to "File Management" → "Clear Sequence"
3. Go to "Network & COM Setup" and reconfigure
4. The instance will be reset on next restart

### Backup Instance Data

Your instance data is stored in:
```
Windows: C:\Users\[Username]\AppData\Local\CardSequenceValidator\CardSequenceValidator\
```

Files to backup:
- `app_cache_instance_1.json`
- `app_cache_instance_2.json`
- `instance_config.json`

## Troubleshooting

### Instance data not saving?
- Check that the app has write permissions to the cache directory
- Ensure you're switching instances properly (use the buttons)

### Wrong instance loads on startup?
- The app loads the last selected instance
- To change, switch to the desired instance before closing

### Logs disappeared after switching?
- This is normal - each instance has separate logs
- Switch back to the previous instance to see its logs

## Need More Details?

See `MULTI_INSTANCE_FEATURE.md` for comprehensive documentation.
