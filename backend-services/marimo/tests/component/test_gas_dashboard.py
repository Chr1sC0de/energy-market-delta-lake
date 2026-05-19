"""Component tests for the gas market dashboard helper surface."""

from collections.abc import Mapping
from datetime import date, datetime, timedelta
from types import SimpleNamespace
from typing import Self

import polars as pl
import pytest

from marimoserver.gas_dashboard import (
    BID_STACK_FACILITY_FILTER_ALL,
    BID_STACK_PARTICIPANT_FILTER_ALL,
    BID_STACK_SOURCE_SYSTEM_FILTER_ALL,
    BID_STACK_TABLE_NAME,
    BID_STACK_TABLE_SPEC,
    BID_STACK_ZONE_FILTER_ALL,
    CUSTOMER_TRANSFER_GAS_DATE_FILTER_ALL,
    CUSTOMER_TRANSFER_MARKET_CODE_FILTER_ALL,
    CUSTOMER_TRANSFER_SOURCE_SYSTEM_FILTER_ALL,
    CUSTOMER_TRANSFER_TABLE_NAME,
    CUSTOMER_TRANSFER_TABLE_SPEC,
    GAS_MODEL_TABLES,
    GAS_QUALITY_QUALITY_TYPE_FILTER_ALL,
    GAS_QUALITY_SOURCE_POINT_FILTER_ALL,
    GAS_QUALITY_TABLE_NAME,
    GAS_QUALITY_TABLE_SPEC,
    MARKET_PRICE_PRICE_TYPE_FILTER_ALL,
    MARKET_PRICE_SOURCE_SYSTEM_FILTER_ALL,
    MARKET_PRICE_SOURCE_TABLE_FILTER_ALL,
    MARKET_PRICE_TABLE_NAME,
    MARKET_PRICE_TABLE_SPEC,
    SCHEDULE_RUN_GAS_DATE_FILTER_ALL,
    SCHEDULE_RUN_SCHEDULE_TYPE_FILTER_ALL,
    SCHEDULE_RUN_SOURCE_SYSTEM_FILTER_ALL,
    SCHEDULE_RUN_TABLE_SPEC,
    SETTLEMENT_ACTIVITY_ACTIVITY_TYPE_FILTER_ALL,
    SETTLEMENT_ACTIVITY_GAS_DATE_FILTER_ALL,
    SETTLEMENT_ACTIVITY_SOURCE_SYSTEM_FILTER_ALL,
    SETTLEMENT_ACTIVITY_TABLE_NAME,
    SETTLEMENT_ACTIVITY_TABLE_SPEC,
    SOURCE_COVERAGE_STATE_COVERED,
    SOURCE_COVERAGE_STATE_EMPTY,
    SOURCE_COVERAGE_STATE_GAP,
    SOURCE_COVERAGE_STATE_UNAVAILABLE,
    SYSTEM_NOTICE_CRITICAL_FILTER_ALL,
    SYSTEM_NOTICE_CRITICAL_FILTER_CRITICAL,
    SYSTEM_NOTICE_CRITICAL_FILTER_NON_CRITICAL,
    SYSTEM_NOTICE_TABLE_NAME,
    SYSTEM_NOTICE_TABLE_SPEC,
    SYSTEM_NOTICE_WINDOW_FILTER_ACTIVE,
    SYSTEM_NOTICE_WINDOW_FILTER_ALL,
    SYSTEM_NOTICE_WINDOW_FILTER_RECENT,
    GasDashboardConfig,
    GasTableLoad,
    GasTableSpec,
    bid_stack_empty_state_markdown,
    bid_stack_facility_options,
    bid_stack_kpi_frame,
    bid_stack_observation_frame,
    bid_stack_participant_options,
    bid_stack_source_summary_frame,
    bid_stack_source_system_options,
    bid_stack_step_summary_frame,
    bid_stack_zone_options,
    cached_load_customer_transfer_table,
    cached_load_bid_stack_table,
    cached_load_gas_quality_table,
    cached_load_gas_model_tables,
    cached_load_market_price_table,
    cached_load_schedule_run_table,
    cached_load_settlement_activity_table,
    cached_load_source_coverage_tables,
    cached_load_system_notice_table,
    customer_transfer_daily_frame,
    customer_transfer_empty_state_markdown,
    customer_transfer_gas_date_options,
    customer_transfer_kpi_frame,
    customer_transfer_market_code_options,
    customer_transfer_observation_frame,
    customer_transfer_source_coverage_frame,
    customer_transfer_source_system_options,
    customer_transfer_summary_frame,
    discover_dashboard_config,
    gas_quality_empty_state_markdown,
    gas_quality_kpi_frame,
    gas_quality_observation_frame,
    gas_quality_quality_type_options,
    gas_quality_source_coverage_frame,
    gas_quality_source_point_options,
    gas_quality_type_summary_frame,
    gas_table_load_status_frame,
    gas_table_load_status_message,
    load_market_price_table,
    load_bid_stack_table,
    load_customer_transfer_table,
    load_gas_quality_table,
    load_gas_model_tables,
    load_source_coverage_tables,
    load_schedule_run_table,
    load_settlement_activity_table,
    load_system_notice_table,
    market_price_empty_state_markdown,
    market_price_kpi_frame,
    market_price_observation_frame,
    market_price_price_type_options,
    market_price_source_system_options,
    market_price_source_table_options,
    market_price_trend_frame,
    market_price_type_summary_frame,
    read_parquet_table,
    render_dashboard_context_panel,
    render_bid_stack_context_links,
    render_customer_transfer_context_links,
    render_market_price_context_links,
    render_schedule_run_context_links,
    render_settlement_activity_context_links,
    render_source_coverage_matrix_html,
    schedule_run_empty_state_markdown,
    schedule_run_gas_date_options,
    schedule_run_kpi_frame,
    schedule_run_observation_frame,
    schedule_run_schedule_type_options,
    schedule_run_source_coverage_frame,
    schedule_run_source_system_options,
    schedule_run_timestamp_summary_frame,
    schedule_run_type_summary_frame,
    settlement_activity_activity_type_options,
    settlement_activity_empty_state_markdown,
    settlement_activity_gas_date_options,
    settlement_activity_kpi_frame,
    settlement_activity_observation_frame,
    settlement_activity_source_coverage_frame,
    settlement_activity_source_system_options,
    settlement_activity_summary_frame,
    source_coverage_empty_state_markdown,
    source_coverage_kpi_frame,
    source_coverage_matrix_frame,
    source_coverage_table_specs_from_catalogue,
    source_coverage_table_specs,
    system_notice_empty_state_markdown,
    system_notice_kpi_frame,
    system_notice_source_coverage_frame,
    system_notice_summary_frame,
    table_load_by_name,
)
from marimoserver.dashboard_registry import (
    DashboardAudience,
    DashboardRegistryEntry,
    DashboardRegistryError,
    DashboardStatus,
)
from marimoserver.gas_model_loader import (
    GasModelSessionCache,
    GasModelReadRequest,
    GasModelTableRead,
    GasModelTableView,
    cache_status_label,
    format_load_duration,
    format_row_limit,
    refresh_token_from_control,
    load_gas_model_read_request,
    load_gas_model_read_requests,
    row_limit_message,
)
from marimoserver.dagster_graphql import DagsterTableAsset
from marimoserver.table_explorer import (
    CataloguedTable,
    TableAvailability,
    TableFormat,
    TablePrefix,
)


def test_read_parquet_table_delegates_to_polars(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[tuple[str, dict[str, str]]] = []

    class FakeLazyFrame:
        def collect(self) -> pl.DataFrame:
            return pl.DataFrame({"source_system": ["GBB"]})

    def scan_parquet(uri: str, storage_options: dict[str, str]) -> FakeLazyFrame:
        captured.append((uri, storage_options))
        return FakeLazyFrame()

    monkeypatch.setattr(pl, "scan_parquet", scan_parquet)

    dataframe = read_parquet_table("s3://bucket/table", {"A": "B"})

    assert dataframe.to_dict(as_series=False) == {"source_system": ["GBB"]}
    assert captured == [("s3://bucket/table/*.parquet", {"A": "B"})]


def test_read_parquet_table_honours_row_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[tuple[str, dict[str, str]] | int] = []

    class FakeLazyFrame:
        def head(self, row_limit: int) -> Self:
            captured.append(row_limit)
            return self

        def collect(self) -> pl.DataFrame:
            return pl.DataFrame({"source_system": ["GBB"]})

    def scan_parquet(uri: str, storage_options: dict[str, str]) -> FakeLazyFrame:
        captured.append((uri, storage_options))
        return FakeLazyFrame()

    monkeypatch.setattr(pl, "scan_parquet", scan_parquet)

    dataframe = read_parquet_table("s3://bucket/table", {"A": "B"}, row_limit=5)

    assert dataframe.to_dict(as_series=False) == {"source_system": ["GBB"]}
    assert captured == [("s3://bucket/table/*.parquet", {"A": "B"}), 5]


def test_discover_dashboard_config_derives_default_aemo_bucket() -> None:
    config = discover_dashboard_config({})

    assert config.development_environment == "dev"
    assert config.runtime_location == "local"
    assert config.name_prefix == "energy-market"
    assert config.aemo_bucket == "dev-energy-market-aemo"
    assert config.table_uri("silver_gas_fact_market_price") == (
        "s3://dev-energy-market-aemo/silver/gas_model/silver_gas_fact_market_price"
    )


def test_discover_dashboard_config_uses_explicit_environment() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_ENVIRONMENT": "LOCAL",
            "NAME_PREFIX": "market-lab",
            "AEMO_BUCKET": "custom-aemo",
            "AWS_ENDPOINT_URL": "http://localhost:4566",
            "AWS_DEFAULT_REGION": "ap-southeast-2",
            "AWS_ACCESS_KEY_ID": "local",
            "AWS_SECRET_ACCESS_KEY": "secret",
            "AWS_ALLOW_HTTP": "false",
        }
    )

    assert config.development_environment == "local"
    assert config.name_prefix == "market-lab"
    assert config.aemo_bucket == "custom-aemo"
    assert config.storage_options() == {
        "AWS_ENDPOINT_URL": "http://localhost:4566",
        "AWS_REGION": "ap-southeast-2",
        "AWS_ACCESS_KEY_ID": "local",
        "AWS_SECRET_ACCESS_KEY": "secret",
        "AWS_ALLOW_HTTP": "false",
        "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
    }
    assert config.full_table_scan_enabled is True


def test_discover_dashboard_config_treats_blank_values_as_unset() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_ENVIRONMENT": "",
            "NAME_PREFIX": "",
            "AWS_ENDPOINT_URL": "",
        }
    )

    assert config.development_environment == "dev"
    assert config.name_prefix == "energy-market"
    assert config.aemo_bucket == "dev-energy-market-aemo"
    assert config.aws_endpoint_url == "http://localstack:4566"


def test_discover_dashboard_config_uses_aws_runtime_defaults() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "DEVELOPMENT_ENVIRONMENT": "prod",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "AWS_DEFAULT_REGION": "ap-southeast-2",
        }
    )

    assert config.runtime_location == "aws"
    assert config.development_environment == "prod"
    assert config.aemo_bucket == "prod-energy-market-aemo"
    assert config.aws_endpoint_url is None
    assert config.aws_access_key_id is None
    assert config.aws_secret_access_key is None
    assert config.aws_allow_http == "false"
    assert config.storage_options() == {
        "AWS_REGION": "ap-southeast-2",
        "AWS_ALLOW_HTTP": "false",
        "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
    }
    assert config.full_table_scan_enabled is False
    assert config.max_preview_rows == 100


def test_discover_dashboard_config_accepts_runtime_overrides() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "MARIMO_MAX_PREVIEW_ROWS": "not-an-int",
            "MARIMO_FULL_TABLE_SCAN_ENABLED": "true",
        }
    )

    assert config.aws_runtime is True
    assert config.max_preview_rows == 100
    assert config.full_table_scan_enabled is True


def test_gas_model_specs_cover_required_dashboard_sections() -> None:
    sections = {spec.section for spec in GAS_MODEL_TABLES}
    table_names = {spec.table_name for spec in GAS_MODEL_TABLES}

    assert {"Prices", "Schedules", "Flow and capacity"} <= sections
    assert "silver_gas_fact_market_price" in table_names
    assert "silver_gas_fact_schedule_run" in table_names
    assert "silver_gas_fact_scheduled_quantity" in table_names
    assert "silver_gas_fact_connection_point_flow" in table_names
    assert "silver_gas_fact_capacity_outlook" in table_names


def test_system_notice_table_loader_uses_bounded_recent_view() -> None:
    captured: list[int | None] = []
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "3",
        }
    )

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured.append(row_limit)
        assert uri == (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_system_notice"
        )
        assert storage_options == config.storage_options()
        return pl.DataFrame(
            {
                "source_notice_id": ["older", "newer"],
                "notice_start_timestamp": [
                    datetime(2024, 1, 1, 1),
                    datetime(2024, 1, 2, 1),
                ],
            }
        )

    load = load_system_notice_table(config, reader=reader)

    assert captured == [3]
    assert load.spec == SYSTEM_NOTICE_TABLE_SPEC
    assert load.row_limit == 3
    assert load.dataframe is not None
    assert load.dataframe["source_notice_id"].to_list() == ["newer", "older"]


def test_cached_system_notice_table_loader_reuses_session_cache() -> None:
    calls: list[int] = []
    config = _dashboard_config()
    cache: GasModelSessionCache = {}

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        calls.append(len(calls) + 1)
        return pl.DataFrame({"source_notice_id": [f"notice-{calls[-1]}"]})

    first_load = cached_load_system_notice_table(config, cache, reader=reader)
    cached_load = cached_load_system_notice_table(config, cache, reader=reader)
    refreshed_load = cached_load_system_notice_table(
        config,
        cache,
        reader=reader,
        refresh_token=1,
    )

    assert calls == [1, 2]
    assert not first_load.cache_hit
    assert cached_load.cache_hit
    assert not refreshed_load.cache_hit
    assert cached_load.dataframe is not None
    assert cached_load.dataframe["source_notice_id"].to_list() == ["notice-1"]
    assert refreshed_load.dataframe is not None
    assert refreshed_load.dataframe["source_notice_id"].to_list() == ["notice-2"]


def test_market_price_table_loader_uses_bounded_recent_view() -> None:
    captured: list[int | None] = []
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "8",
        }
    )

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured.append(row_limit)
        assert uri == (
            "s3://prod-energy-market-aemo/silver/gas_model/silver_gas_fact_market_price"
        )
        assert storage_options == config.storage_options()
        return pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 1), date(2024, 1, 3)],
                "price_type": ["Older", "Newer"],
            }
        )

    load = load_market_price_table(config, reader=reader)

    assert captured == [8]
    assert load.spec == MARKET_PRICE_TABLE_SPEC
    assert load.row_limit == 8
    assert load.dataframe is not None
    assert load.dataframe["price_type"].to_list() == ["Newer", "Older"]


def test_cached_market_price_table_loader_reuses_session_cache() -> None:
    calls: list[int] = []
    config = _dashboard_config()
    cache: GasModelSessionCache = {}

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        calls.append(len(calls) + 1)
        return pl.DataFrame({"price_type": [f"price-{calls[-1]}"]})

    first_load = cached_load_market_price_table(config, cache, reader=reader)
    cached_load = cached_load_market_price_table(config, cache, reader=reader)
    refreshed_load = cached_load_market_price_table(
        config,
        cache,
        reader=reader,
        refresh_token=1,
    )

    assert calls == [1, 2]
    assert not first_load.cache_hit
    assert cached_load.cache_hit
    assert not refreshed_load.cache_hit
    assert cached_load.dataframe is not None
    assert cached_load.dataframe["price_type"].to_list() == ["price-1"]
    assert refreshed_load.dataframe is not None
    assert refreshed_load.dataframe["price_type"].to_list() == ["price-2"]


