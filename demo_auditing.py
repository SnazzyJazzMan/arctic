#!/usr/bin/env python
"""
Simple demo of ArcticDB enterprise audit features.

This demonstrates how the audit trail works with the default Arctic interface.
Since audit is now the default, using adb.Arctic() automatically enforces user_id.
"""

import numpy as np
import pandas as pd
import arcticdb as adb
import os
import json

def main():
    print("=" * 80)
    print("ArcticDB Enterprise Audit Demo")
    print("=" * 80)

    # 1. Create Arctic instance (now uses AuditedArctic by default!)
    print("\n1. Creating Arctic instance...")
    uri = "lmdb://./demo_audit_db"

    # Try to use the audited version
    try:
        from arcticdb.audit import AuditedArctic

        # Check if Arctic is already the audited version
        if adb.Arctic is AuditedArctic:
            # Use AuditedArctic with audit_log_file parameter
            print(f"   ✓ Arctic is AuditedArctic (audit enabled by default)")
            arctic = adb.Arctic(uri, audit_log_file='./demo_audit.log')
            print(f"   ✓ Connected to: {uri}")
            print(f"   ✓ Audit log: ./demo_audit.log")
        else:
            # Fallback: use AuditedArctic explicitly
            print("   ⚠ Arctic is not audited by default, using AuditedArctic explicitly")
            arctic = AuditedArctic(uri, audit_log_file='./demo_audit.log')
            print(f"   ✓ Connected to: {uri}")
            print(f"   ✓ Audit log: ./demo_audit.log")
    except ImportError as e:
        print(f"   ✗ Error: Audit module not available: {e}")
        print("   ✗ Please ensure the audit module is properly installed")
        import traceback
        traceback.print_exc()
        return
    except Exception as e:
        print(f"   ✗ Error creating Arctic instance: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 2. Create or get library
    print("\n2. Setting up library...")
    lib_name = "audit_demo"
    if lib_name not in arctic.list_libraries():
        arctic.create_library(lib_name)
        print(f"   ✓ Created library: {lib_name}")
    else:
        print(f"   ✓ Using existing library: {lib_name}")
    
    lib = arctic[lib_name]
    
    # 3. Create sample data
    print("\n3. Creating sample data...")
    dates = pd.date_range("2024-01-01", periods=50, freq="D")
    df = pd.DataFrame({
        "temperature": np.random.uniform(15, 30, 50),
        "humidity": np.random.uniform(40, 80, 50),
    }, index=dates)
    print(f"   ✓ Created DataFrame with {len(df)} rows")
    
    # 4. Write data WITH user_id (required!)
    print("\n4. Writing data with user_id...")
    symbol = "weather_data"
    try:
        result = lib.write(symbol, df, user_id='alice@company.com')
        print(f"   ✓ Written symbol '{symbol}' version {result.version}")
        print(f"   ✓ User: alice@company.com")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return
    
    # 5. Read data WITH user_id (required!)
    print("\n5. Reading data with user_id...")
    try:
        data = lib.read(symbol, user_id='bob@company.com')
        print(f"   ✓ Read symbol '{symbol}' version {data.version}")
        print(f"   ✓ User: bob@company.com")
        print(f"   ✓ Data shape: {data.data.shape}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return
    
    # 6. Append more data
    print("\n6. Appending data with user_id...")
    df_append = pd.DataFrame({
        "temperature": np.random.uniform(15, 30, 10),
        "humidity": np.random.uniform(40, 80, 10),
    }, index=pd.date_range("2024-02-20", periods=10, freq="D"))
    
    try:
        result = lib.append(symbol, df_append, user_id='charlie@company.com')
        print(f"   ✓ Appended to '{symbol}' version {result.version}")
        print(f"   ✓ User: charlie@company.com")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 7. Demonstrate what happens WITHOUT user_id
    print("\n7. Attempting write WITHOUT user_id (will fail)...")
    try:
        lib.write('test_symbol', df)  # Missing user_id!
        print("   ✗ This should not succeed!")
    except Exception as e:
        print(f"   ✓ Correctly rejected: {str(e)[:60]}...")
    
    # 8. Show the audit trail
    print("\n8. Audit Trail:")
    print("-" * 80)
    if os.path.exists('./demo_audit.log'):
        with open('./demo_audit.log', 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    print(f"   [{entry['timestamp']}] {entry['operation']:12s} "
                          f"by {entry['actor']:25s} → {entry['symbols']}")
                except:
                    pass
    else:
        print("   (Audit log not found)")
    
    print("\n" + "=" * 80)
    print("Demo Complete!")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("  • Every operation requires user_id parameter")
    print("  • All operations are automatically logged")
    print("  • Audit log is in JSON format for easy parsing")
    print("  • User IDs are stored in metadata for traceability")
    print("\nCheck './demo_audit.log' for the complete audit trail!")
    print("=" * 80)


if __name__ == "__main__":
    main()

