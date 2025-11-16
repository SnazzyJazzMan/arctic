#!/usr/bin/env python
"""
Example usage of ArcticDB with enterprise audit logging.

This example demonstrates how to use the AuditedArctic wrapper
to enforce user_id tracking and automatic audit logging.
"""

import pandas as pd
import numpy as np
from arcticdb.audit import AuditedArctic


def main():
    # Initialize AuditedArctic with LMDB backend
    # Audit logs will be written to 'arcticdb_audit.log' by default
    ac = AuditedArctic('lmdb://./audit_demo_db', audit_log_file='audit_demo.log')
    
    # Create a library (or get existing one)
    lib = ac.get_library('demo_library', create_if_missing=True)
    
    print("=" * 80)
    print("ArcticDB Enterprise Audit Demo")
    print("=" * 80)
    
    # Example 1: Write data with user_id
    print("\n1. Writing data with user_id...")
    df1 = pd.DataFrame({
        'price': np.random.randn(100),
        'volume': np.random.randint(1000, 10000, 100)
    }, index=pd.date_range('2024-01-01', periods=100, freq='h'))
    
    result = lib.write('stock_AAPL', df1, user_id='alice@company.com')
    print(f"   ✓ Written symbol 'stock_AAPL' version {result.version}")
    print(f"   ✓ Audit log entry created for user: alice@company.com")
    
    # Example 2: Read data with user_id
    print("\n2. Reading data with user_id...")
    data = lib.read('stock_AAPL', user_id='bob@company.com')
    print(f"   ✓ Read symbol 'stock_AAPL' version {data.version}")
    print(f"   ✓ Audit log entry created for user: bob@company.com")
    print(f"   ✓ Data shape: {data.data.shape}")
    
    # Example 3: Append data with user_id
    print("\n3. Appending data with user_id...")
    df2 = pd.DataFrame({
        'price': np.random.randn(50),
        'volume': np.random.randint(1000, 10000, 50)
    }, index=pd.date_range('2024-01-05 04:00', periods=50, freq='h'))
    
    result = lib.append('stock_AAPL', df2, user_id='charlie@company.com')
    print(f"   ✓ Appended to 'stock_AAPL' version {result.version}")
    print(f"   ✓ Audit log entry created for user: charlie@company.com")
    
    # Example 4: Update data with user_id
    print("\n4. Updating data with user_id...")
    df3 = pd.DataFrame({
        'price': np.random.randn(20),
        'volume': np.random.randint(1000, 10000, 20)
    }, index=pd.date_range('2024-01-01', periods=20, freq='h'))
    
    result = lib.update('stock_AAPL', df3, user_id='diana@company.com')
    print(f"   ✓ Updated 'stock_AAPL' version {result.version}")
    print(f"   ✓ Audit log entry created for user: diana@company.com")
    
    # Example 5: Batch write with user_id
    print("\n5. Batch write with user_id...")
    from arcticdb import WritePayload
    
    df_msft = pd.DataFrame({'price': np.random.randn(100)}, 
                           index=pd.date_range('2024-01-01', periods=100, freq='h'))
    df_googl = pd.DataFrame({'price': np.random.randn(100)}, 
                            index=pd.date_range('2024-01-01', periods=100, freq='h'))
    
    payloads = [
        WritePayload('stock_MSFT', df_msft),
        WritePayload('stock_GOOGL', df_googl)
    ]
    
    results = lib.write_batch(payloads, user_id='system@company.com')
    print(f"   ✓ Batch written {len(results)} symbols")
    print(f"   ✓ Audit log entry created for user: system@company.com")
    
    # Example 6: Batch read with user_id
    print("\n6. Batch read with user_id...")
    batch_data = lib.read_batch(['stock_MSFT', 'stock_GOOGL'], user_id='eve@company.com')
    print(f"   ✓ Batch read {len(batch_data)} symbols")
    print(f"   ✓ Audit log entry created for user: eve@company.com")
    
    # Example 7: What happens without user_id?
    print("\n7. Attempting operation without user_id (will fail)...")
    try:
        lib.write('stock_TSLA', df1)  # Missing user_id!
        print("   ✗ This should not happen!")
    except Exception as e:
        print(f"   ✓ Correctly rejected: {e}")
    
    # Example 8: Using system_id for automated processes
    print("\n8. Using system_id for automated processes...")
    result = lib.write('stock_TSLA', df1, user_id='system_daily_batch')
    print(f"   ✓ Written by system process: system_daily_batch")
    
    print("\n" + "=" * 80)
    print("Demo complete! Check 'audit_demo.log' for audit trail.")
    print("=" * 80)
    
    # Show some audit log entries
    print("\nSample audit log entries:")
    print("-" * 80)
    try:
        with open('audit_demo.log', 'r') as f:
            lines = f.readlines()
            for line in lines[-5:]:  # Show last 5 entries
                print(line.strip())
    except FileNotFoundError:
        print("Audit log file not found yet")


if __name__ == "__main__":
    main()