def test_market_price_summaries_filters_and_context_links() -> None:
    sttm_table = "silver.sttm.silver_int651_v1_ex_ante_market_price_rpt_1"
    vicgas_table = "silver.vicgas.silver_int042_v4_weighted_average_daily_prices_1"
    load = _market_price_load(
        pl.DataFrame(
            {
                "gas_date": ["2024-01-02", "2024-01-01", "2024-01-02"],
                "source_system": ["STTM", "STTM", "VICGAS"],
                "source_table": [sttm_table, sttm_table, vicgas_table],
                "price_type": [
                    "ex_ante_market_price",
                    "ex_ante_market_price",
                    "weighted_average_daily",
                ],
                "schedule_type_id": ["ex_ante", "ex_ante", None],
                "schedule_interval": ["1", "2", None],
                "transmission_id": ["run-2", "run-1", None],
                "source_location_id": ["SYD", "SYD", "VIC"],
                "price_value_gst_ex": [12.0, 10.0, None],
                "weighted_average_price_gst_ex": [None, None, 9.5],
                "cumulative_price": [None, None, None],
                "administered_price": [None, 20.0, None],
                "source_last_updated_timestamp": [
                    "2024-01-02 06:00:00",
                    "2024-01-01 06:00:00",
                    "2024-01-02 05:00:00",
                ],
                "ingested_timestamp": [
                    datetime(2024, 1, 2, 8),
                    datetime(2024, 1, 1, 8),
                    datetime(2024, 1, 2, 7),
                ],
            }
        )
    )

    observations = market_price_observation_frame(
        load,
        "ex_ante_market_price",
        "STTM",
    )
    kpis = market_price_kpi_frame(load)
    type_summary = market_price_type_summary_frame(load)
    trend = market_price_trend_frame(load)
    context_links = render_market_price_context_links()
    vicgas_observations = market_price_observation_frame(
        load,
        source_table_filter=vicgas_table,
    )

    assert market_price_price_type_options(load) == (
        MARKET_PRICE_PRICE_TYPE_FILTER_ALL,
        "ex_ante_market_price",
        "weighted_average_daily",
    )
    assert market_price_source_system_options(load) == (
        MARKET_PRICE_SOURCE_SYSTEM_FILTER_ALL,
        "STTM",
        "VICGAS",
    )
    assert market_price_source_table_options(load) == (
        MARKET_PRICE_SOURCE_TABLE_FILTER_ALL,
        sttm_table,
        vicgas_table,
    )
    assert observations.select(
        "gas date",
        "source system",
        "source table",
        "price type",
        "schedule type",
        "available price measures",
        "price_value_gst_ex",
        "administered_price",
    ).to_dict(as_series=False) == {
        "gas date": [date(2024, 1, 2), date(2024, 1, 1)],
        "source system": ["STTM", "STTM"],
        "source table": [sttm_table, sttm_table],
        "price type": ["ex_ante_market_price", "ex_ante_market_price"],
        "schedule type": ["ex_ante", "ex_ante"],
        "available price measures": [
            "price_value_gst_ex",
            "price_value_gst_ex, administered_price",
        ],
        "price_value_gst_ex": [12.0, 10.0],
        "administered_price": [None, 20.0],
    }
    assert kpis.to_dict(as_series=False) == {
        "metric": [
            "Loaded price rows",
            "Price types",
            "Source systems",
            "Source tables",
            "Latest gas date",
            "Available price measures",
        ],
        "value": ["3", "2", "2", "2", "2024-01-02", "3"],
        "detail": [
            "Full table scan",
            "Distinct price_type values in the current view",
            "Distinct source_system values in the current view",
            "Distinct source_table values represented",
            "Maximum gas_date in the loaded bounded rows",
            ("price_value_gst_ex, weighted_average_price_gst_ex, administered_price"),
        ],
    }
    assert type_summary.select(
        "source system",
        "source table",
        "price type",
        "observations",
        "latest gas date",
        "available price measures",
        "avg price_value_gst_ex",
    ).to_dict(as_series=False) == {
        "source system": ["STTM", "VICGAS"],
        "source table": [sttm_table, vicgas_table],
        "price type": ["ex_ante_market_price", "weighted_average_daily"],
        "observations": [2, 1],
        "latest gas date": [date(2024, 1, 2), date(2024, 1, 2)],
        "available price measures": [
            "price_value_gst_ex, administered_price",
            "weighted_average_price_gst_ex",
        ],
        "avg price_value_gst_ex": [11.0, None],
    }
    assert trend.select(
        "gas date",
        "source system",
        "price type",
        "observations",
        "available price measures",
    ).to_dict(as_series=False) == {
        "gas date": [date(2024, 1, 2), date(2024, 1, 2), date(2024, 1, 1)],
        "source system": ["STTM", "VICGAS", "STTM"],
        "price type": [
            "ex_ante_market_price",
            "weighted_average_daily",
            "ex_ante_market_price",
        ],
        "observations": [1, 1, 1],
        "available price measures": [
            "price_value_gst_ex",
            "weighted_average_price_gst_ex",
            "price_value_gst_ex, administered_price",
        ],
    }
    assert vicgas_observations["source table"].to_list() == [vicgas_table]
    assert 'href="/marimo/gas_market_prices/"' in context_links
    assert 'href="/marimo/sample_energy_market/"' in context_links
    assert "Schedule Context" in context_links
    assert "Planned dashboard" in context_links


def test_market_price_helpers_cover_missing_data_and_filter_empty_state() -> None:
    empty_load = _market_price_load(
        pl.DataFrame(),
        row_limit=4,
    )
    populated_load = _market_price_load(
        pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 2)],
                "source_system": ["STTM"],
                "source_table": ["silver.sttm.market_price"],
                "price_type": ["ex_ante_market_price"],
                "price_value_gst_ex": [12.0],
            }
        )
    )
    missing_date_load = _market_price_load(
        pl.DataFrame(
            {
                "source_system": ["STTM"],
                "source_table": ["silver.sttm.market_price"],
                "price_type": ["ex_ante_market_price"],
                "price_value_gst_ex": [12.0],
            }
        )
    )
    no_measure_load = _market_price_load(
        pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 2)],
                "source_system": ["STTM"],
                "source_table": ["silver.sttm.market_price"],
                "price_type": ["ex_ante_market_price"],
            }
        )
    )
    error_load = GasTableLoad(
        spec=MARKET_PRICE_TABLE_SPEC,
        uri="s3://bucket/silver/gas_model/silver_gas_fact_market_price",
        dataframe=None,
        error="FileNotFoundError: no parquet files found",
        row_limit=4,
        load_duration_seconds=0.01,
        cache_hit=False,
    )

    assert market_price_kpi_frame(empty_load).is_empty()
    assert market_price_type_summary_frame(empty_load).is_empty()
    assert market_price_trend_frame(empty_load).is_empty()
    assert market_price_observation_frame(empty_load).is_empty()
    assert market_price_price_type_options(empty_load) == (
        MARKET_PRICE_PRICE_TYPE_FILTER_ALL,
    )
    assert market_price_kpi_frame(
        populated_load,
        source_system_filter="VICGAS",
    ).is_empty()
    assert market_price_kpi_frame(missing_date_load).row(4, named=True) == {
        "metric": "Latest gas date",
        "value": "unknown",
        "detail": "Maximum gas_date in the loaded bounded rows",
    }
    assert market_price_kpi_frame(no_measure_load).row(5, named=True) == {
        "metric": "Available price measures",
        "value": "0",
        "detail": "none",
    }

    empty_markdown = market_price_empty_state_markdown(empty_load)
    error_markdown = market_price_empty_state_markdown(error_load)
    filtered_markdown = market_price_empty_state_markdown(populated_load)
    missing_load_markdown = market_price_empty_state_markdown(None)
    empty_context_links = render_market_price_context_links(entries=())
    unmounted_entry = DashboardRegistryEntry(
        concept_id="gas-market-prices",
        title="Unmounted Prices",
        description="Available entry without a mounted notebook route.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.AVAILABLE,
        notebook_name=None,
        backing_assets=("silver.gas_model.silver_gas_fact_market_price",),
        generated_gold_paths=(),
        source_chunks=(),
    )
    unmounted_context_links = render_market_price_context_links(
        entries=(unmounted_entry,)
    )

    assert "No market price data is available" in empty_markdown
    assert "silver.gas_model.silver_gas_fact_market_price" in empty_markdown
    assert "Bounded preview reads are capped at `4` rows per table" in empty_markdown
    assert "FileNotFoundError: no parquet files found" in error_markdown
    assert "current filters do not match" in filtered_markdown
    assert "did not receive a market price load result" in missing_load_markdown
    assert "No Market price or Schedule context entries" in empty_context_links
    assert "Unavailable dashboard" in unmounted_context_links


def test_schedule_run_table_loader_uses_bounded_recent_view() -> None:
    captured: list[int | None] = []
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "9",
        }
    )

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured.append(row_limit)
        assert uri == (
            "s3://prod-energy-market-aemo/silver/gas_model/silver_gas_fact_schedule_run"
        )
        assert storage_options == config.storage_options()
        return pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 1), date(2024, 1, 3)],
                "schedule_type_id": ["Older", "Newer"],
                "approval_timestamp": [
                    datetime(2024, 1, 1, 6),
                    datetime(2024, 1, 3, 6),
                ],
            }
        )

    load = load_schedule_run_table(config, reader=reader)

    assert captured == [9]
    assert load.spec == SCHEDULE_RUN_TABLE_SPEC
    assert load.row_limit == 9
    assert load.dataframe is not None
    assert load.dataframe["schedule_type_id"].to_list() == ["Newer", "Older"]


def test_cached_schedule_run_table_loader_reuses_session_cache() -> None:
    calls: list[int] = []
    config = _dashboard_config()
    cache: GasModelSessionCache = {}

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        calls.append(len(calls) + 1)
        return pl.DataFrame({"schedule_type_id": [f"schedule-{calls[-1]}"]})

    first_load = cached_load_schedule_run_table(config, cache, reader=reader)
    cached_load = cached_load_schedule_run_table(config, cache, reader=reader)
    refreshed_load = cached_load_schedule_run_table(
        config,
        cache,
        reader=reader,
        refresh_token=1,
    )

    assert calls == [1, 2]
    assert not first_load.cache_hit
    assert cached_load.cache_hit
    assert not refreshed_load.cache_hit
    assert cached_load.dataframe is not None
    assert cached_load.dataframe["schedule_type_id"].to_list() == ["schedule-1"]
    assert refreshed_load.dataframe is not None
    assert refreshed_load.dataframe["schedule_type_id"].to_list() == ["schedule-2"]


def test_schedule_run_summaries_filters_and_context_links() -> None:
    sttm_table = "silver.sttm.silver_int668_v1_schedule_log_rpt_1"
    vicgas_table = "silver.vicgas.silver_int108_v4_scheduled_run_log_7_1"
    load = _schedule_run_load(
        pl.DataFrame(
            {
                "gas_date": ["2024-01-03", "2024-01-02", "2024-01-03"],
                "source_system": ["STTM", "STTM", "VICGAS"],
                "source_table": [sttm_table, sttm_table, vicgas_table],
                "schedule_type_id": ["ex_ante", "provisional", "pricing"],
                "forecast_demand_version": ["D-1", "D-2", "V1"],
                "demand_type_id": [None, None, "daily"],
                "transmission_id": ["S-2", "S-1", "V-1"],
                "transmission_document_id": ["S-2", "S-1", "VDOC-1"],
                "transmission_group_id": ["SYD", "ADL", "VIC"],
                "objective_function_value": [None, None, 42.25],
                "gas_start_timestamp": [
                    "2024-01-03 00:00:00",
                    "2024-01-02 00:00:00",
                    "2024-01-03 06:00:00",
                ],
                "bid_cutoff_timestamp": [
                    "2024-01-02 12:00:00",
                    "2024-01-01 12:00:00",
                    "2024-01-03 03:00:00",
                ],
                "creation_timestamp": [
                    "2024-01-02 13:00:00",
                    "2024-01-01 13:00:00",
                    "2024-01-03 04:00:00",
                ],
                "approval_timestamp": [
                    "2024-01-02 14:00:00",
                    "2024-01-01 14:00:00",
                    "2024-01-03 09:00:00",
                ],
                "source_last_updated_timestamp": [
                    "2024-01-02 15:00:00",
                    "2024-01-01 15:00:00",
                    "2024-01-03 10:00:00",
                ],
                "ingested_timestamp": [
                    datetime(2024, 1, 2, 16),
                    datetime(2024, 1, 1, 16),
                    datetime(2024, 1, 3, 11),
                ],
            }
        )
    )

    observations = schedule_run_observation_frame(
        load,
        "2024-01-03",
        "STTM",
        "ex_ante",
    )
    kpis = schedule_run_kpi_frame(load)
    type_summary = schedule_run_type_summary_frame(load)
    timestamp_summary = schedule_run_timestamp_summary_frame(load)
    source_coverage = schedule_run_source_coverage_frame(load)
    context_links = render_schedule_run_context_links()

    assert schedule_run_gas_date_options(load) == (
        SCHEDULE_RUN_GAS_DATE_FILTER_ALL,
        "2024-01-03",
        "2024-01-02",
    )
    assert schedule_run_source_system_options(load) == (
        SCHEDULE_RUN_SOURCE_SYSTEM_FILTER_ALL,
        "STTM",
        "VICGAS",
    )
    assert schedule_run_schedule_type_options(load) == (
        SCHEDULE_RUN_SCHEDULE_TYPE_FILTER_ALL,
        "ex_ante",
        "pricing",
        "provisional",
    )
    assert kpis.to_dict(as_series=False) == {
        "metric": [
            "Loaded schedule runs",
            "Schedule types",
            "Source systems",
            "Transmissions",
            "Forecast demand versions",
            "Latest gas date",
            "Latest approval",
        ],
        "value": [
            "3",
            "3",
            "2",
            "3",
            "3",
            "2024-01-03",
            "2024-01-03 09:00:00",
        ],
        "detail": [
            "Full table scan",
            "Distinct schedule_type_id values in the current view",
            "Distinct source_system values in the current view",
            "Distinct transmission_id values in the current view",
            "Distinct forecast_demand_version values represented",
            "Maximum gas_date in the loaded bounded rows",
            "Maximum approval_timestamp in the current view",
        ],
    }
    assert observations.select(
        "gas date",
        "source system",
        "source table",
        "schedule type",
        "forecast demand version",
        "transmission",
        "transmission document",
        "approved",
    ).to_dict(as_series=False) == {
        "gas date": [date(2024, 1, 3)],
        "source system": ["STTM"],
        "source table": [sttm_table],
        "schedule type": ["ex_ante"],
        "forecast demand version": ["D-1"],
        "transmission": ["S-2"],
        "transmission document": ["S-2"],
        "approved": [datetime(2024, 1, 2, 14)],
    }
    assert type_summary.select(
        "source system",
        "source table",
        "schedule type",
        "forecast demand version",
        "runs",
        "transmissions",
        "latest gas date",
    ).to_dict(as_series=False) == {
        "source system": ["STTM", "VICGAS", "STTM"],
        "source table": [sttm_table, vicgas_table, sttm_table],
        "schedule type": ["ex_ante", "pricing", "provisional"],
        "forecast demand version": ["D-1", "V1", "D-2"],
        "runs": [1, 1, 1],
        "transmissions": [1, 1, 1],
        "latest gas date": [date(2024, 1, 3), date(2024, 1, 3), date(2024, 1, 2)],
    }
    assert timestamp_summary.select(
        "gas date",
        "source system",
        "schedule type",
        "runs",
        "latest approval",
    ).to_dict(as_series=False) == {
        "gas date": [date(2024, 1, 3), date(2024, 1, 3), date(2024, 1, 2)],
        "source system": ["STTM", "VICGAS", "STTM"],
        "schedule type": ["ex_ante", "pricing", "provisional"],
        "runs": [1, 1, 1],
        "latest approval": [
            datetime(2024, 1, 2, 14),
            datetime(2024, 1, 3, 9),
            datetime(2024, 1, 1, 14),
        ],
    }
    assert source_coverage.select(
        "source system",
        "source table",
        "schedule runs",
        "schedule types",
        "forecast demand versions",
        "latest gas date",
    ).to_dict(as_series=False) == {
        "source system": ["STTM", "VICGAS"],
        "source table": [sttm_table, vicgas_table],
        "schedule runs": [2, 1],
        "schedule types": [2, 1],
        "forecast demand versions": [2, 1],
        "latest gas date": [date(2024, 1, 3), date(2024, 1, 3)],
    }
    assert 'href="/marimo/gas_schedule_runs/"' in context_links
    assert "Schedule Context" in context_links
    assert "Settlement Context" in context_links
    assert "Gas Day Context" in context_links


