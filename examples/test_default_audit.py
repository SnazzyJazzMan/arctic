#!/usr/bin/env python
"""
Test that Arctic now defaults to AuditedArctic.
"""

import pandas as pd
import tempfile
import shutil

def test_default_audit():
    """Test that importing Arctic gives you AuditedArctic by default."""
    print("Testing that Arctic defaults to AuditedArctic...")
    print("=" * 80)
    
    # Import the normal way
    import arcticdb as adb
    
    # Check what Arctic actually is
    print(f"\n1. Arctic class: {adb.Arctic}")
    print(f"   Module: {adb.Arctic.__module__}")
    
    # Verify it's the audited version
    from arcticdb.audit import AuditedArctic
    if adb.Arctic is AuditedArctic:
        print("   ✓ Arctic is now AuditedArctic (audit is default!)")
    else:
        print("   ✗ Arctic is still the original (audit not default)")
        return False
    
    # Test that it works
    temp_dir = tempfile.mkdtemp(prefix='test_default_audit_')
    
    try:
        print("\n2. Testing normal usage with adb.Arctic()...")
        
        # Use the normal import pattern
        arctic = adb.Arctic(f'lmdb://{temp_dir}/db')
        lib = arctic.get_library('test_lib', create_if_missing=True)
        
        print("   ✓ Created Arctic instance")
        
        # Try to write WITHOUT user_id (should fail)
        df = pd.DataFrame({'value': [1, 2, 3]})
        
        print("\n3. Testing user_id enforcement...")
        try:
            lib.write('test', df)  # Missing user_id
            print("   ✗ FAILED: Should have required user_id")
            return False
        except Exception as e:
            if 'user_id' in str(e):
                print(f"   ✓ Correctly enforced user_id requirement")
            else:
                print(f"   ✗ FAILED: Wrong error: {e}")
                return False
        
        # Write WITH user_id (should work)
        print("\n4. Testing write with user_id...")
        result = lib.write('test', df, user_id='test_user')
        print(f"   ✓ Write successful with user_id")
        
        # Read WITH user_id (should work)
        print("\n5. Testing read with user_id...")
        data = lib.read('test', user_id='test_user')
        print(f"   ✓ Read successful with user_id")
        
        # Check that OriginalArctic is still available
        print("\n6. Checking OriginalArctic is still available...")
        if hasattr(adb, 'OriginalArctic'):
            print(f"   ✓ OriginalArctic available: {adb.OriginalArctic}")
            print("   ✓ Users can still use non-audited version if needed")
        else:
            print("   ⚠ OriginalArctic not available (not critical)")
        
        print("\n" + "=" * 80)
        print("SUCCESS: Arctic now defaults to AuditedArctic! ✓")
        print("=" * 80)
        print("\nThis means:")
        print("  • import arcticdb as adb; adb.Arctic() → requires user_id")
        print("  • All existing code will now enforce audit logging")
        print("  • No code changes needed (except adding user_id parameters)")
        print("  • Use adb.OriginalArctic() if you need non-audited version")
        
        return True
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    import sys
    success = test_default_audit()
    sys.exit(0 if success else 1)

