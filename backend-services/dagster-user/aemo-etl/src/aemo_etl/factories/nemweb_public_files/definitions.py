"""Definitions factory for scheduled NEMWeb public file discovery."""

from collections.abc import Mapping
from dataclasses import dataclass

from cron_descriptor import get_description
from dagster import (
    DefaultScheduleStatus,
    Definitions,
    ScheduleDefinition,
    define_asset_job,
)
from requests import RequestException, Response
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from aemo_etl.asset_organization import GAS_INGESTION_DISCOVERY_GROUP
from aemo_etl.configs import AEMO_BUCKET, LANDING_BUCKET
from aemo_etl.factories.checks import duplicate_row_check_factory
from aemo_etl.factories.nemweb_public_files.assets import (
    SURROGATE_KEY_SOURCES,
    nemweb_public_files_asset_factory,
)
from aemo_etl.factories.nemweb_public_files.ops.dynamic_nemweb_links_fetcher import (
    FilteredDynamicNEMWebLinksFetcher,
    InMemoryCachedLinkFilter,
)
from aemo_etl.factories.nemweb_public_files.ops.nemweb_link_fetcher import (
    HTTPNEMWebLinkFetcher,
    TagFilter,
    default_file_filter,
    default_folder_filter,
)
from aemo_etl.factories.nemweb_public_files.ops.nemweb_link_processor import (
    ParquetProcessor,
    S3NemwebLinkProcessor,
)
from aemo_etl.factories.nemweb_public_files.ops.processed_link_combiner import (
    S3ProcessedLinkCombiner,
)
from aemo_etl.utils import request_get


@dataclass(frozen=True, slots=True, kw_only=True)
class NEMWebPublicFilesSpec:
    """Definition-building spec for one NEMWeb public-file listing asset."""

    domain: str
    table_name: str
    nemweb_relative_href: str
    cron_schedule: str
    default_status: DefaultScheduleStatus
    n_executors: int
    folder_filter: TagFilter
    file_filter: TagFilter
    group_name: str
    tags: Mapping[str, str] | None
    process_retry: int
    initial: int
    exp_base: int
    max_retry_time: int
    table_bucket: str
    landing_bucket: str
    io_manager_key: str
    cached_link_ttl_seconds: float

    @property
    def key_prefix(self) -> list[str]:
        """Return the bronze asset key prefix for this listing table."""
        return ["bronze", self.domain]

    @property
    def s3_prefix(self) -> str:
        """Return the S3 prefix shared by the table and landing objects."""
        return "/".join(self.key_prefix)

    @property
    def table_path(self) -> str:
        """Return the Delta table URI used for cached-link filtering."""
        return f"s3://{self.table_bucket}/{self.s3_prefix}/{self.table_name}"

    @property
    def landing_root(self) -> str:
        """Return the landing bucket root URI for this listing table."""
        return f"s3://{self.landing_bucket}/{self.s3_prefix}"


def build_nemweb_public_files_definitions(
    spec: NEMWebPublicFilesSpec,
) -> Definitions:
    """Build scheduled definitions from a NEMWeb public-file listing spec."""

    @retry(
        stop=stop_after_attempt(spec.process_retry),
        wait=wait_exponential_jitter(
            initial=spec.initial, exp_base=spec.exp_base, max=spec.max_retry_time
        ),
        retry=retry_if_exception_type(RequestException),
        reraise=True,
    )
    def request_getter_with_retries(path: str) -> Response:
        return request_get(path)

    asset = nemweb_public_files_asset_factory(
        tags=spec.tags,
        metadata={
            "dagster/uri": spec.table_path,
            "dagster/table_name": f"bronze.{spec.domain}.{spec.table_name}",
            "cron_schedule": spec.cron_schedule,
            "cron_description": get_description(spec.cron_schedule),
            "s3_landing_root": spec.landing_root,
        },
        io_manager_key=spec.io_manager_key,
        group_name=spec.group_name,
        key_prefix=spec.key_prefix,
        name=spec.table_name,
        nemweb_relative_href=spec.nemweb_relative_href,
        s3_landing_bucket=spec.landing_bucket,
        s3_landing_prefix=spec.s3_prefix,
        nemweb_link_fetcher=HTTPNEMWebLinkFetcher(
            folder_filter=spec.folder_filter,
            file_filter=spec.file_filter,
        ),
        dynamic_nemweb_links_fetcher=FilteredDynamicNEMWebLinksFetcher(
            n_executors=spec.n_executors,
            link_filter=InMemoryCachedLinkFilter(
                table_path=spec.table_path,
                ttl_seconds=spec.cached_link_ttl_seconds,
            ),
        ),
        nemweb_link_processor=S3NemwebLinkProcessor(
            buffer_processor=ParquetProcessor(
                request_getter=request_getter_with_retries
            )
        ),
        processed_link_combiner=S3ProcessedLinkCombiner(),
    )

    asset_check = duplicate_row_check_factory(
        assets_definition=asset,
        check_name="check_for_duplicate_rows",
        primary_key="surrogate_key",
        description=f"Check that surrogate_key({SURROGATE_KEY_SOURCES}) is unique",
    )

    # create a scheduled asset job

    job = define_asset_job(name=f"{spec.table_name}_job", selection=[asset])

    schedule = ScheduleDefinition(
        job=job,
        cron_schedule=spec.cron_schedule,
        default_status=spec.default_status,
    )

    return Definitions(
        assets=[asset],
        jobs=[job],
        schedules=[schedule],
        asset_checks=[asset_check],
    )


def nemweb_public_files_definitions_factory(
    domain: str,
    table_name: str,
    nemweb_relative_href: str,
    cron_schedule: str,
    n_executors: int = 1,
    process_retry: int = 3,
    initial: int = 10,
    exp_base: int = 3,
    max_retry_time: int = 100,
    folder_filter: TagFilter = default_folder_filter,
    file_filter: TagFilter = default_file_filter,
    group_name: str = GAS_INGESTION_DISCOVERY_GROUP,
    tags: Mapping[str, str] | None = None,
    default_status: DefaultScheduleStatus = DefaultScheduleStatus.STOPPED,
    table_bucket: str = AEMO_BUCKET,
    landing_bucket: str = LANDING_BUCKET,
    io_manager_key: str = "aemo_deltalake_append_io_manager",
    cached_link_ttl_seconds: float = 900,
) -> Definitions:
    """Create scheduled definitions for a NEMWeb public file listing asset."""
    return build_nemweb_public_files_definitions(
        NEMWebPublicFilesSpec(
            domain=domain,
            table_name=table_name,
            nemweb_relative_href=nemweb_relative_href,
            cron_schedule=cron_schedule,
            default_status=default_status,
            n_executors=n_executors,
            folder_filter=folder_filter,
            file_filter=file_filter,
            group_name=group_name,
            tags=tags,
            process_retry=process_retry,
            initial=initial,
            exp_base=exp_base,
            max_retry_time=max_retry_time,
            table_bucket=table_bucket,
            landing_bucket=landing_bucket,
            io_manager_key=io_manager_key,
            cached_link_ttl_seconds=cached_link_ttl_seconds,
        )
    )
