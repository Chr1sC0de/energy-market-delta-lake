"""Asset factories for S3-key driven raw and silver datasets."""

import tempfile
from collections.abc import Iterable
from datetime import datetime
from typing import Final, Mapping, Unpack

import polars_hash as plh
from dagster import (
    AssetCheckResult,
    AssetCheckSeverity,
    AssetCheckSpec,
    AssetExecutionContext,
    AssetsDefinition,
    Config,
    MaterializeResult,
    MetadataValue,
    asset,
)
from dagster._core.definitions.asset_key import CoercibleToAssetKey
from dagster_aws.s3 import S3Resource
from polars import Expr, LazyFrame, String, col, lit, scan_delta, scan_parquet
from polars._typing import PolarsDataType
from types_boto3_s3 import S3Client

from aemo_etl.configs import ARCHIVE_BUCKET, LANDING_BUCKET
from aemo_etl.factories.df_from_s3_keys.current_state import (
    collapse_current_state_batch,
    source_table_bronze_materialization_metadata,
    write_source_table_current_state_batch,
)
from aemo_etl.factories.df_from_s3_keys.hooks import Hook
from aemo_etl.models._graph_asset_kwargs import AssetDefinitonParamSpec
from aemo_etl.utils import (
    AEST,
    BYTES_TO_LAZYFRAME_REGISTER,
    bytes_to_lazyframe,
    get_from_s3,
    get_surrogate_key,
)

SOURCE_CONTENT_HASH_COLUMN: Final = "source_content_hash"
SOURCE_CONTENT_HASH_DESCRIPTION: Final = (
    "SHA-256 hash generated from declared source columns, excluding ingestion "
    "metadata, surrogate_key, source_file, and source_content_hash"
)
SKIPPED_S3_KEYS_CHECK_NAME: Final = "check_skipped_s3_keys"
SOURCE_CONTENT_HASH_EXCLUDED_COLUMNS: Final = frozenset(
    {
        "ingested_timestamp",
        "ingested_date",
        "surrogate_key",
        "source_file",
        SOURCE_CONTENT_HASH_COLUMN,
    }
)


class DFFromS3KeysConfiguration(Config):
    """Runtime config containing S3 keys selected by a sensor."""

    s3_keys: list[str] = []


def _asset_key_from_kwargs(
    asset_kwargs: AssetDefinitonParamSpec,
) -> CoercibleToAssetKey:
    """Return the asset key Dagster will assign from @asset kwargs."""
    asset_key = asset_kwargs.get("key")
    if asset_key is not None:
        return asset_key

    name = asset_kwargs.get("name", "_asset")
    key_prefix = asset_kwargs.get("key_prefix")
    if key_prefix is None:
        return name
    if isinstance(key_prefix, str):
        return [key_prefix, name]
    return [*key_prefix, name]


def _skipped_s3_keys_check_result(
    *,
    missing_keys: list[str],
    unsupported_keys: list[str],
    deferred_processed_keys: list[str],
) -> AssetCheckResult:
    """Return the inline check result for selected keys left unresolved."""
    passed = not missing_keys and not unsupported_keys and not deferred_processed_keys
    if passed:
        message = "No selected non-empty S3 keys were skipped or deferred."
    else:
        message = "Selected non-empty S3 keys were skipped or left in landing."

    return AssetCheckResult(
        passed=passed,
        check_name=SKIPPED_S3_KEYS_CHECK_NAME,
        severity=AssetCheckSeverity.WARN,
        metadata={
            "message": MetadataValue.text(message),
            "missing_key_count": len(missing_keys),
            "unsupported_key_count": len(unsupported_keys),
            "deferred_processed_key_count": len(deferred_processed_keys),
            "missing_keys": MetadataValue.json(missing_keys),
            "unsupported_keys": MetadataValue.json(unsupported_keys),
            "deferred_processed_keys": MetadataValue.json(deferred_processed_keys),
        },
    )


def _file_outcome_metadata(
    *,
    processed_keys: list[str],
    archived_keys: list[str],
    zero_byte_keys: list[str],
    deleted_zero_byte_keys: list[str],
    missing_keys: list[str],
    unsupported_keys: list[str],
    deferred_processed_keys: list[str],
) -> dict[str, int]:
    """Return stable materialization counts for selected S3 key outcomes."""
    return {
        "processed_file_count": len(processed_keys),
        "archived_file_count": len(archived_keys),
        "zero_byte_file_count": len(zero_byte_keys),
        "deleted_zero_byte_file_count": len(deleted_zero_byte_keys),
        "missing_key_count": len(missing_keys),
        "unsupported_key_count": len(unsupported_keys),
        "deferred_processed_file_count": len(deferred_processed_keys),
    }


def with_source_content_hash_schema(
    schema: Mapping[str, PolarsDataType],
) -> dict[str, PolarsDataType]:
    """Return schema with the source content hash column declared."""
    return {**schema, SOURCE_CONTENT_HASH_COLUMN: String}


