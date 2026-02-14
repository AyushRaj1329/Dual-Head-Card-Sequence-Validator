# Multi-Instance User Guide

## Overview

Your Card Sequence Validator now supports **two independent instances** that can run simultaneously with completely separate configurations, logs, and settings.

## What is an Instance?

An **instance** is a complete, independent copy of your application's settings and data. Think of it as two separate workspaces:

- **Instance 1**: Your primary workspace with its own network settings, logs, and files
- **Instance 2**: Your secondary workspace with different network settings, logs, and files

## Getting Started

### Step 1: Start the Application

```bash
python main.py
```

The application starts with **Instance 1** selected by default.

### Step 2: Locate the Instance Selector

Look at the top of the home page. You'll see:

```
┌─────────────────────────────────────────────────────────────┐
│  Logo  │  Title  │  Clock  │  Instance 1  Instance 2  │ 🌙 │
│        │         │         │  [Selected]  [Inactive]  │    │
└─────────────────────────────────────────────────────────────┘
```

The instance buttons are located in the header, next to the theme toggle.

### Step 3: Configure Instance 1

1. Click "Network & COM Setup"
2. Enter your network configuration:
   - Local IP: `192.168.1.100`
   - Local Port: `5000`
   - Remote IP: `192.168.1.50`
   - Remote Port: `5001`
3. Click "File Management"
4. Load your sequence file
5. Go to "Scanner & Logging" to start scanning

### Step 4: Switch to Instance 2

1. Click the **"Instance 2"** button in the header
2. A confirmation message appears: "Switched to Instance 2"
3. Notice the button is now highlighted

### Step 5: Configure Instance 2

1. Click "Network & COM Setup"
2. Enter different network settings:
   - Local IP: `192.168.2.100`
   - Local Port: `5001`
   - Remote IP: `192.168.2.50`
   - Remote Port: `5002`
3. Click "File Management"
4. Load a different sequence file
5. Go to "Scanner & Logging" to start scanning

### Step 6: Switch Back to Instance 1

1. Click the **"Instance 1"** button
2. All your Instance 1 settings are restored
3. Continue scanning where you left off

## Key Features

### 🔄 Easy Switching
- One-click instance switching
- Automatic data save/load
- Confirmation messages

### 💾 Separate Storage
- Each instance has its own logs
- Each instance has its own settings
- Each instance has its own network configuration

### 🛡️ Power Loss Protection
- All data is saved automatically
- On restart, the last selected instance loads
- No data loss on unexpected shutdown

### 🎨 Per-Instance Themes
- Each instance can have its own theme
- Instance 1 can use dark mode
- Instance 2 can use light mode

### 📊 Separate Logs
- Instance 1 logs are separate from Instance 2
- Each instance maintains its own scan history
- Logs are preserved across sessions

## Common Tasks

### Task 1: Run Two Different Network Configurations

**Scenario**: You need to test with two different network setups simultaneously.

**Solution**:
1. Configure Instance 1 with network setup A
2. Configure Instance 2 with network setup B
3. Switch between them as needed
4. All settings are preserved

### Task 2: Recover from Power Failure

**Scenario**: Power fails while you're scanning.

**Solution**:
1. Restart the application
2. The last selected instance loads automatically
3. All your logs and settings are restored
4. Continue scanning from where you left off

### Task 3: Run Two Instances Simultaneously

**Scenario**: You want to run both instances at the same time.

**Solution**:
1. Open Terminal 1: `python main.py`
2. Configure Instance 1
3. Open Terminal 2: `python main.py`
4. Configure Instance 2
5. Both instances run independently

### Task 4: Switch Instances During Scanning

**Scenario**: You're scanning with Instance 1 and need to switch to Instance 2.

**Solution**:
1. Click "Instance 2" button
2. Instance 1 data is automatically saved
3. Instance 2 loads with its configuration
4. Continue scanning with Instance 2
5. Click "Instance 1" to switch back anytime

### Task 5: Check Which Instance is Active

**Solution**: Look at the header - the highlighted button shows the active instance.

## Understanding the Data

### Where is My Data Stored?

Your instance data is stored in:

**Windows:**
```
C:\Users\[Your Username]\AppData\Local\CardSequenceValidator\CardSequenceValidator\
```

### What Files Are Created?

Three files are created:

1. **instance_config.json** (Global)
   - Stores which instance was last selected
   - Size: ~50 bytes

