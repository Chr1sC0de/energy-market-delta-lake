"""Asset factories for S3-key driven raw and silver datasets."""

import tempfile
from datetime import datetime
from typing import Final, Mapping, Unpack

from dagster import (
    AssetExecutionContext,
    AssetsDefinition,
    Config,
    asset,
)
from dagster_aws.s3 import S3Resource
import polars_hash as plh
from polars import Expr, LazyFrame, String, col, lit, scan_delta, scan_parquet
from polars._typing import PolarsDataType
from types_boto3_s3 import S3Client

from aemo_etl.configs import ARCHIVE_BUCKET, LANDING_BUCKET
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


def collapse_current_state_batch(batch: LazyFrame) -> LazyFrame:
    """Keep the maximum source_file row for each surrogate_key in a batch."""
    latest_keys = batch.group_by("surrogate_key").agg(
        col("source_file").max().alias("source_file")
    )
    deduped = batch.join(
        latest_keys,
        on=["surrogate_key", "source_file"],
        how="semi",
    )
    return deduped.unique("surrogate_key", maintain_order=False)


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
    content_hash_columns = source_content_hash_columns(schema)

    asset_kwargs.setdefault("metadata", {})

    asset_kwargs.setdefault("kinds", {"table", "deltalake"})

    @asset(**asset_kwargs)
    def _asset(
        context: AssetExecutionContext,
        s3: S3Resource,
        config: DFFromS3KeysConfiguration,
    ) -> LazyFrame:

        s3_client: S3Client = s3.get_client()

        processed = []
        skipped = []

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
                        for hook in postprocess_object_hooks:
                            bytes_ = hook.process(s3_landing_bucket, s3_key, bytes_)

                        df = bytes_to_lazyframe(filetype, bytes_).with_columns(
                            ingested_timestamp=lit(current_time),
                            ingested_date=lit(current_time)
                            .dt.replace_time_zone("UTC")
                            .dt.replace(hour=0, minute=0, second=0, microsecond=0),
                            surrogate_key=get_surrogate_key(surrogate_key_sources),
                        )

                        for hook in postprocess_lazyframe_hooks:
                            df = hook.process(s3_landing_bucket, s3_key, df)

                        # because we'll be moving the file to the archive bucket
                        # use that path here
                        df = df.with_columns(
                            source_file=lit(f"s3://{s3_archive_bucket}/{s3_key}")
                        )

                        # Cast declared columns, add any missing declared columns,
                        # then normalize output order so declared columns always
                        # come first while preserving unknown source columns.
                        collected_schema = df.collect_schema()
                        observed_columns = list(collected_schema.keys())
                        declared_columns = list(schema.keys())
                        unknown_columns = [
                            column
                            for column in observed_columns
                            if column not in schema
                        ]

                        # cast the schema to the correct type
                        df = df.with_columns(
                            col(c).cast(d)
                            for c, d in schema.items()
                            if c in collected_schema
                        )
                        # now add the missing columns
                        df = df.with_columns(
                            lit(None).cast(d).alias(c)
                            for c, d in schema.items()
                            if c not in collected_schema
                        )
                        df = add_source_content_hash(df, content_hash_columns)
                        # now maintain declared column order and append unknown columns
                        df = df.select([*declared_columns, *unknown_columns])

                        # Sink this file immediately to the local staging table
                        # so bytes_ and df can be freed before loading the next
                        # file. schema alignment is enforced via the empty
                        # template frame.
                        df.sink_delta(tmp_uri, mode="append")
                        has_data = True
                        processed.append(s3_key)
                    else:
                        reason = f"skipping {s3_key}, 0 bytes"
                        context.log.info(reason)
                        skipped.append(
                            {
                                "filepath": f"s3://{s3_landing_bucket}/{s3_key}",
                                "reason": reason,
                            }
                        )
                else:
                    reason = f"skipping {s3_key}, no such key"
                    context.log.info(reason)
                    skipped.append(
                        {
                            "filepath": f"s3://{s3_landing_bucket}/{s3_key}",
                            "reason": reason,
                        }
                    )
            else:
                reason = f"{s3_key} filetype {filetype} not supported"
                context.log.info(reason)
                skipped.append(
                    {"filepath": f"s3://{s3_landing_bucket}/{s3_key}", "reason": reason}
                )

        if not has_data:
            context.log.info("no valid dataframes found returning empty dataframe")
            return LazyFrame(schema=schema)

        # now move the files which have been processed to the archive bucket
        for s3_key in processed:
            s3_client.copy_object(
                CopySource={"Bucket": s3_landing_bucket, "Key": s3_key},
                Bucket=s3_archive_bucket,
                Key=s3_key,
            )
            s3_client.delete_object(Bucket=s3_landing_bucket, Key=s3_key)

        batch = scan_delta(tmp_uri)
        return collapse_current_state_batch(batch)

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
