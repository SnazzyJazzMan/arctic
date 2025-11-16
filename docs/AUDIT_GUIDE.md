# ArcticDB Enterprise Audit and Traceability Guide

## Overview

The ArcticDB audit module provides enterprise-grade audit logging and traceability for all database operations. This is essential for:

- **Regulatory Compliance**: Meet SOX, GDPR, and other regulatory requirements
- **Security Auditing**: Track who accessed what data and when
- **Change Tracking**: Maintain complete history of data modifications
- **Accountability**: Ensure all operations are attributed to specific users or systems

## Key Features

### 1. Mandatory User ID

Every read and write operation requires a `user_id` parameter that identifies the actor:

```python
lib.write('symbol', data, user_id='john.doe@company.com')
lib.read('symbol', user_id='jane.smith@company.com')
```

Operations without `user_id` will raise an `ArcticInvalidApiUsageException`.

### 2. Automatic Audit Logging

All operations are automatically logged with:
- **Timestamp**: UTC timestamp of the operation
- **Actor**: User ID or system ID
- **Operation**: Type of operation (read, write, append, update, delete, etc.)
- **Symbols**: List of affected symbols
- **Library**: Library name
- **Version**: Version number (for versioned operations)
- **Success**: Whether the operation succeeded
- **Error Message**: Error details if operation failed

### 3. Metadata Integration

User IDs are stored in symbol metadata with the key `_audit_user_id`, ensuring:
- Complete traceability at the data level
- Ability to query who last modified each version
- Compatibility with existing ArcticDB features

### 4. Thread-Safe Logging

The audit logger is thread-safe and can handle concurrent operations from multiple threads.

## Installation and Setup

### Basic Setup

```python
from arcticdb.audit import AuditedArctic

# Initialize with default audit log file (arcticdb_audit.log)
ac = AuditedArctic('lmdb:///path/to/db')

# Or specify custom audit log file
ac = AuditedArctic('lmdb:///path/to/db', audit_log_file='/var/log/arcticdb/audit.log')

# Get a library
lib = ac.get_library('my_library', create_if_missing=True)
```

### Using with S3

```python
ac = AuditedArctic(
    's3://endpoint:bucket?region=us-east-1&access=KEY&secret=SECRET',
    audit_log_file='/var/log/arcticdb/s3_audit.log'
)
```

## Usage Examples

### Writing Data

```python
import pandas as pd

df = pd.DataFrame({'price': [100, 101, 102]})

# Write with user_id
result = lib.write('stock_AAPL', df, user_id='trader@company.com')
print(f"Written version {result.version}")
```

### Reading Data

```python
# Read with user_id
data = lib.read('stock_AAPL', user_id='analyst@company.com')
print(data.data)
```

### Append and Update

```python
# Append
lib.append('stock_AAPL', new_df, user_id='system_feed')

# Update
lib.update('stock_AAPL', updated_df, user_id='admin@company.com')
```

### Batch Operations

```python
from arcticdb import WritePayload

payloads = [
    WritePayload('sym1', df1),
    WritePayload('sym2', df2),
    WritePayload('sym3', df3)
]

# Batch write
lib.write_batch(payloads, user_id='batch_processor')

# Batch read
results = lib.read_batch(['sym1', 'sym2', 'sym3'], user_id='reporting_system')
```

### System Operations

For automated processes, use descriptive system IDs:

```python
lib.write('daily_summary', df, user_id='system_daily_batch')
lib.write('market_data', df, user_id='system_market_feed')
```

## Migrating Existing Data

If you have existing ArcticDB data without audit metadata, use the migration script:

### Dry Run (Preview Changes)

```bash
python -m arcticdb.scripts.migrate_audit_metadata \
    "lmdb:///path/to/db" \
    my_library \
    --default-user-id system_migration \
    --dry-run
```

### Apply Migration

```bash
python -m arcticdb.scripts.migrate_audit_metadata \
    "lmdb:///path/to/db" \
    my_library \
    --default-user-id system_migration
```

The migration script will:
1. Scan all symbols in the library
2. Check each version for existing audit metadata
3. Add `_audit_user_id` and `_audit_migration_timestamp` to versions without it
4. Skip versions that already have audit metadata
5. Provide a summary of migrated, skipped, and failed versions

## Audit Log Format

Logs are written in JSON format, one entry per line:

```json
{"timestamp": "2024-01-15T10:30:00.123456", "actor": "john.doe", "operation": "write", "symbols": ["stock_AAPL"], "library": "trading", "version": 1, "success": true}
{"timestamp": "2024-01-15T10:31:00.456789", "actor": "jane.smith", "operation": "read", "symbols": ["stock_AAPL"], "library": "trading", "version": 1, "success": true}
```

This format is:
- Easy to parse with standard JSON tools
- Compatible with log aggregation systems (Splunk, ELK, etc.)
- Human-readable for debugging
- Machine-readable for automated analysis

## Best Practices

### 1. User ID Naming Convention

Use consistent naming conventions:
- **Human users**: `firstname.lastname@company.com` or `username`
- **System processes**: `system_<process_name>` (e.g., `system_daily_batch`)
- **Services**: `service_<service_name>` (e.g., `service_api_gateway`)

### 2. Log Rotation

Implement log rotation to manage audit log file size:

```python
import logging
from logging.handlers import RotatingFileHandler

# Custom audit logger with rotation
handler = RotatingFileHandler(
    'audit.log',
    maxBytes=100*1024*1024,  # 100MB
    backupCount=10
)
```

### 3. Centralized Logging

For production environments, forward audit logs to a centralized logging system:
- Use log shippers (Filebeat, Fluentd)
- Send to SIEM systems
- Store in compliance-approved archives

### 4. Access Control

Protect audit log files with appropriate permissions:

```bash
chmod 640 /var/log/arcticdb/audit.log
chown arcticdb:audit /var/log/arcticdb/audit.log
```

## Troubleshooting

### Missing user_id Error

**Error**: `ArcticInvalidApiUsageException: write requires 'user_id' parameter`

**Solution**: Add `user_id` parameter to all operations:
```python
lib.write('symbol', data, user_id='your_user_id')
```

### Audit Log Not Created

**Check**:
1. Write permissions on log file directory
2. Disk space availability
3. Log file path is valid

### Performance Considerations

Audit logging adds minimal overhead:
- Logging is asynchronous where possible
- JSON serialization is fast
- File I/O is buffered

For high-throughput scenarios:
- Use SSD storage for log files
- Consider log aggregation instead of local files
- Monitor disk I/O

## Integration with Existing Code

To migrate existing code to use audit logging:

### Before
```python
import arcticdb as adb
ac = adb.Arctic('lmdb:///path')
lib = ac['my_library']
lib.write('symbol', df)
```

### After
```python
from arcticdb.audit import AuditedArctic
ac = AuditedArctic('lmdb:///path')
lib = ac['my_library']
lib.write('symbol', df, user_id='current_user')
```

## API Reference

See `python/arcticdb/audit/` for complete API documentation:
- `AuditedArctic`: Main entry point
- `AuditedLibrary`: Audited library wrapper
- `AuditLogger`: Audit logging implementation
- `AuditLogEntry`: Audit log entry data structure

