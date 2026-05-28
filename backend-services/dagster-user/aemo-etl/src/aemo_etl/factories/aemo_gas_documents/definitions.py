"""Definitions factory for scheduled AEMO gas document source discovery."""

from collections.abc import Callable, Iterable, Mapping

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

from aemo_etl.configs import (
    AEMO_BUCKET,
    ARCHIVE_BUCKET,
    DEFAULT_SCHEDULE_STATUS,
    LANDING_BUCKET,
)
from aemo_etl.factories.aemo_gas_documents.assets import (
    AEMOGasDocumentObservationLoader,
    DEFAULT_AEMO_MAJOR_PUBLICATIONS_HUB_DOWNLOAD_SOURCE_PAGES,
    BRONZE_AEMO_MAJOR_PUBLICATIONS_HUB_DOWNLOADS_TABLE_NAME,
    BRONZE_AEMO_GAS_DOCUMENT_SOURCES_TABLE_NAME,
    aemo_major_publications_hub_downloads_asset_factory,
    aemo_gas_document_sources_asset_factory,
    request_get_aemo_gas_document,
)
from aemo_etl.factories.aemo_gas_documents.models import (
    DEFAULT_AEMO_GAS_DOCUMENT_SOURCE_PAGES,
    AEMOGasDocumentSourcePage,
)


def aemo_gas_document_sources_definitions_factory(
    *,
    source_pages: Iterable[AEMOGasDocumentSourcePage] = (
        DEFAULT_AEMO_GAS_DOCUMENT_SOURCE_PAGES
    ),
    request_getter: Callable[[str], Response] | None = None,
    cron_schedule: str = "0 3 * * *",
    default_status: DefaultScheduleStatus = DEFAULT_SCHEDULE_STATUS,
    tags: Mapping[str, str] | None = None,
    process_retry: int = 3,
    initial: int = 10,
    exp_base: int = 3,
    max_retry_time: int = 100,
) -> Definitions:
    """Create scheduled definitions for AEMO gas document source metadata."""
    asset_tags = dict(tags or {})
    asset = aemo_gas_document_sources_asset_factory(
        source_pages=source_pages,
        request_getter=request_getter
        or _retrying_aemo_gas_document_request_getter(
            process_retry=process_retry,
            initial=initial,
            exp_base=exp_base,
            max_retry_time=max_retry_time,
        ),
        tags=asset_tags,
        metadata={
            "cron_schedule": cron_schedule,
            "cron_description": get_description(cron_schedule),
        },
    )
    job = define_asset_job(
        name=f"{BRONZE_AEMO_GAS_DOCUMENT_SOURCES_TABLE_NAME}_job",
        selection=[asset],
        tags=asset_tags,
    )
    schedule = ScheduleDefinition(
        job=job,
        cron_schedule=cron_schedule,
        default_status=default_status,
    )

    return Definitions(assets=[asset], jobs=[job], schedules=[schedule])


def aemo_major_publications_hub_downloads_definitions_factory(
    *,
    source_pages: Iterable[AEMOGasDocumentSourcePage] = (
        DEFAULT_AEMO_MAJOR_PUBLICATIONS_HUB_DOWNLOAD_SOURCE_PAGES
    ),
    request_getter: Callable[[str], Response] | None = None,
    observation_loader: AEMOGasDocumentObservationLoader | None = None,
    cron_schedule: str = "30 3 * * *",
    default_status: DefaultScheduleStatus = DEFAULT_SCHEDULE_STATUS,
    tags: Mapping[str, str] | None = None,
    landing_bucket: str = LANDING_BUCKET,
    archive_bucket: str = ARCHIVE_BUCKET,
    aemo_bucket: str = AEMO_BUCKET,
    process_retry: int = 3,
    initial: int = 10,
    exp_base: int = 3,
    max_retry_time: int = 100,
) -> Definitions:
    """Create scheduled definitions for AEMO major-publications source downloads."""
    asset_tags = dict(tags or {})
    asset = aemo_major_publications_hub_downloads_asset_factory(
        source_pages=source_pages,
        request_getter=request_getter
        or _retrying_aemo_gas_document_request_getter(
            process_retry=process_retry,
            initial=initial,
            exp_base=exp_base,
            max_retry_time=max_retry_time,
        ),
        observation_loader=observation_loader,
        landing_bucket=landing_bucket,
        archive_bucket=archive_bucket,
        aemo_bucket=aemo_bucket,
        tags=asset_tags,
        metadata={
            "cron_schedule": cron_schedule,
            "cron_description": get_description(cron_schedule),
        },
    )
    job = define_asset_job(
        name=f"{BRONZE_AEMO_MAJOR_PUBLICATIONS_HUB_DOWNLOADS_TABLE_NAME}_job",
        selection=[asset],
        tags=asset_tags,
    )
    schedule = ScheduleDefinition(
        job=job,
        cron_schedule=cron_schedule,
        default_status=default_status,
    )

    return Definitions(assets=[asset], jobs=[job], schedules=[schedule])


def _retrying_aemo_gas_document_request_getter(
    *,
    process_retry: int,
    initial: int,
    exp_base: int,
    max_retry_time: int,
) -> Callable[[str], Response]:
    """Return an AEMO gas document GET wrapper with retry policy."""

    @retry(
        stop=stop_after_attempt(process_retry),
        wait=wait_exponential_jitter(
            initial=initial, exp_base=exp_base, max=max_retry_time
        ),
        retry=retry_if_exception_type(RequestException),
        reraise=True,
    )
    def request_getter_with_retries(path: str) -> Response:
        return request_get_aemo_gas_document(path)

    return request_getter_with_retries
