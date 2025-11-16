# Running the Audit Demo

## Quick Start

1. **Activate your mamba environment:**
   ```bash
   mamba activate arcticdb
   ```

2. **Run the demo:**
   ```bash
   python demo_auditing.py
   ```

3. **Check the audit log:**
   ```bash
   cat demo_audit.log
   ```

## What the Demo Does

The `demo_auditing.py` script demonstrates:

1. ✅ Creating an Arctic instance (automatically uses AuditedArctic)
2. ✅ Writing data with `user_id='alice@company.com'`
3. ✅ Reading data with `user_id='bob@company.com'`
4. ✅ Appending data with `user_id='charlie@company.com'`
5. ✅ Showing that operations WITHOUT `user_id` are rejected
6. ✅ Displaying the audit trail in human-readable format

## Expected Output

```
================================================================================
ArcticDB Enterprise Audit Demo
================================================================================

1. Creating Arctic instance...
   ✓ Arctic is AuditedArctic (audit enabled by default)
   ✓ Connected to: lmdb://./demo_audit_db
   ✓ Audit log: ./demo_audit.log

2. Setting up library...
   ✓ Created library: audit_demo

3. Creating sample data...
   ✓ Created DataFrame with 50 rows

4. Writing data with user_id...
   ✓ Written symbol 'weather_data' version 1
   ✓ User: alice@company.com

5. Reading data with user_id...
   ✓ Read symbol 'weather_data' version 1
   ✓ User: bob@company.com
   ✓ Data shape: (50, 2)

6. Appending data with user_id...
   ✓ Appended to 'weather_data' version 2
   ✓ User: charlie@company.com

7. Attempting write WITHOUT user_id (will fail)...
   ✓ Correctly rejected: write requires 'user_id' parameter...

8. Audit Trail:
--------------------------------------------------------------------------------
   [2024-11-15T18:30:00.123456] write        by alice@company.com        → ['weather_data']
   [2024-11-15T18:30:01.234567] read         by bob@company.com          → ['weather_data']
   [2024-11-15T18:30:02.345678] append       by charlie@company.com      → ['weather_data']

================================================================================
Demo Complete!
================================================================================
```

## Troubleshooting

### Error: "Audit module not available"

Make sure you're in the ArcticDB directory and have the editable install:

```bash
cd /Users/wv/augmentDemo/ArcticDB
mamba activate arcticdb
python -m pip install --no-build-isolation --no-deps --verbose --editable .
```

### Error: "Arctic.__init__() got an unexpected keyword argument 'audit_log_file'"

This means the `Arctic` class is not pointing to `AuditedArctic`. Check that `python/arcticdb/__init__.py` has been modified correctly.

Run this to verify:
```bash
python test_import_audit.py
```

Should show:
```
✓ Arctic IS AuditedArctic (audit is default!)
```

### Import Errors

If you get import errors, make sure you're running from the ArcticDB directory:

```bash
cd /Users/wv/augmentDemo/ArcticDB
python demo_auditing.py
```

## Files Created by Demo

- `demo_audit_db/` - LMDB database directory
- `demo_audit.log` - JSON audit log file

You can delete these after running the demo:
```bash
rm -rf demo_audit_db demo_audit.log
```

## Next Steps

After running the demo successfully:

1. Update your `/Users/wv/augmentDemo/clientDemo/demo1.py` to add `user_id` parameters
2. Run your own scripts with audit logging
3. Check audit logs for compliance and traceability

## More Information

- **Full Guide**: `docs/AUDIT_GUIDE.md`
- **Implementation Details**: `AUDIT_IMPLEMENTATION_SUMMARY.md`
- **Quick Start**: `QUICK_START_AUDIT.md`