def test_schedule_run_helpers_cover_missing_data_and_filter_empty_state() -> None:
    empty_load = _schedule_run_load(pl.DataFrame(), row_limit=5)
    populated_load = _schedule_run_load(
        pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 3)],
                "source_system": ["STTM"],
                "source_table": ["silver.sttm.schedule_log"],
                "schedule_type_id": ["ex_ante"],
                "forecast_demand_version": ["D-1"],
                "transmission_id": ["S-2"],
            }
        )
    )
    missing_date_load = _schedule_run_load(
        pl.DataFrame(
            {
                "source_system": ["STTM"],
                "source_table": ["silver.sttm.schedule_log"],
                "schedule_type_id": ["ex_ante"],
            }
        )
    )
    error_load = GasTableLoad(
        spec=SCHEDULE_RUN_TABLE_SPEC,
        uri="s3://bucket/silver/gas_model/silver_gas_fact_schedule_run",
        dataframe=None,
        error="FileNotFoundError: no parquet files found",
        row_limit=5,
        load_duration_seconds=0.01,
        cache_hit=False,
    )

    assert schedule_run_kpi_frame(empty_load).is_empty()
    assert schedule_run_type_summary_frame(empty_load).is_empty()
    assert schedule_run_timestamp_summary_frame(empty_load).is_empty()
    assert schedule_run_source_coverage_frame(empty_load).is_empty()
    assert schedule_run_observation_frame(empty_load).is_empty()
    assert schedule_run_gas_date_options(empty_load) == (
        SCHEDULE_RUN_GAS_DATE_FILTER_ALL,
    )
    assert schedule_run_source_system_options(empty_load) == (
        SCHEDULE_RUN_SOURCE_SYSTEM_FILTER_ALL,
    )
    assert schedule_run_schedule_type_options(empty_load) == (
        SCHEDULE_RUN_SCHEDULE_TYPE_FILTER_ALL,
    )
    assert schedule_run_kpi_frame(
        populated_load,
        gas_date_filter="2024-01-04",
    ).is_empty()
    assert schedule_run_kpi_frame(missing_date_load).row(5, named=True) == {
        "metric": "Latest gas date",
        "value": "unknown",
        "detail": "Maximum gas_date in the loaded bounded rows",
    }

    empty_markdown = schedule_run_empty_state_markdown(empty_load)
    error_markdown = schedule_run_empty_state_markdown(error_load)
    filtered_markdown = schedule_run_empty_state_markdown(populated_load)
    missing_load_markdown = schedule_run_empty_state_markdown(None)
    empty_context_links = render_schedule_run_context_links(entries=())
    unmounted_entry = DashboardRegistryEntry(
        concept_id="gas-schedule-runs",
        title="Unmounted Schedule Runs",
        description="Available entry without a mounted notebook route.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.AVAILABLE,
        notebook_name=None,
        backing_assets=("silver.gas_model.silver_gas_fact_schedule_run",),
        generated_gold_paths=(),
        source_chunks=(),
    )
    unmounted_context_links = render_schedule_run_context_links(
        entries=(unmounted_entry,)
    )

    assert "No schedule run data is available" in empty_markdown
    assert "silver.gas_model.silver_gas_fact_schedule_run" in empty_markdown
    assert "Bounded preview reads are capped at `5` rows per table" in empty_markdown
    assert "FileNotFoundError: no parquet files found" in error_markdown
    assert "current filters do not match" in filtered_markdown
    assert "did not receive a schedule run load result" in missing_load_markdown
    assert "No Schedule, Gas Day, or Settlement context entries" in empty_context_links
    assert "Unavailable dashboard" in unmounted_context_links


def test_settlement_activity_table_loader_uses_bounded_recent_view() -> None:
    captured: list[int | None] = []
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "10",
        }
    )

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured.append(row_limit)
        assert uri == (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_settlement_activity"
        )
        assert storage_options == config.storage_options()
        return pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 1), date(2024, 1, 3)],
                "activity_type": ["older", "newer"],
            }
        )

    load = load_settlement_activity_table(config, reader=reader)

    assert captured == [10]
    assert load.spec == SETTLEMENT_ACTIVITY_TABLE_SPEC
    assert load.row_limit == 10
    assert load.dataframe is not None
    assert load.dataframe["activity_type"].to_list() == ["newer", "older"]


def test_cached_settlement_activity_table_loader_reuses_session_cache() -> None:
    calls: list[int] = []
    config = _dashboard_config()
    cache: GasModelSessionCache = {}

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        calls.append(len(calls) + 1)
        return pl.DataFrame({"activity_type": [f"activity-{calls[-1]}"]})

    first_load = cached_load_settlement_activity_table(config, cache, reader=reader)
    cached_load = cached_load_settlement_activity_table(config, cache, reader=reader)
    refreshed_load = cached_load_settlement_activity_table(
        config,
        cache,
        reader=reader,
        refresh_token=1,
    )

    assert calls == [1, 2]
    assert not first_load.cache_hit
    assert cached_load.cache_hit
    assert not refreshed_load.cache_hit
    assert cached_load.dataframe is not None
    assert cached_load.dataframe["activity_type"].to_list() == ["activity-1"]
    assert refreshed_load.dataframe is not None
    assert refreshed_load.dataframe["activity_type"].to_list() == ["activity-2"]


def test_settlement_activity_summaries_filters_and_context_links() -> None:
    int312_table = "silver.vicgas.silver_int312_v4_settlements_activity_1"
    int322_table = "silver.vicgas.silver_int322a_v4_uplift_breakdown_sett_1"
    sttm_table = "silver.sttm.synthetic_settlement_activity"
    load = _settlement_activity_load(
        pl.DataFrame(
            {
                "gas_date": ["2024-01-03", "2024-01-02", "2024-01-03"],
                "source_system": ["VICGAS", "VICGAS", "STTM"],
                "source_table": [int312_table, int322_table, sttm_table],
                "settlement_version_id": [None, "V1", "V2"],
                "activity_type": [
                    "settlements_activity",
                    "uplift_breakdown_settlement",
                    "monthly_cumulative_imbalance_position_long",
                ],
                "schedule_no": [None, "SCH-1", None],
                "network_name": [None, None, "DWGM"],
                "participant_name": [None, None, "Participant One"],
                "amount_gst_ex": [100.0, 50.0, None],
                "quantity_gj": [20.0, None, None],
                "percentage": [2.5, None, None],
                "source_last_updated_timestamp": [
                    "2024-01-03 01:00:00",
                    "2024-01-02 01:00:00",
                    "2024-01-03 02:00:00",
                ],
                "source_file": ["int312.csv", "int322.csv", "sttm.csv"],
                "source_surrogate_key": ["src-312", "src-322", "src-sttm"],
                "ingested_timestamp": [
                    datetime(2024, 1, 3, 3),
                    datetime(2024, 1, 2, 3),
                    datetime(2024, 1, 3, 4),
                ],
            }
        )
    )

    observations = settlement_activity_observation_frame(
        load,
        "2024-01-03",
        "VICGAS",
        "settlements_activity",
    )
    kpis = settlement_activity_kpi_frame(load)
    summary = settlement_activity_summary_frame(load)
    source_coverage = settlement_activity_source_coverage_frame(load)
    context_links = render_settlement_activity_context_links()

    assert settlement_activity_gas_date_options(load) == (
        SETTLEMENT_ACTIVITY_GAS_DATE_FILTER_ALL,
        "2024-01-03",
        "2024-01-02",
    )
    assert settlement_activity_source_system_options(load) == (
        SETTLEMENT_ACTIVITY_SOURCE_SYSTEM_FILTER_ALL,
        "STTM",
        "VICGAS",
    )
    assert settlement_activity_activity_type_options(load) == (
        SETTLEMENT_ACTIVITY_ACTIVITY_TYPE_FILTER_ALL,
        "monthly_cumulative_imbalance_position_long",
        "settlements_activity",
        "uplift_breakdown_settlement",
    )
    assert kpis.to_dict(as_series=False) == {
        "metric": [
            "Loaded settlement activity rows",
            "Activity types",
            "Source systems",
            "Settlement versions",
            "Schedules",
            "Networks",
            "Participants",
            "Amount GST ex",
            "Quantity",
            "Percentage range",
            "Latest gas date",
        ],
        "value": [
            "3",
            "3",
            "2",
            "2",
            "1",
            "1",
            "1",
            "150",
            "20 GJ",
            "2.5 to 2.5",
            "2024-01-03",
        ],
        "detail": [
            "Full table scan",
            "Distinct activity_type values in the current view",
            "Distinct source_system values in the current view",
            "Distinct settlement_version_id values represented",
            "Distinct schedule_no values represented",
            "Distinct network_name values represented",
            "Distinct participant_name values represented",
            "2 populated amount_gst_ex rows",
            "1 populated quantity_gj rows",
            "1 populated percentage rows",
            "Maximum gas_date in the loaded bounded rows",
        ],
    }
    assert observations.select(
        "gas date",
        "source system",
        "source table",
        "settlement version",
        "activity type",
        "schedule",
        "network",
        "participant",
        "amount_gst_ex",
        "quantity_gj",
        "percentage",
        "source identifier",
    ).to_dict(as_series=False) == {
        "gas date": [date(2024, 1, 3)],
        "source system": ["VICGAS"],
        "source table": [int312_table],
        "settlement version": [None],
        "activity type": ["settlements_activity"],
        "schedule": [None],
        "network": [None],
        "participant": [None],
        "amount_gst_ex": [100.0],
        "quantity_gj": [20.0],
        "percentage": [2.5],
        "source identifier": ["src-312"],
    }
    assert summary.select(
        "source system",
        "source table",
        "activity type",
        "settlement version",
        "rows",
        "schedules",
        "networks",
        "participants",
        "total amount gst ex",
        "total quantity gj",
        "avg percentage",
    ).to_dict(as_series=False) == {
        "source system": ["STTM", "VICGAS", "VICGAS"],
        "source table": [sttm_table, int312_table, int322_table],
        "activity type": [
            "monthly_cumulative_imbalance_position_long",
            "settlements_activity",
            "uplift_breakdown_settlement",
        ],
        "settlement version": ["V2", None, "V1"],
        "rows": [1, 1, 1],
        "schedules": [0, 0, 1],
        "networks": [1, 0, 0],
        "participants": [1, 0, 0],
        "total amount gst ex": [0.0, 100.0, 50.0],
        "total quantity gj": [0.0, 20.0, 0.0],
        "avg percentage": [None, 2.5, None],
    }
    assert source_coverage.select(
        "source system",
        "source table",
        "rows",
        "activity types",
        "settlement versions",
        "amount rows",
        "quantity rows",
        "percentage rows",
        "source files",
    ).to_dict(as_series=False) == {
        "source system": ["STTM", "VICGAS", "VICGAS"],
        "source table": [sttm_table, int312_table, int322_table],
        "rows": [1, 1, 1],
        "activity types": [1, 1, 1],
        "settlement versions": [1, 0, 1],
        "amount rows": [0, 1, 1],
        "quantity rows": [0, 1, 0],
        "percentage rows": [0, 1, 0],
        "source files": [1, 1, 1],
    }
    assert 'href="/marimo/gas_settlement_activity/"' in context_links
    assert "Settlement Context" in context_links
    assert "Allocation Context" in context_links
    assert "Participant Context" in context_links
    assert "Gas Day Context" in context_links


def test_settlement_activity_helpers_cover_missing_data_and_filter_empty_state() -> (
    None
):
    empty_load = _settlement_activity_load(pl.DataFrame(), row_limit=5)
    populated_load = _settlement_activity_load(
        pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 3)],
                "source_system": ["VICGAS"],
                "source_table": ["silver.vicgas.settlement_activity"],
                "activity_type": ["settlements_activity"],
                "amount_gst_ex": [100.0],
            }
        )
    )
    missing_date_load = _settlement_activity_load(
        pl.DataFrame(
            {
                "source_system": ["VICGAS"],
                "source_table": ["silver.vicgas.settlement_activity"],
                "activity_type": ["settlements_activity"],
                "amount_gst_ex": [100.0],
            }
        )
    )
    no_measure_load = _settlement_activity_load(
        pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 3)],
                "source_system": ["VICGAS"],
                "activity_type": ["settlements_activity"],
            }
        )
    )
    error_load = GasTableLoad(
        spec=SETTLEMENT_ACTIVITY_TABLE_SPEC,
        uri="s3://bucket/silver/gas_model/silver_gas_fact_settlement_activity",
        dataframe=None,
        error="FileNotFoundError: no parquet files found",
        row_limit=5,
        load_duration_seconds=0.01,
        cache_hit=False,
    )

    assert settlement_activity_kpi_frame(empty_load).is_empty()
    assert settlement_activity_summary_frame(empty_load).is_empty()
    assert settlement_activity_source_coverage_frame(empty_load).is_empty()
    assert settlement_activity_observation_frame(empty_load).is_empty()
    assert settlement_activity_gas_date_options(empty_load) == (
        SETTLEMENT_ACTIVITY_GAS_DATE_FILTER_ALL,
    )
    assert settlement_activity_source_system_options(empty_load) == (
        SETTLEMENT_ACTIVITY_SOURCE_SYSTEM_FILTER_ALL,
    )
    assert settlement_activity_activity_type_options(empty_load) == (
        SETTLEMENT_ACTIVITY_ACTIVITY_TYPE_FILTER_ALL,
    )
    assert settlement_activity_kpi_frame(
        populated_load,
        gas_date_filter="2024-01-04",
    ).is_empty()
    assert settlement_activity_kpi_frame(missing_date_load).row(10, named=True) == {
        "metric": "Latest gas date",
        "value": "unknown",
        "detail": "Maximum gas_date in the loaded bounded rows",
    }
    assert settlement_activity_kpi_frame(no_measure_load).row(7, named=True) == {
        "metric": "Amount GST ex",
        "value": "unknown",
        "detail": "0 populated amount_gst_ex rows",
    }

    empty_markdown = settlement_activity_empty_state_markdown(empty_load)
    error_markdown = settlement_activity_empty_state_markdown(error_load)
    filtered_markdown = settlement_activity_empty_state_markdown(populated_load)
    missing_load_markdown = settlement_activity_empty_state_markdown(None)
    empty_context_links = render_settlement_activity_context_links(entries=())
    unmounted_entry = DashboardRegistryEntry(
        concept_id="settlement-context",
        title="Unmounted Settlement",
        description="Available entry without a mounted notebook route.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.AVAILABLE,
        notebook_name=None,
        backing_assets=("silver.gas_model.silver_gas_fact_settlement_activity",),
        generated_gold_paths=(),
        source_chunks=(),
    )
    unmounted_context_links = render_settlement_activity_context_links(
        entries=(unmounted_entry,)
    )

    assert "No settlement activity data is available" in empty_markdown
    assert "silver.gas_model.silver_gas_fact_settlement_activity" in empty_markdown
    assert "Bounded preview reads are capped at `5` rows per table" in empty_markdown
    assert "FileNotFoundError: no parquet files found" in error_markdown
    assert "current filters do not match" in filtered_markdown
    assert "did not receive a settlement activity load result" in missing_load_markdown
    assert "No Settlement, Allocation, Participant, Gas Day, or Schedule" in (
        empty_context_links
    )
    assert "Unavailable dashboard" in unmounted_context_links


def test_customer_transfer_table_loader_uses_bounded_recent_view() -> None:
    captured: list[int | None] = []
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "12",
        }
    )

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured.append(row_limit)
        assert uri == (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_customer_transfer"
        )
        assert storage_options == config.storage_options()
        return pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 1), date(2024, 1, 3)],
                "market_code": ["older", "newer"],
            }
        )

    load = load_customer_transfer_table(config, reader=reader)

    assert captured == [12]
    assert load.spec == CUSTOMER_TRANSFER_TABLE_SPEC
    assert load.row_limit == 12
    assert load.dataframe is not None
    assert load.dataframe["market_code"].to_list() == ["newer", "older"]


