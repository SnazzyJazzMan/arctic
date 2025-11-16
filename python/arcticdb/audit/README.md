# ArcticDB Audit Module

Enterprise audit logging and traceability for ArcticDB.

## Overview

The audit module provides a wrapper around ArcticDB that enforces user identification and automatic audit logging for all database operations. This is essential for:

- Regulatory compliance (SOX, GDPR, etc.)
- Security auditing and forensics
- Change tracking and accountability
- Data governance

## Quick Start

```python
from arcticdb.audit import AuditedArctic
import pandas as pd

# Initialize with audit logging
ac = AuditedArctic('lmdb:///path/to/db', audit_log_file='audit.log')
lib = ac.get_library('my_library', create_if_missing=True)

# All operations require user_id
df = pd.DataFrame({'value': [1, 2, 3]})
lib.write('symbol', df, user_id='john.doe@company.com')
data = lib.read('symbol', user_id='jane.smith@company.com')
```

## Key Features

### 1. Mandatory User ID
Every operation requires a `user_id` parameter. Operations without it will raise `ArcticInvalidApiUsageException`.

### 2. Automatic Audit Logging
All operations are logged with:
- Timestamp (UTC)
- Actor (user_id)
- Operation type
- Affected symbols
- Library name
- Version number
- Success/failure status

### 3. Metadata Integration
User IDs are stored in symbol metadata (`_audit_user_id`) for complete traceability.

### 4. Thread-Safe
The audit logger is thread-safe for concurrent operations.

## Supported Operations

All major operations are audited:

- `write()` - Write data
- `read()` - Read data
- `append()` - Append data
- `update()` - Update data
- `delete()` - Delete symbol
- `write_batch()` - Batch write
- `read_batch()` - Batch read

## Migration

To add audit metadata to existing data:

```bash
python -m arcticdb.scripts.migrate_audit_metadata \
    "lmdb:///path/to/db" \
    my_library \
    --default-user-id system_migration
```

## Audit Log Format

Logs are written in JSON format:

```json
{
  "timestamp": "2024-01-15T10:30:00.123456",
  "actor": "john.doe@company.com",
  "operation": "write",
  "symbols": ["stock_AAPL"],
  "library": "trading_data",
  "version": 1,
  "success": true
}
```

## Examples

See:
- `examples/audit_example.py` - Comprehensive usage examples
- `examples/test_audit_basic.py` - Basic functionality test
- `docs/AUDIT_GUIDE.md` - Complete documentation

## API Reference

### AuditedArctic

Main entry point for audited ArcticDB operations.

```python
AuditedArctic(uri, audit_log_file=None, **kwargs)
```

**Parameters:**
- `uri`: Arctic URI (e.g., 'lmdb:///path' or 's3://endpoint:bucket')
- `audit_log_file`: Path to audit log file (default: 'arcticdb_audit.log')
- `**kwargs`: Additional arguments passed to Arctic

### AuditedLibrary

Wrapper around Library that enforces audit logging.

All standard Library methods are available but require `user_id` parameter.

### AuditLogger

Handles audit log writing.

```python
AuditLogger(log_file=None, log_level=logging.INFO)
```

### AuditLogEntry

Data structure for audit log entries.

**Fields:**
- `timestamp`: ISO format timestamp
- `actor`: User or system ID
- `operation`: Operation type
- `symbols`: List of affected symbols
- `library`: Library name
- `version`: Version number (optional)
- `metadata`: Additional metadata (optional)
- `success`: Success flag
- `error_message`: Error message if failed (optional)

## Best Practices

1. **User ID Convention**: Use consistent naming (e.g., `firstname.lastname@company.com` for users, `system_<name>` for automated processes)

2. **Log Rotation**: Implement log rotation for production:
   ```python
   from logging.handlers import RotatingFileHandler
   handler = RotatingFileHandler('audit.log', maxBytes=100*1024*1024, backupCount=10)
   ```

3. **Centralized Logging**: Forward logs to SIEM or log aggregation system

4. **Access Control**: Protect audit logs with appropriate file permissions

5. **Regular Audits**: Periodically review audit logs for compliance

## Troubleshooting

**Missing user_id error:**
```
ArcticInvalidApiUsageException: write requires 'user_id' parameter
```
Solution: Add `user_id` to all operations.

**Audit log not created:**
- Check write permissions on log directory
- Verify disk space
- Check log file path is valid

## License

Same as ArcticDB - Business Source License 1.1

## Support

For issues or questions:
- GitHub Issues: https://github.com/man-group/ArcticDB/issues
- Documentation: See `docs/AUDIT_GUIDE.md`

