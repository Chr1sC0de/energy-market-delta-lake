"""Asset factory for extracting zip files from S3 landing storage."""

from typing import Unpack

from dagster import (
    AssetExecutionContext,
    AssetsDefinition,
    Config,
    asset,
)
from dagster_aws.s3 import S3Resource

from aemo_etl.factories.unzipper.file_unzipper import FileUnzipper, S3FileUnzipper
from aemo_etl.models._graph_asset_kwargs import AssetDefinitonParamSpec


class UnzipperConfiguration(Config):
    """Runtime configuration supplying the S3 zip keys to process."""

    s3_keys: list[str] = []


def unzipper_asset_factory(
    s3_landing_bucket: str,
    s3_landing_prefix: str,
    s3_archive_bucket: str,
    file_unzipper: FileUnzipper | None = None,
    **asset_kwargs: Unpack[AssetDefinitonParamSpec],
) -> AssetsDefinition:
    """Return a Dagster asset that unzips S3 zip files in-place.

    The asset accepts a list of S3 keys via ``UnzipperConfiguration`` (populated
    at runtime by the unzipper sensor).  For each key it:

    1. Downloads the zip from S3 to a temp file.
    2. Extracts all members, converting CSVs to Parquet.
    3. Uploads extracted files back to the same S3 prefix.
    4. Deletes the source zip when all members succeeded.

    Parameters
    ----------
    s3_landing_bucket:
        S3 bucket that contains the zip files.
    s3_landing_prefix:
        S3 prefix (folder) within the bucket to scan for zips and write
        extracted files to.
    file_unzipper:
        Strategy object responsible for extraction.  Defaults to
        ``S3FileUnzipper``.
    **asset_kwargs:
        Additional keyword arguments forwarded to ``@asset`` (e.g.
        ``name``, ``key_prefix``, ``group_name``, ``metadata``, …).
    """
    _unzipper: FileUnzipper = file_unzipper or S3FileUnzipper()

    asset_kwargs.setdefault("group_name", "AEMO")
    asset_kwargs.setdefault("kinds", {"s3", "unzipper"})
    asset_kwargs.setdefault(
        "description",
        (
            f"Unzips .zip files found at s3://{s3_landing_bucket}/{s3_landing_prefix}. "
            "CSV members are converted to Parquet; other members are uploaded as-is. "
            "Source zips are deleted after all members are successfully extracted."
        ),
    )

    @asset(**asset_kwargs)
    def _asset(
        context: AssetExecutionContext,
        s3: S3Resource,
        config: UnzipperConfiguration,
    ) -> None:
        if not config.s3_keys:
            context.log.info("No s3_keys provided — nothing to unzip.")
            return

        context.log.info(
            f"Unzipping {len(config.s3_keys)} zip file(s) from "
            f"s3://{s3_landing_bucket}/{s3_landing_prefix}"
        )
        _unzipper.unzip(
            context=context,
            s3=s3,
            s3_source_keys=config.s3_keys,
            s3_landing_bucket=s3_landing_bucket,
            s3_landing_prefix=s3_landing_prefix,
            s3_archive_bucket=s3_archive_bucket,
        )

    return _asset
