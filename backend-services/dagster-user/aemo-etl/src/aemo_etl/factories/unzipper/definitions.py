from dagster import Definitions

from aemo_etl.configs import ARCHIVE_BUCKET, LANDING_BUCKET
from aemo_etl.factories.unzipper.assets import unzipper_asset_factory
from aemo_etl.factories.unzipper.file_unzipper import FileUnzipper


def unzipper_definitions_factory(
    domain: str,
    name: str,
    *,
    s3_landing_bucket: str = LANDING_BUCKET,
    s3_landing_prefix: str | None = None,
    s3_archive_bucket: str = ARCHIVE_BUCKET,
    file_unzipper: FileUnzipper | None = None,
    group_name: str = "gas_raw",
) -> Definitions:
    """Return a ``Definitions`` object containing a sensor-driven unzipper asset.

    Parameters
    ----------
    domain:
        Logical domain label used to derive the default S3 prefix
        (``bronze/{domain}``) when *s3_landing_prefix* is not supplied.
    name:
        Dagster asset name (e.g. ``"unzipper_vicgas"``).
    s3_landing_bucket:
        S3 bucket that contains the zip files.  Defaults to
        ``LANDING_BUCKET``.
    s3_landing_prefix:
        S3 prefix within *s3_landing_bucket*.  Defaults to
        ``"bronze/{domain}"``.
    file_unzipper:
        Injection point for the unzip strategy.  Defaults to
        ``S3FileUnzipper``.
    group_name:
        Dagster group name for the asset.
    """
    prefix = s3_landing_prefix if s3_landing_prefix is not None else f"bronze/{domain}"

    asset = unzipper_asset_factory(
        s3_landing_bucket=s3_landing_bucket,
        s3_landing_prefix=prefix,
        s3_archive_bucket=s3_archive_bucket,
        file_unzipper=file_unzipper,
        name=name,
        key_prefix=["bronze", domain],
        group_name=group_name,
        metadata={
            "s3_landing_root": f"s3://{s3_landing_bucket}/{prefix}",
            # glob_pattern is read by the unzipper sensor to select zip files
            "glob_pattern": "*.zip",
        },
    )

    return Definitions(assets=[asset])
