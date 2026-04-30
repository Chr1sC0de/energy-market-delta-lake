"""Asset factories for S3-key driven raw and silver datasets."""

import tempfile
from datetime import datetime
from typing import Mapping, Unpack

from dagster import (
    AssetExecutionContext,
    AssetsDefinition,
    Config,
    asset,
)
from dagster_aws.s3 import S3Resource
from polars import LazyFrame, col, lit, scan_delta, scan_parquet
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
    table_exists,
)


class DFFromS3KeysConfiguration(Config):
    """Runtime config containing S3 keys selected by a sensor."""

    s3_keys: list[str] = []


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

        if not table_exists(uri):
            return batch

        existing_source_files = scan_delta(uri).select("source_file").unique()
        return batch.join(existing_source_files, on="source_file", how="anti")

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

        latest_keys = cached_df.group_by("surrogate_key").agg(
            col("source_file").max().alias("source_file")
        )

        deduped = cached_df.join(
            latest_keys,
            on=["surrogate_key", "source_file"],
            how="semi",
        )

        last_deduped = deduped.unique("surrogate_key", maintain_order=False)

        last_deduped.sink_parquet(output_path)
        return scan_parquet(output_path)

    return silver_asset
