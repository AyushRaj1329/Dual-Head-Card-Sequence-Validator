# Network Port Constraints and Validation Rules

## Overview
The dual-head system enforces strict port usage rules to prevent conflicts and ensure proper network communication.

## Constraint Rules

### Rule 1: Cross-Head Port Conflicts
**Cannot listen on same IP:Port in both heads**

Head A and Head B cannot both use the same IP:Port combination for listening (input).

#### Examples:

❌ **INVALID - Both heads listening on same port:**
```
Head A Main Scanner Input: 192.168.1.100:5000
Head B Main Scanner Input: 192.168.1.100:5000
ERROR: Port conflict between heads
```

❌ **INVALID - 0.0.0.0 overlaps with specific IP:**
`