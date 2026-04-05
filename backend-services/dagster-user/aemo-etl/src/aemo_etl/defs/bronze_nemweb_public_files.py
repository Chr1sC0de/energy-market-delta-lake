from cron_descriptor import get_description
from dagster import (
    AssetsDefinition,
    AutomationCondition,
    AutomationConditionSensorDefinition,
    Definitions,
    definitions,
)

from aemo_etl.configs import AEMO_BUCKET, LANDING_BUCKET
from aemo_etl.factories.check_duplicate_rows import duplicate_row_check_factory
from aemo_etl.factories.nemweb_public_files.factory import (
    SURROGATE_KEY_SOURCES,
    nemweb_public_files_asset_factory,
)
from aemo_etl.factories.nemweb_public_files.ops.dynamic_nemweb_links_fetcher import (
    FilteredDynamicNEMWebLinksFetcher,
    InMemoryCachedLinkFilter,
)
from aemo_etl.factories.nemweb_public_files.ops.dynamic_zip_links_fetcher import (
    S3DynamicZipLinksFetcher,
)
from aemo_etl.factories.nemweb_public_files.ops.file_unzipper import S3FileUnzipper
from aemo_etl.factories.nemweb_public_files.ops.nemweb_link_fetcher import (
    HTTPNEMWebLinkFetcher,
)
from aemo_etl.factories.nemweb_public_files.ops.nemweb_link_processor import (
    ParquetProcessor,
    S3NemwebLinkProcessor,
)
from aemo_etl.factories.nemweb_public_files.ops.processed_link_combiner import (
    S3ProcessedLinkCombiner,
)

GROUP_NAME = "aemo_metadata"

ASSET_KEYS: list[AssetsDefinition] = []


def definition_factory(
    key_prefix: list[str],
    table_name: str,
    nemweb_relative_href: str,
    cron_schedule: str,
) -> Definitions:

    s3_prefix = "/".join(key_prefix)
    # since we're using the 'aemo_deltalake_append_io_manager' the
    # table we will be writing to will be stored on
    table_path = f"s3://{AEMO_BUCKET}/{s3_prefix}/{table_name}"

    asset = nemweb_public_files_asset_factory(
        metadata={
            "dagster/uri": table_path,
            "dagster/table_name": table_name,
            "cron_schedule": get_description(cron_schedule),
            "s3_landing_root": f"s3://{LANDING_BUCKET}/{s3_prefix}",
        },
        io_manager_key="aemo_deltalake_append_io_manager",
        group_name=GROUP_NAME,
        key_prefix=key_prefix,
        name=table_name,
        nemweb_relative_href=nemweb_relative_href,
        s3_landing_prefix=s3_prefix,
        nemweb_link_fetcher=HTTPNEMWebLinkFetcher(),
        dynamic_zip_link_fetcher=S3DynamicZipLinksFetcher(),
        file_unzipper=S3FileUnzipper(),
        dynamic_nemweb_links_fetcher=FilteredDynamicNEMWebLinksFetcher(
            link_filter=InMemoryCachedLinkFilter(
                table_path=table_path,
                ttl_seconds=900,
            )
        ),
        nemweb_link_processor=S3NemwebLinkProcessor(
            buffer_processor=ParquetProcessor()
        ),
        processed_link_combiner=S3ProcessedLinkCombiner(),
        automation_condition=AutomationCondition.on_cron(cron_schedule)
        & ~AutomationCondition.in_progress(),
    )
    ASSET_KEYS.append(asset)

    asset_check = duplicate_row_check_factory(
        assets_definition=asset,
        check_name="check_for_duplicate_rows",
        primary_key="surrogate_key",
        description=f"Check that surrogate_key({SURROGATE_KEY_SOURCES}) is unique",
    )

    return Definitions(
        assets=[asset],
        asset_checks=[asset_check],
    )


@definitions
def defs() -> Definitions:
    return Definitions.merge(
        definition_factory(
            key_prefix=["bronze", "vicgas"],
            table_name="bronze_nemweb_public_files_vicgas",
            nemweb_relative_href="REPORTS/CURRENT/VicGas",
            cron_schedule="*/15 * * * *",
        ),
        definition_factory(
            key_prefix=["bronze", "gbb"],
            table_name="bronze_nemweb_public_files_gbb",
            nemweb_relative_href="REPORTS/CURRENT/GBB",
            cron_schedule="*/15 * * * *",
        ),
        # as the ASSET_KEYS var is populated dynamically define the sensor last
        Definitions(
            sensors=[
                AutomationConditionSensorDefinition(
                    name="bronze_nemweb_public_files_sensor",
                    target=ASSET_KEYS,
                )
            ],
        ),
    )
