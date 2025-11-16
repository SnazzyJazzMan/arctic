import logging as _logging
import os as _os

import arcticdb_ext as _ext
import sys as _sys

from arcticdb.arctic import Arctic as _OriginalArctic
from arcticdb.options import LibraryOptions, OutputFormat, RuntimeOptions, ArrowOutputStringFormat
from arcticdb.version_store.processing import QueryBuilder, where
from arcticdb.version_store._store import VersionedItem
import arcticdb.version_store.library as library
from arcticdb.tools import set_config_from_env_vars
from arcticdb_ext.version_store import DataError, VersionRequestType
from arcticdb_ext.exceptions import ErrorCode, ErrorCategory
from arcticdb.version_store.library import (
    WritePayload,
    UpdatePayload,
    ReadInfoRequest,
    ReadRequest,
    DeleteRequest,
    col,
    LazyDataFrame,
    LazyDataFrameCollection,
    LazyDataFrameAfterJoin,
    concat,
    StagedDataFinalizeMethod,
    WriteMetadataPayload,
)
from arcticdb.version_store.admin_tools import KeyType, Size

# Enterprise audit module - make it the default Arctic
try:
    from arcticdb.audit import AuditedArctic as Arctic
    from arcticdb import audit
    # Keep original Arctic available for those who need it
    OriginalArctic = _OriginalArctic
except ImportError:
    # Audit module dependencies not available, fall back to original
    Arctic = _OriginalArctic
    audit = None
    OriginalArctic = _OriginalArctic

set_config_from_env_vars(_os.environ)

__version__ = "dev"
