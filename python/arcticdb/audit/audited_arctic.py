"""
Audited wrapper for ArcticDB Arctic class.
"""

from typing import Optional, Union
from arcticdb.arctic import Arctic
from arcticdb.audit.audited_library import AuditedLibrary
from arcticdb.audit.audit_logger import AuditLogger
from arcticdb.options import LibraryOptions, EnterpriseLibraryOptions, OutputFormat, ArrowOutputStringFormat


class AuditedArctic:
    """
    Wrapper around Arctic that returns AuditedLibrary instances.
    
    This ensures all library operations are audited and require user_id.
    
    Examples
    --------
    >>> from arcticdb.audit import AuditedArctic
    >>> ac = AuditedArctic('lmdb:///path/to/db', audit_log_file='audit.log')
    >>> lib = ac.get_library('my_library', create_if_missing=True)
    >>> lib.write('symbol', df, user_id='john.doe')
    >>> data = lib.read('symbol', user_id='john.doe')
    """

    def __init__(
        self,
        uri: str,
        audit_log_file: Optional[str] = None,
        encoding_version=None,
        output_format: Union[OutputFormat, str] = OutputFormat.PANDAS,
        arrow_string_format_default: Union[ArrowOutputStringFormat, "pa.DataType"] = None,
        **kwargs
    ):
        """
        Initialize AuditedArctic instance.
        
        Parameters
        ----------
        uri : str
            Arctic URI (e.g., 'lmdb:///path' or 's3://endpoint:bucket')
        audit_log_file : Optional[str]
            Path to audit log file. Defaults to 'arcticdb_audit.log'
        encoding_version : EncodingVersion, optional
            Encoding version for new libraries
        output_format : Union[OutputFormat, str]
            Default output format
        arrow_string_format_default : Union[ArrowOutputStringFormat, "pa.DataType"]
            Arrow string format default
        **kwargs
            Additional arguments passed to Arctic
        """
        # Initialize the underlying Arctic instance
        arctic_kwargs = {}
        if encoding_version is not None:
            arctic_kwargs['encoding_version'] = encoding_version
        arctic_kwargs['output_format'] = output_format
        if arrow_string_format_default is not None:
            arctic_kwargs['arrow_string_format_default'] = arrow_string_format_default
            
        self._arctic = Arctic(uri, **arctic_kwargs)
        self._audit_logger = AuditLogger(log_file=audit_log_file)
        self._uri = uri

    def get_library(
        self,
        name: str,
        create_if_missing: Optional[bool] = False,
        library_options: Optional[LibraryOptions] = None,
        output_format: Optional[Union[OutputFormat, str]] = None,
        arrow_string_format_default: Optional[Union[ArrowOutputStringFormat, "pa.DataType"]] = None,
    ) -> AuditedLibrary:
        """
        Get an audited library.
        
        Parameters
        ----------
        name : str
            Library name
        create_if_missing : bool
            Create library if it doesn't exist
        library_options : Optional[LibraryOptions]
            Options for library creation
        output_format : Optional[Union[OutputFormat, str]]
            Output format override
        arrow_string_format_default : Optional[Union[ArrowOutputStringFormat, "pa.DataType"]]
            Arrow string format override
            
        Returns
        -------
        AuditedLibrary
            Audited library wrapper
        """
        lib = self._arctic.get_library(
            name,
            create_if_missing=create_if_missing,
            library_options=library_options,
            output_format=output_format,
            arrow_string_format_default=arrow_string_format_default
        )
        return AuditedLibrary(lib, self._audit_logger, name)

    def __getitem__(self, name: str) -> AuditedLibrary:
        """Get library using subscript notation."""
        lib = self._arctic[name]
        return AuditedLibrary(lib, self._audit_logger, name)

    def create_library(
        self,
        name: str,
        library_options: Optional[LibraryOptions] = None,
        enterprise_library_options: Optional[EnterpriseLibraryOptions] = None,
        output_format: Optional[Union[OutputFormat, str]] = None,
        arrow_string_format_default: Optional[Union[ArrowOutputStringFormat, "pa.DataType"]] = None,
    ) -> AuditedLibrary:
        """Create a new audited library."""
        lib = self._arctic.create_library(
            name,
            library_options=library_options,
            enterprise_library_options=enterprise_library_options,
            output_format=output_format,
            arrow_string_format_default=arrow_string_format_default
        )
        return AuditedLibrary(lib, self._audit_logger, name)

    # Delegate non-library-returning methods to underlying Arctic
    def list_libraries(self):
        """List all libraries."""
        return self._arctic.list_libraries()

    def delete_library(self, name: str):
        """Delete a library."""
        return self._arctic.delete_library(name)

    def has_library(self, name: str) -> bool:
        """Check if library exists."""
        return self._arctic.has_library(name)

    def get_uri(self) -> str:
        """Get the URI."""
        return self._uri

    def __repr__(self):
        return f"AuditedArctic(uri={self._uri!r})"

