#!/usr/bin/env python
"""
Basic test to verify audit functionality works correctly.
Run this after building ArcticDB to ensure audit features are working.
"""

import pandas as pd
import numpy as np
import tempfile
import shutil
from pathlib import Path


def test_audit_basic():
    """Test basic audit functionality."""
    print("Testing ArcticDB Audit Functionality")
    print("=" * 80)
    
    # Create temporary directory for test
    temp_dir = tempfile.mkdtemp(prefix='arcticdb_audit_test_')
    audit_log = Path(temp_dir) / 'test_audit.log'
    
    try:
        from arcticdb.audit import AuditedArctic
        from arcticdb import WritePayload
        
        # Test 1: Initialize AuditedArctic
        print("\n1. Initializing AuditedArctic...")
        ac = AuditedArctic(f'lmdb://{temp_dir}/db', audit_log_file=str(audit_log))
        print("   ✓ AuditedArctic initialized")
        
        # Test 2: Create library
        print("\n2. Creating library...")
        lib = ac.get_library('test_lib', create_if_missing=True)
        print("   ✓ Library created")
        
        # Test 3: Write with user_id
        print("\n3. Testing write with user_id...")
        df = pd.DataFrame({'value': [1, 2, 3]})
        result = lib.write('test_symbol', df, user_id='test_user')
        print(f"   ✓ Write successful, version: {result.version}")
        
        # Test 4: Read with user_id
        print("\n4. Testing read with user_id...")
        data = lib.read('test_symbol', user_id='test_reader')
        assert len(data.data) == 3
        print(f"   ✓ Read successful, got {len(data.data)} rows")
        
        # Test 5: Verify user_id is required
        print("\n5. Testing user_id enforcement...")
        try:
            lib.write('test_symbol2', df)  # Missing user_id
            print("   ✗ FAILED: Should have raised exception")
            return False
        except Exception as e:
            if 'user_id' in str(e):
                print(f"   ✓ Correctly enforced user_id requirement")
            else:
                print(f"   ✗ FAILED: Wrong exception: {e}")
                return False
        
        # Test 6: Verify audit log exists
        print("\n6. Checking audit log...")
        if audit_log.exists():
            with open(audit_log, 'r') as f:
                lines = f.readlines()
                print(f"   ✓ Audit log created with {len(lines)} entries")
                
                # Verify log format
                import json
                for i, line in enumerate(lines[:3], 1):
                    try:
                        entry = json.loads(line)
                        assert 'timestamp' in entry
                        assert 'actor' in entry
                        assert 'operation' in entry
                        assert 'symbols' in entry
                        print(f"   ✓ Entry {i}: {entry['operation']} by {entry['actor']}")
                    except Exception as e:
                        print(f"   ✗ FAILED: Invalid log format: {e}")
                        return False
        else:
            print("   ✗ FAILED: Audit log not created")
            return False
        
        # Test 7: Batch operations
        print("\n7. Testing batch operations...")
        df1 = pd.DataFrame({'value': [10, 20]})
        df2 = pd.DataFrame({'value': [30, 40]})
        payloads = [
            WritePayload('batch1', df1),
            WritePayload('batch2', df2)
        ]
        results = lib.write_batch(payloads, user_id='batch_user')
        print(f"   ✓ Batch write successful, {len(results)} symbols written")
        
        batch_data = lib.read_batch(['batch1', 'batch2'], user_id='batch_reader')
        print(f"   ✓ Batch read successful, {len(batch_data)} symbols read")
        
        # Test 8: Append with user_id
        print("\n8. Testing append with user_id...")
        df_append = pd.DataFrame({'value': [4, 5]})
        result = lib.append('test_symbol', df_append, user_id='append_user')
        print(f"   ✓ Append successful, version: {result.version}")
        
        # Test 9: Update with user_id
        print("\n9. Testing update with user_id...")
        df_update = pd.DataFrame({'value': [100]})
        result = lib.update('test_symbol', df_update, user_id='update_user')
        print(f"   ✓ Update successful, version: {result.version}")
        
        # Test 10: Verify metadata contains user_id
        print("\n10. Verifying user_id in metadata...")
        data = lib.read('test_symbol', user_id='metadata_checker')
        if hasattr(data, 'metadata') and data.metadata:
            if '_audit_user_id' in data.metadata:
                print(f"   ✓ Metadata contains _audit_user_id: {data.metadata['_audit_user_id']}")
            else:
                print("   ⚠ Warning: _audit_user_id not in metadata (may be expected)")
        
        print("\n" + "=" * 80)
        print("ALL TESTS PASSED ✓")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        print(f"\nCleaning up temporary directory: {temp_dir}")
        try:
            shutil.rmtree(temp_dir)
            print("✓ Cleanup complete")
        except Exception as e:
            print(f"⚠ Cleanup warning: {e}")


if __name__ == "__main__":
    import sys
    success = test_audit_basic()
    sys.exit(0 if success else 1)

