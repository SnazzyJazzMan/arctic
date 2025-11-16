#!/usr/bin/env python
"""
Migration script to add audit metadata to existing ArcticDB symbols.

This script scans all symbols in a library and adds a default user_id
to all existing versions that don't have audit metadata.

Usage:
    python -m arcticdb.scripts.migrate_audit_metadata <uri> <library_name> [--default-user-id <user_id>]

Example:
    python -m arcticdb.scripts.migrate_audit_metadata "lmdb:///path/to/db" my_library --default-user-id system_migration
"""

import argparse
import sys
from typing import Optional
from datetime import datetime
import arcticdb as adb
from arcticdb.version_store.library import Library


def migrate_library_audit_metadata(
    uri: str,
    library_name: str,
    default_user_id: str = "system_migration",
    dry_run: bool = False
):
    """
    Migrate a library to add audit metadata to all existing symbols.
    
    Parameters
    ----------
    uri : str
        Arctic URI (e.g., 'lmdb:///path/to/db')
    library_name : str
        Name of the library to migrate
    default_user_id : str
        Default user_id to assign to existing data (default: 'system_migration')
    dry_run : bool
        If True, only report what would be done without making changes
    """
    print(f"Starting migration for library: {library_name}")
    print(f"URI: {uri}")
    print(f"Default user_id: {default_user_id}")
    print(f"Dry run: {dry_run}")
    print("-" * 80)
    
    # Connect to Arctic
    try:
        ac = adb.Arctic(uri)
        lib = ac.get_library(library_name)
    except Exception as e:
        print(f"ERROR: Failed to connect to library: {e}")
        sys.exit(1)
    
    # Get all symbols
    try:
        symbols = lib.list_symbols()
        print(f"Found {len(symbols)} symbols to process")
    except Exception as e:
        print(f"ERROR: Failed to list symbols: {e}")
        sys.exit(1)
    
    migrated_count = 0
    skipped_count = 0
    error_count = 0
    
    for symbol in symbols:
        try:
            # Get all versions of this symbol
            versions = lib.list_versions(symbol)
            print(f"\nProcessing symbol: {symbol} ({len(versions)} versions)")
            
            for version_info in versions:
                version = version_info['version']
                
                try:
                    # Read the current version with metadata
                    versioned_item = lib.read(symbol, as_of=version)
                    current_metadata = versioned_item.metadata
                    
                    # Check if audit metadata already exists
                    if isinstance(current_metadata, dict) and '_audit_user_id' in current_metadata:
                        print(f"  Version {version}: Already has audit metadata, skipping")
                        skipped_count += 1
                        continue
                    
                    # Prepare new metadata with audit info
                    if current_metadata is None:
                        new_metadata = {}
                    elif isinstance(current_metadata, dict):
                        new_metadata = current_metadata.copy()
                    else:
                        # If metadata is not a dict, wrap it
                        new_metadata = {"original_metadata": current_metadata}
                    
                    new_metadata["_audit_user_id"] = default_user_id
                    new_metadata["_audit_migration_timestamp"] = datetime.utcnow().isoformat()
                    
                    if not dry_run:
                        # Write metadata update
                        lib.write_metadata(symbol, new_metadata)
                        print(f"  Version {version}: ✓ Migrated")
                        migrated_count += 1
                    else:
                        print(f"  Version {version}: Would migrate (dry run)")
                        migrated_count += 1
                        
                except Exception as e:
                    print(f"  Version {version}: ✗ Error - {e}")
                    error_count += 1
                    
        except Exception as e:
            print(f"ERROR processing symbol {symbol}: {e}")
            error_count += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("Migration Summary:")
    print(f"  Total symbols: {len(symbols)}")
    print(f"  Versions migrated: {migrated_count}")
    print(f"  Versions skipped: {skipped_count}")
    print(f"  Errors: {error_count}")
    
    if dry_run:
        print("\nThis was a DRY RUN. No changes were made.")
        print("Run without --dry-run to apply changes.")
    else:
        print("\nMigration complete!")
    
    return migrated_count, skipped_count, error_count


def main():
    parser = argparse.ArgumentParser(
        description="Migrate ArcticDB library to add audit metadata to existing symbols"
    )
    parser.add_argument("uri", help="Arctic URI (e.g., 'lmdb:///path/to/db')")
    parser.add_argument("library", help="Library name to migrate")
    parser.add_argument(
        "--default-user-id",
        default="system_migration",
        help="Default user_id to assign (default: system_migration)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    
    migrate_library_audit_metadata(
        uri=args.uri,
        library_name=args.library,
        default_user_id=args.default_user_id,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()

