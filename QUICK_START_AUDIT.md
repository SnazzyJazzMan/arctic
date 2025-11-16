# ArcticDB Enterprise Audit - Quick Start Guide

## 🚀 Quick Start (5 minutes)

### 1. Build ArcticDB (if not already done)

```bash
# Activate conda environment
mamba activate arcticdb

# Set environment variables
export ARCTICDB_USING_CONDA=1
export ARCTIC_CMAKE_PRESET=darwin-conda-debug  # or linux-conda-debug

# Build (only needed if you made C++ changes - audit is pure Python)
cd cpp
cmake --build --preset darwin-conda-debug -j 1
cd ..
```

### 2. Test the Audit Implementation

```bash
# Run the basic test
python examples/test_audit_basic.py
```

Expected output:
```
Testing ArcticDB Audit Functionality
================================================================================
1. Initializing AuditedArctic...
   ✓ AuditedArctic initialized
2. Creating library...
   ✓ Library created
...
ALL TESTS PASSED ✓
```

### 3. Try the Example

```bash
# Run the comprehensive example
python examples/audit_example.py
```

This will demonstrate:
- Writing with user_id
- Reading with user_id
- Batch operations
- Error handling
- Audit log creation

### 4. Use in Your Code

```python
from arcticdb.audit import AuditedArctic
import pandas as pd

# Initialize
ac = AuditedArctic('lmdb:///path/to/db', audit_log_file='my_audit.log')
lib = ac.get_library('my_library', create_if_missing=True)

# Write (user_id is REQUIRED)
df = pd.DataFrame({'value': [1, 2, 3]})
lib.write('my_symbol', df, user_id='john.doe@company.com')

# Read (user_id is REQUIRED)
data = lib.read('my_symbol', user_id='jane.smith@company.com')
print(data.data)
```

### 5. Migrate Existing Data (if you have any)

```bash
# Preview what will be migrated (dry run)
python -m arcticdb.scripts.migrate_audit_metadata \
    "lmdb:///path/to/db" \
    my_library \
    --default-user-id system_migration \
    --dry-run

# Apply the migration
python -m arcticdb.scripts.migrate_audit_metadata \
    "lmdb:///path/to/db" \
    my_library \
    --default-user-id system_migration
```

## 📋 Key Points

### ✅ What You Get

1. **Mandatory user_id** - Every operation requires identifying the actor
2. **Automatic audit logs** - All operations logged in JSON format
3. **Metadata integration** - User IDs stored with data for traceability
4. **Migration tools** - Easy migration of existing data
5. **Thread-safe** - Safe for concurrent operations

### ⚠️ Important Changes

**Before (standard ArcticDB):**
```python
lib.write('symbol', df)
lib.read('symbol')
```

**After (with audit):**
```python
lib.write('symbol', df, user_id='user@company.com')
lib.read('symbol', user_id='user@company.com')
```

### 📝 Audit Log Format

Logs are written to file in JSON format:

```json
{"timestamp": "2024-01-15T10:30:00.123456", "actor": "john.doe", "operation": "write", "symbols": ["my_symbol"], "library": "my_library", "version": 1, "success": true}
```

## 🔧 Supported Operations

All these operations require `user_id`:

- `write()` - Write new data
- `read()` - Read data
- `append()` - Append to existing data
- `update()` - Update existing data
- `delete()` - Delete symbol
- `write_batch()` - Batch write
- `read_batch()` - Batch read

## 📚 Documentation

- **Comprehensive Guide**: `docs/AUDIT_GUIDE.md`
- **Implementation Summary**: `AUDIT_IMPLEMENTATION_SUMMARY.md`
- **Module README**: `python/arcticdb/audit/README.md`
- **Main README**: See "Enterprise Audit and Traceability" section

## 🧪 Testing

```bash
# Basic functionality test
python examples/test_audit_basic.py

# Comprehensive example
python examples/audit_example.py
```

## 🐛 Troubleshooting

### Error: "requires 'user_id' parameter"

**Solution**: Add `user_id` to your operation:
```python
lib.write('symbol', df, user_id='your_user_id')
```

### Audit log not created

**Check**:
1. Write permissions on directory
2. Disk space available
3. Path is valid

### Import error

**Solution**: Make sure you're using the audited version:
```python
from arcticdb.audit import AuditedArctic  # Not: from arcticdb import Arctic
```

## 💡 Best Practices

1. **User IDs**: Use email format for humans (`john.doe@company.com`), prefix for systems (`system_batch_job`)
2. **Log Rotation**: Implement for production environments
3. **Centralized Logging**: Forward to SIEM/log aggregation
4. **Access Control**: Protect audit logs with file permissions

## 🎯 Next Steps

1. ✅ Build the project (if needed)
2. ✅ Run `python examples/test_audit_basic.py`
3. ✅ Try `python examples/audit_example.py`
4. ✅ Migrate existing data (if any)
5. ✅ Update your code to use `AuditedArctic`
6. ✅ Add `user_id` to all operations

## 📞 Support

- **Issues**: GitHub Issues
- **Documentation**: `docs/AUDIT_GUIDE.md`
- **Examples**: `examples/` directory

---

**Ready to go!** 🎉

Start with: `python examples/test_audit_basic.py`