def with_source_content_hash_descriptions(
    schema_descriptions: Mapping[str, str],
) -> dict[str, str]:
    """Return schema descriptions with the source content hash described."""
    return {
        **schema_descriptions,
        SOURCE_CONTENT_HASH_COLUMN: SOURCE_CONTENT_HASH_DESCRIPTION,
    }


def source_content_hash_columns(schema: Mapping[str, PolarsDataType]) -> list[str]:
    """Return declared source columns used for source_content_hash."""
    return [
        column
        for column in schema
        if column not in SOURCE_CONTENT_HASH_EXCLUDED_COLUMNS
    ]


def get_source_content_hash(source_columns: list[str]) -> Expr:
    """Build a SHA-256 hash expression from declared source columns."""
    expressions = [col(column).cast(String).fill_null("") for column in source_columns]
    if not expressions:
        expressions = [lit("")]
    return plh.concat_str(*expressions).chash.sha2_256()


def add_source_content_hash(df: LazyFrame, source_columns: list[str]) -> LazyFrame:
    """Add source_content_hash derived from declared source columns."""
    return df.with_columns(
        get_source_content_hash(source_columns).alias(SOURCE_CONTENT_HASH_COLUMN)
    )


def source_table_bronze_frame_from_bytes(
    *,
    s3_bucket: str,
    s3_key: str,
    object_bytes: bytes,
    schema: Mapping[str, PolarsDataType],
    surrogate_key_sources: list[str] | tuple[str, ...],
    current_time: datetime,
    postprocess_object_hooks: Iterable[Hook[bytes]] = (),
    postprocess_lazyframe_hooks: Iterable[Hook[LazyFrame]] = (),
    source_file_bucket: str = ARCHIVE_BUCKET,
) -> LazyFrame:
    """Parse and normalize one source-table object into bronze rows."""
    filetype = s3_key.rsplit(".")[-1].lower()
    if filetype not in BYTES_TO_LAZYFRAME_REGISTER:
        raise ValueError(f"{s3_key} filetype {filetype} not supported")

    for hook in postprocess_object_hooks:
        object_bytes = hook.process(s3_bucket, s3_key, object_bytes)

    df = bytes_to_lazyframe(filetype, object_bytes).with_columns(
        ingested_timestamp=lit(current_time),
        ingested_date=lit(current_time)
        .dt.replace_time_zone("UTC")
        .dt.replace(hour=0, minute=0, second=0, microsecond=0),
        surrogate_key=get_surrogate_key(list(surrogate_key_sources)),
    )

    for hook in postprocess_lazyframe_hooks:
        df = hook.process(s3_bucket, s3_key, df)

    df = df.with_columns(source_file=lit(f"s3://{source_file_bucket}/{s3_key}"))

    collected_schema = df.collect_schema()
    observed_columns = list(collected_schema.keys())
    declared_columns = list(schema.keys())
    unknown_columns = [column for column in observed_columns if column not in schema]

    df = df.with_columns(
        col(column).cast(data_type)
        for column, data_type in schema.items()
        if column in collected_schema
    )
    df = df.with_columns(
        lit(None).cast(data_type).alias(column)
        for column, data_type in schema.items()
        if column not in collected_schema
    )
    df = add_source_content_hash(df, source_content_hash_columns(schema))
    return df.select([*declared_columns, *unknown_columns])