def test_cached_customer_transfer_table_loader_reuses_session_cache() -> None:
    calls: list[int] = []
    config = _dashboard_config()
    cache: GasModelSessionCache = {}

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        calls.append(len(calls) + 1)
        return pl.DataFrame({"market_code": [f"market-{calls[-1]}"]})

    first_load = cached_load_customer_transfer_table(config, cache, reader=reader)
    cached_load = cached_load_customer_transfer_table(config, cache, reader=reader)
    refreshed_load = cached_load_customer_transfer_table(
        config,
        cache,
        reader=reader,
        refresh_token=1,
    )

    assert calls == [1, 2]
    assert not first_load.cache_hit
    assert cached_load.cache_hit
    assert not refreshed_load.cache_hit
    assert cached_load.dataframe is not None
    assert cached_load.dataframe["market_code"].to_list() == ["market-1"]
    assert refreshed_load.dataframe is not None
    assert refreshed_load.dataframe["market_code"].to_list() == ["market-2"]


def test_customer_transfer_summaries_filters_and_context_links() -> None:
    int311_table = "silver.vicgas.silver_int311_v5_customer_transfers_1"
    load = _customer_transfer_load(
        pl.DataFrame(
            {
                "gas_date": ["2024-01-03", "2024-01-02", "2024-01-03"],
                "market_code": ["VIC", "VIC", "NSW"],
                "source_system": ["VICGAS", "VICGAS", "VICGAS"],
                "source_table": [int311_table, int311_table, int311_table],
                "transfers_lodged": [10, 5, 3],
                "transfers_completed": [8, 4, 1],
                "transfers_cancelled": [2, 1, 0],
                "int_transfers_lodged": [1, 2, 0],
                "int_transfers_completed": [1, 1, 0],
                "int_transfers_cancelled": [0, 1, 0],
                "greenfields_received": [7, 4, 2],
                "source_surrogate_key": ["src-vic-1", "src-vic-2", "src-nsw-1"],
                "source_file": ["int311-a.csv", "int311-b.csv", "int311-a.csv"],
                "ingested_timestamp": [
                    datetime(2024, 1, 3, 3),
                    datetime(2024, 1, 2, 3),
                    datetime(2024, 1, 3, 4),
                ],
            }
        )
    )

    observations = customer_transfer_observation_frame(
        load,
        "2024-01-03",
        "VIC",
        "VICGAS",
    )
    kpis = customer_transfer_kpi_frame(load)
    summary = customer_transfer_summary_frame(load)
    daily = customer_transfer_daily_frame(load)
    source_coverage = customer_transfer_source_coverage_frame(load)
    context_links = render_customer_transfer_context_links()

    assert customer_transfer_gas_date_options(load) == (
        CUSTOMER_TRANSFER_GAS_DATE_FILTER_ALL,
        "2024-01-03",
        "2024-01-02",
    )
    assert customer_transfer_market_code_options(load) == (
        CUSTOMER_TRANSFER_MARKET_CODE_FILTER_ALL,
        "NSW",
        "VIC",
    )
    assert customer_transfer_source_system_options(load) == (
        CUSTOMER_TRANSFER_SOURCE_SYSTEM_FILTER_ALL,
        "VICGAS",
    )
    assert kpis.to_dict(as_series=False) == {
        "metric": [
            "Loaded customer transfer rows",
            "Market codes",
            "Source systems",
            "Transfers lodged",
            "Transfers completed",
            "Transfers cancelled",
            "Internal transfers lodged",
            "Internal transfers completed",
            "Internal transfers cancelled",
            "Greenfields received",
            "Latest gas date",
        ],
        "value": ["3", "2", "1", "18", "13", "3", "3", "2", "1", "13", "2024-01-03"],
        "detail": [
            "Full table scan",
            "Distinct market_code values in the current view",
            "Distinct source_system values in the current view",
            "3 populated transfers_lodged rows",
            "3 populated transfers_completed rows",
            "3 populated transfers_cancelled rows",
            "3 populated int_transfers_lodged rows",
            "3 populated int_transfers_completed rows",
            "3 populated int_transfers_cancelled rows",
            "3 populated greenfields_received rows",
            "Maximum gas_date in the loaded bounded rows",
        ],
    }
    assert observations.select(
        "gas date",
        "market code",
        "source system",
        "source table",
        "transfers_lodged",
        "transfers_completed",
        "transfers_cancelled",
        "int_transfers_lodged",
        "greenfields_received",
        "source identifier",
    ).to_dict(as_series=False) == {
        "gas date": [date(2024, 1, 3)],
        "market code": ["VIC"],
        "source system": ["VICGAS"],
        "source table": [int311_table],
        "transfers_lodged": [10],
        "transfers_completed": [8],
        "transfers_cancelled": [2],
        "int_transfers_lodged": [1],
        "greenfields_received": [7],
        "source identifier": ["src-vic-1"],
    }
    assert summary.select(
        "market code",
        "source system",
        "source table",
        "rows",
        "gas days",
        "transfers lodged",
        "transfers completed",
        "transfers cancelled",
        "internal transfers lodged",
        "greenfields received",
        "latest gas date",
    ).to_dict(as_series=False) == {
        "market code": ["VIC", "NSW"],
        "source system": ["VICGAS", "VICGAS"],
        "source table": [int311_table, int311_table],
        "rows": [2, 1],
        "gas days": [2, 1],
        "transfers lodged": [15, 3],
        "transfers completed": [12, 1],
        "transfers cancelled": [3, 0],
        "internal transfers lodged": [3, 0],
        "greenfields received": [11, 2],
        "latest gas date": [date(2024, 1, 3), date(2024, 1, 3)],
    }
    assert daily.select(
        "gas date",
        "market code",
        "transfers lodged",
        "transfers completed",
        "transfers cancelled",
        "internal transfers lodged",
        "greenfields received",
    ).to_dict(as_series=False) == {
        "gas date": [date(2024, 1, 3), date(2024, 1, 3), date(2024, 1, 2)],
        "market code": ["NSW", "VIC", "VIC"],
        "transfers lodged": [3, 10, 5],
        "transfers completed": [1, 8, 4],
        "transfers cancelled": [0, 2, 1],
        "internal transfers lodged": [0, 1, 2],
        "greenfields received": [2, 7, 4],
    }
    assert source_coverage.select(
        "source system",
        "source table",
        "rows",
        "market codes",
        "gas days",
        "source files",
        "source identifiers",
    ).to_dict(as_series=False) == {
        "source system": ["VICGAS"],
        "source table": [int311_table],
        "rows": [3],
        "market codes": [2],
        "gas days": [2],
        "source files": [2],
        "source identifiers": [3],
    }
    assert 'href="/marimo/gas_customer_transfer_activity/"' in context_links
    assert "Customer Transfer And Retail Activity" in context_links
    assert "Participant Context" in context_links
    assert "Gas Day Context" in context_links
    assert "Settlement Context" in context_links


def test_customer_transfer_helpers_cover_missing_data_and_filter_empty_state() -> None:
    empty_load = _customer_transfer_load(pl.DataFrame(), row_limit=6)
    populated_load = _customer_transfer_load(
        pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 3)],
                "market_code": ["VIC"],
                "source_system": ["VICGAS"],
                "transfers_lodged": [10],
            }
        )
    )
    missing_date_load = _customer_transfer_load(
        pl.DataFrame(
            {
                "market_code": ["VIC"],
                "source_system": ["VICGAS"],
                "transfers_lodged": [10],
            }
        )
    )
    no_measure_load = _customer_transfer_load(
        pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 3)],
                "market_code": ["VIC"],
                "source_system": ["VICGAS"],
            }
        )
    )
    error_load = GasTableLoad(
        spec=CUSTOMER_TRANSFER_TABLE_SPEC,
        uri="s3://bucket/silver/gas_model/silver_gas_fact_customer_transfer",
        dataframe=None,
        error="FileNotFoundError: no parquet files found",
        row_limit=6,
        load_duration_seconds=0.01,
        cache_hit=False,
    )

    assert customer_transfer_kpi_frame(empty_load).is_empty()
    assert customer_transfer_summary_frame(empty_load).is_empty()
    assert customer_transfer_daily_frame(empty_load).is_empty()
    assert customer_transfer_source_coverage_frame(empty_load).is_empty()
    assert customer_transfer_observation_frame(empty_load).is_empty()
    assert customer_transfer_gas_date_options(empty_load) == (
        CUSTOMER_TRANSFER_GAS_DATE_FILTER_ALL,
    )
    assert customer_transfer_market_code_options(empty_load) == (
        CUSTOMER_TRANSFER_MARKET_CODE_FILTER_ALL,
    )
    assert customer_transfer_source_system_options(empty_load) == (
        CUSTOMER_TRANSFER_SOURCE_SYSTEM_FILTER_ALL,
    )
    assert customer_transfer_kpi_frame(
        populated_load,
        gas_date_filter="2024-01-04",
    ).is_empty()
    assert customer_transfer_kpi_frame(missing_date_load).row(10, named=True) == {
        "metric": "Latest gas date",
        "value": "unknown",
        "detail": "Maximum gas_date in the loaded bounded rows",
    }
    assert customer_transfer_kpi_frame(no_measure_load).row(3, named=True) == {
        "metric": "Transfers lodged",
        "value": "unknown",
        "detail": "0 populated transfers_lodged rows",
    }

    empty_markdown = customer_transfer_empty_state_markdown(empty_load)
    error_markdown = customer_transfer_empty_state_markdown(error_load)
    filtered_markdown = customer_transfer_empty_state_markdown(populated_load)
    missing_load_markdown = customer_transfer_empty_state_markdown(None)
    empty_context_links = render_customer_transfer_context_links(entries=())
    unmounted_entry = DashboardRegistryEntry(
        concept_id="gas-customer-transfer-activity",
        title="Unmounted Customer Transfer",
        description="Available entry without a mounted notebook route.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.AVAILABLE,
        notebook_name=None,
        backing_assets=("silver.gas_model.silver_gas_fact_customer_transfer",),
        generated_gold_paths=(),
        source_chunks=(),
    )
    unmounted_context_links = render_customer_transfer_context_links(
        entries=(unmounted_entry,)
    )

    assert "No customer transfer data is available" in empty_markdown
    assert "silver.gas_model.silver_gas_fact_customer_transfer" in empty_markdown
    assert "Bounded preview reads are capped at `6` rows per table" in empty_markdown
    assert "FileNotFoundError: no parquet files found" in error_markdown
    assert "current filters do not match" in filtered_markdown
    assert "did not receive a customer transfer load result" in missing_load_markdown
    assert "No Customer transfer, Participant, Gas Day, or Settlement" in (
        empty_context_links
    )
    assert "Unavailable dashboard" in unmounted_context_links


def test_bid_stack_table_loader_uses_bounded_recent_view() -> None:
    captured: list[int | None] = []
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "11",
        }
    )

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured.append(row_limit)
        assert uri == (
            "s3://prod-energy-market-aemo/silver/gas_model/silver_gas_fact_bid_stack"
        )
        assert storage_options == config.storage_options()
        return pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 1), date(2024, 1, 3)],
                "bid_id": ["older", "newer"],
            }
        )

    load = load_bid_stack_table(config, reader=reader)

    assert captured == [11]
    assert load.spec == BID_STACK_TABLE_SPEC
    assert load.row_limit == 11
    assert load.dataframe is not None
    assert load.dataframe["bid_id"].to_list() == ["newer", "older"]


def test_cached_bid_stack_table_loader_reuses_session_cache() -> None:
    calls: list[int] = []
    config = _dashboard_config()
    cache: GasModelSessionCache = {}

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        calls.append(len(calls) + 1)
        return pl.DataFrame({"bid_id": [f"bid-{calls[-1]}"]})

    first_load = cached_load_bid_stack_table(config, cache, reader=reader)
    cached_load = cached_load_bid_stack_table(config, cache, reader=reader)
    refreshed_load = cached_load_bid_stack_table(
        config,
        cache,
        reader=reader,
        refresh_token=1,
    )

    assert calls == [1, 2]
    assert not first_load.cache_hit
    assert cached_load.cache_hit
    assert not refreshed_load.cache_hit
    assert cached_load.dataframe is not None
    assert cached_load.dataframe["bid_id"].to_list() == ["bid-1"]
    assert refreshed_load.dataframe is not None
    assert refreshed_load.dataframe["bid_id"].to_list() == ["bid-2"]


def test_bid_stack_summaries_filters_and_context_links() -> None:
    sttm_table = "silver.sttm.silver_int659_v1_bid_offer_rpt_1"
    vicgas_table = "silver.vicgas.silver_int314_v4_bid_stack_1"
    load = _bid_stack_load(
        pl.DataFrame(
            {
                "gas_date": ["2024-01-03", "2024-01-03", "2024-01-02"],
                "source_system": ["STTM", "STTM", "VICGAS"],
                "source_table": [sttm_table, sttm_table, vicgas_table],
                "source_report_id": ["INT659", "INT659", "INT314"],
                "participant_id": ["P1", "P1", "V1"],
                "participant_name": ["Participant One", "Participant One", "Vic One"],
                "source_hub_id": ["SYD", "SYD", None],
                "source_hub_name": ["Sydney", "Sydney", None],
                "source_facility_id": ["FAC1", "FAC1", None],
                "facility_name": ["Pipeline A", "Pipeline A", None],
                "source_point_id": ["FAC1", "FAC1", "MIRN-A"],
                "schedule_identifier": ["SCH1", "SCH1", None],
                "bid_id": ["BID-1", "BID-1", "BID-2"],
                "bid_step": [1, 2, 1],
                "bid_price": [9.5, 12.0, 8.0],
                "bid_qty_gj": [100.0, 50.0, 30.0],
                "step_qty_gj": [None, None, 30.0],
                "offer_type": ["offer", "offer", "bid"],
                "inject_withdraw": [None, None, "withdraw"],
                "schedule_type": [None, None, "d-1"],
                "schedule_time": [None, None, "06:00"],
                "bid_cutoff_timestamp": [
                    None,
                    None,
                    "2024-01-01 13:00:00",
                ],
                "source_last_updated_timestamp": [
                    "2024-01-02 04:00:00",
                    "2024-01-02 05:00:00",
                    "2024-01-01 06:00:00",
                ],
                "source_surrogate_key": ["src-1", "src-2", "src-3"],
                "source_file": ["sttm.csv", "sttm.csv", "vicgas.csv"],
                "ingested_timestamp": [
                    datetime(2024, 1, 2, 6),
                    datetime(2024, 1, 2, 7),
                    datetime(2024, 1, 1, 7),
                ],
            }
        )
    )

    observations = bid_stack_observation_frame(
        load,
        "P1",
        "FAC1",
        "SYD",
        "STTM",
    )
    kpis = bid_stack_kpi_frame(load)
    step_summary = bid_stack_step_summary_frame(load)
    source_summary = bid_stack_source_summary_frame(load)
    context_links = render_bid_stack_context_links()

    assert bid_stack_participant_options(load) == (
        BID_STACK_PARTICIPANT_FILTER_ALL,
        "P1",
        "V1",
    )
    assert bid_stack_facility_options(load) == (
        BID_STACK_FACILITY_FILTER_ALL,
        "FAC1",
    )
    assert bid_stack_zone_options(load) == (
        BID_STACK_ZONE_FILTER_ALL,
        "SYD",
    )
    assert bid_stack_source_system_options(load) == (
        BID_STACK_SOURCE_SYSTEM_FILTER_ALL,
        "STTM",
        "VICGAS",
    )
    assert kpis.to_dict(as_series=False) == {
        "metric": [
            "Loaded bid stack rows",
            "Source systems",
            "Participants",
            "Facilities",
            "Zones",
            "Bid steps",
            "Bid price range",
            "Loaded bid quantity",
            "Accepted source identifiers",
            "Latest gas date",
        ],
        "value": ["3", "2", "2", "1", "1", "2", "8 to 12", "180 GJ", "3", "2024-01-03"],
        "detail": [
            "Full table scan",
            "Distinct source_system values in the current view",
            "Distinct participant_id values represented",
            "Distinct source_facility_id values represented",
            "Distinct source_hub_id values represented",
            "Distinct bid_step values represented",
            "Minimum and maximum bid_price in the current view",
            "Sum of bid_qty_gj in loaded bounded rows",
            "Distinct source_surrogate_key values represented",
            "Maximum gas_date in the loaded bounded rows",
        ],
    }
    assert step_summary.select(
        "source system",
        "zone",
        "facility",
        "bid step",
        "rows",
        "participants",
        "bid ids",
        "min bid price",
        "total bid quantity gj",
        "total step quantity gj",
        "latest gas date",
    ).to_dict(as_series=False) == {
        "source system": ["STTM", "STTM", "VICGAS"],
        "zone": ["SYD", "SYD", None],
        "facility": ["FAC1", "FAC1", None],
        "bid step": [1, 2, 1],
        "rows": [1, 1, 1],
        "participants": [1, 1, 1],
        "bid ids": [1, 1, 1],
        "min bid price": [9.5, 12.0, 8.0],
        "total bid quantity gj": [100.0, 50.0, 30.0],
        "total step quantity gj": [0.0, 0.0, 30.0],
        "latest gas date": [date(2024, 1, 3), date(2024, 1, 3), date(2024, 1, 2)],
    }
    assert source_summary.select(
        "source system",
        "source table",
        "source report",
        "rows",
        "participants",
        "facilities",
        "zones",
        "bid ids",
        "bid steps",
        "accepted source identifiers",
        "source files",
        "latest gas date",
    ).to_dict(as_series=False) == {
        "source system": ["STTM", "VICGAS"],
        "source table": [sttm_table, vicgas_table],
        "source report": ["INT659", "INT314"],
        "rows": [2, 1],
        "participants": [1, 1],
        "facilities": [1, 0],
        "zones": [1, 0],
        "bid ids": [1, 1],
        "bid steps": [2, 1],
        "accepted source identifiers": [2, 1],
        "source files": [1, 1],
        "latest gas date": [date(2024, 1, 3), date(2024, 1, 2)],
    }
    assert observations.select(
        "gas date",
        "source system",
        "source table",
        "source report",
        "participant",
        "zone",
        "facility",
        "bid id",
        "bid step",
        "bid price",
        "bid quantity gj",
        "accepted source identifier",
    ).to_dict(as_series=False) == {
        "gas date": [date(2024, 1, 3), date(2024, 1, 3)],
        "source system": ["STTM", "STTM"],
        "source table": [sttm_table, sttm_table],
        "source report": ["INT659", "INT659"],
        "participant": ["P1", "P1"],
        "zone": ["SYD", "SYD"],
        "facility": ["FAC1", "FAC1"],
        "bid id": ["BID-1", "BID-1"],
        "bid step": [2, 1],
        "bid price": [12.0, 9.5],
        "bid quantity gj": [50.0, 100.0],
        "accepted source identifier": ["src-2", "src-1"],
    }
    assert 'href="/marimo/gas_bid_offer_stack/"' in context_links
    assert "Bid / Offer" in context_links
    assert "Participant Context" in context_links
    assert "Facility Context" in context_links
    assert "Schedule Context" in context_links


