# Cache File Structure - Dual Head System

## Answer: The Program Creates 2 Cache Files

For the dual-head system, the program creates **2 separate cache files** - one for each head:

### Cache Files Created:

1. **`app_cache_instance_1.json`** - Head A (Right side)
2. **`app_cache_instance_2.json`** - Head B (Left side)

### Location:
```
C:\Users\[USERNAME]\AppData\Local\CardSequenceValidator\CardSequenceValidator\
├── app_cache_instance_1.json  ← Head A settings
├── app_cache_instance_2.json  ← Head B settings
└── instance_config.json        ← Global config (not used in dual-head mode)
```

## Why 2 Separa