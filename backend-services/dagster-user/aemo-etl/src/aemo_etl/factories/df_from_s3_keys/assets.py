from datetime import datetime
from typing import Mapping, Unpack

from dagster import (
    AssetExecutionContext,
    AssetsDefinition,
    Config,
    asset,
)
from dagster_aws.s3 import S3Resource
from polars import LazyFrame, col, concat, lit, row_index, scan_delta
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


# Define the config schema
class DFFromS3KeysConfiguration(Config):
    s3_keys: list[str] = []


def bronze_df_from_s3_keys_asset_factory(
    schema: Mapping[str, PolarsDataType],
    surrogate_key_sources: list[str],
    postprocess_object_hooks: list[Hook[bytes]] | None = None,
    postprocess_lazyframe_hooks: list[Hook[LazyFrame]] | None = None,
    s3_archive_bucket: str = ARCHIVE_BUCKET,
    s3_landing_bucket: str = LANDING_BUCKET,
    **asset_kwargs: Unpack[AssetDefinitonParamSpec],
) -> AssetsDefinition:

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

        dfs = []

        processed = []
        skipped = []

        current_time = datetime.now(AEST)

        for s3_key in config.s3_keys:
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

                        dfs.append(df)
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

        if len(dfs) == 0:
            context.log.info("no valid dataframes found returning empty dataframe")
            return LazyFrame(schema=schema)

        df = concat([LazyFrame(schema=schema), *dfs], how="diagonal_relaxed")

        # now move the files which have been processed to the archive bucket
        for s3_key in processed:
            s3_client.copy_object(
                CopySource={"Bucket": s3_landing_bucket, "Key": s3_key},
                Bucket=s3_archive_bucket,
                Key=s3_key,
            )
            s3_client.delete_object(Bucket=s3_landing_bucket, Key=s3_key)

        return df

    return _asset


def silver_df_from_s3_keys_asset_factory(
    uri: str,
    **asset_kwargs: Unpack[AssetDefinitonParamSpec],
) -> AssetsDefinition:

    asset_kwargs.setdefault("metadata", {})

    asset_kwargs.setdefault("kinds", {"table", "deltalake"})

    # now create a silver asset which deduplicates the rows and cleans up the data
    @asset(**asset_kwargs)
    def silver_asset(df: LazyFrame) -> LazyFrame:
        deduped_df = (
            df.with_columns(
                row_index().over("surrogate_key", order_by="ingested_timestamp")
            )
            .filter(col.index == 0)
            .drop("index")
        )

        if not table_exists(uri):
            return deduped_df

        latest = scan_delta(uri)

        max_date = latest.select(col.ingested_date.max()).collect().item()

        max_ts = (
            latest.filter(col.ingested_date == max_date)
            .select(col.ingested_timestamp.max())
            .collect()
            .item()
        )

        latest_keys = (
            latest.filter(
                (col.ingested_date >= max_date) & (col.ingested_timestamp >= max_ts)
            )
            .select("surrogate_key")
            .unique()
        )

        output = deduped_df.join(latest_keys, on="surrogate_key", how="anti")

        return output

    return silver_asset
