# Advanced Features Q&A

## Table of Contents
1. [Q1: Checksum Digit Validation](#q1-checksum-digit-validation)
2. [Q2: Multi-Instance Log and Cache Management](#q2-multi-instance-log-and-cache-management)
3. [Q3: Two-Instance Configuration with Dedicated Settings](#q3-two-instance-configuration-with-dedicated-settings)
4. [Q4: MSI Installer with Hardware Locking](#q4-msi-installer-with-hardware-locking)

---

## Q1: Checksum Digit Validation

### Question:
If scanned input has check digits, can I trim my scanned data according to the number of checksum digits and then check it from the loaded file? Can I take input from the user for the number of checksum digits?

### Answer: YES - This is fully implementable

### Implementation Approach:

#### 1. Add Checksum Configuration to Settings
Add a new setting in the application to specify the number of checksum digits:

**Location:** Settings window or Network Setup window

**Fields to Add:**
- Checksum Digits: Number input (0-10)
- Checksum Position: Dropdown (Start/End)
- Validation Mode: Dropdown (Ignore Checksum/Validate Checksum)

#### 2. Data Processing Flow

```
Scanned QR Code: "HESH1355ABC123"
                      ↓
User Setting: Checksum Digits = 6, Position = End
                      ↓
Trim Checksum: "HESH1355ABC123" → "HESH1355"
                      ↓
Compare with File: "HESH1355" == "HESH1355" ✓
                      ↓
Optional: Validate Checksum "ABC123"
```

#### 3. Code Implementation

**Step 1: Add Settings to app_state.py**
```python
# In AppState.__init__()
self.checksum_digits = 0  # Number of checksum digits to trim
self.checksum_position = "end"  # "start" or "end"
self.checksum_validation = "ignore"  # "ignore" or "validate"
```

**Step 2: Modify Scan Processing**
```python
def process_scanned_data(self, scanned_data):
    # Trim checksum digits
    if self.checksum_digits > 0:
        if self.checksum_position == "end":
            # Remove last N digits
            trimmed_data = scanned_data[:-self.checksum_digits]
            checksum = scanned_data[-self.checksum_digits:]
        else:  # start
            # Remove first N digits
            trimmed_data = scanned_data[self.checksum_digits:]
            checksum = scanned_data[:self.checksum_digits]
    else:
        trimmed_data = scanned_data
        checksum = None
    
    # Compare trimmed data with file
    return trimmed_data, checksum
```

**Step 3: Add UI for Checksum Settings**
```python
# In settings window or network setup
checksum_group = QGroupBox("Checksum Configuration")
layout = QFormLayout()

self.checksum_digits = QSpinBox()
self.checksum_digits.setRange(0, 10)
self.checksum_digits.setValue(0)
layout.addRow("Checksum Digits:", self.checksum_digits)

self.checksum_position = QComboBox()
self.checksum_position.addItems(["End", "Start"])
layout.addRow("Checksum Position:", self.checksum_position)

self.checksum_validation = QComboBox()
self.checksum_validation.addItems(["Ignore Checksum", "Validate Checksum"])
layout.addRow("Validation Mode:", self.checksum_validation)

checksum_group.setLayout(layout)
```

#### 4. Checksum Validation Algorithms

If you want to validate checksums, common algorithms include:

**Modulo 10 (Luhn Algorithm):**
```python
def validate_luhn(data, checksum):
    digits = [int(d) for d in data]
    checksum_digit = int(checksum)
    
    # Double every second digit from right
    for i in range(len(digits) - 2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    
    total = sum(digits)
    calculated = (10 - (total % 10)) % 10
    return calculated == checksum_digit
```

**Modulo 11:**
```python
def validate_mod11(data, checksum):
    weights = range(2, len(data) + 2)
    total = sum(int(d) * w for d, w in zip(reversed(data), weights))
    calculated = (11 - (total % 11)) % 11
    return str(calculated) == checksum
```

#### 5. Benefits

✅ Flexible - User can configure checksum length
✅ Compatible - Works with existing file format
✅ Validation - Optional checksum verification
✅ Error Detection - Catches scanning errors

### Recommendation:
Implement this feature in a new "Advanced Settings" section with clear documentation about checksum formats.

---

## Q2: Multi-Instance Log and Cache Management

### Question:
If I am running two instances of the application, how do I differentiate between logs? How does each instance identify its cache data? Is this data saved in ROM or RAM?

### Answer: Current Behavior and Solutions

### Current Behavior (Single Instance Design)

**Cache Storage Location (ROM - Persistent):**
```
C:\Users\<username>\AppData\Local\YourCompany\CardSequenceValidator\app_cache.json
```

**Data Stored:**
- Network configuration (Main Scanner, Output, On-Demand)
- Card type selection
- Theme preference
- Last loaded file path
- Output format selection

**Logs Storage (RAM - Temporary):**
- Logs are stored in memory (Python list)
- NOT saved to disk automatically
- Lost on application close (unless exported)

### Problem with Multiple Instances

**Current Issue:**
- Both instances share the SAME cache file
- Last instance to close overwrites the cache
- No log separation between instances
- Configuration conflicts

**Example Conflict:**
```
Instance 1: Saves config → app_cache.json
Instance 2: Saves config → app_cache.json (overwrites Instance 1)
Instance 1: Closes → Loads Instance 2's config (wrong!)
```

### Solution 1: Instance-Specific Cache Files

**Approach:** Use Process ID (PID) to create unique cache files

**Implementation:**
```python
import os

class AppState:
    def __init__(self):
        # Get unique process ID
        self.instance_id = os.getpid()
        
        # Create instance-specific cache path
        cache_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppLocalDataLocation
        )
        self.cache_file = os.path.join(
            cache_dir, 
            f"app_cache_instance_{self.instance_id}.json"
        )
```

**Result:**
```
Instance 1 (PID 12345): app_cache_instance_12345.json
Instance 2 (PID 67890): app_cache_instance_67890.json
```

**Pros:**
✅ Complete isolation between instances
✅ No configuration conflicts
✅ Each instance maintains its own settings

**Cons:**
❌ Cache files accumulate (need cleanup)
❌ Settings don't persist across restarts
❌ New PID every time application starts

### Solution 2: Named Instances with Profile Selection

**Approach:** Let user choose instance name at startup

**Implementation:**
```python
# At application startup
class InstanceSelector(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Instance")
        
        layout = QVBoxLayout()
        
        self.instance_combo = QComboBox()
        self.instance_combo.addItems(["Instance 1", "Instance 2"])
        layout.addWidget(QLabel("Select Instance:"))
        layout.addWidget(self.instance_combo)
        
        btn = QPushButton("Start")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
        
        self.setLayout(layout)
    
    def get_instance_name(self):
        return self.instance_combo.currentText()

# In main.py
app = QApplication(sys.argv)
selector = InstanceSelector()
if selector.exec() == QDialog.DialogCode.Accepted:
    instance_name = selector.get_instance_name()
    app_state = AppState(instance_name=instance_name)
```

**Cache Files:**
```
app_cache_instance_1.json
app_cache_instance_2.json
```

**Pros:**
✅ Settings persist across restarts
✅ User controls which instance to use
✅ Clean, predictable file structure

**Cons:**
❌ User must select instance each time
❌ Limited to predefined instances

### Solution 3: Log File Separation

**Approach:** Save logs to separate files per instance

**Implementation:**
```python
class AppState:
    def __init__(self, instance_name="default"):
        self.instance_name = instance_name
        
        # Create logs directory
        log_dir = os.path.join(
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppLocalDataLocation
            ),
            "logs"
        )
        os.makedirs(log_dir, exist_ok=True)
        
        # Instance-specific log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(
            log_dir,
            f"{instance_name}_{timestamp}.log"
        )
    
    def add_log(self, entry):
        # Add to memory
        self.logs.append(entry)
        
        # Also write to file (persistent)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"{entry['timestamp']} - {entry['message']}\n")
```

**Log Files:**
```
logs/
  ├── Instance_1_20260213_143022.log
  ├── Instance_1_20260213_150145.log
  ├── Instance_2_20260213_143030.log
  └── Instance_2_20260213_151200.log
```

**Pros:**
✅ Complete log history preserved
✅ Easy to identify which instance generated logs
✅ Logs survive application crashes

**Cons:**
❌ Disk space usage grows over time
❌ Need log rotation/cleanup mechanism

### RAM vs ROM Storage

**RAM (Volatile - Lost on Power Off):**
- Current logs list (`self.logs`)
- Application state variables
- UI state
- Active network connections

**ROM/Disk (Persistent - Survives Power Off):**
- Cache file (`app_cache.json`)
- Exported log files
- Configuration files
- Application executable

### Recommended Solution

**Best Approach:** Combination of Solutions 2 & 3

1. **Instance Selection at Startup** - User chooses Instance 1 or Instance 2
2. **Separate Cache Files** - Each instance has its own configuration
3. **Persistent Logs** - Logs written to disk in real-time
4. **Automatic Cleanup** - Delete old log files after 30 days

**Benefits:**
✅ Clear instance separation
✅ Settings persist across restarts
✅ Complete log history
✅ No configuration conflicts
✅ Easy troubleshooting

---

## Q3: Two-Instance Configuration with Dedicated Settings

### Question:
Can I limit to only two instances with dedicated settings, hardcoded IPs, and separate log locations?

### Answer: YES - Fully Implementable

### Implementation Strategy

#### 1. Instance Locking (Limit to 2 Instances)

**Approach:** Use lock files to track running instances

**Implementation:**
```python
import os
import sys
from pathlib import Path

class InstanceManager:
    def __init__(self):
        self.lock_dir = Path(QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppLocalDataLocation
        )) / "locks"
        self.lock_dir.mkdir(exist_ok=True)
        
        self.instance_id = None
        self.lock_file = None
    
    def acquire_instance(self):
        """Try to acquire an instance slot (1 or 2)"""
        for instance_num in [1, 2]:
            lock_file = self.lock_dir / f"instance_{instance_num}.lock"
            
            # Try to create lock file
            try:
                # Check if lock file exists and process is still running
                if lock_file.exists():
                    with open(lock_file, 'r') as f:
                        pid = int(f.read().strip())
                    
                    # Check if process is still running
                    if self.is_process_running(pid):
                        continue  # Instance occupied
                    else:
                        # Stale lock file, remove it
                        lock_file.unlink()
                
                # Create lock file with current PID
                with open(lock_file, 'w') as f:
                    f.write(str(os.getpid()))
                
                self.instance_id = instance_num
                self.lock_file = lock_file
                return instance_num
                
            except Exception as e:
                continue
        
        # No available instance
        return None
    
    def is_process_running(self, pid):
        """Check if a process is running"""
        try:
            os.kill(pid, 0)  # Signal 0 doesn't kill, just checks
            return True
        except OSError:
            return False
    
    def release_instance(self):
        """Release the instance lock"""
        if self.lock_file and self.lock_file.exists():
            self.lock_file.unlink()
```

**Usage in main.py:**
```python
# In main.py
app = QApplication(sys.argv)

# Try to acquire instance
instance_mgr = InstanceManager()
instance_id = instance_mgr.acquire_instance()

if instance_id is None:
    QMessageBox.critical(
        None, 
        "Instance Limit Reached",
        "Maximum 2 instances are already running.\n"
        "Please close one instance before starting another."
    )
    sys.exit(1)

# Create app state with instance ID
app_state = AppState(instance_id=instance_id)

# Show which instance is running
QMessageBox.information(
    None,
    f"Instance {instance_id} Started",
    f"Running as Instance {instance_id}"
)

# ... rest of application startup ...

# Release lock on exit
app.aboutToQuit.connect(instance_mgr.release_instance)
```

#### 2. Hardcoded IP/Port Configuration per Instance

**Approach:** Define network settings per instance in configuration

**Implementation:**
```python
# constants.py
INSTANCE_CONFIGS = {
    1: {
        'name': 'Production Line 1',
        'main_scanner': {
            'local_ip': '192.168.1.100',
            'local_port': 5000,
            'remote_ip': '192.168.1.50',
            'remote_port': 6000
        },
        'output': {
            'local_ip': '192.168.1.100',
            'local_port': 7000,
            'remote_ip': '192.168.1.200',  # PLC 1
            'remote_port': 8000
        },
        'ondemand': {
            'com_port': 'COM3',
            'baud_rate': 115200
        }
    },
    2: {
        'name': 'Production Line 2',
        'main_scanner': {
            'local_ip': '192.168.1.101',
            'local_port': 5001,
            'remote_ip': '192.168.1.51',
            'remote_port': 6001
        },
        'output': {
            'local_ip': '192.168.1.101',
            'local_port': 7001,
            'remote_ip': '192.168.1.201',  # PLC 2
            'remote_port': 8001
        },
        'ondemand': {
            'com_port': 'COM4',
            'baud_rate': 115200
        }
    }
}
```

**Apply Configuration:**
```python
class AppState:
    def __init__(self, instance_id):
        self.instance_id = instance_id
        self.instance_name = INSTANCE_CONFIGS[instance_id]['name']
        
        # Load hardcoded configuration
        self.load_instance_config()
    
    def load_instance_config(self):
        """Load hardcoded configuration for this instance"""
        config = INSTANCE_CONFIGS[self.instance_id]
        
        # Apply main scanner config
        self.main_scanner_config = config['main_scanner']
        
        # Apply output config
        self.output_config = config['output']
        
        # Apply on-demand config
        self.start_card_scan_port = config['ondemand']['com_port']
        self.baud_rate = config['ondemand']['baud_rate']
```

#### 3. Separate Log Locations per Instance

**Implementation:**
```python
class AppState:
    def __init__(self, instance_id):
        self.instance_id = instance_id
        
        # Create instance-specific directories
        base_dir = Path(QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppLocalDataLocation
        ))
        
        # Instance directory
        self.instance_dir = base_dir / f"instance_{instance_id}"
        self.instance_dir.mkdir(exist_ok=True)
        
        # Logs directory
        self.logs_dir = self.instance_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Cache file
        self.cache_file = self.instance_dir / "app_cache.json"
        
        # Current log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_log_file = self.logs_dir / f"session_{timestamp}.log"
```

**Directory Structure:**
```
C:\Users\<user>\AppData\Local\YourCompany\CardSequenceValidator\
├── instance_1\
│   ├── app_cache.json
│   └── logs\
│       ├── session_20260213_140000.log
│       ├── session_20260213_150000.log
│       └── session_20260213_160000.log
├── instance_2\
│   ├── app_cache.json
│   └── logs\
│       ├── session_20260213_140100.log
│       ├── session_20260213_150100.log
│       └── session_20260213_160100.log
└── locks\
    ├── instance_1.lock
    └── instance_2.lock
```

#### 4. Instance Identification in UI

**Show Instance Info:**
```python
class MainWindow(QMainWindow):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        
        # Update window title with instance info
        instance_name = INSTANCE_CONFIGS[app_state.instance_id]['name']
        self.setWindowTitle(
            f"Card Sequence Validator - {instance_name} (Instance {app_state.instance_id})"
        )
        
        # Add instance indicator to status bar
        self.statusBar().showMessage(
            f"Instance {app_state.instance_id}: {instance_name}"
        )
```

#### 5. Network Setup Window Behavior

**Option A: Read-Only (Hardcoded)**
```python
class NetworkSetupWindow(QMainWindow):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        
        # Disable editing for hardcoded configs
        self.main_local_ip.setEnabled(False)
        self.main_local_port.setEnabled(False)
        self.main_remote_ip.setEnabled(False)
        self.main_remote_port.setEnabled(False)
        
        # Show info message
        info_label = QLabel(
            f"Network settings are hardcoded for Instance {app_state.instance_id}"
        )
        info_label.setStyleSheet("color: orange; font-weight: bold;")
```

**Option B: Editable with Override**
```python
# Allow editing but save to instance-specific cache
# Hardcoded values are defaults, user can override
```

### Summary: Two-Instance System

**Features:**
✅ Maximum 2 instances enforced
✅ Each instance has dedicated network configuration
✅ Separate log directories per instance
✅ Separate cache files per instance
✅ Instance identification in UI
✅ Automatic lock file cleanup
✅ Settings persist across restarts

**File Structure:**
```
instance_1/
  ├── app_cache.json (Instance 1 settings)
  └── logs/ (Instance 1 logs)
instance_2/
  ├── app_cache.json (Instance 2 settings)
  └── logs/ (Instance 2 logs)
locks/
  ├── instance_1.lock (PID tracking)
  └── instance_2.lock (PID tracking)
```

---

## Q4: MSI Installer with Hardware Locking

### Question:
How can I convert this program to an MSI file that installs securely, runs only on the installed system, and is non-shareable?

### Answer: Multi-Step Process

### Step 1: Create Executable with PyInstaller

**Install PyInstaller:**
```bash
pip install pyinstaller
```

**Create Executable:**
```bash
pyinstaller --name="CardSequenceValidator" ^
            --onefile ^
            --windowed ^
            --icon=assets/Icon.png ^
            --add-data="assets;assets" ^
            --add-data="card_example;card_example" ^
            main.py
```

**Options Explained:**
- `--onefile`: Single executable file
- `--windowed`: No console window (GUI only)
- `--icon`: Application icon
- `--add-data`: Include assets and examples

**Output:**
```
dist/
  └── CardSequenceValidator.exe
```

### Step 2: Implement Hardware Locking

**Approach:** Bind application to specific hardware using machine fingerprint

**Implementation:**

**Create hardware_lock.py:**
```python
import hashlib
import platform
import subprocess
import uuid
import os
from pathlib import Path

class HardwareLock:
    def __init__(self):
        self.license_file = Path.home() / ".card_validator_license"
    
    def get_machine_id(self):
        """Generate unique machine fingerprint"""
        # Get CPU ID
        cpu_id = self._get_cpu_id()
        
        # Get motherboard serial
        mb_serial = self._get_motherboard_serial()
        
        # Get MAC address
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) 
                       for i in range(0, 48, 8)])
        
        # Combine and hash
        machine_string = f"{cpu_id}|{mb_serial}|{mac}"
        machine_id = hashlib.sha256(machine_string.encode()).hexdigest()
        
        return machine_id
    
    def _get_cpu_id(self):
        """Get CPU ID (Windows)"""
        try:
            result = subprocess.check_output(
                "wmic cpu get ProcessorId", 
                shell=True
            ).decode()
            return result.split('\n')[1].strip()
        except:
            return "UNKNOWN_CPU"
    
    def _get_motherboard_serial(self):
        """Get motherboard serial (Windows)"""
        try:
            result = subprocess.check_output(
                "wmic baseboard get SerialNumber", 
                shell=True
            ).decode()
            return result.split('\n')[1].strip()
        except:
            return "UNKNOWN_MB"
    
    def is_licensed(self):
        """Check if application is licensed for this machine"""
        if not self.license_file.exists():
            return False
        
        try:
            with open(self.license_file, 'r') as f:
                stored_id = f.read().strip()
            
            current_id = self.get_machine_id()
            return stored_id == current_id
        except:
            return False
    
    def activate_license(self, license_key):
        """Activate license with provided key"""
        # Verify license key format
        expected_key = self._generate_license_key()
        
        if license_key == expected_key:
            # Save machine ID to license file
            machine_id = self.get_machine_id()
            with open(self.license_file, 'w') as f:
                f.write(machine_id)
            return True
        return False
    
    def _generate_license_key(self):
        """Generate license key for this machine"""
        machine_id = self.get_machine_id()
        # Add secret salt
        secret = "YOUR_SECRET_SALT_HERE"
        combined = f"{machine_id}|{secret}"
        license_key = hashlib.sha256(combined.encode()).hexdigest()[:16].upper()
        return license_key
    
    def get_license_key_for_machine(self):
        """Get the license key needed for this machine (for admin use)"""
        return self._generate_license_key()
```

**Integrate into main.py:**
```python
from hardware_lock import HardwareLock

def main():
    app = QApplication(sys.argv)
    
    # Check hardware lock
    hw_lock = HardwareLock()
    
    if not hw_lock.is_licensed():
        # Show activation dialog
        license_key, ok = QInputDialog.getText(
            None,
            "License Activation Required",
            f"This application is not licensed for this machine.\n\n"
            f"Machine ID: {hw_lock.get_machine_id()[:16]}...\n\n"
            f"Please enter your license key:",
            QLineEdit.EchoMode.Normal
        )
        
        if ok and license_key:
            if hw_lock.activate_license(license_key):
                QMessageBox.information(
                    None,
                    "Activation Successful",
                    "Application has been successfully activated!"
                )
            else:
                QMessageBox.critical(
                    None,
                    "Activation Failed",
                    "Invalid license key for this machine."
                )
                sys.exit(1)
        else:
            sys.exit(1)
    
    # Continue with normal startup
    # ... rest of application ...
```

**License Key Generation Tool (for admin):**
```python
# generate_license.py
from hardware_lock import HardwareLock

def main():
    print("=== License Key Generator ===")
    print("\nRun this on the target machine to get its license key.\n")
    
    hw_lock = HardwareLock()
    machine_id = hw_lock.get_machine_id()
    license_key = hw_lock.get_license_key_for_machine()
    
    print(f"Machine ID: {machine_id}")
    print(f"License Key: {license_key}")
    print("\nProvide this license key to activate the application.")

if __name__ == "__main__":
    main()
```

### Step 3: Create MSI Installer

**Option A: Using WiX Toolset (Professional)**

**Install WiX Toolset:**
Download from: https://wixtoolset.org/

**Create Product.wxs:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" 
           Name="Card Sequence Validator" 
           Language="1033" 
           Version="1.0.0.0" 
           Manufacturer="Your Company" 
           UpgradeCode="PUT-GUID-HERE">
    
    <Package InstallerVersion="200" 
             Compressed="yes" 
             InstallScope="perMachine" />
    
    <MajorUpgrade DowngradeErrorMessage="A newer version is already installed." />
    <MediaTemplate EmbedCab="yes" />
    
    <Feature Id="ProductFeature" Title="Card Sequence Validator" Level="1">
      <ComponentGroupRef Id="ProductComponents" />
    </Feature>
    
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFilesFolder">
        <Directory Id="INSTALLFOLDER" Name="CardSequenceValidator" />
      </Directory>
      <Directory Id="ProgramMenuFolder">
        <Directory Id="ApplicationProgramsFolder" Name="Card Sequence Validator"/>
      </Directory>
    </Directory>
    
    <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
      <Component Id="MainExecutable" Guid="PUT-GUID-HERE">
        <File Id="CardSequenceValidatorEXE" 
              Source="dist\CardSequenceValidator.exe" 
              KeyPath="yes" 
              Checksum="yes"/>
      </Component>
    </ComponentGroup>
    
    <!-- Start Menu Shortcut -->
    <DirectoryRef Id="ApplicationProgramsFolder">
      <Component Id="ApplicationShortcut" Guid="PUT-GUID-HERE">
        <Shortcut Id="ApplicationStartMenuShortcut"
                  Name="Card Sequence Validator"
                  Description="Card Sequence Validation Application"
                  Target="[INSTALLFOLDER]CardSequenceValidator.exe"
                  WorkingDirectory="INSTALLFOLDER"/>
        <RemoveFolder Id="ApplicationProgramsFolder" On="uninstall"/>
        <RegistryValue Root="HKCU" 
                       Key="Software\YourCompany\CardSequenceValidator" 
                       Name="installed" 
                       Type="integer" 
                       Value="1" 
                       KeyPath="yes"/>
      </Component>
    </DirectoryRef>
  </Product>
</Wix>
```

**Build MSI:**
```bash
candle Product.wxs
light -ext WixUIExtension Product.wixobj -out CardSequenceValidator.msi
```

**Option B: Using Advanced Installer (GUI-based, Easier)**

1. Download Advanced Installer: https://www.advancedinstaller.com/
2. Create new project → Simple → MSI
3. Add files from `dist/` folder
4. Configure:
   - Product Details (Name, Version, Company)
   - Install Location (Program Files)
   - Shortcuts (Start Menu, Desktop)
   - Prerequisites (.NET, VC++ Redistributables if needed)
5. Build → Generate MSI

**Option C: Using Inno Setup (Free, Simple)**

**Install Inno Setup:**
Download from: https://jrsoftware.org/isinfo.php

**Create installer.iss:**
```ini
[Setup]
AppName=Card Sequence Validator
AppVersion=1.0
DefaultDirName={pf}\CardSequenceValidator
DefaultGroupName=Card Sequence Validator
OutputDir=output
OutputBaseFilename=CardSequenceValidatorSetup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "dist\CardSequenceValidator.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs
Source: "card_example\*"; DestDir: "{app}\card_example"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\Card Sequence Validator"; Filename: "{app}\CardSequenceValidator.exe"
Name: "{commondesktop}\Card Sequence Validator"; Filename: "{app}\CardSequenceValidator.exe"

[Run]
Filename: "{app}\CardSequenceValidator.exe"; Description: "Launch Card Sequence Validator"; Flags: postinstall nowait skipifsilent
```

**Build Installer:**
```bash
iscc installer.iss
```

### Step 4: Additional Security Measures

#### 1. Code Obfuscation
```bash
pip install pyarmor
pyarmor obfuscate main.py
```

#### 2. Digital Signature
```bash
# Sign the executable with a code signing certificate
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com CardSequenceValidator.exe
```

#### 3. Anti-Debugging
```python
import ctypes
import sys

def is_debugger_present():
    """Check if debugger is attached (Windows)"""
    return ctypes.windll.kernel32.IsDebuggerPresent() != 0

def anti_debug_check():
    if is_debugger_present():
        QMessageBox.critical(None, "Error", "Debugging detected!")
        sys.exit(1)

# Call at startup
anti_debug_check()
```

### Step 5: Deployment Workflow

**For Each Customer Machine:**

1. **Generate License Key:**
   ```bash
   # Run on target machine
   python generate_license.py
   # Output: License Key: A1B2C3D4E5F6G7H8
   ```

2. **Install Application:**
   ```bash
   # Run MSI installer
   CardSequenceValidator.msi
   ```

3. **Activate License:**
   - Launch application
   - Enter license key when prompted
   - Application binds to hardware

4. **Verification:**
   - License file created: `C:\Users\<user>\.card_validator_license`
   - Contains encrypted machine ID
   - Application runs normally

### Security Features Summary

✅ **Hardware Binding:** Application tied to specific machine
✅ **License Validation:** Requires valid license key
✅ **Non-Transferable:** Won't run on different hardware
✅ **Encrypted Storage:** License file is hashed
✅ **MSI Installer:** Professional installation experience
✅ **Digital Signature:** (Optional) Verified publisher
✅ **Code Obfuscation:** (Optional) Harder to reverse engineer
✅ **Anti-Debugging:** (Optional) Prevents tampering

### Limitations

⚠️ **Hardware Changes:** Major hardware changes (motherboard, CPU) will require re-activation
⚠️ **Determined Attackers:** No protection is 100% foolproof
⚠️ **Backup Strategy:** Keep license key records for customer support

### Recommended Tools

**Best Combination:**
1. **PyInstaller** - Create executable
2. **Hardware Lock** - Bind to machine
3. **Advanced Installer** - Create MSI (easiest)
4. **Code Signing** - Add trust (optional but recommended)

**Cost:**
- PyInstaller: Free
- Hardware Lock: Free (custom code)
- Advanced Installer: Free (limited) or $500+ (full)
- WiX Toolset: Free
- Inno Setup: Free
- Code Signing Certificate: $100-300/year

---

## Summary

### Q1: Checksum Validation
✅ Fully implementable with user-configurable checksum digits
✅ Supports trimming from start or end
✅ Optional validation with common algorithms

### Q2: Multi-Instance Management
✅ Use instance-specific cache files
✅ Separate log directories per instance
✅ Cache stored in ROM (persistent), logs can be RAM or ROM

### Q3: Two-Instance System
✅ Limit to 2 instances with lock files
✅ Hardcoded IP/port per instance
✅ Separate settings and logs per instance
✅ Automatic instance identification

### Q4: MSI with Hardware Locking
✅ Create executable with PyInstaller
✅ Implement hardware fingerprinting
✅ Generate MSI with WiX/Advanced Installer/Inno Setup
✅ License key system for activation
✅ Non-transferable, machine-specific installation

All features are implementable with the provided code examples and tools!
