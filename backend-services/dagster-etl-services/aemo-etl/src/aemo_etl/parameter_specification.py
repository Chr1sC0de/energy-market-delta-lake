from datetime import datetime
from pathlib import Path
from typing import IO, Any, Literal, Mapping

from deltalake import (
    CommitProperties,
    DeltaTable,
    PostCommitHookProperties,
    WriterProperties,
)
from polars import LazyFrame, QueryOptFlags, ScanCastOptions
from polars._typing import (
    EngineType,
    FileSource,
    ParallelStrategy,
    ParquetMetadata,
    SchemaDict,
    SyncOnCloseMethod,
)
from polars.datatypes import DataType, DataTypeClass
from polars.io import PartitionBy
from polars.io.cloud import CredentialProvider, CredentialProviderFunction
from polars.lazyframe import GPUEngine
from polars.lazyframe.opt_flags import DEFAULT_QUERY_OPT_FLAGS
from pydantic import BaseModel, Field

# the following is the set of rebuilt types
_ = {DataTypeClass, DataType, CredentialProvider, GPUEngine}

LazyFrame.sink_parquet


class PolarsLazyFrameSinkParquetParamSpec(BaseModel, arbitrary_types_allowed=True):
    path: str | Path | IO[bytes] | PartitionBy
    compression: str = "zstd"
    compression_level: int | None = None
    statistics: bool | str | dict[str, bool] = True
    row_group_size: int | None = None
    data_page_size: int | None = None
    maintain_order: bool = True
    storage_options: dict[str, Any] | None = None
    credential_provider: CredentialProviderFunction | Literal["auto"] | None = "auto"
    retries: int = 2
    sync_on_close: SyncOnCloseMethod | None = None
    metadata: ParquetMetadata | None = None
    mkdir: bool = False
    lazy: bool = False
    engine: EngineType = "auto"
    optimizations: QueryOptFlags = DEFAULT_QUERY_OPT_FLAGS


class PolarsLazyFrameScanParquetParamSpec(BaseModel, arbitrary_types_allowed=True):
    source: FileSource
    n_rows: int | None = None
    row_index_name: str | None = None
    row_index_offset: int = 0
    parallel: ParallelStrategy = "auto"
    use_statistics: bool = True
    hive_partitioning: bool | None = None
    glob: bool = True
    schema_: SchemaDict | None = Field(default=None, alias="schema")
    hive_schema: SchemaDict | None = None
    try_parse_hive_dates: bool = True
    rechunk: bool = False
    low_memory: bool = False
    cache: bool = True
    storage_options: dict[str, Any] | None = None
    credential_provider: CredentialProviderFunction | Literal["auto"] | None = "auto"
    retries: int = 2
    include_file_paths: str | None = None
    missing_columns: Literal["insert", "raise"] = "insert"
    cast_options: ScanCastOptions | None = None


class PolarsDeltaLakeWriteParamSpec(BaseModel, arbitrary_types_allowed=True):
    partition_by: list[str] | str | None = None
    mode: Literal["error", "append", "overwrite", "ignore"] = "error"
    name: str | None = None
    description: str | None = None
    configuration: Mapping[str, str | None] | None = None
    schema_mode: Literal["merge", "overwrite"] | None = None
    storage_options: dict[str, str] | None = None
    predicate: str | None = None
    target_file_size: int | None = None
    writer_properties: WriterProperties | None = None
    post_commithook_properties: PostCommitHookProperties | None = None
    commit_properties: CommitProperties | None = None


class PolarsDeltaLakeMergeParamSpec(BaseModel):
    predicate: str | None = None
    source_alias: str | None = None
    target_alias: str | None = None
    merge_schema: bool = False
    error_on_type_mismatch: bool = True
    writer_properties: WriterProperties | None = None
    streamed_exec: bool = True
    post_commithook_properties: PostCommitHookProperties | None = None
    commit_properties: CommitProperties | None = None


class PolarsDataFrameWriteDeltaParamSpec(BaseModel, arbitrary_types_allowed=True):
    target: str | Path | DeltaTable
    mode: Literal["error", "append", "overwrite", "ignore", "merge"] = "error"
    storage_options: dict[str, str] | None = None
    credential_provider: CredentialProviderFunction | Literal["auto"] | None = "auto"
    delta_write_options: PolarsDeltaLakeWriteParamSpec | None = None
    delta_merge_options: PolarsDeltaLakeMergeParamSpec | None = None


class PolarsDataFrameReadScanDeltaParamSpec(BaseModel, arbitrary_types_allowed=True):
    source: str | DeltaTable
    version: int | str | datetime | None = None
    rechunk: bool | None = None
    storage_options: dict[str, Any] | None = None
    credential_provider: CredentialProviderFunction | Literal["auto"] | None = "auto"
    delta_table_options: dict[str, Any] | None = None
    use_pyarrow: bool = False
    pyarrow_options: dict[str, Any] | None = None
