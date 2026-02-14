# Multi-Instance Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Application Startup                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  main.py                                                        │
│  ├─ Read instance_config.json                                  │
│  ├─ Call set_current_instance(instance_num)                    │
│  └─ Create AppState(card_type=CardType.HALF)                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  AppState.__init__()                                            │
│  ├─ load_instance_selection()                                  │
│  ├─ load_output_formats()                                      │
│  ├─ load_cache()  ◄─── Loads instance-specific cache           │
│  └─ Restore UDP connections                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  HomePage (UI)                                                  │
│  ├─ Display Instance Selector (Instance 1 / Instance 2)        │
│  ├─ Display current instance data                              │
│  └─ Ready for user interaction                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Instance Switching Flow

```
┌──────────────────────────────────────────────────────────────────┐
│  User clicks Instance Button (1 or 2)                           │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  HomePage.switch_instance(instance_num)                         │
└──────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
        ┌────────────┐ ┌────────────┐ ┌────────────┐
        │   Save     │ │  Switch    │ │   Load     │
        │   Cache    │ │  Instance  │ │   Cache    │
        └────────────┘ └────────────┘ └────────────┘
                │             │             │
                └─────────────┼─────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  Update UI                                                       │
│  ├─ Update status indicators                                    │
│  ├─ Update logs display                                         │
│  └─ Update configuration display                                │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  Show Confirmation Message                                      │
│  "Switched to Instance X"                                       │
└──────────────────────────────────────────────────────────────────┘
```

## Data Storage Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  User Data Directory                                            │
│  C:\Users\[Username]\AppData\Local\CardSequenceValidator\...   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  instance_config.json (Global)                           │  │
│  │  {                                                       │  │
│  │    "current_instance": 1                                 │  │
│  │  }                                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  app_cache_instance_1.json (Instance 1 Data)            │  │
│  │  {                                                       │  │
│  │    "card_type": "half",                                  │  │
│  │    "main_scanner_config": {...},                         │  │
│  │    "log_data": [...],                                    │  │
│  │    "current_theme": "dark",                              │  │
│  │    ...                                                   │  │
│  │  }                                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  app_cache_instance_2.json (Instance 2 Data)            │  │
│  │  {                                                       │  │
│  │    "card_type": "quarter",                               │  │
│  │    "main_scanner_config": {...},                         │  │
│  │    "log_data": [...],                                    │  │
│  │    "current_theme": "light",                             │  │
│  │    ...                                                   │  │
│  │  }                                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Global Instance Management

```
┌─────────────────────────────────────────────────────────────────┐
│  src/app_state.py - Global Instance State                      │
│                                                                 │
│  _current_instance = 1  (Global variable)                      │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  set_current_instance(instance_num)                     │   │
│  │  └─ Sets _current_instance to 1 or 2                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  get_current_instance()                                 │   │
│  │  └─ Returns current _current_instance value             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  get_cache_file_path()                                  │   │
│  │  └─ Returns instance-specific cache file path:          │   │
│  │     app_cache_instance_1.json or                        │   │
│  │     app_cache_instance_2.json                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## AppState Instance Methods

```
┌─────────────────────────────────────────────────────────────────┐
│  AppState Class                                                 │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  __init__()                                             │   │
│  │  ├─ self.current_instance = get_current_instance()     │   │
│  │  ├─ load_instance_selection()                          │   │
│  │  └─ load_cache()  (instance-specific)                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  save_cache()                                           │   │
│  │  ├─ Save to instance-specific cache file               │   │
│  │  └─ Call save_instance_selection()                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  load_cache()                                           │   │
│  │  └─ Load from instance-specific cache file             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  save_instance_selection()                              │   │
│  │  └─ Save current instance to instance_config.json      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  load_instance_selection()                              │   │
│  │  └─ Load last selected instance from config            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## HomePage Instance UI

```
┌─────────────────────────────────────────────────────────────────┐
│  HomePage Header                                                │
│                                                                 │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │   Logo       │  │  Title & Subtitle│  │  Clock Widget    │  │
│  └──────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                 │
│                    ┌──────────────────────────────────────┐    │
│                    │  Instance Selector                   │    │
│                    │  ┌──────────────┐ ┌──────────────┐  │    │
│                    │  │ Instance 1   │ │ Instance 2   │  │    │
│                    │  │ [Selected]   │ │              │  │    │
│                    │  └──────────────┘ └──────────────┘  │    │
│                    └──────────────────────────────────────┘    │
│                                                                 │
│                                    ┌──────────────────────┐    │
│                                    │  Theme Toggle        │    │
│                                    │  [Light Mode]        │    │
│                                    └──────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Power Failure Recovery Flow

```
┌──────────────────────────────────────────────────────────────────┐
│  Normal Operation                                               │
│  ├─ Auto-save every 5 minutes                                  │
│  ├─ Auto-save every 1000 scans                                 │
│  └─ Data written atomically (temp file + rename)               │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  Power Failure Occurs                                           │
│  └─ Last saved state is preserved in cache files               │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  Application Restarts                                           │
│  ├─ Read instance_config.json (has last selected instance)     │
│  ├─ Load that instance's cache file                            │
│  └─ All data restored to last saved state                      │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  User Can Continue                                              │
│  └─ All logs, settings, and configurations are restored        │
└──────────────────────────────────────────────────────────────────┘
```

## Atomic Write Protection

```
┌──────────────────────────────────────────────────────────────────┐
│  Normal File Write (Unsafe)                                     │
│                                                                 │
│  app_cache_instance_1.json                                      │
│  ├─ Write data...                                              │
│  ├─ Power fails during write                                   │
│  └─ File is corrupted (partial data)                           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Atomic Write (Safe)                                            │
│                                                                 │
│  Step 1: Write to temp file                                    │
│  └─ app_cache_instance_1.json.tmp                              │
│                                                                 │
│  Step 2: Flush to disk                                         │
│  └─ os.fsync() ensures data is written                         │
│                                                                 │
│  Step 3: Atomic rename                                         │
│  └─ Rename .tmp to final name (atomic operation)               │
│                                                                 │
│  Result: Either old or new file exists, never partial data     │
└──────────────────────────────────────────────────────────────────┘
```

## Concurrent Instance Execution

```
┌──────────────────────────────────────────────────────────────────┐
│  Terminal 1                          │  Terminal 2              │
│  python main.py                      │  python main.py          │
│  ├─ Loads Instance 1                 │  ├─ Loads Instance 2     │
│  ├─ Separate cache file              │  ├─ Separate cache file  │
│  ├─ Separate logs                    │  ├─ Separate logs        │
│  ├─ Separate network config          │  ├─ Separate network cfg │
│  └─ Can run simultaneously           │  └─ Can run simultaneously
│                                      │                          │
│  Instance 1 Data                     │  Instance 2 Data         │
│  ├─ app_cache_instance_1.json        │  ├─ app_cache_instance_2.json
│  ├─ Network: 192.168.1.100:5000      │  ├─ Network: 192.168.2.100:5001
│  ├─ Card Type: Half                  │  ├─ Card Type: Quarter   │
│  └─ Logs: 500 scans                  │  └─ Logs: 300 scans      │
│                                      │                          │
└──────────────────────────────────────────────────────────────────┘
```

## Summary

The multi-instance architecture provides:
- **Isolation**: Each instance has completely separate data
- **Persistence**: All data is saved atomically
- **Recovery**: Power failure protection with automatic restoration
- **Flexibility**: Easy switching between instances
- **Scalability**: Can run multiple instances simultaneously
