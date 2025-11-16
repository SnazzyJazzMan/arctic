"""
Audit logging functionality for ArcticDB operations.
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Any
import threading


@dataclass
class AuditLogEntry:
    """Represents a single audit log entry."""
    timestamp: str
    actor: str  # user_id or system_id
    operation: str  # read, write, append, update, delete, etc.
    symbols: List[str]
    library: str
    version: Optional[int] = None
    metadata: Optional[dict] = None
    success: bool = True
    error_message: Optional[str] = None

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    def to_json(self):
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


class AuditLogger:
    """
    Handles audit logging for ArcticDB operations.
    
    Logs are written to both a file and Python's logging system.
    Thread-safe for concurrent operations.
    """

    def __init__(self, log_file: Optional[str] = None, log_level: int = logging.INFO):
        """
        Initialize the audit logger.
        
        Parameters
        ----------
        log_file : Optional[str]
            Path to the audit log file. If None, defaults to 'arcticdb_audit.log' in current directory.
        log_level : int
            Logging level (default: logging.INFO)
        """
        self.log_file = Path(log_file) if log_file else Path("arcticdb_audit.log")
        self._lock = threading.Lock()
        
        # Set up Python logger
        self.logger = logging.getLogger("arcticdb.audit")
        self.logger.setLevel(log_level)
        
        # File handler for audit logs
        if not self.logger.handlers:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(log_level)
            formatter = logging.Formatter('%(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
            # Also add console handler for visibility
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s - AUDIT - %(message)s'
            ))
            self.logger.addHandler(console_handler)

    def log(self, entry: AuditLogEntry):
        """
        Log an audit entry.
        
        Parameters
        ----------
        entry : AuditLogEntry
            The audit log entry to record
        """
        with self._lock:
            self.logger.info(entry.to_json())

    def log_operation(
        self,
        actor: str,
        operation: str,
        symbols: List[str],
        library: str,
        version: Optional[int] = None,
        metadata: Optional[dict] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """
        Log an operation with individual parameters.
        
        Parameters
        ----------
        actor : str
            User ID or system ID performing the operation
        operation : str
            Type of operation (read, write, append, etc.)
        symbols : List[str]
            List of symbols affected
        library : str
            Library name
        version : Optional[int]
            Version number if applicable
        metadata : Optional[dict]
            Additional metadata
        success : bool
            Whether the operation succeeded
        error_message : Optional[str]
            Error message if operation failed
        """
        entry = AuditLogEntry(
            timestamp=datetime.utcnow().isoformat(),
            actor=actor,
            operation=operation,
            symbols=symbols if isinstance(symbols, list) else [symbols],
            library=library,
            version=version,
            metadata=metadata,
            success=success,
            error_message=error_message
        )
        self.log(entry)

    def query_logs(
        self,
        actor: Optional[str] = None,
        operation: Optional[str] = None,
        symbol: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> List[AuditLogEntry]:
        """
        Query audit logs with filters.
        
        Parameters
        ----------
        actor : Optional[str]
            Filter by actor
        operation : Optional[str]
            Filter by operation type
        symbol : Optional[str]
            Filter by symbol
        start_time : Optional[str]
            Filter by start timestamp (ISO format)
        end_time : Optional[str]
            Filter by end timestamp (ISO format)
            
        Returns
        -------
        List[AuditLogEntry]
            Matching audit log entries
        """
        # This is a simple implementation - for production, consider using a database
        raise NotImplementedError("Query functionality requires database backend")