def bronze_df_from_s3_keys_asset_factory(
    uri: str,
    schema: Mapping[str, PolarsDataType],
    surrogate_key_sources: list[str],
    postprocess_object_hooks: list[Hook[bytes]] | None = None,
    postprocess_lazyframe_hooks: list[Hook[LazyFrame]] | None = None,
    s3_archive_bucket: str = ARCHIVE_BUCKET,
    s3_landing_bucket: str = LANDING_BUCKET,
    **asset_kwargs: Unpack[AssetDefinitonParamSpec],
) -> AssetsDefinition:
    """Create a bronze asset that ingests selected S3 objects into Delta."""
    postprocess_object_hooks = postprocess_object_hooks or []
    postprocess_lazyframe_hooks = postprocess_lazyframe_hooks or []
    schema = with_source_content_hash_schema(schema)

    asset_kwargs.setdefault("metadata", {})

    asset_kwargs.setdefault("kinds", {"table", "deltalake"})
    asset_kwargs["check_specs"] = [
        *(asset_kwargs.get("check_specs") or ()),
        AssetCheckSpec(
            name=SKIPPED_S3_KEYS_CHECK_NAME,
            asset=_asset_key_from_kwargs(asset_kwargs),
            description=(
                "Warns when selected non-empty S3 keys are skipped or left in "
                "landing storage."
            ),
            blocking=False,
        ),
    ]

    @asset(**asset_kwargs)
    def _asset(
        context: AssetExecutionContext,
        s3: S3Resource,
        config: DFFromS3KeysConfiguration,
    ) -> MaterializeResult:  # type: ignore[type-arg]

        s3_client: S3Client = s3.get_client()

        processed_keys: list[str] = []
        zero_byte_keys: list[str] = []
        missing_keys: list[str] = []
        unsupported_keys: list[str] = []

        current_time = datetime.now(AEST)

        # Use a local temp directory as a staging Delta table so that each
        # file's bytes and LazyFrame are freed from memory immediately after
        # sinking, rather than accumulating all frames before writing.
        tmp_dir = tempfile.mkdtemp()
        tmp_uri = f"{tmp_dir}/bronze_staging"
        has_data = False

        for s3_key in dict.fromkeys(config.s3_keys):
            filetype = s3_key.rsplit(".")[-1].lower()
            if filetype in BYTES_TO_LAZYFRAME_REGISTER:
                # since we don't know the state of the file we unfortunately can't just lazy
                # load the file. There are cases where we will have to pre-process the dataframe
                # and it might actually be easier.
                bytes_ = get_from_s3(
                    s3_client, s3_landing_bucket, s3_key, logger=context.log
                )
                if bytes_ is not None:
                    if len(bytes_) > 0:
                        df = source_table_bronze_frame_from_bytes(
                            s3_bucket=s3_landing_bucket,
                            s3_key=s3_key,
                            object_bytes=bytes_,
                            schema=schema,
                            surrogate_key_sources=surrogate_key_sources,
                            current_time=current_time,
                            postprocess_object_hooks=postprocess_object_hooks,
                            postprocess_lazyframe_hooks=postprocess_lazyframe_hooks,
                            source_file_bucket=s3_archive_bucket,
                        )

                        # Sink this file immediately to the local staging table
                        # so bytes_ and df can be freed before loading the next
                        # file. schema alignment is enforced via the empty
                        # template frame.
                        df.sink_delta(tmp_uri, mode="append")
                        has_data = True
                        processed_keys.append(s3_key)
                    else:
                        context.log.info(f"skipping {s3_key}, 0 bytes")
                        zero_byte_keys.append(s3_key)
                else:
                    reason = f"skipping {s3_key}, no such key"
                    context.log.warning(reason)
                    missing_keys.append(s3_key)
            else:
                reason = f"{s3_key} filetype {filetype} not supported"
                context.log.warning(reason)
                unsupported_keys.append(s3_key)

        if not has_data:
            context.log.info("no valid dataframes found returning empty dataframe")
            current_state_batch = LazyFrame(schema=schema)
        else:
            batch = scan_delta(tmp_uri)
            current_state_batch = collapse_current_state_batch(batch)

        write_result = write_source_table_current_state_batch(
            current_state_batch,
            target_table_uri=uri,
            logger=context.log,
        )

        archived_keys: list[str] = []
        deferred_processed_keys: list[str] = []
        if write_result.wrote_table:
            for s3_key in processed_keys:
                s3_client.copy_object(
                    CopySource={"Bucket": s3_landing_bucket, "Key": s3_key},
                    Bucket=s3_archive_bucket,
                    Key=s3_key,
                )
                s3_client.delete_object(Bucket=s3_landing_bucket, Key=s3_key)
                archived_keys.append(s3_key)
        else:
            deferred_processed_keys = processed_keys.copy()
            for s3_key in deferred_processed_keys:
                context.log.warning(
                    "leaving processed source-table bronze file in landing "
                    f"because no Delta table write occurred: {s3_key}"
                )

        deleted_zero_byte_keys: list[str] = []
        for s3_key in zero_byte_keys:
            s3_client.delete_object(Bucket=s3_landing_bucket, Key=s3_key)
            deleted_zero_byte_keys.append(s3_key)
            context.log.info(f"deleted zero-byte landing object {s3_key}")

        return MaterializeResult(
            metadata={
                **source_table_bronze_materialization_metadata(write_result),
                **_file_outcome_metadata(
                    processed_keys=processed_keys,
                    archived_keys=archived_keys,
                    zero_byte_keys=zero_byte_keys,
                    deleted_zero_byte_keys=deleted_zero_byte_keys,
                    missing_keys=missing_keys,
                    unsupported_keys=unsupported_keys,
                    deferred_processed_keys=deferred_processed_keys,
                ),
            },
            check_results=[
                _skipped_s3_keys_check_result(
                    missing_keys=missing_keys,
                    unsupported_keys=unsupported_keys,
                    deferred_processed_keys=deferred_processed_keys,
                )
            ],
        )

    return _asset


def silver_df_from_s3_keys_asset_factory(
    **asset_kwargs: Unpack[AssetDefinitonParamSpec],
) -> AssetsDefinition:
    """Create a silver asset that keeps the latest row per surrogate key."""
    asset_kwargs.setdefault("metadata", {})

    asset_kwargs.setdefault("kinds", {"table", "parquet"})

    @asset(**asset_kwargs)
    def silver_asset(df: LazyFrame) -> LazyFrame:
        tmp_dir = tempfile.mkdtemp()
        input_path = f"{tmp_dir}/silver_input.parquet"
        output_path = f"{tmp_dir}/silver_current.parquet"

        df.sink_parquet(input_path)
        cached_df = scan_parquet(input_path)

        last_deduped = collapse_current_state_batch(cached_df)

        last_deduped.sink_parquet(output_path)
        return scan_parquet(output_path)

    return silver_asset
