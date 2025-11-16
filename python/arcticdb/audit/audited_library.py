"""
Audited wrapper for ArcticDB Library with user_id enforcement.
"""

from typing import Any, Optional, List, Union
from functools import wraps
from arcticdb.version_store.library import Library, WritePayload, UpdatePayload, ReadRequest
from arcticdb.audit.audit_logger import AuditLogger
from arcticdb.exceptions import ArcticInvalidApiUsageException


def _ensure_user_id(func):
    """Decorator to ensure user_id is provided for operations."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if 'user_id' not in kwargs or kwargs['user_id'] is None:
            raise ArcticInvalidApiUsageException(
                f"{func.__name__} requires 'user_id' parameter for audit compliance. "
                "Please provide user_id='your_user_id' or system_id='your_system_id'"
            )
        return func(self, *args, **kwargs)
    return wrapper


class AuditedLibrary:
    """
    Wrapper around ArcticDB Library that enforces audit logging.
    
    All read and write operations require a user_id parameter and are automatically logged.
    """

    def __init__(self, library: Library, audit_logger: AuditLogger, library_name: str):
        """
        Initialize audited library wrapper.
        
        Parameters
        ----------
        library : Library
            The underlying ArcticDB library
        audit_logger : AuditLogger
            Audit logger instance
        library_name : str
            Name of the library for audit logs
        """
        self._library = library
        self._audit_logger = audit_logger
        self._library_name = library_name

    def _log_operation(self, operation: str, symbols: List[str], user_id: str, 
                      version: Optional[int] = None, success: bool = True, 
                      error_message: Optional[str] = None):
        """Internal method to log operations."""
        self._audit_logger.log_operation(
            actor=user_id,
            operation=operation,
            symbols=symbols,
            library=self._library_name,
            version=version,
            success=success,
            error_message=error_message
        )

    @_ensure_user_id
    def write(self, symbol: str, data: Any, metadata: Any = None, 
              prune_previous_versions: bool = False, staged: bool = False,
              validate_index: bool = True, index_column: Optional[str] = None,
              user_id: Optional[str] = None) -> Any:
        """
        Write data with audit logging.
        
        Parameters
        ----------
        symbol : str
            Symbol name
        data : Any
            Data to write
        metadata : Any, optional
            Metadata to attach
        prune_previous_versions : bool
            Whether to prune previous versions
        staged : bool
            Whether to stage the write
        validate_index : bool
            Whether to validate the index
        index_column : Optional[str]
            Index column for Arrow tables
        user_id : str
            REQUIRED - User or system ID performing the write
            
        Returns
        -------
        VersionedItem
            The versioned item that was written
        """
        try:
            # Inject user_id into metadata for storage
            audit_metadata = metadata if metadata is not None else {}
            if not isinstance(audit_metadata, dict):
                audit_metadata = {"original_metadata": audit_metadata}
            audit_metadata["_audit_user_id"] = user_id
            
            result = self._library.write(
                symbol=symbol,
                data=data,
                metadata=audit_metadata,
                prune_previous_versions=prune_previous_versions,
                staged=staged,
                validate_index=validate_index,
                index_column=index_column
            )
            self._log_operation("write", [symbol], user_id, version=result.version, success=True)
            return result
        except Exception as e:
            self._log_operation("write", [symbol], user_id, success=False, error_message=str(e))
            raise

    @_ensure_user_id
    def read(self, symbol: str, as_of: Optional[Any] = None, date_range: Optional[tuple] = None,
             user_id: Optional[str] = None, **kwargs) -> Any:
        """
        Read data with audit logging.
        
        Parameters
        ----------
        symbol : str
            Symbol name
        as_of : Optional[Any]
            Version to read
        date_range : Optional[tuple]
            Date range filter
        user_id : str
            REQUIRED - User or system ID performing the read
        **kwargs
            Additional read parameters
            
        Returns
        -------
        VersionedItem
            The data that was read
        """
        try:
            result = self._library.read(symbol=symbol, as_of=as_of, date_range=date_range, **kwargs)
            version = result.version if hasattr(result, 'version') else None
            self._log_operation("read", [symbol], user_id, version=version, success=True)
            return result
        except Exception as e:
            self._log_operation("read", [symbol], user_id, success=False, error_message=str(e))
            raise

    @_ensure_user_id
    def append(self, symbol: str, data: Any, metadata: Any = None,
               prune_previous_versions: bool = False, validate_index: bool = True,
               user_id: Optional[str] = None, **kwargs) -> Any:
        """Append data with audit logging."""
        try:
            audit_metadata = metadata if metadata is not None else {}
            if not isinstance(audit_metadata, dict):
                audit_metadata = {"original_metadata": audit_metadata}
            audit_metadata["_audit_user_id"] = user_id

            result = self._library.append(
                symbol=symbol, data=data, metadata=audit_metadata,
                prune_previous_versions=prune_previous_versions,
                validate_index=validate_index, **kwargs
            )
            self._log_operation("append", [symbol], user_id, version=result.version, success=True)
            return result
        except Exception as e:
            self._log_operation("append", [symbol], user_id, success=False, error_message=str(e))
            raise

    @_ensure_user_id
    def update(self, symbol: str, data: Any, metadata: Any = None,
               prune_previous_versions: bool = False, user_id: Optional[str] = None, **kwargs) -> Any:
        """Update data with audit logging."""
        try:
            audit_metadata = metadata if metadata is not None else {}
            if not isinstance(audit_metadata, dict):
                audit_metadata = {"original_metadata": audit_metadata}
            audit_metadata["_audit_user_id"] = user_id

            result = self._library.update(
                symbol=symbol, data=data, metadata=audit_metadata,
                prune_previous_versions=prune_previous_versions, **kwargs
            )
            self._log_operation("update", [symbol], user_id, version=result.version, success=True)
            return result
        except Exception as e:
            self._log_operation("update", [symbol], user_id, success=False, error_message=str(e))
            raise

    @_ensure_user_id
    def delete(self, symbol: str, user_id: Optional[str] = None, **kwargs):
        """Delete symbol with audit logging."""
        try:
            self._library.delete(symbol=symbol, **kwargs)
            self._log_operation("delete", [symbol], user_id, success=True)
        except Exception as e:
            self._log_operation("delete", [symbol], user_id, success=False, error_message=str(e))
            raise

    @_ensure_user_id
    def write_batch(self, payloads: List[WritePayload], prune_previous_versions: bool = False,
                    user_id: Optional[str] = None, **kwargs) -> List[Any]:
        """Write batch with audit logging."""
        symbols = [p.symbol for p in payloads]
        try:
            # Inject user_id into each payload's metadata
            audited_payloads = []
            for p in payloads:
                audit_metadata = p.metadata if p.metadata is not None else {}
                if not isinstance(audit_metadata, dict):
                    audit_metadata = {"original_metadata": audit_metadata}
                audit_metadata["_audit_user_id"] = user_id
                audited_payloads.append(WritePayload(p.symbol, p.data, audit_metadata, p.index_column))

            results = self._library.write_batch(audited_payloads, prune_previous_versions, **kwargs)
            self._log_operation("write_batch", symbols, user_id, success=True)
            return results
        except Exception as e:
            self._log_operation("write_batch", symbols, user_id, success=False, error_message=str(e))
            raise

    @_ensure_user_id
    def read_batch(self, symbols: List[str], user_id: Optional[str] = None, **kwargs) -> List[Any]:
        """Read batch with audit logging."""
        try:
            results = self._library.read_batch(symbols, **kwargs)
            self._log_operation("read_batch", symbols, user_id, success=True)
            return results
        except Exception as e:
            self._log_operation("read_batch", symbols, user_id, success=False, error_message=str(e))
            raise

    # Delegate other methods to underlying library (non-audited for now, can be extended)
    def __getattr__(self, name):
        """Delegate unknown attributes to the underlying library."""
        return getattr(self._library, name)

