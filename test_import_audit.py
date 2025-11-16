#!/usr/bin/env python
"""Quick test to verify audit module imports correctly."""

print("Testing audit module import...")

try:
    import arcticdb as adb
    print(f"✓ arcticdb imported")
    print(f"  Arctic class: {adb.Arctic}")
    print(f"  Arctic module: {adb.Arctic.__module__}")
    
    from arcticdb.audit import AuditedArctic
    print(f"✓ AuditedArctic imported")
    print(f"  AuditedArctic: {AuditedArctic}")
    
    if adb.Arctic is AuditedArctic:
        print(f"✓ Arctic IS AuditedArctic (audit is default!)")
    else:
        print(f"⚠ Arctic is NOT AuditedArctic (audit not default)")
        print(f"  adb.Arctic: {adb.Arctic}")
        print(f"  AuditedArctic: {AuditedArctic}")
    
    print("\n✓ All imports successful!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