def test_bid_stack_helpers_cover_missing_data_and_filter_empty_state() -> None:
    empty_load = _bid_stack_load(pl.DataFrame(), row_limit=4)
    populated_load = _bid_stack_load(
        pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 3)],
                "source_system": ["STTM"],
                "participant_id": ["P1"],
                "source_facility_id": ["FAC1"],
                "source_hub_id": ["SYD"],
                "bid_id": ["BID-1"],
                "bid_step": [1],
                "bid_price": [9.5],
                "bid_qty_gj": [100.0],
                "source_surrogate_key": ["src-1"],
            }
        )
    )
    missing_date_load = _bid_stack_load(
        pl.DataFrame(
            {
                "source_system": ["STTM"],
                "participant_id": ["P1"],
                "source_facility_id": ["FAC1"],
                "source_hub_id": ["SYD"],
                "bid_id": ["BID-1"],
                "bid_step": [1],
                "bid_price": [9.5],
                "bid_qty_gj": [100.0],
            }
        )
    )
    error_load = GasTableLoad(
        spec=BID_STACK_TABLE_SPEC,
        uri="s3://bucket/silver/gas_model/silver_gas_fact_bid_stack",
        dataframe=None,
        error="FileNotFoundError: no parquet files found",
        row_limit=4,
        load_duration_seconds=0.01,
        cache_hit=False,
    )

    assert bid_stack_kpi_frame(empty_load).is_empty()
    assert bid_stack_step_summary_frame(empty_load).is_empty()
    assert bid_stack_source_summary_frame(empty_load).is_empty()
    assert bid_stack_observation_frame(empty_load).is_empty()
    assert bid_stack_participant_options(empty_load) == (
        BID_STACK_PARTICIPANT_FILTER_ALL,
    )
    assert bid_stack_facility_options(empty_load) == (BID_STACK_FACILITY_FILTER_ALL,)
    assert bid_stack_zone_options(empty_load) == (BID_STACK_ZONE_FILTER_ALL,)
    assert bid_stack_source_system_options(empty_load) == (
        BID_STACK_SOURCE_SYSTEM_FILTER_ALL,
    )
    assert bid_stack_kpi_frame(
        populated_load,
        participant_filter="missing-participant",
    ).is_empty()
    assert bid_stack_kpi_frame(missing_date_load).row(9, named=True) == {
        "metric": "Latest gas date",
        "value": "unknown",
        "detail": "Maximum gas_date in the loaded bounded rows",
    }

    empty_markdown = bid_stack_empty_state_markdown(empty_load)
    error_markdown = bid_stack_empty_state_markdown(error_load)
    filtered_markdown = bid_stack_empty_state_markdown(populated_load)
    missing_load_markdown = bid_stack_empty_state_markdown(None)
    empty_context_links = render_bid_stack_context_links(entries=())
    unmounted_entry = DashboardRegistryEntry(
        concept_id="bid-offer-context",
        title="Unmounted Bid / Offer",
        description="Available entry without a mounted notebook route.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.AVAILABLE,
        notebook_name=None,
        backing_assets=("silver.gas_model.silver_gas_fact_bid_stack",),
        generated_gold_paths=(),
        source_chunks=(),
    )
    unmounted_context_links = render_bid_stack_context_links(entries=(unmounted_entry,))

    assert "No Bid / Offer stack data is available" in empty_markdown
    assert "silver.gas_model.silver_gas_fact_bid_stack" in empty_markdown
    assert "Bounded preview reads are capped at `4` rows per table" in empty_markdown
    assert "FileNotFoundError: no parquet files found" in error_markdown
    assert "current filters do not match" in filtered_markdown
    assert "did not receive a Bid / Offer stack load result" in missing_load_markdown
    assert "No Bid / Offer, Participant, Facility, or Schedule context" in (
        empty_context_links
    )
    assert "Unavailable dashboard" in unmounted_context_links


def test_gas_quality_table_loader_uses_bounded_recent_view() -> None:
    captured: list[int | None] = []
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "7",
        }
    )

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured.append(row_limit)
        assert uri == (
            "s3://prod-energy-market-aemo/silver/gas_model/silver_gas_fact_gas_quality"
        )
        assert storage_options == config.storage_options()
        return pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 1), date(2024, 1, 3)],
                "quality_type": ["Older", "Newer"],
            }
        )

    load = load_gas_quality_table(config, reader=reader)

    assert captured == [7]
    assert load.spec == GAS_QUALITY_TABLE_SPEC
    assert load.row_limit == 7
    assert load.dataframe is not None
    assert load.dataframe["quality_type"].to_list() == ["Newer", "Older"]


def test_cached_gas_quality_table_loader_reuses_session_cache() -> None:
    calls: list[int] = []
    config = _dashboard_config()
    cache: GasModelSessionCache = {}

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        calls.append(len(calls) + 1)
        return pl.DataFrame({"quality_type": [f"quality-{calls[-1]}"]})

    first_load = cached_load_gas_quality_table(config, cache, reader=reader)
    cached_load = cached_load_gas_quality_table(config, cache, reader=reader)
    refreshed_load = cached_load_gas_quality_table(
        config,
        cache,
        reader=reader,
        refresh_token=1,
    )

    assert calls == [1, 2]
    assert not first_load.cache_hit
    assert cached_load.cache_hit
    assert not refreshed_load.cache_hit
    assert cached_load.dataframe is not None
    assert cached_load.dataframe["quality_type"].to_list() == ["quality-1"]
    assert refreshed_load.dataframe is not None
    assert refreshed_load.dataframe["quality_type"].to_list() == ["quality-2"]


def test_gas_quality_summaries_filters_and_source_coverage() -> None:
    load = _gas_quality_load(
        pl.DataFrame(
            {
                "gas_date": [
                    "2024-01-02",
                    "2024-01-01",
                    "2024-01-01",
                ],
                "gas_interval": ["1", "2", None],
                "source_point_id": ["MIRN-A", "MIRN-B", "ZONE-1"],
                "point_name": ["Meter A", "Meter B", "Zone 1"],
                "quality_type": ["Heating value", "Wobbe index", "methane"],
                "unit": ["MJ/m3", "MJ/m3", "composition"],
                "quantity": [39.2, 45.0, 0.89],
                "source_system": ["VICGAS", "VICGAS", "VICGAS"],
                "source_table": [
                    "silver.vicgas.silver_int140_v5_gas_quality_data_1",
                    "silver.vicgas.silver_int140_v5_gas_quality_data_1",
                    "silver.vicgas.silver_int176_v4_gas_composition_data_1",
                ],
                "source_last_updated_timestamp": [
                    "2024-01-02 06:00:00",
                    "2024-01-01 06:00:00",
                    "2024-01-01 07:00:00",
                ],
                "ingested_timestamp": [
                    datetime(2024, 1, 2, 8),
                    datetime(2024, 1, 1, 8),
                    datetime(2024, 1, 1, 9),
                ],
            }
        )
    )

    observations = gas_quality_observation_frame(
        load,
        "Heating value",
        "MIRN-A",
    )
    kpis = gas_quality_kpi_frame(load)
    type_summary = gas_quality_type_summary_frame(load)
    source_coverage = gas_quality_source_coverage_frame(load)

    assert gas_quality_quality_type_options(load) == (
        GAS_QUALITY_QUALITY_TYPE_FILTER_ALL,
        "Heating value",
        "Wobbe index",
        "methane",
    )
    assert gas_quality_source_point_options(load) == (
        GAS_QUALITY_SOURCE_POINT_FILTER_ALL,
        "MIRN-A",
        "MIRN-B",
        "ZONE-1",
    )
    assert observations.to_dict(as_series=False) == {
        "gas date": [date(2024, 1, 2)],
        "gas interval": ["1"],
        "source point": ["MIRN-A"],
        "point name": ["Meter A"],
        "quality type": ["Heating value"],
        "unit": ["MJ/m3"],
        "quantity": [39.2],
        "source system": ["VICGAS"],
        "source table": ["silver.vicgas.silver_int140_v5_gas_quality_data_1"],
        "source updated": [datetime(2024, 1, 2, 6)],
        "latest ingest": [datetime(2024, 1, 2, 8)],
    }
    assert kpis.to_dict(as_series=False) == {
        "metric": [
            "Loaded observations",
            "Quality types",
            "Units",
            "Source points",
            "Source tables",
            "Latest gas date",
        ],
        "value": ["3", "3", "2", "3", "2", "2024-01-02"],
        "detail": [
            "Full table scan",
            "Distinct quality_type values in the current view",
            "Distinct unit values in the current view",
            "Distinct source_point_id values in the current view",
            "Distinct source_table values represented",
            "Maximum gas_date in the loaded bounded rows",
        ],
    }
    assert type_summary.select(
        "quality type",
        "unit",
        "observations",
        "source points",
        "latest gas date",
        "avg quantity",
    ).to_dict(as_series=False) == {
        "quality type": ["Heating value", "Wobbe index", "methane"],
        "unit": ["MJ/m3", "MJ/m3", "composition"],
        "observations": [1, 1, 1],
        "source points": [1, 1, 1],
        "latest gas date": [date(2024, 1, 2), date(2024, 1, 1), date(2024, 1, 1)],
        "avg quantity": [39.2, 45.0, 0.89],
    }
    assert source_coverage.select(
        "source table",
        "observations",
        "quality types",
        "source points",
        "latest gas date",
    ).to_dict(as_series=False) == {
        "source table": [
            "silver.vicgas.silver_int140_v5_gas_quality_data_1",
            "silver.vicgas.silver_int176_v4_gas_composition_data_1",
        ],
        "observations": [2, 1],
        "quality types": [2, 1],
        "source points": [2, 1],
        "latest gas date": [date(2024, 1, 2), date(2024, 1, 1)],
    }


def test_gas_quality_helpers_cover_missing_data_and_filter_empty_state() -> None:
    empty_load = _gas_quality_load(
        pl.DataFrame(),
        row_limit=4,
    )
    populated_load = _gas_quality_load(
        pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 2)],
                "source_point_id": ["MIRN-A"],
                "quality_type": ["Heating value"],
                "unit": ["MJ/m3"],
                "quantity": [39.2],
            }
        )
    )
    missing_date_load = _gas_quality_load(
        pl.DataFrame(
            {
                "source_point_id": ["MIRN-A"],
                "quality_type": ["Heating value"],
                "unit": ["MJ/m3"],
                "quantity": [39.2],
            }
        )
    )
    error_load = GasTableLoad(
        spec=GAS_QUALITY_TABLE_SPEC,
        uri="s3://bucket/silver/gas_model/silver_gas_fact_gas_quality",
        dataframe=None,
        error="FileNotFoundError: no parquet files found",
        row_limit=4,
        load_duration_seconds=0.01,
        cache_hit=False,
    )

    assert gas_quality_observation_frame(empty_load).is_empty()
    assert gas_quality_type_summary_frame(empty_load).is_empty()
    assert gas_quality_kpi_frame(empty_load).is_empty()
    assert gas_quality_source_coverage_frame(empty_load).is_empty()
    assert gas_quality_quality_type_options(empty_load) == (
        GAS_QUALITY_QUALITY_TYPE_FILTER_ALL,
    )
    assert gas_quality_observation_frame(populated_load)["gas date"].to_list() == [
        date(2024, 1, 2)
    ]
    assert gas_quality_kpi_frame(missing_date_load).row(5, named=True) == {
        "metric": "Latest gas date",
        "value": "unknown",
        "detail": "Maximum gas_date in the loaded bounded rows",
    }

    empty_markdown = gas_quality_empty_state_markdown(empty_load)
    error_markdown = gas_quality_empty_state_markdown(error_load)
    filtered_markdown = gas_quality_empty_state_markdown(populated_load)
    missing_load_markdown = gas_quality_empty_state_markdown(None)

    assert "No gas quality or composition data is available" in empty_markdown
    assert "silver.gas_model.silver_gas_fact_gas_quality" in empty_markdown
    assert "Bounded preview reads are capped at `4` rows per table" in empty_markdown
    assert "FileNotFoundError: no parquet files found" in error_markdown
    assert "current filters do not match" in filtered_markdown
    assert "did not receive a gas quality load result" in missing_load_markdown