2. **app_cache_instance_1.json** (Instance 1)
   - Stores all Instance 1 data
   - Includes: settings, logs, network config, theme
   - Size: Varies (typically 10-100 KB)

3. **app_cache_instance_2.json** (Instance 2)
   - Stores all Instance 2 data
   - Includes: settings, logs, network config, theme
   - Size: Varies (typically 10-100 KB)

### How Often is Data Saved?

Data is automatically saved:
- Every 5 minutes
- After every 1000 scans
- When switching instances
- When closing the application

## Troubleshooting

### Problem: I switched instances but my data is gone

**Solution**: 
- Each instance has separate data
- Switch back to the previous instance to see its data
- This is normal behavior

### Problem: The wrong instance loads when I start the app

**Solution**:
- The app loads the last selected instance
- To change which instance loads by default:
  1. Switch to the desired instance
  2. Close the application
  3. Restart - that instance will now load

### Problem: I can't find my cache files

**Solution**:
- Windows: Open File Explorer
- Type in address bar: `%APPDATA%\Local\CardSequenceValidator\CardSequenceValidator\`
- Press Enter
- You should see the cache files

### Problem: My data isn't saving

**Solution**:
- Check that the application has write permissions to the cache directory
- Try running the application as Administrator
- Check that you have enough disk space
- Look for error messages in the console

### Problem: I want to reset an instance

**Solution**:
1. Switch to that instance
2. Go to "File Management" → "Clear Sequence"
3. Go to "Network & COM Setup" and reconfigure
4. The instance will be reset

## Best Practices

### ✅ Do's

- ✅ Use the instance buttons to switch (don't just close and restart)
- ✅ Check which instance is selected before scanning
- ✅ Let the app auto-save (every 5 minutes)
- ✅ Keep track of which instance uses which network config
- ✅ Backup your cache directory periodically

### ❌ Don'ts

- ❌ Don't manually edit cache files
- ❌ Don't delete cache files while the app is running
- ❌ Don't force-close the app without using the close button
- ❌ Don't assume both instances have the same data

## Advanced Usage

### Running Two Instances Simultaneously

You can run the application twice to have both instances active:

**Terminal 1:**
```bash
python main.py
# Instance 1 loads
# Configure and start scanning
```

**Terminal 2:**
```bash
python main.py
# Instance 2 loads
# Configure and start scanning
```

Both instances run independently with separate data.

### Backing Up Your Data

To backup your instance data:

1. Navigate to: `C:\Users\[Your Username]\AppData\Local\CardSequenceValidator\CardSequenceValidator\`
2. Copy these files:
   - `instance_config.json`
   - `app_cache_instance_1.json`
   - `app_cache_instance_2.json`
3. Save them to a backup location

### Restoring from Backup

To restore from backup:

1. Close the application
2. Navigate to: `C:\Users\[Your Username]\AppData\Local\CardSequenceValidator\CardSequenceValidator\`
3. Replace the cache files with your backup copies
4. Restart the application

## FAQ

**Q: Can I run both instances at the same time?**
A: Yes! Open the application twice in different terminals.

**Q: Will my data be lost if the power fails?**
A: No. All data is saved automatically every 5 minutes. On restart, the last selected instance loads with all data restored.

**Q: Can each instance have different themes?**
A: Yes. Each instance remembers its own theme preference.

**Q: How much disk space do I need?**
A: Very little. Each cache file is typically 10-100 KB.

**Q: Can I delete an instance?**
A: You can reset an instance by clearing its data, but you can't delete the instance itself. Both instances are always available.

**Q: What happens if I switch instances while scanning?**
A: The current instance's data is saved, and the new instance loads. You can continue scanning with the new instance.

**Q: Can I rename instances?**
A: Not currently, but you can keep track of which instance uses which configuration.

**Q: How do I know which instance is active?**
A: Look at the header - the highlighted button shows the active instance.

**Q: What if I accidentally close the app?**
A: All data is saved automatically. When you restart, the last selected instance loads with all data restored.

## Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Look at the console output for error messages
3. Verify the cache directory exists and is writable
4. Try restarting the application
5. Check that you have enough disk space

## Summary

The multi-instance feature allows you to:
- Run two independent instances with separate configurations
- Switch between instances with one click
- Maintain separate logs for each instance
- Recover from power failures automatically
- Run both instances simultaneously if needed

All data is automatically saved and protected against corruption.

**Happy scanning!** 🎉
