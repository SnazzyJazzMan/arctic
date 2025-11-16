# Making Audit the Default Behavior

## What Changed

Modified `python/arcticdb/__init__.py` so that:

```python
import arcticdb as adb
arctic = adb.Arctic('lmdb://path')  # This now creates AuditedArctic!
```

## How It Works

**Before:**
- `Arctic` → Original Arctic (no audit)
- `AuditedArctic` → Audited version (requires user_id)

**After:**
- `Arctic` → **AuditedArctic** (requires user_id) ✓
- `OriginalArctic` → Original Arctic (for backward compatibility)

## Impact on Your Code

### Your demo1.py - NO CHANGES NEEDED to import!

**Current code:**
```python
import arcticdb as adb

arctic = adb.Arctic(uri)  # Now automatically uses AuditedArctic!
lib = arctic[lib_name]

# Only need to add user_id parameters:
lib.write(symbol, df, user_id='demo_user')
lib.read(symbol, user_id='demo_user')
```

**You DON'T need to change:**
- ❌ `import arcticdb as adb` → stays the same
- ❌ `adb.Arctic(uri)` → stays the same

**You ONLY need to add:**
- ✅ `user_id='...'` parameter to write/read operations

## Testing

Activate your mamba environment and run:

```bash
mamba activate arcticdb

# Test that Arctic is now AuditedArctic
python -c "
import arcticdb as adb
from arcticdb.audit import AuditedArctic
print('Arctic is AuditedArctic:', adb.Arctic is AuditedArctic)
print('Arctic class:', adb.Arctic)
"
```

Expected output:
```
Arctic is AuditedArctic: True
Arctic class: <class 'arcticdb.audit.audited_arctic.AuditedArctic'>
```

## Updated demo1.py

Your `/Users/wv/augmentDemo/clientDemo/demo1.py` now only needs these changes:

```python
import numpy as np
import pandas as pd
import arcticdb as adb  # ← NO CHANGE NEEDED!

def main():
    uri = "lmdb://./arcticdb_demo"
    arctic = adb.Arctic(uri)  # ← NO CHANGE NEEDED! (now uses AuditedArctic automatically)
    
    # ... rest of setup code ...
    
    # Just add user_id to operations:
    write_result = lib.write(symbol, df, user_id='demo_user')  # ← ADD user_id
    read_result = lib.read(symbol, user_id='demo_user')        # ← ADD user_id
    lib.write(symbol, df2, user_id='demo_user')                # ← ADD user_id
```

## Benefits

1. **Minimal code changes** - Only add `user_id` parameters
2. **No import changes** - Keep using `import arcticdb as adb`
3. **Automatic enforcement** - All code now requires audit trail
4. **Backward compatibility** - Use `adb.OriginalArctic()` if needed

## If You Need Non-Audited Version

For special cases where you don't want audit logging:

```python
import arcticdb as adb

# Use the original Arctic (no audit)
arctic = adb.OriginalArctic('lmdb://path')
lib = arctic['my_lib']
lib.write('symbol', df)  # No user_id required
```

## Audit Log Location

By default, audit logs go to `arcticdb_audit.log` in the current directory.

To specify a custom location:

```python
import arcticdb as adb

# Specify audit log file
arctic = adb.Arctic('lmdb://path', audit_log_file='/var/log/my_audit.log')
```

## Summary

✅ **Done!** The change is already made in `python/arcticdb/__init__.py`

Now when you (or anyone) does:
```python
import arcticdb as adb
arctic = adb.Arctic('lmdb://path')
```

They automatically get the audited version that requires `user_id`!

Your demo1.py only needs to add `user_id='demo_user'` to the 3 operations (2 writes + 1 read).