def test_system_notice_summary_filters_critical_and_notice_windows() -> None:
    reference_time = datetime(2024, 1, 10, 12)
    load = _system_notice_load(
        pl.DataFrame(
            {
                "source_notice_id": [
                    "active-critical",
                    "old-critical",
                    "recent-noncritical",
                    "future-critical",
                ],
                "critical_notice": [True, True, False, True],
                "notice_start_timestamp": [
                    reference_time - timedelta(hours=2),
                    reference_time - timedelta(days=30),
                    reference_time - timedelta(days=1),
                    reference_time + timedelta(days=1),
                ],
                "notice_end_timestamp": [
                    reference_time + timedelta(hours=2),
                    reference_time - timedelta(days=29),
                    reference_time - timedelta(hours=1),
                    reference_time + timedelta(days=2),
                ],
                "system_message": [
                    "Linepack warning",
                    "Expired constraint",
                    "Recent information",
                    "Upcoming warning",
                ],
                "system_email_message": [
                    "Linepack email",
                    "Expired email",
                    "Recent email",
                    "Upcoming email",
                ],
                "url_path": ["/active", "/old", "/recent", "/future"],
                "source_system": ["VICGAS"] * 4,
                "source_table": [
                    "silver.vicgas.silver_int029a_v4_system_notices_1",
                    "silver.vicgas.silver_int029a_v4_system_notices_1",
                    "silver.vicgas.silver_int929a_v4_system_notices_1",
                    "silver.vicgas.silver_int929a_v4_system_notices_1",
                ],
            }
        )
    )

    active_critical = system_notice_summary_frame(
        load,
        SYSTEM_NOTICE_CRITICAL_FILTER_CRITICAL,
        SYSTEM_NOTICE_WINDOW_FILTER_ACTIVE,
        reference_time=reference_time,
    )
    recent_noncritical = system_notice_summary_frame(
        load,
        SYSTEM_NOTICE_CRITICAL_FILTER_NON_CRITICAL,
        SYSTEM_NOTICE_WINDOW_FILTER_RECENT,
        reference_time=reference_time,
        recent_days=2,
    )
    no_active_noncritical = system_notice_summary_frame(
        load,
        SYSTEM_NOTICE_CRITICAL_FILTER_NON_CRITICAL,
        SYSTEM_NOTICE_WINDOW_FILTER_ACTIVE,
        reference_time=reference_time,
    )
    all_loaded_preview = system_notice_summary_frame(
        load,
        SYSTEM_NOTICE_CRITICAL_FILTER_ALL,
        SYSTEM_NOTICE_WINDOW_FILTER_ALL,
        reference_time=reference_time,
        preview_rows=10,
    )
    active_recent_default = system_notice_summary_frame(
        load,
        reference_time=reference_time,
        recent_days=2,
        preview_rows=10,
    )
    source_coverage = system_notice_source_coverage_frame(
        load,
        reference_time=reference_time,
    )
    kpis = system_notice_kpi_frame(load, reference_time=reference_time, recent_days=2)

    assert active_critical.to_dict(as_series=False) == {
        "notice id": ["active-critical"],
        "critical": [True],
        "window": ["Active"],
        "start": [reference_time - timedelta(hours=2)],
        "end": [reference_time + timedelta(hours=2)],
        "message": ["Linepack warning"],
        "email message": ["Linepack email"],
        "url": ["/active"],
        "source system": ["VICGAS"],
        "source table": ["silver.vicgas.silver_int029a_v4_system_notices_1"],
    }
    assert recent_noncritical["notice id"].to_list() == ["recent-noncritical"]
    assert recent_noncritical["window"].to_list() == ["Ended"]
    assert no_active_noncritical.is_empty()
    assert all_loaded_preview["window"].to_list() == [
        "Active",
        "Upcoming",
        "Ended",
        "Ended",
    ]
    assert active_recent_default["notice id"].to_list() == [
        "active-critical",
        "future-critical",
        "recent-noncritical",
    ]
    assert kpis.to_dict(as_series=False) == {
        "metric": [
            "Loaded notices",
            "Critical notices",
            "Active notices",
            "Recent notices",
            "Source tables",
        ],
        "value": ["4", "3", "1", "3", "2"],
        "detail": [
            "Full table scan",
            "Rows where the critical flag is true",
            "Active at 2024-01-10 12:00",
            "Started or ended in the last 2 days",
            "Distinct system notice source tables represented",
        ],
    }
    assert source_coverage.select(
        "source table", "notices", "critical notices"
    ).to_dict(as_series=False) == {
        "source table": [
            "silver.vicgas.silver_int029a_v4_system_notices_1",
            "silver.vicgas.silver_int929a_v4_system_notices_1",
        ],
        "notices": [2, 2],
        "critical notices": [2, 1],
    }


def test_system_notice_kpis_and_empty_state_cover_missing_data() -> None:
    empty_load = _system_notice_load(
        pl.DataFrame(),
        row_limit=4,
    )
    error_load = GasTableLoad(
        spec=SYSTEM_NOTICE_TABLE_SPEC,
        uri="s3://bucket/silver/gas_model/silver_gas_fact_system_notice",
        dataframe=None,
        error="FileNotFoundError: no parquet files found",
        row_limit=4,
        load_duration_seconds=0.01,
        cache_hit=False,
    )

    assert system_notice_summary_frame(empty_load).is_empty()
    assert system_notice_kpi_frame(empty_load).is_empty()
    assert system_notice_source_coverage_frame(empty_load).is_empty()

    empty_markdown = system_notice_empty_state_markdown(empty_load)
    error_markdown = system_notice_empty_state_markdown(error_load)

    assert "No system notice data is available for this view" in empty_markdown
    assert "`silver.gas_model.silver_gas_fact_system_notice`" in empty_markdown
    assert "Bounded preview reads are capped at `4` rows per table" in empty_markdown
    assert "FileNotFoundError: no parquet files found" in error_markdown


def test_system_notice_helpers_cover_default_reference_and_filter_empty_state() -> None:
    load = _system_notice_load(
        pl.DataFrame(
            {
                "source_notice_id": ["open-window"],
                "critical_notice": [False],
                "notice_start_timestamp": [None],
                "notice_end_timestamp": [None],
                "system_message": ["Window dates are not supplied"],
            }
        )
    )
    string_timestamp_load = _system_notice_load(
        pl.DataFrame(
            {
                "source_notice_id": ["string-window"],
                "critical_notice": [True],
                "notice_start_timestamp": ["2024-01-01 00:00:00"],
                "notice_end_timestamp": ["2024-01-02 00:00:00"],
            }
        )
    )

    default_kpis = system_notice_kpi_frame(load)
    parsed_summary = system_notice_summary_frame(
        string_timestamp_load,
        window_filter=SYSTEM_NOTICE_WINDOW_FILTER_ALL,
        reference_time=datetime(2024, 1, 1, 12),
    )
    filtered_empty_markdown = system_notice_empty_state_markdown(load)
    missing_load_markdown = system_notice_empty_state_markdown(None)

    assert default_kpis["metric"].to_list() == [
        "Loaded notices",
        "Critical notices",
        "Active notices",
        "Recent notices",
        "Source tables",
    ]
    assert default_kpis["value"].to_list() == ["1", "0", "0", "0", "0"]
    assert parsed_summary["start"].to_list() == [datetime(2024, 1, 1)]
    assert parsed_summary["end"].to_list() == [datetime(2024, 1, 2)]
    assert "current filters do not match" in filtered_empty_markdown
    assert "did not receive a system notice load result" in missing_load_markdown


def test_load_gas_model_tables_passes_configured_uri_storage_and_limit() -> None:
    captured: list[tuple[str, Mapping[str, str], int | None]] = []
    config = _dashboard_config()
    specs = [
        GasTableSpec(
            section="Prices",
            label="Market prices",
            table_name="silver_gas_fact_market_price",
        )
    ]

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured.append((uri, storage_options, row_limit))
        return pl.DataFrame({"source_system": ["STTM"]})

    loads = load_gas_model_tables(config, specs=specs, reader=reader)

    assert len(loads) == 1
    assert loads[0].available
    assert loads[0].error is None
    assert captured == [
        (
            "s3://dev-energy-market-aemo/silver/gas_model/silver_gas_fact_market_price",
            config.storage_options(),
            None,
        )
    ]


def test_load_gas_model_tables_limits_aws_reads() -> None:
    captured: list[int | None] = []
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "17",
        }
    )
    specs = [
        GasTableSpec(
            section="Prices",
            label="Market prices",
            table_name="silver_gas_fact_market_price",
        )
    ]

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured.append(row_limit)
        return pl.DataFrame({"source_system": ["STTM"]})

    loads = load_gas_model_tables(config, specs=specs, reader=reader)

    assert loads[0].available
    assert captured == [17]
    assert loads[0].row_limit == 17
    assert loads[0].is_limited


def test_cached_load_gas_model_tables_reuses_cache_until_refresh() -> None:
    calls: list[str] = []
    clock_values = iter((10.0, 10.025, 20.0, 20.05))
    config = _dashboard_config()
    specs = [
        GasTableSpec(
            section="Prices",
            label="Market prices",
            table_name="silver_gas_fact_market_price",
            date_columns=("gas_date",),
        )
    ]
    cache: GasModelSessionCache = {}

    def clock() -> float:
        return next(clock_values)

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        calls.append(uri)
        return pl.DataFrame(
            {
                "gas_date": ["2024-01-01", "2024-01-03"],
                "price": [10.0, 30.0],
            }
        )

    first_load = cached_load_gas_model_tables(
        config,
        cache,
        specs=specs,
        reader=reader,
        clock=clock,
    )[0]
    cached_recent_load = cached_load_gas_model_tables(
        config,
        cache,
        specs=specs,
        reader=reader,
        view=GasModelTableView.RECENT,
        clock=clock,
    )[0]
    refreshed_load = cached_load_gas_model_tables(
        config,
        cache,
        specs=specs,
        reader=reader,
        refresh_token=1,
        clock=clock,
    )[0]

    assert len(calls) == 2
    assert not first_load.cache_hit
    assert first_load.load_duration_seconds == pytest.approx(0.025)
    assert cached_recent_load.cache_hit
    assert cached_recent_load.load_duration_seconds == pytest.approx(0.025)
    assert cached_recent_load.dataframe is not None
    assert cached_recent_load.dataframe.to_dict(as_series=False) == {
        "gas_date": ["2024-01-03", "2024-01-01"],
        "price": [30.0, 10.0],
    }
    assert not refreshed_load.cache_hit
    assert refreshed_load.load_duration_seconds == pytest.approx(0.05)


def test_cached_load_gas_model_tables_uses_stable_run_button_refresh_token() -> None:
    class RunButtonControl:
        value = False

    calls: list[int] = []
    clock_values = iter((1.0, 1.01, 2.0, 2.02, 3.0, 3.03))
    config = _dashboard_config()
    specs = [
        GasTableSpec(
            section="Prices",
            label="Market prices",
            table_name="silver_gas_fact_market_price",
        )
    ]
    cache: GasModelSessionCache = {}
    refresh_control = RunButtonControl()

    def clock() -> float:
        return next(clock_values)

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        calls.append(len(calls) + 1)
        return pl.DataFrame({"read_version": [calls[-1]]})

    first_load = cached_load_gas_model_tables(
        config,
        cache,
        specs=specs,
        reader=reader,
        refresh_token=refresh_token_from_control(refresh_control),
        clock=clock,
    )[0]

    refresh_control.value = True
    refreshed_load = cached_load_gas_model_tables(
        config,
        cache,
        specs=specs,
        reader=reader,
        refresh_token=refresh_token_from_control(refresh_control),
        clock=clock,
    )[0]

    refresh_control.value = False
    reset_load = cached_load_gas_model_tables(
        config,
        cache,
        specs=specs,
        reader=reader,
        refresh_token=refresh_token_from_control(refresh_control),
        clock=clock,
    )[0]

    refresh_control.value = True
    second_refreshed_load = cached_load_gas_model_tables(
        config,
        cache,
        specs=specs,
        reader=reader,
        refresh_token=refresh_token_from_control(refresh_control),
        clock=clock,
    )[0]

    assert calls == [1, 2, 3]
    assert not first_load.cache_hit
    assert not refreshed_load.cache_hit
    assert reset_load.cache_hit
    assert not second_refreshed_load.cache_hit
    assert reset_load.dataframe is not None
    assert reset_load.dataframe.item() == 2
    assert second_refreshed_load.dataframe is not None
    assert second_refreshed_load.dataframe.item() == 3


def test_gas_table_load_status_reports_bounded_limit_cache_and_timing() -> None:
    clock_values = iter((1.0, 1.125))
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "17",
        }
    )
    specs = [
        GasTableSpec(
            section="Prices",
            label="Market prices",
            table_name="silver_gas_fact_market_price",
        )
    ]

    def clock() -> float:
        return next(clock_values)

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        assert row_limit == 17
        return pl.DataFrame({"source_system": ["STTM", "DWGM"]})

    loads = load_gas_model_tables(
        config,
        specs=specs,
        reader=reader,
        clock=clock,
    )
    message = gas_table_load_status_message(loads)
    status = gas_table_load_status_frame(loads)

    assert (
        "Bounded preview reads are capped at `17` rows per table by "
        "`MARIMO_MAX_PREVIEW_ROWS`."
    ) in message
    assert "- Load timing: `125 ms` across `1` table reads" in message
    assert "- Session cache: `0` hits; use **Refresh data**" in message
    assert status.row(0, named=True)["row limit"] == "Bounded preview: 17 rows max"
    assert status.row(0, named=True)["load time"] == "125 ms"
    assert status.row(0, named=True)["cache"] == "Refreshed read"


def test_gas_table_load_status_handles_empty_unavailable_and_no_loads() -> None:
    empty_spec = GasTableSpec(
        section="Prices",
        label="Market prices",
        table_name="empty_prices",
    )
    missing_spec = GasTableSpec(
        section="Schedules",
        label="Schedule runs",
        table_name="missing_schedules",
    )
    loads = [
        GasTableLoad(
            spec=empty_spec,
            uri="s3://bucket/empty_prices",
            dataframe=pl.DataFrame(),
            error=None,
            row_limit=None,
            load_duration_seconds=0.0005,
            cache_hit=True,
        ),
        GasTableLoad(
            spec=missing_spec,
            uri="s3://bucket/missing_schedules",
            dataframe=None,
            error="FileNotFoundError: no parquet files found",
            row_limit=17,
            load_duration_seconds=2.5,
            cache_hit=False,
        ),
    ]

    message = gas_table_load_status_message(loads)
    status = gas_table_load_status_frame(loads)

    assert gas_table_load_status_message([]) == (
        "No `silver.gas_model` tables were requested."
    )
    assert (
        "Bounded preview reads are capped at `17` rows per table by "
        "`MARIMO_MAX_PREVIEW_ROWS`."
    ) in message
    assert status["status"].to_list() == ["Empty", "Unavailable"]
    assert status["load time"].to_list() == ["<1 ms", "2.50 s"]
    assert status["cache"].to_list() == ["Session cache hit", "Refreshed read"]


def test_shared_load_display_helpers_cover_full_scan_messages() -> None:
    table_read = GasModelTableRead(
        table_name="prices",
        uri="s3://bucket/prices",
        dataframe=pl.DataFrame({"price": [10.0]}),
        error=None,
        row_limit=5,
        load_duration_seconds=0.01,
    )
    empty_read = GasModelTableRead(
        table_name="empty",
        uri="s3://bucket/empty",
        dataframe=pl.DataFrame(),
        error=None,
        row_limit=None,
        load_duration_seconds=0.0,
    )

    assert table_read.available
    assert table_read.is_limited
    assert not empty_read.available
    assert not empty_read.is_limited
    assert format_load_duration(0.0005) == "<1 ms"
    assert format_load_duration(2.5) == "2.50 s"
    assert format_row_limit(None) == "Full table scan"
    assert row_limit_message(None) == (
        "Full table scans are enabled; row counts reflect loaded table data."
    )
    assert cache_status_label(True) == "Session cache hit"


def test_refresh_token_from_control_handles_missing_and_unhashable_values() -> None:
    class Control:
        value = ["not", "hashable"]

    class HashableControl:
        value = 2

    class RunButtonControl:
        value = False

    refresh_control = RunButtonControl()

    assert refresh_token_from_control(None) == 0
    assert refresh_token_from_control(HashableControl()) == 2
    assert refresh_token_from_control(Control()) == "['not', 'hashable']"
    assert refresh_token_from_control(refresh_control) == 0

    refresh_control.value = True
    assert refresh_token_from_control(refresh_control) == 1
    assert refresh_token_from_control(refresh_control) == 1

    refresh_control.value = False
    assert refresh_token_from_control(refresh_control) == 1

    refresh_control.value = True
    assert refresh_token_from_control(refresh_control) == 2


