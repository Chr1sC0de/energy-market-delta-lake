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

from aemo_etl.configs import DEFAULT_SCHEDULE_STATUS
from aemo_etl.factories.aemo_gas_documents.assets import (
    BRONZE_AEMO_GAS_DOCUMENT_SOURCES_TABLE_NAME,
    aemo_gas_document_sources_asset_factory,
)
from aemo_etl.factories.aemo_gas_documents.models import (
    DEFAULT_AEMO_GAS_DOCUMENT_SOURCE_PAGES,
    AEMOGasDocumentSourcePage,
)
from aemo_etl.utils import request_get


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

    @retry(
        stop=stop_after_attempt(process_retry),
        wait=wait_exponential_jitter(
            initial=initial, exp_base=exp_base, max=max_retry_time
        ),
        retry=retry_if_exception_type(RequestException),
        reraise=True,
    )
    def request_getter_with_retries(path: str) -> Response:
        return request_get(path)

    asset_tags = dict(tags or {})
    asset = aemo_gas_document_sources_asset_factory(
        source_pages=source_pages,
        request_getter=request_getter or request_getter_with_retries,
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
