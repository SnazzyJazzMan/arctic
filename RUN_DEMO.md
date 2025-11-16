# How to Run the Audit Demo

## You're Already in the Right Environment!

I can see you're in the `(arcticdb)` environment. Perfect!

## The Fix

I just fixed the import error. The issue was:
- `ArcticInvalidApiUsageException` is in `library.py`, not `exceptions.py`
- Changed the import in `audited_library.py`

## Run the Demo Now

Since you're already in the `(arcticdb)` environment, just run:

```bash
python demo_auditing.py
```

## If You Still Get Errors

The Python cache might be stale. Clear it and try again:

```bash
# Clear Python cache
find python/arcticdb/audit -name "*.pyc" -delete
find python/arcticdb/audit -name "__pycache__" -type d -exec rm -rf {} +

# Run demo
python demo_auditing.py
```

## Expected Output

You should see:

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

... (rest of demo output)
```

## If It Works

You'll see:
- ✅ All operations succeed with `user_id`
- ✅ Operations without `user_id` are rejected
- ✅ Audit trail is displayed

Then check the audit log:
```bash
cat demo_audit.log
```

## Clean Up After Demo

```bash
rm -rf demo_audit_db demo_audit.log
```

## Next: Update Your demo1.py

Once this works, you can update `/Users/wv/augmentDemo/clientDemo/demo1.py` by just adding `user_id` parameters!