def test_load_gas_model_read_requests_cover_available_missing_and_empty() -> None:
    config = _dashboard_config()
    requests = (
        GasModelReadRequest("available"),
        GasModelReadRequest("missing"),
        GasModelReadRequest("empty"),
    )

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        assert storage_options == config.storage_options()
        assert row_limit is None
        if uri.endswith("/missing"):
            raise FileNotFoundError("no parquet files found")
        if uri.endswith("/empty"):
            return pl.DataFrame()
        return pl.DataFrame({"source_system": ["STTM"]})

    loads = load_gas_model_read_requests(config, requests, reader=reader)

    assert loads[0].available
    assert loads[0].table_name == "available"
    assert loads[0].uri == "s3://dev-energy-market-aemo/silver/gas_model/available"
    assert not loads[0].is_limited
    assert not loads[1].available
    assert loads[1].dataframe is None
    assert loads[1].error == "FileNotFoundError: no parquet files found"
    assert not loads[2].available
    assert loads[2].dataframe is not None
    assert loads[2].dataframe.is_empty()
    assert loads[2].error is None


def test_load_gas_model_read_request_keeps_recent_view_without_date_columns() -> None:
    config = _dashboard_config()
    request = GasModelReadRequest(
        table_name="silver_gas_fact_market_price",
        view=GasModelTableView.RECENT,
        date_columns=("missing_date",),
    )

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        return pl.DataFrame({"price": [10.0, 30.0]})

    load = load_gas_model_read_request(config, request, reader=reader)

    assert load.table_name == "silver_gas_fact_market_price"
    assert load.available
    assert load.dataframe is not None
    assert load.dataframe.to_dict(as_series=False) == {"price": [10.0, 30.0]}


def test_load_gas_model_read_requests_support_recent_bounded_aws_view() -> None:
    captured: list[int | None] = []
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "2",
        }
    )
    request = GasModelReadRequest(
        table_name="silver_gas_fact_market_price",
        view=GasModelTableView.RECENT,
        date_columns=("gas_date",),
    )

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured.append(row_limit)
        assert uri == (
            "s3://prod-energy-market-aemo/silver/gas_model/silver_gas_fact_market_price"
        )
        assert storage_options == config.storage_options()
        return pl.DataFrame(
            {
                "gas_date": ["2024-01-01", "2024-01-03"],
                "price": [10.0, 30.0],
            }
        )

    loads = load_gas_model_read_requests(config, (request,), reader=reader)

    assert captured == [2]
    assert loads[0].is_limited
    assert loads[0].row_limit == 2
    assert loads[0].dataframe is not None
    assert loads[0].dataframe.to_dict(as_series=False) == {
        "gas_date": ["2024-01-03", "2024-01-01"],
        "price": [30.0, 10.0],
    }


def test_load_gas_model_tables_returns_empty_state_detail_on_read_error() -> None:
    config = _dashboard_config()
    specs = [
        GasTableSpec(
            section="Prices",
            label="Market prices",
            table_name="silver_gas_fact_market_price",
        )
    ]

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        raise RuntimeError("no delta log found\ntraceback detail")

    loads = load_gas_model_tables(config, specs=specs, reader=reader)

    assert len(loads) == 1
    assert not loads[0].available
    assert loads[0].dataframe is None
    assert loads[0].error == "RuntimeError: no delta log found"
    assert "\n" not in loads[0].error


def test_load_gas_model_tables_handles_empty_exception_message() -> None:
    config = _dashboard_config()
    specs = [
        GasTableSpec(
            section="Prices",
            label="Market prices",
            table_name="silver_gas_fact_market_price",
        )
    ]

    class EmptyMessageError(Exception):
        def __str__(self) -> str:
            return ""

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        raise EmptyMessageError

    loads = load_gas_model_tables(config, specs=specs, reader=reader)

    assert loads[0].error == "EmptyMessageError"


def test_table_load_by_name_returns_matching_load() -> None:
    config = _dashboard_config()
    specs = [
        GasTableSpec(section="Prices", label="Market prices", table_name="prices"),
        GasTableSpec(section="Schedules", label="Schedules", table_name="schedules"),
    ]

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        return pl.DataFrame({"source_system": ["STTM"]})

    loads = load_gas_model_tables(config, specs=specs, reader=reader)

    assert table_load_by_name(loads, "schedules") == loads[1]
    assert table_load_by_name(loads, "missing") is None


def test_source_coverage_table_specs_use_registry_backing_assets() -> None:
    specs = source_coverage_table_specs()
    table_names = {spec.table_name for spec in specs}

    assert "silver_gas_fact_market_price" in table_names
    assert "silver_gas_dim_facility" in table_names
    assert "silver_gas_fact_customer_transfer" in table_names
    assert len(table_names) == len(specs)


def test_source_coverage_table_specs_skip_non_gas_model_and_label_sections() -> None:
    entry = DashboardRegistryEntry(
        concept_id="custom-context",
        title="Custom",
        description="Custom source coverage entry.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.PLANNED,
        notebook_name=None,
        backing_assets=(
            "bronze.gas_model.raw",
            "silver.gas_model.silver_gas_dim_date",
            "silver.gas_model.silver_gas_fact_market_price",
            "silver.gas_model.silver_gas_participant_market_membership",
            "silver.gas_model.silver_gas_dim_date",
        ),
        generated_gold_paths=(),
        source_chunks=(),
    )

    specs = source_coverage_table_specs((entry,))
    sections = {spec.table_name: spec.section for spec in specs}
    labels = {spec.table_name: spec.label for spec in specs}

    assert tuple(spec.table_name for spec in specs) == (
        "silver_gas_dim_date",
        "silver_gas_fact_market_price",
        "silver_gas_participant_market_membership",
    )
    assert sections == {
        "silver_gas_dim_date": "Dimensions",
        "silver_gas_fact_market_price": "Facts",
        "silver_gas_participant_market_membership": "Associations",
    }
    assert labels["silver_gas_fact_market_price"] == "Fact Market Price"


def test_source_coverage_table_specs_from_catalogue_dedupes_discovered_rows() -> None:
    dim_table = "silver_gas_dim_facility"
    fact_table = "silver_gas_fact_market_price"
    association_table = "silver_gas_participant_market_membership"
    catalogue_rows = (
        CataloguedTable(
            entry_id=f"asset:silver/gas_model/{dim_table}",
            status=TableAvailability.LIVE,
            asset=DagsterTableAsset(
                asset_key=("silver", "gas_model", dim_table),
                group_name="gas_model",
                kinds=("python", "parquet"),
                description=None,
                uri=f"s3://bucket/silver/gas_model/{dim_table}",
                columns=(),
                is_materializable=True,
                is_executable=True,
                latest_materialization_timestamp=None,
            ),
            table=None,
        ),
        CataloguedTable(
            entry_id="",
            status=TableAvailability.LIVE,
            asset=None,
            table=TablePrefix(
                bucket="bucket",
                prefix=f"silver/gas_model/{dim_table}",
                table_format=TableFormat.PARQUET,
                parquet_files=(f"silver/gas_model/{dim_table}/part-000.parquet",),
            ),
        ),
        SimpleNamespace(uri=f"s3://bucket/silver/gas_model/{fact_table}"),
        SimpleNamespace(uri=f"silver.gas_model.{association_table}"),
        SimpleNamespace(uri="s3://bucket/bronze/gas_model/ignored"),
    )

    specs = source_coverage_table_specs_from_catalogue(catalogue_rows)

    assert tuple(spec.table_name for spec in specs) == (
        dim_table,
        fact_table,
        association_table,
    )
    assert {spec.table_name: spec.section for spec in specs} == {
        dim_table: "Dimensions",
        fact_table: "Facts",
        association_table: "Associations",
    }


def test_source_coverage_loaders_use_shared_bounded_loader() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "4",
        }
    )
    captured: list[tuple[str, int | None]] = []

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        assert storage_options == config.storage_options()
        captured.append((uri, row_limit))
        return pl.DataFrame()

    loads = load_source_coverage_tables(config, reader=reader)

    assert loads
    assert len(captured) == len(source_coverage_table_specs())
    assert {row_limit for _, row_limit in captured} == {4}
    assert captured[0][0].startswith("s3://prod-energy-market-aemo/silver/gas_model/")


def test_cached_source_coverage_loader_uses_session_cache() -> None:
    config = _dashboard_config()
    spec = GasTableSpec(
        section="Facts",
        label="Market prices",
        table_name="silver_gas_fact_market_price",
    )
    calls = 0

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        nonlocal calls
        assert row_limit == 100
        calls += 1
        return pl.DataFrame({"source_system": ["GBB"], "source_table": ["table"]})

    cache: GasModelSessionCache = {}
    first = cached_load_source_coverage_tables(
        config,
        cache,
        specs=(spec,),
        reader=reader,
        refresh_token="same",
    )
    second = cached_load_source_coverage_tables(
        config,
        cache,
        specs=(spec,),
        reader=reader,
        refresh_token="same",
    )

    assert calls == 1
    assert not first[0].cache_hit
    assert second[0].cache_hit


def test_source_coverage_matrix_returns_empty_schema_for_no_loads() -> None:
    matrix = source_coverage_matrix_frame(())
    empty_markdown = source_coverage_empty_state_markdown(())

    assert matrix.is_empty()
    assert matrix.columns == [
        "asset",
        "section",
        "table",
        "source system",
        "source table",
        "coverage state",
        "rows loaded",
        "row limit",
        "source fields",
        "table explorer",
        "asset metadata",
        "uri",
        "detail",
    ]
    assert "No source coverage tables were requested" in empty_markdown


def test_source_coverage_matrix_summarizes_single_source_table_column() -> None:
    load = _source_coverage_load(
        "silver_gas_fact_market_price",
        pl.DataFrame(
            {
                "source_system": ["GBB", "GBB", "STTM"],
                "source_table": [
                    "silver.gbb.price_report",
                    "silver.gbb.price_report",
                    "silver.sttm.price_report",
                ],
            }
        ),
    )

    matrix = source_coverage_matrix_frame((load,))

    assert matrix.to_dict(as_series=False)["coverage state"] == [
        SOURCE_COVERAGE_STATE_COVERED,
        SOURCE_COVERAGE_STATE_COVERED,
    ]
    assert matrix.select("source system", "source table", "rows loaded").to_dicts() == [
        {
            "source system": "GBB",
            "source table": "silver.gbb.price_report",
            "rows loaded": 2,
        },
        {
            "source system": "STTM",
            "source table": "silver.sttm.price_report",
            "rows loaded": 1,
        },
    ]
    assert matrix.row(0, named=True)["table explorer"] == (
        "/marimo/table_explorer/?search=silver_gas_fact_market_price"
    )


def test_source_coverage_matrix_renders_unavailable_and_empty_states() -> None:
    unavailable_load = _source_coverage_load(
        "silver_gas_fact_market_price",
        None,
        error="RuntimeError: missing parquet",
    )
    empty_load = _source_coverage_load(
        "silver_gas_fact_schedule_run",
        pl.DataFrame(),
    )

    matrix = source_coverage_matrix_frame((unavailable_load, empty_load))
    rows = matrix.select("table", "coverage state", "detail").to_dicts()
    empty_markdown = source_coverage_empty_state_markdown(
        (unavailable_load, empty_load)
    )

    assert rows == [
        {
            "table": "silver_gas_fact_market_price",
            "coverage state": SOURCE_COVERAGE_STATE_UNAVAILABLE,
            "detail": "Read detail: RuntimeError: missing parquet",
        },
        {
            "table": "silver_gas_fact_schedule_run",
            "coverage state": SOURCE_COVERAGE_STATE_EMPTY,
            "detail": "The table read succeeded but returned no rows.",
        },
    ]
    assert "1` reads were unavailable" in empty_markdown
    assert "1` reads" in empty_markdown
    assert "returned no rows" in empty_markdown


def test_source_coverage_matrix_expands_source_tables_list_column() -> None:
    load = _source_coverage_load(
        "silver_gas_fact_schedule_run",
        pl.DataFrame(
            {
                "source_system": ["VICGAS", "VICGAS"],
                "source_tables": [
                    [
                        "silver.vicgas.schedule_header",
                        "silver.vicgas.schedule_detail",
                    ],
                    ["silver.vicgas.schedule_header"],
                ],
            }
        ),
    )

    matrix = source_coverage_matrix_frame((load,))

    assert matrix.select("source table", "rows loaded").to_dicts() == [
        {"source table": "silver.vicgas.schedule_header", "rows loaded": 2},
        {"source table": "silver.vicgas.schedule_detail", "rows loaded": 1},
    ]
    assert set(matrix.get_column("source fields").to_list()) == {
        "source_system, source_tables"
    }


def test_source_coverage_matrix_marks_missing_source_table_columns_as_gap() -> None:
    load = _source_coverage_load(
        "silver_gas_dim_facility",
        pl.DataFrame(
            {
                "source_system": ["GBB", "GBB"],
                "facility_id": ["F1", "F2"],
            }
        ),
    )

    matrix = source_coverage_matrix_frame((load,))
    row = matrix.row(0, named=True)

    assert row["coverage state"] == SOURCE_COVERAGE_STATE_GAP
    assert row["source system"] == "GBB"
    assert row["source table"] == "(missing source_table/source_tables column)"
    assert row["rows loaded"] == 2
    assert "Missing source_table/source_tables columns" in row["detail"]


def test_source_coverage_matrix_marks_missing_source_fields_as_gap() -> None:
    load = _source_coverage_load(
        "silver_gas_dim_facility",
        pl.DataFrame({"facility_id": ["F1"]}),
    )

    matrix = source_coverage_matrix_frame((load,))
    row = matrix.row(0, named=True)

    assert row["coverage state"] == SOURCE_COVERAGE_STATE_GAP
    assert row["source system"] == "(missing source_system column)"
    assert row["source table"] == "(missing source_table/source_tables column)"
    assert row["source fields"] == "(none)"


def test_source_coverage_matrix_marks_missing_and_empty_source_systems() -> None:
    missing_system_load = _source_coverage_load(
        "silver_gas_fact_market_price",
        pl.DataFrame({"source_table": ["silver.gbb.price_report"]}),
    )
    empty_system_load = _source_coverage_load(
        "silver_gas_fact_schedule_run",
        pl.DataFrame(
            {
                "source_system": [""],
                "source_table": ["silver.sttm.schedule_report"],
            }
        ),
    )

    matrix = source_coverage_matrix_frame((missing_system_load, empty_system_load))
    rows = matrix.select("source system", "coverage state", "detail").to_dicts()

    assert rows == [
        {
            "source system": "(missing source_system column)",
            "coverage state": SOURCE_COVERAGE_STATE_GAP,
            "detail": "Missing source_system column; source table values were present.",
        },
        {
            "source system": "(empty source_system value)",
            "coverage state": SOURCE_COVERAGE_STATE_GAP,
            "detail": (
                "source_system column is present but empty for these loaded rows."
            ),
        },
    ]


def test_source_coverage_matrix_marks_empty_source_table_values() -> None:
    none_load = _source_coverage_load(
        "silver_gas_fact_market_price",
        pl.DataFrame({"source_system": ["GBB"], "source_table": [None]}),
    )
    nan_load = _source_coverage_load(
        "silver_gas_fact_schedule_run",
        pl.DataFrame({"source_system": ["STTM"], "source_table": [float("nan")]}),
    )
    numeric_load = _source_coverage_load(
        "silver_gas_fact_capacity_outlook",
        pl.DataFrame({"source_system": ["GBB"], "source_table": [123]}),
    )

    matrix = source_coverage_matrix_frame((none_load, nan_load, numeric_load))
    rows = matrix.select(
        "source system",
        "source table",
        "coverage state",
        "rows loaded",
    ).to_dicts()

    assert rows == [
        {
            "source system": "GBB",
            "source table": "(empty source_table/source_tables value)",
            "coverage state": SOURCE_COVERAGE_STATE_GAP,
            "rows loaded": 1,
        },
        {
            "source system": "STTM",
            "source table": "(empty source_table/source_tables value)",
            "coverage state": SOURCE_COVERAGE_STATE_GAP,
            "rows loaded": 1,
        },
        {
            "source system": "GBB",
            "source table": "123",
            "coverage state": SOURCE_COVERAGE_STATE_COVERED,
            "rows loaded": 1,
        },
    ]


