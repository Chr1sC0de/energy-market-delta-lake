from typing import Callable

import bs4
from cron_descriptor import get_description
from dagster import (
    AssetsDefinition,
    AutomationCondition,
    Definitions,
    OpExecutionContext,
)
from requests import RequestException, Response
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from aemo_etl.configs import AEMO_BUCKET, LANDING_BUCKET
from aemo_etl.factories.assets.nemweb_public_files.factory import (
    SURROGATE_KEY_SOURCES,
    nemweb_public_files_asset_factory,
)
from aemo_etl.factories.assets.nemweb_public_files.ops.dynamic_nemweb_links_fetcher import (
    FilteredDynamicNEMWebLinksFetcher,
    InMemoryCachedLinkFilter,
)
from aemo_etl.factories.assets.nemweb_public_files.ops.dynamic_zip_links_fetcher import (
    S3DynamicZipLinksFetcher,
)
from aemo_etl.factories.assets.nemweb_public_files.ops.file_unzipper import (
    S3FileUnzipper,
)
from aemo_etl.factories.assets.nemweb_public_files.ops.nemweb_link_fetcher import (
    HTTPNEMWebLinkFetcher,
    default_folder_filter,
)
from aemo_etl.factories.assets.nemweb_public_files.ops.nemweb_link_processor import (
    ParquetProcessor,
    S3NemwebLinkProcessor,
)
from aemo_etl.factories.assets.nemweb_public_files.ops.processed_link_combiner import (
    S3ProcessedLinkCombiner,
)
from aemo_etl.factories.checks.check_duplicate_rows import duplicate_row_check_factory
from aemo_etl.utils import request_get

ASSET_KEYS: list[AssetsDefinition] = []


def nemweb_public_files_definition_factory(
    domain: str,
    table_name: str,
    nemweb_relative_href: str,
    cron_schedule: str,
    batch_size: int = 5,
    process_retry: int = 3,
    initial: int = 3,
    exp_base: int = 3,
    max_retry_time: int = 100,
    folder_filter: Callable[
        [OpExecutionContext, bs4.Tag], bool
    ] = default_folder_filter,
    group_name: str = "gas_raw",
) -> Definitions:

    @retry(
        stop=stop_after_attempt(process_retry),
        wait=wait_exponential_jitter(initial=10, exp_base=exp_base, max=max_retry_time),
        retry=retry_if_exception_type(RequestException),
        reraise=True,
    )
    def request_getter_with_retries(path: str) -> Response:  # pragma: no cover
        return request_get(path)

    key_prefix = ["bronze", domain]
    s3_prefix = "/".join(key_prefix)
    # since we're using the 'aemo_deltalake_append_io_manager' the
    # table we will be writing to will be stored on
    table_path = f"s3://{AEMO_BUCKET}/{s3_prefix}/{table_name}"

    asset = nemweb_public_files_asset_factory(
        metadata={
            "dagster/uri": table_path,
            "dagster/table_name": f"bronze.{domain}.{table_name}",
            "cron_schedule": get_description(cron_schedule),
            "s3_landing_root": f"s3://{LANDING_BUCKET}/{s3_prefix}",
        },
        io_manager_key="aemo_deltalake_append_io_manager",
        group_name=group_name,
        key_prefix=key_prefix,
        name=table_name,
        nemweb_relative_href=nemweb_relative_href,
        s3_landing_prefix=s3_prefix,
        nemweb_link_fetcher=HTTPNEMWebLinkFetcher(folder_filter=folder_filter),
        dynamic_zip_link_fetcher=S3DynamicZipLinksFetcher(),
        file_unzipper=S3FileUnzipper(),
        dynamic_nemweb_links_fetcher=FilteredDynamicNEMWebLinksFetcher(
            batch_size=batch_size,
            link_filter=InMemoryCachedLinkFilter(
                table_path=table_path,
                ttl_seconds=900,
            ),
        ),
        nemweb_link_processor=S3NemwebLinkProcessor(
            buffer_processor=ParquetProcessor(
                request_getter=request_getter_with_retries
            )
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