def test_source_coverage_matrix_links_catalogue_rows_when_available() -> None:
    table_name = "silver_gas_fact_market_price"
    load = _source_coverage_load(
        table_name,
        pl.DataFrame(
            {
                "source_system": ["STTM"],
                "source_table": ["silver.sttm.price_report"],
            }
        ),
    )
    asset = DagsterTableAsset(
        asset_key=("silver", "gas_model", table_name),
        group_name="gas_model",
        kinds=("python", "parquet"),
        description=None,
        uri=f"s3://dev-energy-market-aemo/silver/gas_model/{table_name}",
        columns=(),
        is_materializable=True,
        is_executable=True,
        latest_materialization_timestamp=None,
    )
    catalogue_row = CataloguedTable(
        entry_id=f"asset:silver/gas_model/{table_name}",
        status=TableAvailability.LIVE,
        asset=asset,
        table=None,
    )

    matrix = source_coverage_matrix_frame((load,), (catalogue_row, catalogue_row))
    row = matrix.row(0, named=True)

    assert row["table explorer"] == (
        "/marimo/table_explorer/?table=asset%3Asilver%2Fgas_model%2F"
        "silver_gas_fact_market_price"
    )
    assert row["asset metadata"] == (
        "/marimo/table_explorer/?asset=asset%3Asilver%2Fgas_model%2F"
        "silver_gas_fact_market_price"
    )
    assert row["uri"] == (
        "s3://dev-energy-market-aemo/silver/gas_model/silver_gas_fact_market_price"
    )


def test_render_source_coverage_matrix_html_includes_deep_link_anchors() -> None:
    table_name = "silver_gas_fact_market_price"
    load = _source_coverage_load(
        table_name,
        pl.DataFrame(
            {
                "source_system": ["STTM"],
                "source_table": ["silver.sttm.price_report"],
            }
        ),
    )
    catalogue_row = CataloguedTable(
        entry_id=f"asset:silver/gas_model/{table_name}",
        status=TableAvailability.LIVE,
        asset=DagsterTableAsset(
            asset_key=("silver", "gas_model", table_name),
            group_name="gas_model",
            kinds=("python", "parquet"),
            description=None,
            uri=f"s3://dev-energy-market-aemo/silver/gas_model/{table_name}",
            columns=(),
            is_materializable=True,
            is_executable=True,
            latest_materialization_timestamp=None,
        ),
        table=None,
    )

    matrix = source_coverage_matrix_frame((load,), (catalogue_row,))
    html = render_source_coverage_matrix_html(matrix)

    assert 'data-link-target="table-explorer"' in html
    assert 'data-link-target="asset-metadata"' in html
    assert (
        'href="/marimo/table_explorer/?table=asset%3Asilver%2Fgas_model%2F'
        'silver_gas_fact_market_price"'
    ) in html
    assert (
        'href="/marimo/table_explorer/?asset=asset%3Asilver%2Fgas_model%2F'
        'silver_gas_fact_market_price"'
    ) in html
    assert "Open table</a>" in html
    assert "Open asset</a>" in html
    assert "<button" not in html.lower()


def test_render_source_coverage_matrix_html_escapes_values_and_missing_links() -> None:
    matrix = pl.DataFrame(
        [
            {
                "asset": "silver.gas_model.<unsafe>",
                "section": "Facts",
                "table": "<unsafe>",
                "source system": "GBB",
                "source table": "silver.gbb.<unsafe>",
                "coverage state": SOURCE_COVERAGE_STATE_COVERED,
                "rows loaded": 1,
                "row limit": "100 rows",
                "source fields": "source_system, source_table",
                "table explorer": "javascript:alert(1)",
                "asset metadata": "",
                "uri": "s3://bucket/<unsafe>",
                "detail": "1 < 2",
            }
        ]
    )

    html = render_source_coverage_matrix_html(matrix)

    assert "&lt;unsafe&gt;" in html
    assert "1 &lt; 2" in html
    assert "<unsafe>" not in html
    assert "javascript:alert" not in html
    assert (
        '<span class="source-coverage-matrix__missing-link">Unavailable</span>'
    ) in html


def test_render_source_coverage_matrix_html_handles_empty_and_overflow_rows() -> None:
    empty_html = render_source_coverage_matrix_html(source_coverage_matrix_frame(()))
    matrix = pl.DataFrame(
        [
            {
                "asset": "silver.gas_model.first",
                "section": "Facts",
                "table": "first",
                "source system": "GBB",
                "source table": None,
                "coverage state": SOURCE_COVERAGE_STATE_GAP,
                "rows loaded": 1234,
                "row limit": "100 rows",
                "source fields": "(none)",
                "table explorer": None,
                "asset metadata": None,
                "uri": "",
                "detail": "Missing source table",
            },
            {
                "asset": "silver.gas_model.second",
                "section": "Facts",
                "table": "second",
                "source system": "STTM",
                "source table": "silver.sttm.price_report",
                "coverage state": SOURCE_COVERAGE_STATE_COVERED,
                "rows loaded": 1,
                "row limit": "100 rows",
                "source fields": "source_system, source_table",
                "table explorer": "/marimo/table_explorer/?search=second",
                "asset metadata": "",
                "uri": "s3://bucket/silver/gas_model/second",
                "detail": "Covered",
            },
        ]
    )

    html = render_source_coverage_matrix_html(matrix, max_rows=1)

    assert "No source coverage rows match the current filters." in empty_html
    assert 'data-row-count="2"' in html
    assert 'data-rendered-row-count="1"' in html
    assert "1 additional rows are hidden by the dashboard display limit." in html
    assert ">1,234</td>" in html
    assert "Missing source table" in html
    assert "silver.sttm.price_report" not in html
    assert (
        '<span class="source-coverage-matrix__missing-link">Unavailable</span>'
    ) in html


def test_source_coverage_matrix_uses_catalogue_uri_and_storage_fallbacks() -> None:
    table_name = "silver_gas_fact_market_price"
    load = _source_coverage_load(
        table_name,
        pl.DataFrame(
            {
                "source_system": ["GBB"],
                "source_table": ["silver.gbb.price_report"],
            }
        ),
    )
    asset_uri_row = CataloguedTable(
        entry_id=f"asset:bronze/{table_name}",
        status=TableAvailability.LIVE,
        asset=DagsterTableAsset(
            asset_key=("bronze", table_name),
            group_name="gas_model",
            kinds=("python",),
            description=None,
            uri=f"s3://bucket/silver/gas_model/{table_name}",
            columns=(),
            is_materializable=True,
            is_executable=True,
            latest_materialization_timestamp=None,
        ),
        table=None,
    )
    storage_row = CataloguedTable(
        entry_id="",
        status=TableAvailability.LIVE,
        asset=None,
        table=TablePrefix(
            bucket="bucket",
            prefix=f"silver/gas_model/{table_name}",
            table_format=TableFormat.PARQUET,
            parquet_files=(f"silver/gas_model/{table_name}/part-000.parquet",),
        ),
    )
    ignored_rows = (
        SimpleNamespace(uri="s3://bucket/bronze/table"),
        SimpleNamespace(uri="s3://bucket/silver/gas_model/"),
    )
    dotted_row = SimpleNamespace(
        entry_id="dotted-row",
        asset=None,
        table=None,
        uri=f"silver.gas_model.{table_name}",
    )

    asset_matrix = source_coverage_matrix_frame((load,), (asset_uri_row,))
    storage_matrix = source_coverage_matrix_frame(
        (load,),
        (*ignored_rows, storage_row),
    )
    dotted_matrix = source_coverage_matrix_frame((load,), (dotted_row,))

    assert asset_matrix.row(0, named=True)["uri"] == (
        f"s3://bucket/silver/gas_model/{table_name}"
    )
    assert storage_matrix.row(0, named=True)["table explorer"] == (
        "/marimo/table_explorer/"
    )
    assert storage_matrix.row(0, named=True)["asset metadata"] == ""
    assert dotted_matrix.row(0, named=True)["table explorer"] == (
        "/marimo/table_explorer/?table=dotted-row"
    )


def test_source_coverage_kpi_frame_counts_covered_sources_and_gaps() -> None:
    covered_load = _source_coverage_load(
        "silver_gas_fact_market_price",
        pl.DataFrame(
            {
                "source_system": ["GBB", "STTM"],
                "source_table": [
                    "silver.gbb.price_report",
                    "silver.sttm.price_report",
                ],
            }
        ),
    )
    gap_load = _source_coverage_load(
        "silver_gas_dim_facility",
        pl.DataFrame({"source_system": ["GBB"], "facility_id": ["F1"]}),
    )
    matrix = source_coverage_matrix_frame((covered_load, gap_load))

    kpis = source_coverage_kpi_frame((covered_load, gap_load), matrix)
    values = {row["metric"]: row["value"] for row in kpis.to_dicts()}

    assert values["Requested assets"] == "2"
    assert values["Loaded assets"] == "2"
    assert values["Assets with source coverage"] == "1"
    assert values["Assets with coverage gaps"] == "1"
    assert values["Source systems"] == "2"
    assert values["Source tables"] == "2"


def test_source_coverage_kpi_frame_handles_empty_matrix() -> None:
    kpis = source_coverage_kpi_frame((), source_coverage_matrix_frame(()))
    values = {row["metric"]: row["value"] for row in kpis.to_dicts()}

    assert values["Requested assets"] == "0"
    assert values["Assets with source coverage"] == "0"
    assert values["Source systems"] == "0"


def test_render_dashboard_context_panel_covers_complete_concept() -> None:
    html = render_dashboard_context_panel("gas-market-overview")
    no_related_html = render_dashboard_context_panel(
        "gas-market-overview",
        related_limit=0,
    )

    assert "Gas Market Overview" in html
    assert "generated-gold paths" in html
    assert "source chunk IDs" in html
    assert "backing assets" in html
    assert "tools/gas-market-knowledge-base/generated/gold/glossary/gas-day.md" in html
    assert "chunk-gbb-guide-gas-day" in html
    assert "silver.gas_model.silver_gas_fact_market_price" in html
    assert "Gas Day Context" in html
    assert "No related concepts share generated-gold paths" in no_related_html


def test_render_dashboard_context_panel_handles_missing_optional_fields() -> None:
    entry = DashboardRegistryEntry(
        concept_id="minimal-context",
        title="Minimal Context",
        description="Registry entry with only required context metadata.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.PLANNED,
        notebook_name=None,
        backing_assets=("silver.gas_model.minimal_table",),
        generated_gold_paths=(),
        source_chunks=(),
    )

    html = render_dashboard_context_panel("minimal-context", entries=(entry,))

    assert "Minimal Context" in html
    assert "No generated-gold paths recorded in the Marimo registry." in html
    assert "No source chunk IDs recorded in the Marimo registry." in html
    assert "No notebook route recorded" in html
    assert "silver.gas_model.minimal_table" in html


def test_render_dashboard_context_panel_includes_dashboard_usage_metadata() -> None:
    html = render_dashboard_context_panel("gbb-interactive-map")

    assert 'data-concept-id="gbb-interactive-map"' in html
    assert 'data-status="available"' in html
    assert 'data-notebook-name="gbb_interactive_map"' in html
    assert 'data-notebook-route="/marimo/gbb_interactive_map/"' in html
    assert "<dt>Audiences</dt>" in html
    assert "operator, analyst, stakeholder" in html
    assert "/marimo/gbb_interactive_map/" in html


def test_render_dashboard_context_panel_rejects_unknown_concept() -> None:
    with pytest.raises(DashboardRegistryError, match="concept not found"):
        render_dashboard_context_panel("missing-context")


def _source_coverage_load(
    table_name: str,
    dataframe: pl.DataFrame | None,
    *,
    error: str | None = None,
) -> GasTableLoad:
    return GasTableLoad(
        spec=GasTableSpec(
            section="Facts",
            label=table_name,
            table_name=table_name,
        ),
        uri=f"s3://bucket/silver/gas_model/{table_name}",
        dataframe=dataframe,
        error=error,
        row_limit=100,
        load_duration_seconds=0.01,
        cache_hit=False,
    )


def _system_notice_load(
    dataframe: pl.DataFrame,
    *,
    row_limit: int | None = None,
) -> GasTableLoad:
    return GasTableLoad(
        spec=SYSTEM_NOTICE_TABLE_SPEC,
        uri=f"s3://bucket/silver/gas_model/{SYSTEM_NOTICE_TABLE_NAME}",
        dataframe=dataframe,
        error=None,
        row_limit=row_limit,
        load_duration_seconds=0.01,
        cache_hit=False,
    )


def _gas_quality_load(
    dataframe: pl.DataFrame,
    *,
    row_limit: int | None = None,
) -> GasTableLoad:
    return GasTableLoad(
        spec=GAS_QUALITY_TABLE_SPEC,
        uri=f"s3://bucket/silver/gas_model/{GAS_QUALITY_TABLE_NAME}",
        dataframe=dataframe,
        error=None,
        row_limit=row_limit,
        load_duration_seconds=0.01,
        cache_hit=False,
    )


def _customer_transfer_load(
    dataframe: pl.DataFrame,
    *,
    row_limit: int | None = None,
) -> GasTableLoad:
    return GasTableLoad(
        spec=CUSTOMER_TRANSFER_TABLE_SPEC,
        uri=f"s3://bucket/silver/gas_model/{CUSTOMER_TRANSFER_TABLE_NAME}",
        dataframe=dataframe,
        error=None,
        row_limit=row_limit,
        load_duration_seconds=0.01,
        cache_hit=False,
    )


def _settlement_activity_load(
    dataframe: pl.DataFrame,
    *,
    row_limit: int | None = None,
) -> GasTableLoad:
    return GasTableLoad(
        spec=SETTLEMENT_ACTIVITY_TABLE_SPEC,
        uri=f"s3://bucket/silver/gas_model/{SETTLEMENT_ACTIVITY_TABLE_NAME}",
        dataframe=dataframe,
        error=None,
        row_limit=row_limit,
        load_duration_seconds=0.01,
        cache_hit=False,
    )


def _bid_stack_load(
    dataframe: pl.DataFrame,
    *,
    row_limit: int | None = None,
) -> GasTableLoad:
    return GasTableLoad(
        spec=BID_STACK_TABLE_SPEC,
        uri=f"s3://bucket/silver/gas_model/{BID_STACK_TABLE_NAME}",
        dataframe=dataframe,
        error=None,
        row_limit=row_limit,
        load_duration_seconds=0.01,
        cache_hit=False,
    )


def _market_price_load(
    dataframe: pl.DataFrame,
    *,
    row_limit: int | None = None,
) -> GasTableLoad:
    return GasTableLoad(
        spec=MARKET_PRICE_TABLE_SPEC,
        uri=f"s3://bucket/silver/gas_model/{MARKET_PRICE_TABLE_NAME}",
        dataframe=dataframe,
        error=None,
        row_limit=row_limit,
        load_duration_seconds=0.01,
        cache_hit=False,
    )


def _schedule_run_load(
    dataframe: pl.DataFrame,
    *,
    row_limit: int | None = None,
) -> GasTableLoad:
    return GasTableLoad(
        spec=SCHEDULE_RUN_TABLE_SPEC,
        uri=f"s3://bucket/silver/gas_model/{SCHEDULE_RUN_TABLE_SPEC.table_name}",
        dataframe=dataframe,
        error=None,
        row_limit=row_limit,
        load_duration_seconds=0.01,
        cache_hit=False,
    )


def _dashboard_config() -> GasDashboardConfig:
    return discover_dashboard_config(
        {
            "DEVELOPMENT_ENVIRONMENT": "dev",
            "NAME_PREFIX": "energy-market",
            "AWS_ENDPOINT_URL": "http://localstack:4566",
            "AWS_DEFAULT_REGION": "ap-southeast-4",
            "AWS_ACCESS_KEY_ID": "test",
            "AWS_SECRET_ACCESS_KEY": "test",
            "AWS_ALLOW_HTTP": "true",
        }
    )
