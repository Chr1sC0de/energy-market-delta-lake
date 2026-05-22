"""Component tests for the gas market dashboard helper surface."""

from collections.abc import Mapping
from datetime import date, datetime, timedelta
from types import SimpleNamespace
from typing import Self

import polars as pl
import pytest

from marimoserver.bounded_read_diagnostics import dashboard_read_behavior_frame
from marimoserver.citation_chain_explorer import (
    build_citation_chain_explorer,
    render_citation_chain_explorer_html,
)
from marimoserver.concept_asset_explorer import (
    build_concept_asset_explorer,
    concept_mapping_by_title,
    render_concept_asset_explorer_html,
    table_name_from_asset_id,
    table_explorer_route_for_asset,
)
from marimoserver.gas_dashboard import (
    BID_STACK_FACILITY_FILTER_ALL,
    BID_STACK_PARTICIPANT_FILTER_ALL,
    BID_STACK_SOURCE_SYSTEM_FILTER_ALL,
    BID_STACK_TABLE_NAME,
    BID_STACK_TABLE_SPEC,
    BID_STACK_ZONE_FILTER_ALL,
    STTM_CONTINGENCY_GAS_GRAIN_FILTER_ALL,
    STTM_CONTINGENCY_GAS_HUB_FILTER_ALL,
    STTM_CONTINGENCY_GAS_QUANTITY_TYPE_FILTER_ALL,
    STTM_CONTINGENCY_GAS_SOURCE_SYSTEM_FILTER_ALL,
    STTM_CONTINGENCY_GAS_TABLE_NAME,
    STTM_CONTINGENCY_GAS_TABLE_SPEC,
    CUSTOMER_TRANSFER_GAS_DATE_FILTER_ALL,
    CUSTOMER_TRANSFER_MARKET_CODE_FILTER_ALL,
    CUSTOMER_TRANSFER_SOURCE_SYSTEM_FILTER_ALL,
    CUSTOMER_TRANSFER_TABLE_NAME,
    CUSTOMER_TRANSFER_TABLE_SPEC,
    CONNECTION_POINT_CONTEXT_ID,
    CONNECTION_POINT_DIM_TABLE_NAME,
    CONNECTION_POINT_FLOW_TABLE_NAME,
    CONNECTION_POINT_TABLE_SPECS,
    CAPACITY_CONTEXT_ID,
    CAPACITY_AUCTION_CONTEXT_ID,
    CAPACITY_AUCTION_SOURCE_SYSTEM_FILTER_ALL,
    CAPACITY_AUCTION_TABLE_NAME,
    CAPACITY_AUCTION_TABLE_SPEC,
    CAPACITY_TRANSACTION_CONTEXT_ID,
    CAPACITY_TRANSACTION_SOURCE_SYSTEM_FILTER_ALL,
    CAPACITY_TRANSACTION_TABLE_NAME,
    CAPACITY_TRANSACTION_TABLE_SPEC,
    CAPACITY_OUTLOOK_FACILITY_FILTER_ALL,
    CAPACITY_OUTLOOK_SOURCE_SYSTEM_FILTER_ALL,
    CAPACITY_OUTLOOK_TABLE_NAME,
    CAPACITY_OUTLOOK_TABLE_SPEC,
    GAS_MODEL_TABLES,
    GAS_DAY_CONTEXT_ID,
    GAS_QUALITY_QUALITY_TYPE_FILTER_ALL,
    GAS_QUALITY_SOURCE_POINT_FILTER_ALL,
    GAS_QUALITY_TABLE_NAME,
    GAS_QUALITY_TABLE_SPEC,
    HEATING_VALUE_PRESSURE_CONTEXT_ID,
    HEATING_VALUE_PRESSURE_IDENTIFIER_FILTER_ALL,
    HEATING_VALUE_PRESSURE_SOURCE_SYSTEM_FILTER_ALL,
    HEATING_VALUE_PRESSURE_SOURCE_TABLE_FILTER_ALL,
    HEATING_VALUE_TABLE_NAME,
    HEATING_VALUE_TABLE_SPEC,
    HUB_ZONE_CONTEXT_ID,
    HUB_ZONE_DIM_TABLE_NAME,
    HUB_ZONE_TABLE_SPECS,
    LOCATION_DIM_TABLE_NAME,
    LINEPACK_ADEQUACY_FLAG_FILTER_ALL,
    LINEPACK_CONTEXT_ID,
    LINEPACK_FACILITY_FILTER_ALL,
    LINEPACK_GAS_DATE_FILTER_ALL,
    LINEPACK_SOURCE_SYSTEM_FILTER_ALL,
    LINEPACK_TABLE_NAME,
    LINEPACK_TABLE_SPEC,
    LINEPACK_ZONE_FILTER_ALL,
    FACILITY_CAPACITY_OUTLOOK_TABLE_NAME,
    FACILITY_CONTEXT_ID,
    FACILITY_DIM_TABLE_NAME,
    FACILITY_FLOW_STORAGE_CONTEXT_ID,
    FACILITY_FLOW_STORAGE_FACILITY_FILTER_ALL,
    FACILITY_FLOW_STORAGE_GAS_DATE_FILTER_ALL,
    FACILITY_FLOW_STORAGE_SOURCE_SYSTEM_FILTER_ALL,
    FACILITY_FLOW_STORAGE_TABLE_NAME,
    FACILITY_FLOW_STORAGE_TABLE_SPEC,
    FORECAST_ACTUAL_CONTEXT_ID,
    FORECAST_ACTUAL_FACILITY_FILTER_ALL,
    FORECAST_ACTUAL_GAS_DATE_FILTER_ALL,
    FORECAST_ACTUAL_SOURCE_SYSTEM_FILTER_ALL,
    FORECAST_ACTUAL_TABLE_SPECS,
    FACILITY_TABLE_SPECS,
    FLOW_CONTEXT_ID,
    FLOW_TABLE_SPECS,
    MARKET_PRICE_GAS_DATE_FILTER_ALL,
    MARKET_PRICE_PRICE_TYPE_FILTER_ALL,
    MARKET_PRICE_SOURCE_SYSTEM_FILTER_ALL,
    MARKET_PRICE_SOURCE_TABLE_FILTER_ALL,
    MARKET_PRICE_TABLE_NAME,
    MARKET_PRICE_TABLE_SPEC,
    NOMINATION_FORECAST_CONTEXT_ID,
    NOMINATION_FORECAST_FACILITY_FILTER_ALL,
    NOMINATION_FORECAST_GAS_DATE_FILTER_ALL,
    NOMINATION_FORECAST_LOCATION_FILTER_ALL,
    NOMINATION_FORECAST_SOURCE_SYSTEM_FILTER_ALL,
    NOMINATION_FORECAST_TABLE_NAME,
    NOMINATION_FORECAST_TABLE_SPEC,
    OPERATIONAL_METER_FLOW_CONTEXT_ID,
    OPERATIONAL_METER_FLOW_TABLE_SPECS,
    OPERATIONAL_METER_FLOW_TABLE_NAME,
    OPERATIONAL_POINT_DIM_TABLE_NAME,
    PARTICIPANT_CONTEXT_ID,
    PARTICIPANT_DIM_TABLE_NAME,
    PARTICIPANT_MARKET_MEMBERSHIP_TABLE_NAME,
    PARTICIPANT_TABLE_SPECS,
    PIPELINE_CONNECTION_OPERATIONS_CONTEXT_ID,
    PIPELINE_CONNECTION_OPERATIONS_TABLE_SPECS,
    PIPELINE_SEGMENT_DIM_TABLE_NAME,
    SCHEDULE_RUN_GAS_DATE_FILTER_ALL,
    SCHEDULE_RUN_SCHEDULE_TYPE_FILTER_ALL,
    SCHEDULE_RUN_SOURCE_SYSTEM_FILTER_ALL,
    SCHEDULE_RUN_TABLE_SPEC,
    SCHEDULED_QUANTITY_GAS_DATE_FILTER_ALL,
    SCHEDULED_QUANTITY_SCHEDULE_TYPE_FILTER_ALL,
    SCHEDULED_QUANTITY_SOURCE_SYSTEM_FILTER_ALL,
    SCHEDULED_QUANTITY_TABLE_NAME,
    SCHEDULED_QUANTITY_TABLE_SPEC,
    SCADA_PRESSURE_TABLE_NAME,
    SCADA_PRESSURE_TABLE_SPEC,
    SETTLEMENT_ACTIVITY_ACTIVITY_TYPE_FILTER_ALL,
    SETTLEMENT_ACTIVITY_GAS_DATE_FILTER_ALL,
    SETTLEMENT_ACTIVITY_SOURCE_SYSTEM_FILTER_ALL,
    SETTLEMENT_ACTIVITY_TABLE_NAME,
    SETTLEMENT_ACTIVITY_TABLE_SPEC,
    STTM_CAPACITY_SETTLEMENT_COMPONENT_FILTER_ALL,
    STTM_CAPACITY_SETTLEMENT_FACILITY_FILTER_ALL,
    STTM_CAPACITY_SETTLEMENT_GAS_DATE_FILTER_ALL,
    STTM_CAPACITY_SETTLEMENT_HUB_FILTER_ALL,
    STTM_CAPACITY_SETTLEMENT_STAGE_FILTER_ALL,
    STTM_CAPACITY_SETTLEMENT_TABLE_NAME,
    STTM_CAPACITY_SETTLEMENT_TABLE_SPEC,
    STTM_ALLOCATION_LIMIT_TABLE_NAME,
    STTM_ALLOCATION_LIMIT_TABLE_SPEC,
    STTM_ALLOCATION_QUANTITY_TABLE_NAME,
    STTM_ALLOCATION_QUANTITY_TABLE_SPEC,
    STTM_MARKET_SETTLEMENT_COMPONENT_FILTER_ALL,
    STTM_MARKET_SETTLEMENT_GAS_DATE_FILTER_ALL,
    STTM_MARKET_SETTLEMENT_PERIOD_FILTER_ALL,
    STTM_MARKET_SETTLEMENT_STAGE_FILTER_ALL,
    STTM_MARKET_SETTLEMENT_TABLE_NAME,
    STTM_MARKET_SETTLEMENT_TABLE_SPEC,
    STTM_MOS_ALLOCATION_CONTEXT_ID,
    STTM_MOS_ALLOCATION_FACILITY_FILTER_ALL,
    STTM_MOS_ALLOCATION_GAS_DATE_FILTER_ALL,
    STTM_MOS_ALLOCATION_HUB_FILTER_ALL,
    STTM_MOS_ALLOCATION_SOURCE_SYSTEM_FILTER_ALL,
    STTM_MOS_ALLOCATION_TABLE_SPECS,
    STTM_MOS_STACK_TABLE_NAME,
    STTM_MOS_STACK_TABLE_SPEC,
    STTM_DEFAULT_ALLOCATION_NOTICE_TABLE_NAME,
    STTM_DEFAULT_ALLOCATION_NOTICE_TABLE_SPEC,
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
    cached_load_capacity_auction_table,
    cached_load_capacity_transaction_table,
    cached_load_capacity_outlook_table,
    cached_load_sttm_contingency_gas_table,
    cached_load_connection_point_context_tables,
    cached_load_facility_context_tables,
    cached_load_facility_flow_storage_table,
    cached_load_forecast_actual_tables,
    cached_load_flow_context_tables,
    cached_load_gas_day_tables,
    cached_load_hub_zone_context_tables,
    cached_load_gas_quality_table,
    cached_load_heating_value_pressure_tables,
    cached_load_linepack_table,
    cached_load_gas_model_tables,
    cached_load_market_price_table,
    cached_load_nomination_forecast_table,
    cached_load_operational_meter_flow_tables,
    cached_load_participant_context_tables,
    cached_load_pipeline_connection_operations_tables,
    cached_load_schedule_run_table,
    cached_load_scheduled_quantity_table,
    cached_load_settlement_activity_table,
    cached_load_sttm_capacity_settlement_table,
    cached_load_sttm_market_settlement_table,
    cached_load_sttm_mos_allocation_tables,
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
    capacity_auction_auction_date_options,
    capacity_auction_capacity_period_options,
    capacity_auction_empty_state_markdown,
    capacity_auction_kpi_frame,
    capacity_auction_metric_frame,
    capacity_auction_metric_options,
    capacity_auction_observation_frame,
    capacity_auction_source_system_options,
    capacity_auction_summary_frame,
    capacity_auction_zone_options,
    capacity_transaction_date_options,
    capacity_transaction_empty_state_markdown,
    capacity_transaction_facility_options,
    capacity_transaction_kpi_frame,
    capacity_transaction_location_options,
    capacity_transaction_observation_frame,
    capacity_transaction_source_coverage_frame,
    capacity_transaction_source_system_options,
    capacity_transaction_summary_frame,
    capacity_transaction_type_options,
    capacity_outlook_capacity_type_options,
    capacity_outlook_date_range_options,
    capacity_outlook_direction_options,
    capacity_outlook_empty_state_markdown,
    capacity_outlook_facility_options,
    capacity_outlook_kpi_frame,
    capacity_outlook_observation_frame,
    capacity_outlook_source_coverage_frame,
    capacity_outlook_source_coverage_options,
    capacity_outlook_source_system_options,
    capacity_outlook_summary_frame,
    connection_point_context_empty_state_markdown,
    connection_point_dimension_coverage_frame,
    connection_point_dimension_preview_frame,
    connection_point_relationship_frame,
    connection_point_source_system_frame,
    connection_point_table_specs,
    discover_dashboard_config,
    facility_context_empty_state_markdown,
    facility_dimension_coverage_frame,
    facility_dimension_preview_frame,
    facility_flow_storage_daily_frame,
    facility_flow_storage_empty_state_markdown,
    facility_flow_storage_facility_options,
    facility_flow_storage_gas_date_options,
    facility_flow_storage_kpi_frame,
    facility_flow_storage_observation_frame,
    facility_flow_storage_source_coverage_frame,
    facility_flow_storage_source_system_options,
    facility_flow_storage_summary_frame,
    facility_relationship_frame,
    facility_table_specs,
    forecast_actual_bounded_scope_markdown,
    forecast_actual_comparison_frame,
    forecast_actual_empty_state_markdown,
    forecast_actual_facility_options,
    forecast_actual_gas_date_options,
    forecast_actual_kpi_frame,
    forecast_actual_source_system_options,
    forecast_actual_storage_frame,
    flow_context_empty_state_markdown,
    flow_kpi_frame,
    flow_recent_observation_frame,
    flow_source_summary_frame,
    flow_table_specs,
    gas_quality_empty_state_markdown,
    gas_quality_kpi_frame,
    gas_quality_observation_frame,
    gas_quality_quality_type_options,
    gas_quality_source_coverage_frame,
    gas_quality_source_point_options,
    gas_quality_type_summary_frame,
    heating_value_observation_frame,
    heating_value_pressure_empty_state_markdown,
    heating_value_pressure_field_summary_frame,
    heating_value_pressure_identifier_frame,
    heating_value_pressure_identifier_options,
    heating_value_pressure_kpi_frame,
    heating_value_pressure_source_coverage_frame,
    heating_value_pressure_source_system_options,
    heating_value_pressure_source_table_options,
    gas_day_bounded_examples_frame,
    gas_day_examples_empty_state_markdown,
    gas_day_field_discovery_frame,
    gas_day_kpi_frame,
    gas_day_table_specs,
    gas_table_load_status_frame,
    gas_table_load_status_message,
    hub_zone_context_empty_state_markdown,
    hub_zone_dimension_coverage_frame,
    hub_zone_identifier_preview_frame,
    hub_zone_source_system_frame,
    hub_zone_table_specs,
    load_market_price_table,
    load_bid_stack_table,
    load_capacity_auction_table,
    load_capacity_transaction_table,
    load_capacity_outlook_table,
    load_sttm_contingency_gas_table,
    load_connection_point_context_tables,
    load_customer_transfer_table,
    load_facility_context_tables,
    load_facility_flow_storage_table,
    load_forecast_actual_tables,
    load_flow_context_tables,
    load_gas_day_tables,
    load_hub_zone_context_tables,
    load_gas_quality_table,
    load_heating_value_pressure_tables,
    load_linepack_table,
    load_gas_model_tables,
    load_nomination_forecast_table,
    load_operational_meter_flow_tables,
    load_participant_context_tables,
    load_pipeline_connection_operations_tables,
    load_source_coverage_tables,
    load_schedule_run_table,
    load_scheduled_quantity_table,
    load_settlement_activity_table,
    load_sttm_capacity_settlement_table,
    load_sttm_market_settlement_table,
    load_sttm_mos_allocation_tables,
    load_system_notice_table,
    market_price_bounded_scope_markdown,
    market_price_empty_state_markdown,
    market_price_exception_frame,
    market_price_gas_date_options,
    market_price_kpi_frame,
    market_price_observation_frame,
    market_price_price_type_options,
    market_price_source_system_options,
    market_price_source_table_options,
    market_price_trend_diagnostic_frame,
    market_price_trend_frame,
    market_price_type_summary_frame,
    linepack_adequacy_flag_options,
    linepack_empty_state_markdown,
    linepack_facility_options,
    linepack_gas_date_options,
    linepack_kpi_frame,
    linepack_observation_frame,
    linepack_source_coverage_frame,
    linepack_source_system_options,
    linepack_summary_frame,
    linepack_zone_options,
    nomination_forecast_daily_frame,
    nomination_forecast_empty_state_markdown,
    nomination_forecast_facility_options,
    nomination_forecast_gas_date_options,
    nomination_forecast_kpi_frame,
    nomination_forecast_location_options,
    nomination_forecast_observation_frame,
    nomination_forecast_source_coverage_frame,
    nomination_forecast_source_system_options,
    nomination_forecast_summary_frame,
    operational_meter_flow_empty_state_markdown,
    operational_meter_flow_kpi_frame,
    operational_meter_flow_point_context_frame,
    operational_meter_flow_relationship_gap_frame,
    operational_meter_flow_summary_frame,
    operational_meter_flow_table_specs,
    participant_context_empty_state_markdown,
    participant_dimension_coverage_frame,
    participant_dimension_preview_frame,
    participant_membership_coverage_frame,
    participant_membership_preview_frame,
    participant_related_market_fact_frame,
    participant_table_specs,
    pipeline_connection_flow_summary_frame,
    pipeline_connection_metadata_frame,
    pipeline_connection_operations_empty_state_markdown,
    pipeline_connection_operations_kpi_frame,
    pipeline_connection_operations_table_specs,
    pipeline_connection_relationship_gap_frame,
    read_parquet_table,
    render_dashboard_context_panel,
    render_bid_stack_context_links,
    render_capacity_auction_context_links,
    render_capacity_transaction_context_links,
    render_capacity_outlook_context_links,
    render_connection_point_context_links,
    render_customer_transfer_context_links,
    render_market_price_context_links,
    render_nomination_forecast_context_links,
    render_facility_context_links,
    render_facility_flow_storage_context_links,
    render_forecast_actual_context_links,
    render_flow_context_links,
    render_heating_value_pressure_context_links,
    render_hub_zone_context_links,
    render_linepack_context_links,
    render_operational_meter_flow_context_links,
    render_participant_context_links,
    render_pipeline_connection_operations_context_links,
    render_schedule_run_context_links,
    render_scheduled_quantity_context_links,
    render_settlement_activity_context_links,
    render_sttm_capacity_settlement_context_links,
    render_sttm_contingency_gas_context_links,
    render_sttm_market_settlement_context_links,
    render_sttm_mos_allocation_context_links,
    render_source_coverage_matrix_html,
    scada_pressure_observation_frame,
    schedule_run_empty_state_markdown,
    schedule_run_gas_date_options,
    schedule_run_kpi_frame,
    schedule_run_observation_frame,
    schedule_run_schedule_type_options,
    schedule_run_source_coverage_frame,
    schedule_run_source_system_options,
    schedule_run_timestamp_summary_frame,
    schedule_run_type_summary_frame,
    scheduled_quantity_empty_state_markdown,
    scheduled_quantity_gas_date_options,
    scheduled_quantity_kpi_frame,
    scheduled_quantity_observation_frame,
    scheduled_quantity_schedule_context_frame,
    scheduled_quantity_schedule_type_options,
    scheduled_quantity_source_coverage_frame,
    scheduled_quantity_source_point_frame,
    scheduled_quantity_source_system_options,
    scheduled_quantity_type_summary_frame,
    settlement_activity_activity_type_options,
    settlement_activity_empty_state_markdown,
    settlement_activity_gas_date_options,
    settlement_activity_kpi_frame,
    settlement_activity_observation_frame,
    settlement_activity_source_coverage_frame,
    settlement_activity_source_system_options,
    settlement_activity_summary_frame,
    sttm_capacity_settlement_component_options,
    sttm_capacity_settlement_empty_state_markdown,
    sttm_capacity_settlement_facility_options,
    sttm_capacity_settlement_gas_date_options,
    sttm_capacity_settlement_hub_options,
    sttm_capacity_settlement_kpi_frame,
    sttm_capacity_settlement_observation_frame,
    sttm_capacity_settlement_source_coverage_frame,
    sttm_capacity_settlement_stage_options,
    sttm_capacity_settlement_summary_frame,
    sttm_allocation_limit_summary_frame,
    sttm_allocation_quantity_summary_frame,
    sttm_default_allocation_notice_summary_frame,
    sttm_mos_allocation_empty_state_markdown,
    sttm_mos_allocation_facility_options,
    sttm_mos_allocation_fact_summary_frame,
    sttm_mos_allocation_gas_date_options,
    sttm_mos_allocation_hub_options,
    sttm_mos_allocation_kpi_frame,
    sttm_mos_allocation_source_coverage_frame,
    sttm_mos_allocation_source_system_options,
    sttm_mos_stack_summary_frame,
    sttm_market_settlement_component_options,
    sttm_market_settlement_empty_state_markdown,
    sttm_market_settlement_gas_date_options,
    sttm_market_settlement_kpi_frame,
    sttm_market_settlement_observation_frame,
    sttm_market_settlement_period_options,
    sttm_market_settlement_source_coverage_frame,
    sttm_market_settlement_stage_options,
    sttm_market_settlement_summary_frame,
    source_coverage_empty_state_markdown,
    source_coverage_kpi_frame,
    source_coverage_matrix_frame,
    source_coverage_table_specs_from_catalogue,
    source_coverage_table_specs,
    sttm_contingency_gas_bid_offer_summary_frame,
    sttm_contingency_gas_empty_state_markdown,
    sttm_contingency_gas_grain_options,
    sttm_contingency_gas_grain_summary_frame,
    sttm_contingency_gas_hub_options,
    sttm_contingency_gas_kpi_frame,
    sttm_contingency_gas_observation_frame,
    sttm_contingency_gas_quantity_type_options,
    sttm_contingency_gas_source_summary_frame,
    sttm_contingency_gas_source_system_options,
    system_notice_empty_state_markdown,
    system_notice_kpi_frame,
    system_notice_source_coverage_frame,
    system_notice_summary_frame,
    table_load_by_name,
    _dataframe_min_value,
    _latest_datetime,
    _optional_float,
)
from marimoserver.dashboard_registry import (
    DashboardAudience,
    DashboardRegistryEntry,
    DashboardRegistryError,
    DashboardStatus,
    SourceChunkReference,
    registry_entry_by_concept_id,
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
from marimoserver.source_lineage_explorer import (
    render_source_lineage_explorer_html,
    source_lineage_empty_state_markdown,
    source_lineage_frame,
    source_lineage_kpi_frame,
)
from marimoserver.table_explorer import (
    CataloguedTable,
    TableAvailability,
    discover_table_explorer_config,
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


def test_dashboard_read_behavior_frame_renders_per_dashboard_policy() -> None:
    environment = {
        "DEVELOPMENT_LOCATION": "aws",
        "AEMO_BUCKET": "prod-energy-market-aemo",
        "MARIMO_TABLE_BUCKETS": "prod-energy-market-aemo, prod-energy-market-io",
        "MARIMO_MAX_PREVIEW_ROWS": "42",
    }
    gas_config = discover_dashboard_config(environment)
    table_config = discover_table_explorer_config(environment)

    rows = {
        row["dashboard"]: row
        for row in dashboard_read_behavior_frame(gas_config, table_config).to_dicts()
    }

    assert rows["AWS Bounded Read Diagnostics"]["read behavior"] == (
        "Configuration and registry metadata only"
    )
    assert rows["AWS Bounded Read Diagnostics"]["row policy"] == "No table-row reads"
    assert rows["Concept-to-Asset Explorer"]["read behavior"] == (
        "Registry metadata browser"
    )
    assert rows["Concept-to-Asset Explorer"]["row policy"] == "No table-row reads"
    assert rows["Citation-Chain Explorer"]["read behavior"] == (
        "Registry metadata browser"
    )
    assert rows["Citation-Chain Explorer"]["row policy"] == "No table-row reads"
    assert rows["S3 Bucket Health"]["view"] == "Object listing"
    assert rows["S3 Bucket Health"]["row policy"] == "10,000 objects per bucket"
    assert rows["Gas Model Table Explorer"]["row policy"] == (
        "Bounded preview: 42 rows max"
    )
    assert rows["Gas Market Prices"]["view"] == "Recent-only bounded view"
    assert rows["Gas Market Prices"]["row policy"] == ("Bounded preview: 42 rows max")
    assert rows["Forecast Vs Actual Flow And Storage"]["read behavior"] == (
        "Focused gas_model dashboard table read"
    )
    assert rows["Forecast Vs Actual Flow And Storage"]["view"] == (
        "Recent-only bounded view"
    )
    assert rows["Forecast Vs Actual Flow And Storage"]["row policy"] == (
        "Bounded preview: 42 rows max"
    )
    assert rows["STTM Contingency Gas"]["read behavior"] == (
        "Focused gas_model dashboard table read"
    )
    assert rows["STTM Contingency Gas"]["view"] == "Recent-only bounded view"
    assert rows["STTM Contingency Gas"]["row policy"] == (
        "Bounded preview: 42 rows max"
    )
    assert rows["STTM Market Settlement"]["read behavior"] == (
        "Focused gas_model dashboard table read"
    )
    assert rows["STTM Market Settlement"]["view"] == "Recent-only bounded view"
    assert rows["STTM Market Settlement"]["row policy"] == (
        "Bounded preview: 42 rows max"
    )
    assert rows["Source Coverage Matrix"]["view"] == "Forced bounded sample"
    assert rows["Source Coverage Matrix"]["row policy"] == (
        "Bounded preview: 42 rows max"
    )
    assert rows["Source Table Lineage Explorer"]["read behavior"] == (
        "Registry-backed source metadata inspection"
    )
    assert rows["Source Table Lineage Explorer"]["view"] == "Forced bounded sample"
    assert rows["Source Table Lineage Explorer"]["row policy"] == (
        "Bounded preview: 42 rows max"
    )
    assert rows["Gas Day Context"]["read behavior"] == (
        "Registry-backed Gas Day date-field inspection"
    )
    assert rows["Gas Day Context"]["view"] == "Forced bounded sample"
    assert rows["Gas Day Context"]["row policy"] == "Bounded preview: 42 rows max"
    assert rows["Facility Context"]["read behavior"] == (
        "Registry-backed Facility relationship inspection"
    )
    assert rows["Facility Context"]["view"] == "Forced bounded sample"
    assert rows["Facility Context"]["row policy"] == "Bounded preview: 42 rows max"


def test_dashboard_read_behavior_frame_forces_explainer_bounded_policy() -> None:
    environment = {
        "DEVELOPMENT_LOCATION": "aws",
        "AEMO_BUCKET": "prod-energy-market-aemo",
        "MARIMO_TABLE_BUCKETS": "prod-energy-market-aemo, prod-energy-market-io",
        "MARIMO_FULL_TABLE_SCAN_ENABLED": "true",
        "MARIMO_MAX_PREVIEW_ROWS": "42",
    }
    gas_config = discover_dashboard_config(environment)
    table_config = discover_table_explorer_config(environment)

    rows = {
        row["dashboard"]: row
        for row in dashboard_read_behavior_frame(gas_config, table_config).to_dicts()
    }

    assert rows["Participant Context"]["read behavior"] == (
        "Registry-backed Participant relationship inspection"
    )
    assert rows["Participant Context"]["view"] == "Forced bounded sample"
    assert rows["Participant Context"]["row policy"] == ("Bounded preview: 42 rows max")
    assert rows["Participant Context"]["scope"] == (
        f"{len(PARTICIPANT_TABLE_SPECS)} participant-oriented gas_model tables"
    )
    assert rows["Connection Point Context"]["read behavior"] == (
        "Registry-backed Connection Point relationship inspection"
    )
    assert rows["Connection Point Context"]["view"] == "Forced bounded sample"
    assert rows["Connection Point Context"]["row policy"] == (
        "Bounded preview: 42 rows max"
    )
    assert rows["Connection Point Context"]["scope"] == (
        f"{len(CONNECTION_POINT_TABLE_SPECS)} connection-point-oriented gas_model tables"
    )
    assert rows["Hub / Zone Context"]["read behavior"] == (
        "Registry-backed Hub / Zone relationship inspection"
    )
    assert rows["Hub / Zone Context"]["view"] == "Forced bounded sample"
    assert rows["Hub / Zone Context"]["row policy"] == ("Bounded preview: 42 rows max")
    assert rows["Hub / Zone Context"]["scope"] == (
        f"{len(HUB_ZONE_TABLE_SPECS)} hub/zone-oriented gas_model tables"
    )


def test_dashboard_read_behavior_frame_handles_unknown_available_dashboard() -> None:
    gas_config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "MARIMO_MAX_PREVIEW_ROWS": "33",
        }
    )
    table_config = discover_table_explorer_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "MARIMO_TABLE_BUCKETS": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "33",
        }
    )
    custom_entry = DashboardRegistryEntry(
        concept_id="custom-dashboard",
        title="Custom Dashboard",
        description="Custom available dashboard.",
        audiences=(DashboardAudience.OPERATOR,),
        status=DashboardStatus.AVAILABLE,
        notebook_name="custom_dashboard",
        backing_assets=(),
        generated_gold_paths=(),
        source_chunks=(),
    )

    rows = dashboard_read_behavior_frame(
        gas_config,
        table_config,
        entries=(custom_entry,),
    ).to_dicts()

    assert rows == [
        {
            "dashboard": "Custom Dashboard",
            "route": "/marimo/custom_dashboard/",
            "audience": "operator",
            "read behavior": "Dashboard-specific read behavior",
            "view": "See dashboard",
            "row policy": "Bounded preview: 33 rows max",
            "scope": "(none configured)",
            "side effects": "Read-only",
        }
    ]


def test_citation_chain_explorer_renders_complete_records() -> None:
    complete_entry = DashboardRegistryEntry(
        concept_id="complete-citation-context",
        title="Complete Citation Context",
        description="Concept with full citation chain metadata.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.AVAILABLE,
        notebook_name="complete_citation_context",
        backing_assets=("silver.gas_model.silver_gas_fact_market_price",),
        generated_gold_paths=(
            "tools/gas-market-knowledge-base/generated/gold/glossary/schedule.md",
        ),
        source_chunks=(
            SourceChunkReference(
                chunk_id="chunk-complete",
                silver_chunk_path=(
                    "tools/gas-market-knowledge-base/generated/silver/chunks/"
                    "sttm/procedure/sha256-source/chunk-complete.md"
                ),
                source_hash="source-hash",
            ),
        ),
    )

    explorer = build_citation_chain_explorer((complete_entry,))
    html = render_citation_chain_explorer_html(explorer)

    assert len(explorer.complete_concepts) == 1
    assert explorer.coverage_gap_count == 0
    assert 'data-coverage-state="complete"' in html
    assert "chunk-complete" in html
    assert "chunk-complete.md" in html
    assert "source-hash" in html


def test_citation_chain_explorer_uses_registry_metadata_by_default() -> None:
    explorer = build_citation_chain_explorer()
    html = render_citation_chain_explorer_html()
    concepts_by_id = {concept.concept_id: concept for concept in explorer.concepts}

    assert "citation-chain-explorer" in concepts_by_id
    assert concepts_by_id["gas-day-context"].complete
    assert concepts_by_id["citation-chain-explorer"].metadata_gaps == (
        "No source chunk IDs recorded in the Marimo registry.",
    )
    assert 'data-concept-id="gas-day-context"' in html
    assert "chunk-gbb-guide-gas-day" in html
    assert "chunk-gbb-guide-gas-day.md" in html
    assert "9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410" in html
    assert "No source chunks recorded in the Marimo registry." in html


def test_citation_chain_explorer_renders_incomplete_records_as_coverage_gaps() -> None:
    incomplete_entry = DashboardRegistryEntry(
        concept_id="incomplete-citation-context",
        title="Incomplete Citation Context",
        description="Concept missing generated-gold and source hash metadata.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.PLANNED,
        notebook_name=None,
        backing_assets=("silver.gas_model.silver_gas_fact_market_price",),
        generated_gold_paths=(),
        source_chunks=(SourceChunkReference(chunk_id="chunk-incomplete"),),
    )

    explorer = build_citation_chain_explorer((incomplete_entry,))
    html = render_citation_chain_explorer_html(explorer)

    assert explorer.complete_concepts == ()
    assert explorer.coverage_gap_count == 3
    assert 'data-coverage-state="gap"' in html
    assert "No generated-gold path recorded in the Marimo registry." in html
    assert "No silver chunk path recorded for `chunk-incomplete`." in html
    assert "No source hash recorded for `chunk-incomplete`." in html
    assert "No silver chunk path recorded" in html
    assert "No source hash recorded" in html


def test_gas_model_specs_cover_required_dashboard_sections() -> None:
    sections = {spec.section for spec in GAS_MODEL_TABLES}
    table_names = {spec.table_name for spec in GAS_MODEL_TABLES}

    assert {"Prices", "Schedules", "Flow and capacity"} <= sections
    assert "silver_gas_fact_market_price" in table_names
    assert "silver_gas_fact_schedule_run" in table_names
    assert "silver_gas_fact_scheduled_quantity" in table_names
    assert "silver_gas_fact_connection_point_flow" in table_names
    assert "silver_gas_fact_capacity_outlook" in table_names


def test_concept_asset_explorer_maps_concepts_to_assets_and_routes() -> None:
    explorer = build_concept_asset_explorer()
    flow = concept_mapping_by_title(explorer, "Flow")

    assert flow is not None
    assert flow.mapped
    assert any(
        asset.asset_id == "silver.gas_model.silver_gas_fact_connection_point_flow"
        and asset.table_explorer_route
        == (
            "/marimo/table_explorer/?asset=asset%3Asilver%2Fgas_model%2F"
            "silver_gas_fact_connection_point_flow"
        )
        for asset in flow.assets
    )
    assert any(
        dashboard.title == "GBB Interactive Map"
        and dashboard.navigation_route == "/marimo/gbb_interactive_map/"
        for dashboard in flow.available_dashboards
    )
    assert any(
        dashboard.concept_id == "flow-context"
        and dashboard.navigation_route == "/marimo/flow_operations/"
        for dashboard in flow.available_dashboards
    )

    html = render_concept_asset_explorer_html(explorer)

    assert 'data-concept-count="13"' in html
    assert 'data-coverage-state="mapped"' in html
    assert 'data-link-scope="table explorer entry"' in html
    assert "silver.gas_model.silver_gas_fact_connection_point_flow" in html


def test_concept_asset_explorer_marks_unmapped_concepts_as_coverage_gaps() -> None:
    empty_context = DashboardRegistryEntry(
        concept_id="empty-context",
        title="Empty Context",
        description="Concept with citation metadata but no backing assets.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.PLANNED,
        notebook_name=None,
        backing_assets=(),
        generated_gold_paths=(
            "tools/gas-market-knowledge-base/generated/gold/glossary/empty.md",
        ),
        source_chunks=(SourceChunkReference("chunk-empty"),),
    )

    explorer = build_concept_asset_explorer((empty_context,))
    html = render_concept_asset_explorer_html(explorer)

    assert [concept.title for concept in explorer.unmapped_concepts] == ["Empty"]
    assert explorer.unmapped_concepts[0].metadata_gaps == (
        "No backing silver.gas_model assets are mapped to this concept.",
    )
    assert 'data-coverage-state="unmapped-concept"' in html
    assert 'data-gap-kind="unmapped-concepts"' in html
    assert "No backing silver.gas_model assets are mapped to this concept." in html


def test_concept_asset_explorer_marks_unmapped_assets_as_coverage_gaps() -> None:
    mapped_entry = DashboardRegistryEntry(
        concept_id="flow-context",
        title="Flow Context",
        description="Flow concept with a mapped table asset.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.PLANNED,
        notebook_name=None,
        backing_assets=("silver.gas_model.silver_gas_fact_connection_point_flow",),
        generated_gold_paths=(
            "tools/gas-market-knowledge-base/generated/gold/glossary/flow.md",
        ),
        source_chunks=(),
    )
    unmapped_entry = DashboardRegistryEntry(
        concept_id="gas-quality-composition",
        title="Gas Quality And Composition",
        description="Dashboard asset without generated glossary metadata.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.AVAILABLE,
        notebook_name="gas_quality_composition",
        backing_assets=("silver.gas_model.silver_gas_fact_gas_quality",),
        generated_gold_paths=(),
        source_chunks=(),
    )

    explorer = build_concept_asset_explorer((mapped_entry, unmapped_entry))
    flow = concept_mapping_by_title(explorer, "Flow")

    assert flow is not None
    assert [asset.asset_id for asset in flow.assets] == [
        "silver.gas_model.silver_gas_fact_connection_point_flow"
    ]
    assert [asset.asset_id for asset in explorer.unmapped_assets] == [
        "silver.gas_model.silver_gas_fact_gas_quality"
    ]
    assert explorer.unmapped_assets[0].table_explorer_route == (
        "/marimo/table_explorer/?asset=asset%3Asilver%2Fgas_model%2F"
        "silver_gas_fact_gas_quality"
    )
    assert table_explorer_route_for_asset("bronze.raw.table") is None
    assert "silver.gas_model.silver_gas_fact_gas_quality" in (
        render_concept_asset_explorer_html(explorer)
    )


def test_concept_asset_explorer_renders_missing_path_and_link_fallbacks() -> None:
    fallback_entry = DashboardRegistryEntry(
        concept_id="fallback-context",
        title="Fallback Context",
        description="Concept with a registry asset but missing citation metadata.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.PLANNED,
        notebook_name=None,
        backing_assets=("silver.gas_model.",),
        generated_gold_paths=(),
        source_chunks=(),
    )

    explorer = build_concept_asset_explorer((fallback_entry,))
    html = render_concept_asset_explorer_html(explorer)

    assert concept_mapping_by_title(explorer, "missing") is None
    assert table_name_from_asset_id("silver.gas_model.") is None
    assert explorer.unmapped_concepts == ()
    assert explorer.unmapped_assets == ()
    assert 'data-unmapped-concept-count="0"' in html
    assert 'data-unmapped-asset-count="0"' in html
    assert "No table explorer link" in html
    assert "No generated-gold path recorded in the registry." in html


def test_concept_asset_explorer_renders_unmapped_asset_without_table_link() -> None:
    unmapped_entry = DashboardRegistryEntry(
        concept_id="unsupported-dashboard",
        title="Unsupported Dashboard",
        description="Dashboard with a malformed asset ID fixture.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.AVAILABLE,
        notebook_name="unsupported_dashboard",
        backing_assets=("silver.gas_model.invalid/path",),
        generated_gold_paths=(),
        source_chunks=(),
    )

    explorer = build_concept_asset_explorer((unmapped_entry,))
    html = render_concept_asset_explorer_html(explorer)

    assert explorer.concept_mappings == ()
    assert table_name_from_asset_id("silver.gas_model.invalid/path") is None
    assert [asset.table_explorer_route for asset in explorer.unmapped_assets] == [None]
    assert 'data-unmapped-asset-count="1"' in html
    assert "No table explorer link" in html


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

    assert market_price_gas_date_options(load) == (
        MARKET_PRICE_GAS_DATE_FILTER_ALL,
        "2024-01-02",
        "2024-01-01",
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
    assert market_price_kpi_frame(load, gas_date_filter="2024-01-01").row(
        0,
        named=True,
    ) == {
        "metric": "Loaded price rows",
        "value": "1",
        "detail": "Full table scan",
    }
    assert 'href="/marimo/gas_market_prices/"' in context_links
    assert 'href="/marimo/sample_energy_market/"' in context_links
    assert "Schedule Context" in context_links
    assert "Planned dashboard" in context_links


def test_market_price_bounded_trend_and_exception_helpers_label_scope() -> None:
    sttm_table = "silver.sttm.silver_int651_v1_ex_ante_market_price_rpt_1"
    vicgas_table = "silver.vicgas.silver_int042_v4_weighted_average_daily_prices_1"
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "MARIMO_MAX_PREVIEW_ROWS": "7",
        }
    )
    load = _market_price_load(
        pl.DataFrame(
            {
                "gas_date": [
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-04",
                    "2024-01-03",
                ],
                "source_system": ["STTM", "STTM", "STTM", "STTM", "VICGAS"],
                "source_table": [
                    sttm_table,
                    sttm_table,
                    sttm_table,
                    sttm_table,
                    vicgas_table,
                ],
                "price_type": [
                    "ex_ante_market_price",
                    "ex_ante_market_price",
                    "ex_ante_market_price",
                    "ex_ante_market_price",
                    "weighted_average_daily",
                ],
                "price_value_gst_ex": [10.0, 12.0, -4.0, None, None],
                "weighted_average_price_gst_ex": [None, None, None, None, 0.0],
            }
        ),
        row_limit=7,
    )

    bounded_scope = market_price_bounded_scope_markdown(config, load)
    diagnostics = market_price_trend_diagnostic_frame(load)
    exception_candidates = market_price_exception_frame(load)
    missing_measure_candidates = market_price_exception_frame(
        load,
        gas_date_filter="2024-01-04",
    )

    assert "AWS mode uses sampled/recent-only bounded reads" in bounded_scope
    assert "Bounded preview reads are capped at `7` rows per table" in bounded_scope
    assert diagnostics.select(
        "source system",
        "source table",
        "price type",
        "measure",
        "gas days",
        "observations",
        "first gas date",
        "latest gas date",
        "first avg price",
        "latest avg price",
        "bounded change",
        "bounded change %",
        "min observed price",
        "max observed price",
    ).head(1).to_dict(as_series=False) == {
        "source system": ["STTM"],
        "source table": [sttm_table],
        "price type": ["ex_ante_market_price"],
        "measure": ["price_value_gst_ex"],
        "gas days": [3],
        "observations": [3],
        "first gas date": [date(2024, 1, 1)],
        "latest gas date": [date(2024, 1, 3)],
        "first avg price": [10.0],
        "latest avg price": [-4.0],
        "bounded change": [-14.0],
        "bounded change %": [-140.0],
        "min observed price": [-4.0],
        "max observed price": [12.0],
    }
    assert exception_candidates.select(
        "candidate",
        "gas date",
        "source system",
        "price type",
        "measure",
        "value",
    ).head(3).to_dict(as_series=False) == {
        "candidate": [
            "Negative price value",
            "Missing price measures",
            "Zero price value",
        ],
        "gas date": [date(2024, 1, 3), date(2024, 1, 4), date(2024, 1, 3)],
        "source system": ["STTM", "STTM", "VICGAS"],
        "price type": [
            "ex_ante_market_price",
            "ex_ante_market_price",
            "weighted_average_daily",
        ],
        "measure": [
            "price_value_gst_ex",
            "none",
            "weighted_average_price_gst_ex",
        ],
        "value": [-4.0, None, 0.0],
    }
    assert missing_measure_candidates.select(
        "candidate",
        "measure",
        "bounded comparison",
    ).to_dict(as_series=False) == {
        "candidate": ["Missing price measures"],
        "measure": ["none"],
        "bounded comparison": ["No populated price measure columns"],
    }


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
    assert market_price_trend_diagnostic_frame(empty_load).is_empty()
    assert market_price_exception_frame(empty_load).is_empty()
    assert market_price_observation_frame(empty_load).is_empty()
    assert market_price_gas_date_options(empty_load) == (
        MARKET_PRICE_GAS_DATE_FILTER_ALL,
    )
    assert market_price_price_type_options(empty_load) == (
        MARKET_PRICE_PRICE_TYPE_FILTER_ALL,
    )
    assert market_price_trend_diagnostic_frame(no_measure_load).is_empty()
    assert market_price_exception_frame(populated_load).is_empty()
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
    local_scope_markdown = market_price_bounded_scope_markdown(
        _dashboard_config(),
        populated_load,
    )
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
    assert "Local mode uses the configured gas dashboard read policy" in (
        local_scope_markdown
    )
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


def test_scheduled_quantity_table_loader_uses_bounded_recent_view() -> None:
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
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_scheduled_quantity"
        )
        assert storage_options == config.storage_options()
        return pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 1), date(2024, 1, 3)],
                "quantity_type": ["older_quantity", "newer_quantity"],
                "source_last_updated_timestamp": [
                    datetime(2024, 1, 1, 6),
                    datetime(2024, 1, 3, 6),
                ],
            }
        )

    load = load_scheduled_quantity_table(config, reader=reader)

    assert captured == [8]
    assert load.spec == SCHEDULED_QUANTITY_TABLE_SPEC
    assert load.row_limit == 8
    assert load.dataframe is not None
    assert load.dataframe["quantity_type"].to_list() == [
        "newer_quantity",
        "older_quantity",
    ]


def test_cached_scheduled_quantity_table_loader_reuses_session_cache() -> None:
    calls: list[int] = []
    config = _dashboard_config()
    cache: GasModelSessionCache = {}

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        calls.append(len(calls) + 1)
        return pl.DataFrame({"quantity_type": [f"quantity-{calls[-1]}"]})

    first_load = cached_load_scheduled_quantity_table(config, cache, reader=reader)
    cached_load = cached_load_scheduled_quantity_table(config, cache, reader=reader)
    refreshed_load = cached_load_scheduled_quantity_table(
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
    assert cached_load.dataframe["quantity_type"].to_list() == ["quantity-1"]
    assert refreshed_load.dataframe is not None
    assert refreshed_load.dataframe["quantity_type"].to_list() == ["quantity-2"]


def test_scheduled_quantity_summaries_filters_and_context_links() -> None:
    sttm_table = "silver.sttm.silver_int652_v1_ex_ante_schedule_quantity_rpt_1"
    vicgas_table = "silver.vicgas.silver_int316_v4_operational_gas_1"
    load = _scheduled_quantity_load(
        pl.DataFrame(
            {
                "gas_date": [
                    "2024-01-03",
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-03",
                ],
                "source_system": ["STTM", "STTM", "VICGAS", "VICGAS"],
                "source_table": [sttm_table, sttm_table, vicgas_table, vicgas_table],
                "quantity_type": [
                    "sttm_ex_ante_scheduled_qty",
                    "sttm_provisional_scheduled_qty",
                    "operational_gas",
                    "out_of_merit_gas",
                ],
                "schedule_type_id": ["ex_ante", "provisional", "pricing", "pricing"],
                "transmission_id": ["S-2", "S-1", "V-1", "V-2"],
                "transmission_doc_id": ["SDOC-2", "SDOC-1", "VDOC-1", "VDOC-2"],
                "source_point_id": ["FAC-A", "FAC-A", "HV-ZONE", None],
                "quantity_gj": [100.0, 50.0, 11.5, 7.0],
                "volume_kscm": [None, None, 1.25, None],
                "amount_gst_ex": [None, None, None, 99.5],
                "source_last_updated_timestamp": [
                    "2024-01-02 15:00:00",
                    "2024-01-01 15:00:00",
                    "2024-01-03 10:00:00",
                    "2024-01-03 11:00:00",
                ],
                "source_surrogate_key": ["src-2", "src-1", "src-v1", "src-v2"],
                "source_file": ["sttm-2.csv", "sttm-1.csv", "vic-1.csv", "vic-2.csv"],
                "ingested_timestamp": [
                    datetime(2024, 1, 2, 16),
                    datetime(2024, 1, 1, 16),
                    datetime(2024, 1, 3, 12),
                    datetime(2024, 1, 3, 13),
                ],
            }
        )
    )

    observations = scheduled_quantity_observation_frame(
        load,
        "2024-01-03",
        "STTM",
        "ex_ante",
    )
    kpis = scheduled_quantity_kpi_frame(load)
    type_summary = scheduled_quantity_type_summary_frame(load)
    source_points = scheduled_quantity_source_point_frame(load)
    schedule_context = scheduled_quantity_schedule_context_frame(
        load,
        "2024-01-03",
        "STTM",
        "ex_ante",
    )
    source_coverage = scheduled_quantity_source_coverage_frame(load)
    context_links = render_scheduled_quantity_context_links()

    assert scheduled_quantity_gas_date_options(load) == (
        SCHEDULED_QUANTITY_GAS_DATE_FILTER_ALL,
        "2024-01-03",
        "2024-01-02",
    )
    assert scheduled_quantity_source_system_options(load) == (
        SCHEDULED_QUANTITY_SOURCE_SYSTEM_FILTER_ALL,
        "STTM",
        "VICGAS",
    )
    assert scheduled_quantity_schedule_type_options(load) == (
        SCHEDULED_QUANTITY_SCHEDULE_TYPE_FILTER_ALL,
        "ex_ante",
        "pricing",
        "provisional",
    )
    assert kpis.to_dict(as_series=False) == {
        "metric": [
            "Loaded scheduled quantity rows",
            "Quantity types",
            "Schedule types",
            "Source systems",
            "Source points",
            "Transmissions",
            "Total quantity_gj",
            "Total volume_kscm",
            "Total amount_gst_ex",
            "Latest gas date",
        ],
        "value": [
            "4",
            "4",
            "3",
            "2",
            "2",
            "4",
            "168.5",
            "1.25",
            "99.5",
            "2024-01-03",
        ],
        "detail": [
            "Full table scan",
            "Distinct quantity_type values in the current view",
            "Distinct schedule_type_id values in the current view",
            "Distinct source_system values in the current view",
            "Distinct source_point_id values in the current view",
            "Distinct transmission_id values linkable to schedule runs",
            "4 rows with populated quantity_gj",
            "1 rows with populated volume_kscm",
            "1 rows with populated amount_gst_ex",
            "Maximum gas_date in the loaded bounded rows",
        ],
    }
    assert observations.select(
        "gas date",
        "source system",
        "source table",
        "quantity type",
        "schedule type",
        "transmission",
        "source point",
        "quantity_gj",
    ).to_dict(as_series=False) == {
        "gas date": [date(2024, 1, 3)],
        "source system": ["STTM"],
        "source table": [sttm_table],
        "quantity type": ["sttm_ex_ante_scheduled_qty"],
        "schedule type": ["ex_ante"],
        "transmission": ["S-2"],
        "source point": ["FAC-A"],
        "quantity_gj": [100.0],
    }
    assert type_summary.select(
        "source system",
        "quantity type",
        "schedule type",
        "source points",
        "total quantity_gj",
        "total volume_kscm",
        "total amount_gst_ex",
        "latest gas date",
    ).head(4).to_dict(as_series=False) == {
        "source system": ["STTM", "VICGAS", "VICGAS", "STTM"],
        "quantity type": [
            "sttm_ex_ante_scheduled_qty",
            "operational_gas",
            "out_of_merit_gas",
            "sttm_provisional_scheduled_qty",
        ],
        "schedule type": ["ex_ante", "pricing", "pricing", "provisional"],
        "source points": [1, 1, 0, 1],
        "total quantity_gj": [100.0, 11.5, 7.0, 50.0],
        "total volume_kscm": [0.0, 1.25, 0.0, 0.0],
        "total amount_gst_ex": [0.0, 0.0, 99.5, 0.0],
        "latest gas date": [
            date(2024, 1, 3),
            date(2024, 1, 3),
            date(2024, 1, 3),
            date(2024, 1, 2),
        ],
    }
    assert source_points.select(
        "source point",
        "source system",
        "schedule type",
        "rows",
        "total quantity_gj",
    ).head(2).to_dict(as_series=False) == {
        "source point": ["FAC-A", "HV-ZONE"],
        "source system": ["STTM", "VICGAS"],
        "schedule type": ["ex_ante", "pricing"],
        "rows": [1, 1],
        "total quantity_gj": [100.0, 11.5],
    }
    assert schedule_context.select(
        "gas date",
        "source system",
        "schedule type",
        "transmission",
        "transmission document",
        "quantity rows",
        "total quantity_gj",
    ).to_dict(as_series=False) == {
        "gas date": [date(2024, 1, 3)],
        "source system": ["STTM"],
        "schedule type": ["ex_ante"],
        "transmission": ["S-2"],
        "transmission document": ["SDOC-2"],
        "quantity rows": [1],
        "total quantity_gj": [100.0],
    }
    assert source_coverage.select(
        "source system",
        "source table",
        "rows",
        "quantity types",
        "schedule types",
        "source points",
        "gas days",
    ).to_dict(as_series=False) == {
        "source system": ["STTM", "VICGAS"],
        "source table": [sttm_table, vicgas_table],
        "rows": [2, 2],
        "quantity types": [2, 2],
        "schedule types": [2, 1],
        "source points": [1, 1],
        "gas days": [2, 1],
    }
    assert 'href="/marimo/gas_scheduled_quantities/"' in context_links
    assert 'href="/marimo/gas_schedule_runs/"' in context_links
    assert "Schedule Context" in context_links
    assert "Gas Day Context" in context_links
    assert "Flow Context" in context_links


def test_scheduled_quantity_helpers_cover_missing_data_and_filter_empty_state() -> None:
    empty_load = _scheduled_quantity_load(pl.DataFrame(), row_limit=6)
    populated_load = _scheduled_quantity_load(
        pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 3)],
                "source_system": ["STTM"],
                "source_table": ["silver.sttm.schedule_quantity"],
                "quantity_type": ["sttm_ex_ante_scheduled_qty"],
                "schedule_type_id": ["ex_ante"],
                "source_point_id": ["FAC-A"],
                "quantity_gj": [100.0],
            }
        )
    )
    missing_date_load = _scheduled_quantity_load(
        pl.DataFrame(
            {
                "source_system": ["STTM"],
                "source_table": ["silver.sttm.schedule_quantity"],
                "quantity_type": ["sttm_ex_ante_scheduled_qty"],
            }
        )
    )
    error_load = GasTableLoad(
        spec=SCHEDULED_QUANTITY_TABLE_SPEC,
        uri="s3://bucket/silver/gas_model/silver_gas_fact_scheduled_quantity",
        dataframe=None,
        error="FileNotFoundError: no parquet files found",
        row_limit=6,
        load_duration_seconds=0.01,
        cache_hit=False,
    )

    assert scheduled_quantity_kpi_frame(empty_load).is_empty()
    assert scheduled_quantity_type_summary_frame(empty_load).is_empty()
    assert scheduled_quantity_source_point_frame(empty_load).is_empty()
    assert scheduled_quantity_schedule_context_frame(empty_load).is_empty()
    assert scheduled_quantity_source_coverage_frame(empty_load).is_empty()
    assert scheduled_quantity_observation_frame(empty_load).is_empty()
    assert scheduled_quantity_gas_date_options(empty_load) == (
        SCHEDULED_QUANTITY_GAS_DATE_FILTER_ALL,
    )
    assert scheduled_quantity_source_system_options(empty_load) == (
        SCHEDULED_QUANTITY_SOURCE_SYSTEM_FILTER_ALL,
    )
    assert scheduled_quantity_schedule_type_options(empty_load) == (
        SCHEDULED_QUANTITY_SCHEDULE_TYPE_FILTER_ALL,
    )
    assert scheduled_quantity_kpi_frame(
        populated_load,
        gas_date_filter="2024-01-04",
    ).is_empty()
    assert scheduled_quantity_kpi_frame(missing_date_load).row(9, named=True) == {
        "metric": "Latest gas date",
        "value": "unknown",
        "detail": "Maximum gas_date in the loaded bounded rows",
    }

    empty_markdown = scheduled_quantity_empty_state_markdown(empty_load)
    error_markdown = scheduled_quantity_empty_state_markdown(error_load)
    filtered_markdown = scheduled_quantity_empty_state_markdown(populated_load)
    missing_load_markdown = scheduled_quantity_empty_state_markdown(None)
    empty_context_links = render_scheduled_quantity_context_links(entries=())
    unmounted_entry = DashboardRegistryEntry(
        concept_id="gas-scheduled-quantities",
        title="Unmounted Scheduled Quantities",
        description="Available entry without a mounted notebook route.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.AVAILABLE,
        notebook_name=None,
        backing_assets=("silver.gas_model.silver_gas_fact_scheduled_quantity",),
        generated_gold_paths=(),
        source_chunks=(),
    )
    unmounted_context_links = render_scheduled_quantity_context_links(
        entries=(unmounted_entry,)
    )

    assert "No scheduled quantity data is available" in empty_markdown
    assert "silver.gas_model.silver_gas_fact_scheduled_quantity" in empty_markdown
    assert "Bounded preview reads are capped at `6` rows per table" in empty_markdown
    assert "FileNotFoundError: no parquet files found" in error_markdown
    assert "current filters do not match" in filtered_markdown
    assert "did not receive a scheduled quantity load result" in missing_load_markdown
    assert "No Scheduled quantity, Schedule run, Gas Day, or Flow context" in (
        empty_context_links
    )
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


def test_sttm_market_settlement_table_loader_uses_bounded_recent_view() -> None:
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
            "silver_gas_fact_sttm_market_settlement"
        )
        assert storage_options == config.storage_options()
        return pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 1), date(2024, 1, 3)],
                "settlement_component": ["older", "newer"],
            }
        )

    load = load_sttm_market_settlement_table(config, reader=reader)

    assert captured == [12]
    assert load.spec == STTM_MARKET_SETTLEMENT_TABLE_SPEC
    assert load.row_limit == 12
    assert load.dataframe is not None
    assert load.dataframe["settlement_component"].to_list() == ["newer", "older"]


def test_cached_sttm_market_settlement_table_loader_reuses_session_cache() -> None:
    calls: list[int] = []
    config = _dashboard_config()
    cache: GasModelSessionCache = {}

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        calls.append(len(calls) + 1)
        return pl.DataFrame({"settlement_component": [f"component-{calls[-1]}"]})

    first_load = cached_load_sttm_market_settlement_table(
        config,
        cache,
        reader=reader,
    )
    cached_load = cached_load_sttm_market_settlement_table(
        config,
        cache,
        reader=reader,
    )
    refreshed_load = cached_load_sttm_market_settlement_table(
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
    assert cached_load.dataframe["settlement_component"].to_list() == ["component-1"]
    assert refreshed_load.dataframe is not None
    assert refreshed_load.dataframe["settlement_component"].to_list() == ["component-2"]


def test_sttm_market_settlement_summaries_filters_and_context_links() -> None:
    int662_table = "silver.sttm.silver_int662_v1_provisional_deviation_rpt_1"
    int678_table = "silver.sttm.silver_int678_v1_net_market_balance_daily_amounts_rpt_1"
    int679_table = (
        "silver.sttm.silver_int679_v1_net_market_balance_settlement_amounts_rpt_1"
    )
    period_label = "2024-01-01 to 2024-01-31"
    load = _sttm_market_settlement_load(
        pl.DataFrame(
            {
                "gas_date": ["2024-01-03", "2024-01-03", None, None],
                "period_start_date": [None, None, "2024-01-01", "2024-01-01"],
                "period_end_date": [None, None, "2024-01-31", "2024-01-31"],
                "source_system": ["STTM", "STTM", "STTM", "STTM"],
                "source_table": [
                    int662_table,
                    int662_table,
                    int678_table,
                    int679_table,
                ],
                "source_report_id": ["INT662", "INT662", "INT678", "INT679"],
                "settlement_run_id": [None, None, None, "SET-1"],
                "settlement_stage": [
                    "provisional_deviation",
                    "provisional_deviation",
                    "nmb_daily_amounts",
                    "nmb_settlement_amounts",
                ],
                "settlement_component": [
                    "total_deviation_qty",
                    "deviation_charge",
                    "total_withdrawals",
                    "net_market_balance",
                ],
                "source_hub_id": ["SYD", "SYD", "SYD", "BNE"],
                "source_hub_name": ["Sydney", "Sydney", "Sydney", "Brisbane"],
                "source_facility_id": ["FAC-1", "FAC-1", None, None],
                "facility_name": ["Pipeline A", "Pipeline A", None, None],
                "quantity_gj": [10.0, None, 50.0, None],
                "amount": [None, 25.0, None, 100.0],
                "source_last_updated_timestamp": [
                    "2024-01-03 01:00:00",
                    "2024-01-03 01:05:00",
                    "2024-02-01 01:00:00",
                    "2024-02-01 02:00:00",
                ],
                "source_surrogate_key": ["src-1", "src-2", "src-3", "src-4"],
                "source_file": ["int662.csv", "int662.csv", "int678.csv", "int679.csv"],
                "ingested_timestamp": [
                    datetime(2024, 1, 3, 2),
                    datetime(2024, 1, 3, 2, 5),
                    datetime(2024, 2, 1, 2),
                    datetime(2024, 2, 1, 3),
                ],
            }
        )
    )

    kpis = sttm_market_settlement_kpi_frame(load)
    settlement_summary = sttm_market_settlement_summary_frame(load)
    source_coverage = sttm_market_settlement_source_coverage_frame(load)
    observations = sttm_market_settlement_observation_frame(
        load,
        STTM_MARKET_SETTLEMENT_GAS_DATE_FILTER_ALL,
        period_label,
        "nmb_settlement_amounts",
        "net_market_balance",
    )
    daily_kpis = sttm_market_settlement_kpi_frame(
        load,
        "2024-01-03",
        STTM_MARKET_SETTLEMENT_PERIOD_FILTER_ALL,
        "provisional_deviation",
        STTM_MARKET_SETTLEMENT_COMPONENT_FILTER_ALL,
    )
    context_links = render_sttm_market_settlement_context_links()

    assert sttm_market_settlement_gas_date_options(load) == (
        STTM_MARKET_SETTLEMENT_GAS_DATE_FILTER_ALL,
        "2024-01-03",
    )
    assert sttm_market_settlement_period_options(load) == (
        STTM_MARKET_SETTLEMENT_PERIOD_FILTER_ALL,
        period_label,
    )
    assert sttm_market_settlement_stage_options(load) == (
        STTM_MARKET_SETTLEMENT_STAGE_FILTER_ALL,
        "nmb_daily_amounts",
        "nmb_settlement_amounts",
        "provisional_deviation",
    )
    assert sttm_market_settlement_component_options(load) == (
        STTM_MARKET_SETTLEMENT_COMPONENT_FILTER_ALL,
        "deviation_charge",
        "net_market_balance",
        "total_deviation_qty",
        "total_withdrawals",
    )
    assert kpis.select("metric", "value", "detail").to_dict(as_series=False) == {
        "metric": [
            "Loaded STTM market settlement rows",
            "Settlement runs",
            "Settlement stages",
            "Components",
            "Hubs",
            "Facilities",
            "Gas Days",
            "Settlement periods",
            "Quantity",
            "Quantity range",
            "Amount",
            "Amount range",
            "Latest Gas Day",
            "Latest settlement period end",
            "Accepted source identifiers",
        ],
        "value": [
            "4",
            "1",
            "3",
            "4",
            "2",
            "1",
            "1",
            "1",
            "60 GJ",
            "10 to 50",
            "125",
            "25 to 100",
            "2024-01-03",
            "2024-01-31",
            "4",
        ],
        "detail": [
            "Full table scan",
            "Distinct settlement_run_id values represented",
            "Distinct settlement_stage values represented",
            "Distinct settlement_component values represented",
            "Distinct source_hub_id values represented",
            "Distinct source_facility_id values represented",
            "Distinct gas_date values represented",
            "Distinct period_start_date to period_end_date spans",
            "2 populated quantity_gj rows",
            "Minimum and maximum quantity_gj in the current view",
            "2 populated amount rows",
            "Minimum and maximum amount in the current view",
            "Maximum gas_date in the loaded bounded rows",
            "Maximum period_end_date in the loaded bounded rows",
            "Distinct source_surrogate_key values represented",
        ],
    }
    assert daily_kpis.row(0, named=True) == {
        "metric": "Loaded STTM market settlement rows",
        "value": "2",
        "detail": "Full table scan",
    }
    assert observations.select(
        "gas date",
        "period start",
        "period end",
        "settlement run",
        "settlement stage",
        "component",
        "hub",
        "facility",
        "quantity_gj",
        "amount",
        "source report",
        "accepted source identifier",
    ).to_dict(as_series=False) == {
        "gas date": [None],
        "period start": [date(2024, 1, 1)],
        "period end": [date(2024, 1, 31)],
        "settlement run": ["SET-1"],
        "settlement stage": ["nmb_settlement_amounts"],
        "component": ["net_market_balance"],
        "hub": ["BNE"],
        "facility": [None],
        "quantity_gj": [None],
        "amount": [100.0],
        "source report": ["INT679"],
        "accepted source identifier": ["src-4"],
    }
    assert settlement_summary.sort(["source report", "component"]).select(
        "settlement run",
        "settlement stage",
        "component",
        "hub",
        "facility",
        "source report",
        "period start",
        "period end",
        "rows",
        "gas days",
        "quantity rows",
        "total quantity gj",
        "amount rows",
        "total amount",
    ).to_dict(as_series=False) == {
        "settlement run": [None, None, None, "SET-1"],
        "settlement stage": [
            "provisional_deviation",
            "provisional_deviation",
            "nmb_daily_amounts",
            "nmb_settlement_amounts",
        ],
        "component": [
            "deviation_charge",
            "total_deviation_qty",
            "total_withdrawals",
            "net_market_balance",
        ],
        "hub": ["SYD", "SYD", "SYD", "BNE"],
        "facility": ["FAC-1", "FAC-1", None, None],
        "source report": ["INT662", "INT662", "INT678", "INT679"],
        "period start": [None, None, date(2024, 1, 1), date(2024, 1, 1)],
        "period end": [None, None, date(2024, 1, 31), date(2024, 1, 31)],
        "rows": [1, 1, 1, 1],
        "gas days": [1, 1, 0, 0],
        "quantity rows": [0, 1, 1, 0],
        "total quantity gj": [0.0, 10.0, 50.0, 0.0],
        "amount rows": [1, 0, 0, 1],
        "total amount": [25.0, 0.0, 0.0, 100.0],
    }
    assert source_coverage.select(
        "source system",
        "source table",
        "source report",
        "rows",
        "settlement runs",
        "settlement stages",
        "components",
        "hubs",
        "facilities",
        "gas days",
        "periods",
        "quantity rows",
        "amount rows",
        "source identifiers",
    ).to_dict(as_series=False) == {
        "source system": ["STTM", "STTM", "STTM"],
        "source table": [int662_table, int678_table, int679_table],
        "source report": ["INT662", "INT678", "INT679"],
        "rows": [2, 1, 1],
        "settlement runs": [0, 0, 1],
        "settlement stages": [1, 1, 1],
        "components": [2, 1, 1],
        "hubs": [1, 1, 1],
        "facilities": [1, 0, 0],
        "gas days": [1, 0, 0],
        "periods": [0, 1, 1],
        "quantity rows": [1, 1, 0],
        "amount rows": [1, 0, 1],
        "source identifiers": [2, 1, 1],
    }
    assert 'href="/marimo/gas_sttm_market_settlement/"' in context_links
    assert "Settlement Context" in context_links
    assert "Allocation Context" in context_links
    assert "Hub / Zone Context" in context_links
    assert "Facility Context" in context_links
    assert "Gas Day Context" in context_links


def test_sttm_market_settlement_helpers_cover_missing_data_and_filter_empty_state() -> (
    None
):
    empty_load = _sttm_market_settlement_load(pl.DataFrame(), row_limit=5)
    populated_load = _sttm_market_settlement_load(
        pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 3)],
                "source_system": ["STTM"],
                "source_table": ["silver.sttm.market_settlement"],
                "source_report_id": ["INT662"],
                "settlement_stage": ["provisional_deviation"],
                "settlement_component": ["total_deviation_qty"],
                "source_hub_id": ["SYD"],
                "quantity_gj": [10.0],
            }
        )
    )
    missing_date_load = _sttm_market_settlement_load(
        pl.DataFrame(
            {
                "period_start_date": [date(2024, 1, 1)],
                "period_end_date": [date(2024, 1, 31)],
                "source_system": ["STTM"],
                "settlement_stage": ["nmb_settlement_amounts"],
                "settlement_component": ["net_market_balance"],
                "source_hub_id": ["SYD"],
                "amount": [100.0],
            }
        )
    )
    no_measure_load = _sttm_market_settlement_load(
        pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 3)],
                "source_system": ["STTM"],
                "settlement_stage": ["provisional_deviation"],
                "settlement_component": ["total_deviation_qty"],
                "source_hub_id": ["SYD"],
            }
        )
    )
    error_load = GasTableLoad(
        spec=STTM_MARKET_SETTLEMENT_TABLE_SPEC,
        uri="s3://bucket/silver/gas_model/silver_gas_fact_sttm_market_settlement",
        dataframe=None,
        error="FileNotFoundError: no parquet files found",
        row_limit=5,
        load_duration_seconds=0.01,
        cache_hit=False,
    )

    assert sttm_market_settlement_kpi_frame(empty_load).is_empty()
    assert sttm_market_settlement_summary_frame(empty_load).is_empty()
    assert sttm_market_settlement_source_coverage_frame(empty_load).is_empty()
    assert sttm_market_settlement_observation_frame(empty_load).is_empty()
    assert sttm_market_settlement_gas_date_options(empty_load) == (
        STTM_MARKET_SETTLEMENT_GAS_DATE_FILTER_ALL,
    )
    assert sttm_market_settlement_period_options(empty_load) == (
        STTM_MARKET_SETTLEMENT_PERIOD_FILTER_ALL,
    )
    assert sttm_market_settlement_stage_options(empty_load) == (
        STTM_MARKET_SETTLEMENT_STAGE_FILTER_ALL,
    )
    assert sttm_market_settlement_component_options(empty_load) == (
        STTM_MARKET_SETTLEMENT_COMPONENT_FILTER_ALL,
    )
    assert sttm_market_settlement_kpi_frame(
        populated_load,
        settlement_stage_filter="missing-stage",
    ).is_empty()
    assert sttm_market_settlement_kpi_frame(missing_date_load).row(
        12,
        named=True,
    ) == {
        "metric": "Latest Gas Day",
        "value": "unknown",
        "detail": "Maximum gas_date in the loaded bounded rows",
    }
    assert sttm_market_settlement_kpi_frame(no_measure_load).row(8, named=True) == {
        "metric": "Quantity",
        "value": "unknown",
        "detail": "0 populated quantity_gj rows",
    }

    empty_markdown = sttm_market_settlement_empty_state_markdown(empty_load)
    error_markdown = sttm_market_settlement_empty_state_markdown(error_load)
    filtered_markdown = sttm_market_settlement_empty_state_markdown(populated_load)
    missing_load_markdown = sttm_market_settlement_empty_state_markdown(None)
    empty_context_links = render_sttm_market_settlement_context_links(entries=())
    unmounted_entry = DashboardRegistryEntry(
        concept_id="sttm-market-settlement",
        title="Unmounted STTM Market Settlement",
        description="Available entry without a mounted notebook route.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.AVAILABLE,
        notebook_name=None,
        backing_assets=("silver.gas_model.silver_gas_fact_sttm_market_settlement",),
        generated_gold_paths=(),
        source_chunks=(),
    )
    unmounted_context_links = render_sttm_market_settlement_context_links(
        entries=(unmounted_entry,)
    )

    assert "No STTM market settlement data is available" in empty_markdown
    assert "silver.gas_model.silver_gas_fact_sttm_market_settlement" in (empty_markdown)
    assert "Bounded preview reads are capped at `5` rows per table" in empty_markdown
    assert "FileNotFoundError: no parquet files found" in error_markdown
    assert "current filters do not match" in filtered_markdown
    assert (
        "did not receive an STTM market settlement load result" in missing_load_markdown
    )
    assert "No STTM market settlement, Settlement, Allocation" in empty_context_links
    assert "Unavailable dashboard" in unmounted_context_links


def test_sttm_capacity_settlement_table_loader_uses_bounded_recent_view() -> None:
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
            "silver_gas_fact_sttm_capacity_settlement"
        )
        assert storage_options == config.storage_options()
        return pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 1), date(2024, 1, 3)],
                "capacity_settlement_component": ["older", "newer"],
            }
        )

    load = load_sttm_capacity_settlement_table(config, reader=reader)

    assert captured == [12]
    assert load.spec == STTM_CAPACITY_SETTLEMENT_TABLE_SPEC
    assert load.row_limit == 12
    assert load.dataframe is not None
    assert load.dataframe["capacity_settlement_component"].to_list() == [
        "newer",
        "older",
    ]


def test_cached_sttm_capacity_settlement_table_loader_reuses_session_cache() -> None:
    calls: list[int] = []
    config = _dashboard_config()
    cache: GasModelSessionCache = {}

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        calls.append(len(calls) + 1)
        return pl.DataFrame(
            {"capacity_settlement_component": [f"component-{calls[-1]}"]}
        )

    first_load = cached_load_sttm_capacity_settlement_table(
        config,
        cache,
        reader=reader,
    )
    cached_load = cached_load_sttm_capacity_settlement_table(
        config,
        cache,
        reader=reader,
    )
    refreshed_load = cached_load_sttm_capacity_settlement_table(
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
    assert cached_load.dataframe["capacity_settlement_component"].to_list() == [
        "component-1"
    ]
    assert refreshed_load.dataframe is not None
    assert refreshed_load.dataframe["capacity_settlement_component"].to_list() == [
        "component-2"
    ]


def test_sttm_capacity_settlement_summaries_filters_and_context_links() -> None:
    int664_table = "silver.sttm.silver_int664_v1_daily_provisional_mos_allocation_rpt_1"
    int681_table = "silver.sttm.silver_int681_v1_daily_provisional_capacity_data_rpt_1"
    int682_table = "silver.sttm.silver_int682_v1_settlement_mos_and_capacity_data_rpt_1"
    load = _sttm_capacity_settlement_load(
        pl.DataFrame(
            {
                "gas_date": ["2024-01-03", "2024-01-03", "2024-01-04", None],
                "source_system": ["STTM", "STTM", "STTM", "STTM"],
                "source_table": [
                    int664_table,
                    int664_table,
                    int681_table,
                    int682_table,
                ],
                "source_report_id": ["INT664", "INT664", "INT681", "INT682"],
                "settlement_run_id": [None, None, None, "SET-1"],
                "settlement_stage": [
                    "provisional_mos_allocation",
                    "provisional_mos_allocation",
                    "provisional_capacity",
                    "settlement_mos_capacity",
                ],
                "capacity_settlement_component": [
                    "mos_allocated_qty",
                    "mos_overrun_qty",
                    "firm_not_flowed",
                    "as_available_flowed",
                ],
                "source_hub_id": ["SYD", "SYD", "BNE", "SYD"],
                "source_hub_name": ["Sydney", "Sydney", "Brisbane", "Sydney"],
                "source_facility_id": ["FAC-1", "FAC-1", "FAC-2", "FAC-1"],
                "facility_name": [
                    "Pipeline A",
                    "Pipeline A",
                    "Pipeline B",
                    "Pipeline A",
                ],
                "quantity_gj": [10.0, 2.0, 5.0, 7.5],
                "source_last_updated_timestamp": [
                    "2024-01-03 01:00:00",
                    "2024-01-03 01:05:00",
                    "2024-01-04 01:00:00",
                    "2024-02-01 02:00:00",
                ],
                "source_surrogate_key": ["src-1", "src-2", "src-3", "src-4"],
                "source_file": [
                    "int664.csv",
                    "int664.csv",
                    "int681.csv",
                    "int682.csv",
                ],
                "ingested_timestamp": [
                    datetime(2024, 1, 3, 2),
                    datetime(2024, 1, 3, 2, 5),
                    datetime(2024, 1, 4, 2),
                    datetime(2024, 2, 1, 3),
                ],
            }
        )
    )

    kpis = sttm_capacity_settlement_kpi_frame(load)
    settlement_summary = sttm_capacity_settlement_summary_frame(load)
    source_coverage = sttm_capacity_settlement_source_coverage_frame(load)
    observations = sttm_capacity_settlement_observation_frame(
        load,
        STTM_CAPACITY_SETTLEMENT_GAS_DATE_FILTER_ALL,
        "settlement_mos_capacity",
        "as_available_flowed",
        "SYD",
        "FAC-1",
    )
    daily_kpis = sttm_capacity_settlement_kpi_frame(
        load,
        "2024-01-03",
        "provisional_mos_allocation",
        STTM_CAPACITY_SETTLEMENT_COMPONENT_FILTER_ALL,
        "SYD",
        "FAC-1",
    )
    context_links = render_sttm_capacity_settlement_context_links()

    assert sttm_capacity_settlement_gas_date_options(load) == (
        STTM_CAPACITY_SETTLEMENT_GAS_DATE_FILTER_ALL,
        "2024-01-04",
        "2024-01-03",
    )
    assert sttm_capacity_settlement_stage_options(load) == (
        STTM_CAPACITY_SETTLEMENT_STAGE_FILTER_ALL,
        "provisional_capacity",
        "provisional_mos_allocation",
        "settlement_mos_capacity",
    )
    assert sttm_capacity_settlement_component_options(load) == (
        STTM_CAPACITY_SETTLEMENT_COMPONENT_FILTER_ALL,
        "as_available_flowed",
        "firm_not_flowed",
        "mos_allocated_qty",
        "mos_overrun_qty",
    )
    assert sttm_capacity_settlement_hub_options(load) == (
        STTM_CAPACITY_SETTLEMENT_HUB_FILTER_ALL,
        "BNE",
        "SYD",
    )
    assert sttm_capacity_settlement_facility_options(load) == (
        STTM_CAPACITY_SETTLEMENT_FACILITY_FILTER_ALL,
        "FAC-1",
        "FAC-2",
    )
    assert kpis.select("metric", "value", "detail").to_dict(as_series=False) == {
        "metric": [
            "Loaded STTM capacity settlement rows",
            "Settlement runs",
            "Settlement stages",
            "Capacity settlement components",
            "Hubs",
            "Facilities",
            "Source reports",
            "Gas Days",
            "Quantity",
            "Quantity range",
            "Latest Gas Day",
            "Accepted source identifiers",
        ],
        "value": [
            "4",
            "1",
            "3",
            "4",
            "2",
            "2",
            "3",
            "2",
            "24.5 GJ",
            "2 to 10",
            "2024-01-04",
            "4",
        ],
        "detail": [
            "Full table scan",
            "Distinct settlement_run_id values represented",
            "Distinct settlement_stage values represented",
            "Distinct capacity_settlement_component values represented",
            "Distinct source_hub_id values represented",
            "Distinct source_facility_id values represented",
            "Distinct source_report_id values represented",
            "Distinct gas_date values represented",
            "4 populated quantity_gj rows",
            "Minimum and maximum quantity_gj in the current view",
            "Maximum gas_date in the loaded bounded rows",
            "Distinct source_surrogate_key values represented",
        ],
    }
    assert daily_kpis.row(0, named=True) == {
        "metric": "Loaded STTM capacity settlement rows",
        "value": "2",
        "detail": "Full table scan",
    }
    assert observations.select(
        "gas date",
        "settlement run",
        "settlement stage",
        "capacity settlement component",
        "hub",
        "facility",
        "quantity_gj",
        "source report",
        "accepted source identifier",
    ).to_dict(as_series=False) == {
        "gas date": [None],
        "settlement run": ["SET-1"],
        "settlement stage": ["settlement_mos_capacity"],
        "capacity settlement component": ["as_available_flowed"],
        "hub": ["SYD"],
        "facility": ["FAC-1"],
        "quantity_gj": [7.5],
        "source report": ["INT682"],
        "accepted source identifier": ["src-4"],
    }
    assert settlement_summary.sort(
        ["source report", "capacity settlement component"]
    ).select(
        "settlement run",
        "settlement stage",
        "capacity settlement component",
        "hub",
        "facility",
        "source report",
        "rows",
        "gas days",
        "quantity rows",
        "total quantity gj",
        "min quantity gj",
        "max quantity gj",
    ).to_dict(as_series=False) == {
        "settlement run": [None, None, None, "SET-1"],
        "settlement stage": [
            "provisional_mos_allocation",
            "provisional_mos_allocation",
            "provisional_capacity",
            "settlement_mos_capacity",
        ],
        "capacity settlement component": [
            "mos_allocated_qty",
            "mos_overrun_qty",
            "firm_not_flowed",
            "as_available_flowed",
        ],
        "hub": ["SYD", "SYD", "BNE", "SYD"],
        "facility": ["FAC-1", "FAC-1", "FAC-2", "FAC-1"],
        "source report": ["INT664", "INT664", "INT681", "INT682"],
        "rows": [1, 1, 1, 1],
        "gas days": [1, 1, 1, 0],
        "quantity rows": [1, 1, 1, 1],
        "total quantity gj": [10.0, 2.0, 5.0, 7.5],
        "min quantity gj": [10.0, 2.0, 5.0, 7.5],
        "max quantity gj": [10.0, 2.0, 5.0, 7.5],
    }
    assert source_coverage.select(
        "source system",
        "source table",
        "source report",
        "rows",
        "settlement runs",
        "settlement stages",
        "capacity settlement components",
        "hubs",
        "facilities",
        "gas days",
        "quantity rows",
        "source identifiers",
    ).to_dict(as_series=False) == {
        "source system": ["STTM", "STTM", "STTM"],
        "source table": [int664_table, int681_table, int682_table],
        "source report": ["INT664", "INT681", "INT682"],
        "rows": [2, 1, 1],
        "settlement runs": [0, 0, 1],
        "settlement stages": [1, 1, 1],
        "capacity settlement components": [2, 1, 1],
        "hubs": [1, 1, 1],
        "facilities": [1, 1, 1],
        "gas days": [1, 1, 0],
        "quantity rows": [2, 1, 1],
        "source identifiers": [2, 1, 1],
    }
    assert 'href="/marimo/gas_sttm_capacity_settlement/"' in context_links
    assert 'href="/marimo/gas_sttm_market_settlement/"' in context_links
    assert "Capacity Context" in context_links
    assert "Settlement Context" in context_links
    assert "MOS Context" in context_links
    assert "Allocation Context" in context_links
    assert "Facility Context" in context_links
    assert "Hub / Zone Context" in context_links


def test_sttm_capacity_settlement_helpers_cover_missing_data_and_filter_empty_state() -> (
    None
):
    empty_load = _sttm_capacity_settlement_load(pl.DataFrame(), row_limit=5)
    populated_load = _sttm_capacity_settlement_load(
        pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 3)],
                "source_system": ["STTM"],
                "source_table": ["silver.sttm.capacity_settlement"],
                "source_report_id": ["INT664"],
                "settlement_stage": ["provisional_mos_allocation"],
                "capacity_settlement_component": ["mos_allocated_qty"],
                "source_hub_id": ["SYD"],
                "source_facility_id": ["FAC-1"],
                "quantity_gj": [10.0],
            }
        )
    )
    missing_date_load = _sttm_capacity_settlement_load(
        pl.DataFrame(
            {
                "source_system": ["STTM"],
                "settlement_stage": ["settlement_mos_capacity"],
                "capacity_settlement_component": ["as_available_flowed"],
                "source_hub_id": ["SYD"],
                "source_facility_id": ["FAC-1"],
                "quantity_gj": [7.5],
            }
        )
    )
    no_measure_load = _sttm_capacity_settlement_load(
        pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 3)],
                "source_system": ["STTM"],
                "settlement_stage": ["provisional_mos_allocation"],
                "capacity_settlement_component": ["mos_allocated_qty"],
                "source_hub_id": ["SYD"],
                "source_facility_id": ["FAC-1"],
            }
        )
    )
    error_load = GasTableLoad(
        spec=STTM_CAPACITY_SETTLEMENT_TABLE_SPEC,
        uri="s3://bucket/silver/gas_model/silver_gas_fact_sttm_capacity_settlement",
        dataframe=None,
        error="FileNotFoundError: no parquet files found",
        row_limit=5,
        load_duration_seconds=0.01,
        cache_hit=False,
    )

    assert sttm_capacity_settlement_kpi_frame(empty_load).is_empty()
    assert sttm_capacity_settlement_summary_frame(empty_load).is_empty()
    assert sttm_capacity_settlement_source_coverage_frame(empty_load).is_empty()
    assert sttm_capacity_settlement_observation_frame(empty_load).is_empty()
    assert sttm_capacity_settlement_gas_date_options(empty_load) == (
        STTM_CAPACITY_SETTLEMENT_GAS_DATE_FILTER_ALL,
    )
    assert sttm_capacity_settlement_stage_options(empty_load) == (
        STTM_CAPACITY_SETTLEMENT_STAGE_FILTER_ALL,
    )
    assert sttm_capacity_settlement_component_options(empty_load) == (
        STTM_CAPACITY_SETTLEMENT_COMPONENT_FILTER_ALL,
    )
    assert sttm_capacity_settlement_hub_options(empty_load) == (
        STTM_CAPACITY_SETTLEMENT_HUB_FILTER_ALL,
    )
    assert sttm_capacity_settlement_facility_options(empty_load) == (
        STTM_CAPACITY_SETTLEMENT_FACILITY_FILTER_ALL,
    )
    assert sttm_capacity_settlement_kpi_frame(
        populated_load,
        settlement_stage_filter="missing-stage",
    ).is_empty()
    assert sttm_capacity_settlement_kpi_frame(missing_date_load).row(
        10,
        named=True,
    ) == {
        "metric": "Latest Gas Day",
        "value": "unknown",
        "detail": "Maximum gas_date in the loaded bounded rows",
    }
    assert sttm_capacity_settlement_kpi_frame(no_measure_load).row(8, named=True) == {
        "metric": "Quantity",
        "value": "unknown",
        "detail": "0 populated quantity_gj rows",
    }

    empty_markdown = sttm_capacity_settlement_empty_state_markdown(empty_load)
    error_markdown = sttm_capacity_settlement_empty_state_markdown(error_load)
    filtered_markdown = sttm_capacity_settlement_empty_state_markdown(populated_load)
    missing_load_markdown = sttm_capacity_settlement_empty_state_markdown(None)
    empty_context_links = render_sttm_capacity_settlement_context_links(entries=())
    unmounted_entry = DashboardRegistryEntry(
        concept_id="sttm-capacity-settlement",
        title="Unmounted STTM Capacity Settlement",
        description="Available entry without a mounted notebook route.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.AVAILABLE,
        notebook_name=None,
        backing_assets=("silver.gas_model.silver_gas_fact_sttm_capacity_settlement",),
        generated_gold_paths=(),
        source_chunks=(),
    )
    unmounted_context_links = render_sttm_capacity_settlement_context_links(
        entries=(unmounted_entry,)
    )

    assert "No STTM capacity settlement data is available" in empty_markdown
    assert "silver.gas_model.silver_gas_fact_sttm_capacity_settlement" in (
        empty_markdown
    )
    assert "Bounded preview reads are capped at `5` rows per table" in empty_markdown
    assert "FileNotFoundError: no parquet files found" in error_markdown
    assert "current filters do not match" in filtered_markdown
    assert (
        "did not receive an STTM capacity settlement load result"
        in missing_load_markdown
    )
    assert "No STTM capacity settlement, STTM market settlement" in empty_context_links
    assert "Unavailable dashboard" in unmounted_context_links


def test_sttm_mos_allocation_table_loader_uses_bounded_recent_view() -> None:
    captured: list[tuple[str, int | None]] = []
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
        captured.append((uri, row_limit))
        assert storage_options == config.storage_options()
        return pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 1), date(2024, 1, 3)],
                "source_system": ["STTM", "STTM"],
            }
        )

    loads = load_sttm_mos_allocation_tables(config, reader=reader)

    assert [load.spec for load in loads] == list(STTM_MOS_ALLOCATION_TABLE_SPECS)
    assert [load.row_limit for load in loads] == [12, 12, 12, 12]
    assert captured == [
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_sttm_mos_stack",
            12,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_sttm_allocation_quantity",
            12,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_sttm_allocation_limit",
            12,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_sttm_default_allocation_notice",
            12,
        ),
    ]


def test_cached_sttm_mos_allocation_table_loader_reuses_session_cache() -> None:
    calls: list[int] = []
    config = _dashboard_config()
    cache: GasModelSessionCache = {}

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        calls.append(len(calls) + 1)
        return pl.DataFrame({"source_system": [f"STTM-{calls[-1]}"]})

    first_loads = cached_load_sttm_mos_allocation_tables(config, cache, reader=reader)
    cached_loads = cached_load_sttm_mos_allocation_tables(config, cache, reader=reader)
    refreshed_loads = cached_load_sttm_mos_allocation_tables(
        config,
        cache,
        reader=reader,
        refresh_token=1,
    )

    assert calls == [1, 2, 3, 4, 5, 6, 7, 8]
    assert not any(load.cache_hit for load in first_loads)
    assert all(load.cache_hit for load in cached_loads)
    assert not any(load.cache_hit for load in refreshed_loads)
    assert cached_loads[0].dataframe is not None
    assert cached_loads[0].dataframe["source_system"].to_list() == ["STTM-1"]
    assert refreshed_loads[0].dataframe is not None
    assert refreshed_loads[0].dataframe["source_system"].to_list() == ["STTM-5"]


def test_sttm_mos_allocation_summaries_filters_and_context_links() -> None:
    mos_table = "silver.sttm.silver_int665_v1_mos_stack_data_rpt_1"
    allocation_table = "silver.sttm.silver_int658_v1_latest_allocation_quantity_rpt_1"
    limit_table = (
        "silver.sttm.silver_int688_v1_allocation_warning_limit_thresholds_rpt_1"
    )
    notice_table = "silver.sttm.silver_int675_v1_default_allocation_notice_rpt_1"
    loads = _sttm_mos_allocation_loads(
        mos_stack=pl.DataFrame(
            {
                "mos_stack_context": ["estimate", "used_step"],
                "settlement_run_id": [None, "SET-1"],
                "gas_date": ["2024-01-03", "2024-01-04"],
                "effective_from_date": ["2024-01-01", None],
                "effective_to_date": ["2024-01-31", None],
                "source_system": ["STTM", "STTM"],
                "source_table": [mos_table, mos_table],
                "source_report_id": ["INT665", "INT683"],
                "source_hub_id": ["SYD", "SYD"],
                "source_hub_name": ["Sydney", "Sydney"],
                "source_facility_id": ["FAC-1", "FAC-1"],
                "facility_name": ["Pipeline A", "Pipeline A"],
                "stack_id": ["STACK-1", "STACK-1"],
                "stack_type": ["price", "price"],
                "stack_step_id": ["1", "2"],
                "participant_id": ["P1", "P1"],
                "participant_name": ["Participant 1", "Participant 1"],
                "estimated_maximum_quantity_gj": [100.0, None],
                "step_quantity_gj": [20.0, 5.0],
                "step_price": [2.0, 7.0],
                "source_last_updated_timestamp": [
                    "2024-01-03 01:00:00",
                    "2024-01-04 01:00:00",
                ],
                "source_surrogate_key": ["mos-1", "mos-2"],
                "source_file": ["int665.csv", "int683.csv"],
                "ingested_timestamp": [
                    datetime(2024, 1, 3, 2),
                    datetime(2024, 1, 4, 2),
                ],
            }
        ),
        allocation_quantity=pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 3), date(2024, 1, 4)],
                "allocation_version": ["latest", "latest"],
                "source_system": ["STTM", "STTM"],
                "source_table": [allocation_table, allocation_table],
                "source_report_id": ["INT658", "INT658"],
                "source_hub_id": ["SYD", "BNE"],
                "source_hub_name": ["Sydney", "Brisbane"],
                "source_facility_id": ["FAC-1", "FAC-2"],
                "facility_name": ["Pipeline A", "Pipeline B"],
                "flow_direction": ["receipt", "delivery"],
                "allocation_qty_inc_mos_gj": [12.0, 8.0],
                "allocation_qty_quality_type": ["actual", "estimated"],
                "source_last_updated_timestamp": [
                    datetime(2024, 1, 3, 3),
                    datetime(2024, 1, 4, 3),
                ],
                "source_surrogate_key": ["alloc-1", "alloc-2"],
                "source_file": ["int658.csv", "int658.csv"],
                "ingested_timestamp": [
                    datetime(2024, 1, 3, 4),
                    datetime(2024, 1, 4, 4),
                ],
            }
        ),
        allocation_limit=pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 3)],
                "source_system": ["STTM"],
                "source_table": [limit_table],
                "source_report_id": ["INT688"],
                "source_hub_id": ["SYD"],
                "source_hub_name": ["Sydney"],
                "source_facility_id": ["FAC-1"],
                "facility_name": ["Pipeline A"],
                "upper_warning_limit_gj": [30.0],
                "lower_warning_limit_gj": [3.0],
                "source_report_timestamp": [datetime(2024, 1, 3, 5)],
                "source_last_updated_timestamp": [datetime(2024, 1, 3, 5, 5)],
                "source_surrogate_key": ["limit-1"],
                "source_file": ["int688.csv"],
                "ingested_timestamp": [datetime(2024, 1, 3, 6)],
            }
        ),
        default_notice=pl.DataFrame(
            {
                "notice_id": ["NOTICE-1"],
                "gas_date": [date(2024, 1, 3)],
                "source_system": ["STTM"],
                "source_table": [notice_table],
                "source_report_id": ["INT675"],
                "source_hub_id": ["SYD"],
                "source_hub_name": ["Sydney"],
                "source_facility_id": ["FAC-1"],
                "facility_name": ["Pipeline A"],
                "notice_message": ["Default allocation applied"],
                "source_last_updated_timestamp": [datetime(2024, 1, 3, 7)],
                "source_surrogate_key": ["notice-1"],
                "source_file": ["int675.csv"],
                "ingested_timestamp": [datetime(2024, 1, 3, 8)],
            }
        ),
    )

    kpis = sttm_mos_allocation_kpi_frame(loads)
    fact_summary = sttm_mos_allocation_fact_summary_frame(loads)
    mos_summary = sttm_mos_stack_summary_frame(loads)
    allocation_summary = sttm_allocation_quantity_summary_frame(loads)
    limit_summary = sttm_allocation_limit_summary_frame(loads)
    notice_summary = sttm_default_allocation_notice_summary_frame(loads)
    source_coverage = sttm_mos_allocation_source_coverage_frame(loads)
    filtered_kpis = sttm_mos_allocation_kpi_frame(
        loads,
        "2024-01-03",
        "STTM",
        "SYD",
        "FAC-1",
    )
    context_links = render_sttm_mos_allocation_context_links()

    assert sttm_mos_allocation_gas_date_options(loads) == (
        STTM_MOS_ALLOCATION_GAS_DATE_FILTER_ALL,
        "2024-01-04",
        "2024-01-03",
    )
    assert sttm_mos_allocation_source_system_options(loads) == (
        STTM_MOS_ALLOCATION_SOURCE_SYSTEM_FILTER_ALL,
        "STTM",
    )
    assert sttm_mos_allocation_hub_options(loads) == (
        STTM_MOS_ALLOCATION_HUB_FILTER_ALL,
        "BNE",
        "SYD",
    )
    assert sttm_mos_allocation_facility_options(loads) == (
        STTM_MOS_ALLOCATION_FACILITY_FILTER_ALL,
        "FAC-1",
        "FAC-2",
    )
    assert kpis.select("metric", "value").to_dict(as_series=False) == {
        "metric": [
            "Loaded STTM MOS/allocation rows",
            "MOS stack rows",
            "Allocation quantity rows",
            "Allocation limit rows",
            "Default allocation notice rows",
            "Gas Days",
            "Hubs",
            "Facilities",
            "Source reports",
            "Allocation quantity inc MOS",
            "MOS step quantity",
            "MOS estimated maximum",
            "Allocation warning limits",
            "Default allocation notices",
            "Latest Gas Day",
        ],
        "value": [
            "6",
            "2",
            "2",
            "1",
            "1",
            "2",
            "2",
            "2",
            "5",
            "20 GJ",
            "25 GJ",
            "100 GJ",
            "2",
            "1",
            "2024-01-04",
        ],
    }
    assert filtered_kpis.row(0, named=True) == {
        "metric": "Loaded STTM MOS/allocation rows",
        "value": "4",
        "detail": "Full table scan",
    }
    assert fact_summary.select(
        "fact", "rows", "primary measure", "primary value"
    ).to_dict(as_series=False) == {
        "fact": [
            "MOS stack",
            "Allocation quantity",
            "Allocation limit",
            "Default allocation notice",
        ],
        "rows": [2, 2, 1, 1],
        "primary measure": [
            "Total step quantity",
            "Total allocation qty inc MOS",
            "Upper warning limit range",
            "Distinct notices",
        ],
        "primary value": ["25 GJ", "20 GJ", "30 to 30", "1"],
    }
    assert mos_summary.select(
        "mos stack context",
        "settlement run",
        "stack type",
        "hub",
        "facility",
        "source report",
        "rows",
        "stack steps",
        "total step quantity gj",
        "min step price",
        "max step price",
    ).sort("source report").to_dict(as_series=False) == {
        "mos stack context": ["estimate", "used_step"],
        "settlement run": [None, "SET-1"],
        "stack type": ["price", "price"],
        "hub": ["SYD", "SYD"],
        "facility": ["FAC-1", "FAC-1"],
        "source report": ["INT665", "INT683"],
        "rows": [1, 1],
        "stack steps": [1, 1],
        "total step quantity gj": [20.0, 5.0],
        "min step price": [2.0, 7.0],
        "max step price": [2.0, 7.0],
    }
    assert allocation_summary.select(
        "allocation version",
        "flow direction",
        "allocation quality type",
        "hub",
        "facility",
        "rows",
        "total allocation qty inc mos gj",
    ).sort("hub").to_dict(as_series=False) == {
        "allocation version": ["latest", "latest"],
        "flow direction": ["delivery", "receipt"],
        "allocation quality type": ["estimated", "actual"],
        "hub": ["BNE", "SYD"],
        "facility": ["FAC-2", "FAC-1"],
        "rows": [1, 1],
        "total allocation qty inc mos gj": [8.0, 12.0],
    }
    assert limit_summary.select(
        "hub",
        "facility",
        "upper limit rows",
        "min upper warning limit gj",
        "lower limit rows",
        "min lower warning limit gj",
    ).to_dict(as_series=False) == {
        "hub": ["SYD"],
        "facility": ["FAC-1"],
        "upper limit rows": [1],
        "min upper warning limit gj": [30.0],
        "lower limit rows": [1],
        "min lower warning limit gj": [3.0],
    }
    assert notice_summary.select(
        "notice",
        "hub",
        "facility",
        "notice messages",
        "sample notice message",
    ).to_dict(as_series=False) == {
        "notice": ["NOTICE-1"],
        "hub": ["SYD"],
        "facility": ["FAC-1"],
        "notice messages": [1],
        "sample notice message": ["Default allocation applied"],
    }
    assert source_coverage.select(
        "fact",
        "source table",
        "source report",
        "rows",
        "gas days",
        "source identifiers",
    ).sort("source report").to_dict(as_series=False) == {
        "fact": [
            "Allocation quantity",
            "MOS stack",
            "Default allocation notice",
            "MOS stack",
            "Allocation limit",
        ],
        "source table": [
            allocation_table,
            mos_table,
            notice_table,
            mos_table,
            limit_table,
        ],
        "source report": ["INT658", "INT665", "INT675", "INT683", "INT688"],
        "rows": [2, 1, 1, 1, 1],
        "gas days": [2, 1, 1, 1, 1],
        "source identifiers": [2, 1, 1, 1, 1],
    }
    assert 'href="/marimo/gas_sttm_mos_allocation/"' in context_links
    assert "MOS Context" in context_links
    assert "Allocation Context" in context_links
    assert "Settlement Context" in context_links
    assert "Capacity Context" in context_links
    assert "Facility Context" in context_links
    assert "Hub / Zone Context" in context_links


def test_sttm_mos_allocation_helpers_cover_missing_data_and_filter_empty_state() -> (
    None
):
    empty_loads = _sttm_mos_allocation_loads(
        mos_stack=pl.DataFrame(),
        allocation_quantity=pl.DataFrame(),
        allocation_limit=pl.DataFrame(),
        default_notice=pl.DataFrame(),
        row_limit=5,
    )
    partial_loads = _sttm_mos_allocation_loads(
        mos_stack=pl.DataFrame(
            {
                "source_system": ["STTM"],
                "source_hub_id": ["SYD"],
                "source_facility_id": ["FAC-1"],
                "step_quantity_gj": [5.0],
            }
        ),
        allocation_quantity=pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 3)],
                "source_system": ["STTM"],
                "source_hub_id": ["SYD"],
                "source_facility_id": ["FAC-1"],
                "allocation_qty_inc_mos_gj": [10.0],
            }
        ),
        allocation_limit=pl.DataFrame(),
        default_notice=pl.DataFrame(),
    )
    error_loads = [
        GasTableLoad(
            spec=STTM_MOS_STACK_TABLE_SPEC,
            uri="s3://bucket/silver/gas_model/silver_gas_fact_sttm_mos_stack",
            dataframe=None,
            error="FileNotFoundError: no parquet files found",
            row_limit=5,
            load_duration_seconds=0.01,
            cache_hit=False,
        )
    ]

    assert sttm_mos_allocation_kpi_frame(empty_loads).is_empty()
    assert sttm_mos_allocation_fact_summary_frame(empty_loads).is_empty()
    assert sttm_mos_stack_summary_frame(empty_loads).is_empty()
    assert sttm_allocation_quantity_summary_frame(empty_loads).is_empty()
    assert sttm_allocation_limit_summary_frame(empty_loads).is_empty()
    assert sttm_default_allocation_notice_summary_frame(empty_loads).is_empty()
    assert sttm_mos_allocation_source_coverage_frame(empty_loads).is_empty()
    assert sttm_mos_allocation_gas_date_options(empty_loads) == (
        STTM_MOS_ALLOCATION_GAS_DATE_FILTER_ALL,
    )
    assert sttm_mos_allocation_source_system_options(empty_loads) == (
        STTM_MOS_ALLOCATION_SOURCE_SYSTEM_FILTER_ALL,
    )
    assert sttm_mos_allocation_hub_options(empty_loads) == (
        STTM_MOS_ALLOCATION_HUB_FILTER_ALL,
    )
    assert sttm_mos_allocation_facility_options(empty_loads) == (
        STTM_MOS_ALLOCATION_FACILITY_FILTER_ALL,
    )
    assert sttm_mos_allocation_kpi_frame(
        partial_loads,
        hub_filter="MISSING",
    ).is_empty()
    assert sttm_mos_allocation_kpi_frame(partial_loads).row(14, named=True) == {
        "metric": "Latest Gas Day",
        "value": "2024-01-03",
        "detail": "Maximum gas_date in the loaded bounded rows",
    }
    assert (
        sttm_mos_stack_summary_frame(partial_loads).row(0, named=True)[
            "total step quantity gj"
        ]
        == 5.0
    )

    empty_markdown = sttm_mos_allocation_empty_state_markdown(empty_loads)
    missing_loads_markdown = sttm_mos_allocation_empty_state_markdown(())
    error_markdown = sttm_mos_allocation_empty_state_markdown(error_loads)
    filtered_markdown = sttm_mos_allocation_empty_state_markdown(partial_loads)
    empty_context_links = render_sttm_mos_allocation_context_links(entries=())
    unmounted_entry = DashboardRegistryEntry(
        concept_id=STTM_MOS_ALLOCATION_CONTEXT_ID,
        title="Unmounted STTM MOS And Allocation",
        description="Available entry without a mounted notebook route.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.AVAILABLE,
        notebook_name=None,
        backing_assets=("silver.gas_model.silver_gas_fact_sttm_mos_stack",),
        generated_gold_paths=(),
        source_chunks=(),
    )
    unmounted_context_links = render_sttm_mos_allocation_context_links(
        entries=(unmounted_entry,)
    )

    assert "No STTM MOS/allocation data is available" in empty_markdown
    assert "did not receive MOS/allocation load results" in missing_loads_markdown
    assert "silver.gas_model.silver_gas_fact_sttm_mos_stack" in empty_markdown
    assert "Bounded preview reads are capped at `5` rows per table" in empty_markdown
    assert "FileNotFoundError: no parquet files found" in error_markdown
    assert "current filters do not match" in filtered_markdown
    assert "No STTM MOS/allocation, MOS, Allocation" in empty_context_links
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


def test_facility_flow_storage_metadata_and_loader_use_recent_bounded_rows() -> None:
    entry = registry_entry_by_concept_id(FACILITY_FLOW_STORAGE_CONTEXT_ID)
    html = render_dashboard_context_panel(FACILITY_FLOW_STORAGE_CONTEXT_ID)
    context_links = render_facility_flow_storage_context_links()
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "13",
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

    load = load_facility_flow_storage_table(config, reader=reader)

    assert entry is not None
    assert entry.status is DashboardStatus.AVAILABLE
    assert entry.notebook_name == "facility_flow_storage"
    assert entry.notebook_route == "/marimo/facility_flow_storage/"
    assert entry.backing_assets == (
        "silver.gas_model.silver_gas_fact_facility_flow_storage",
    )
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/facility.md"
        in entry.generated_gold_paths
    )
    assert "chunk-gbb-procedures-daily-flow-storage" in entry.source_chunk_ids
    assert "Facility Flow And Storage" in html
    assert "chunk-gbb-procedures-daily-flow-storage" in html
    assert 'href="/marimo/facility_flow_storage/"' in context_links
    assert "Facility Context" in context_links
    assert "Flow Context" in context_links
    assert "Capacity Context" in context_links
    assert load.spec == FACILITY_FLOW_STORAGE_TABLE_SPEC
    assert captured == [
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_facility_flow_storage",
            13,
        )
    ]

    cache: GasModelSessionCache = {}
    cached_calls = 0

    def cached_reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        nonlocal cached_calls
        assert uri.endswith(f"/{FACILITY_FLOW_STORAGE_TABLE_NAME}")
        assert storage_options == config.storage_options()
        assert row_limit == 13
        cached_calls += 1
        return pl.DataFrame({"source_system": ["GBB"]})

    first_cached = cached_load_facility_flow_storage_table(
        config,
        cache,
        reader=cached_reader,
        refresh_token="same",
    )
    second_cached = cached_load_facility_flow_storage_table(
        config,
        cache,
        reader=cached_reader,
        refresh_token="same",
    )
    refreshed = cached_load_facility_flow_storage_table(
        config,
        cache,
        reader=cached_reader,
        refresh_token="changed",
    )

    assert cached_calls == 2
    assert not first_cached.cache_hit
    assert second_cached.cache_hit
    assert not refreshed.cache_hit


def test_facility_flow_storage_helpers_summarize_fields_and_sources() -> None:
    source_table = "silver.gbb.silver_gasbb_actual_flow_storage"
    load = _facility_flow_storage_load(
        pl.DataFrame(
            {
                "source_system": ["GBB", "GBB", "GBB"],
                "source_tables": [[source_table], [source_table], []],
                "facility_key": ["fac-1", "fac-1", "fac-2"],
                "location_key": ["loc-1", "loc-1", "loc-2"],
                "gas_date": [
                    date(2024, 1, 2),
                    date(2024, 1, 3),
                    date(2024, 1, 3),
                ],
                "source_facility_id": ["F1", "F1", "F2"],
                "source_location_id": ["L1", "L1", "L2"],
                "demand_tj": [10.0, 12.0, None],
                "supply_tj": [4.0, 6.0, 8.0],
                "transfer_in_tj": [1.0, 2.0, None],
                "transfer_out_tj": [0.0, 1.0, 3.0],
                "held_in_storage_tj": [50.0, 54.0, None],
                "cushion_gas_storage_tj": [5.0, 6.0, None],
                "source_file": ["a.parquet", "b.parquet", "c.parquet"],
                "source_last_updated_timestamp": [
                    datetime(2024, 1, 2, 6),
                    datetime(2024, 1, 3, 6),
                    datetime(2024, 1, 3, 7),
                ],
                "ingested_timestamp": [
                    datetime(2024, 1, 2, 8),
                    datetime(2024, 1, 3, 8),
                    datetime(2024, 1, 3, 9),
                ],
            }
        ),
        row_limit=20,
    )

    kpis = facility_flow_storage_kpi_frame(load)
    summary = facility_flow_storage_summary_frame(load)
    daily = facility_flow_storage_daily_frame(load)
    source_coverage = facility_flow_storage_source_coverage_frame(load)
    observations = facility_flow_storage_observation_frame(load)
    filtered_kpis = facility_flow_storage_kpi_frame(load, facility_filter="F2")
    source_filtered_kpis = facility_flow_storage_kpi_frame(
        load,
        source_system_filter="GBB",
    )
    kpi_values = {row["metric"]: row["value"] for row in kpis.to_dicts()}
    filtered_kpi_values = {
        row["metric"]: row["value"] for row in filtered_kpis.to_dicts()
    }
    source_filtered_kpi_values = {
        row["metric"]: row["value"] for row in source_filtered_kpis.to_dicts()
    }

    assert facility_flow_storage_gas_date_options(load) == (
        FACILITY_FLOW_STORAGE_GAS_DATE_FILTER_ALL,
        "2024-01-03",
        "2024-01-02",
    )
    assert facility_flow_storage_facility_options(load) == (
        FACILITY_FLOW_STORAGE_FACILITY_FILTER_ALL,
        "F1",
        "F2",
    )
    assert facility_flow_storage_source_system_options(load) == (
        FACILITY_FLOW_STORAGE_SOURCE_SYSTEM_FILTER_ALL,
        "GBB",
    )
    assert kpi_values["Loaded facility rows"] == "3"
    assert kpi_values["Facility keys"] == "2"
    assert kpi_values["Source facilities"] == "2"
    assert kpi_values["Source tables"] == "1"
    assert kpi_values["Latest gas date"] == "2024-01-03"
    assert kpi_values["Demand"] == "22 TJ"
    assert kpi_values["Supply"] == "18 TJ"
    assert kpi_values["Transfer out"] == "4 TJ"
    assert kpi_values["Held in storage"] == "104 TJ"
    assert filtered_kpi_values["Loaded facility rows"] == "1"
    assert source_filtered_kpi_values["Loaded facility rows"] == "3"
    assert summary.select(
        "source system",
        "source table",
        "facility key",
        "source facility id",
        "rows",
        "gas days",
        "total demand tj",
        "total supply tj",
        "latest held storage tj",
        "latest gas date",
    ).to_dict(as_series=False) == {
        "source system": ["GBB", "GBB"],
        "source table": [
            source_table,
            "(empty source_table/source_tables value)",
        ],
        "facility key": ["fac-1", "fac-2"],
        "source facility id": ["F1", "F2"],
        "rows": [2, 1],
        "gas days": [2, 1],
        "total demand tj": [22.0, 0.0],
        "total supply tj": [10.0, 8.0],
        "latest held storage tj": [54.0, None],
        "latest gas date": [date(2024, 1, 3), date(2024, 1, 3)],
    }
    assert daily.select(
        "gas date",
        "rows",
        "facilities",
        "total demand tj",
        "total supply tj",
        "total held storage tj",
    ).to_dict(as_series=False) == {
        "gas date": [date(2024, 1, 3), date(2024, 1, 2)],
        "rows": [2, 1],
        "facilities": [2, 1],
        "total demand tj": [12.0, 10.0],
        "total supply tj": [14.0, 4.0],
        "total held storage tj": [54.0, 50.0],
    }
    assert source_coverage.select(
        "source system",
        "source table",
        "rows",
        "facility keys",
        "source facilities",
        "gas days",
        "measure rows",
        "latest gas date",
    ).to_dict(as_series=False) == {
        "source system": ["GBB", "GBB"],
        "source table": [
            source_table,
            "(empty source_table/source_tables value)",
        ],
        "rows": [2, 1],
        "facility keys": [1, 1],
        "source facilities": [1, 1],
        "gas days": [2, 1],
        "measure rows": [2, 1],
        "latest gas date": [date(2024, 1, 3), date(2024, 1, 3)],
    }
    assert observations.select(
        "gas date",
        "source facility id",
        "demand_tj",
        "supply_tj",
        "held_in_storage_tj",
    ).to_dicts()[:2] == [
        {
            "gas date": date(2024, 1, 3),
            "source facility id": "F2",
            "demand_tj": None,
            "supply_tj": 8.0,
            "held_in_storage_tj": None,
        },
        {
            "gas date": date(2024, 1, 3),
            "source facility id": "F1",
            "demand_tj": 12.0,
            "supply_tj": 6.0,
            "held_in_storage_tj": 54.0,
        },
    ]


def test_facility_flow_storage_helpers_cover_missing_data_behavior() -> None:
    empty_load = _facility_flow_storage_load(pl.DataFrame(), row_limit=6)
    partial_load = _facility_flow_storage_load(
        pl.DataFrame(
            {
                "source_system": ["GBB"],
                "gas_date": [date(2024, 1, 4)],
                "source_facility_id": ["F1"],
                "demand_tj": [10.0],
            }
        ),
        row_limit=6,
    )
    no_measure_load = _facility_flow_storage_load(
        pl.DataFrame(
            {
                "source_system": ["GBB"],
                "gas_date": [date(2024, 1, 4)],
                "source_facility_id": ["F1"],
            }
        ),
        row_limit=6,
    )
    error_load = GasTableLoad(
        spec=FACILITY_FLOW_STORAGE_TABLE_SPEC,
        uri="s3://bucket/silver/gas_model/silver_gas_fact_facility_flow_storage",
        dataframe=None,
        error="FileNotFoundError: no parquet files found",
        row_limit=6,
        load_duration_seconds=0.01,
        cache_hit=False,
    )

    assert facility_flow_storage_kpi_frame(empty_load).is_empty()
    assert facility_flow_storage_summary_frame(empty_load).is_empty()
    assert facility_flow_storage_daily_frame(empty_load).is_empty()
    assert facility_flow_storage_source_coverage_frame(empty_load).is_empty()
    assert facility_flow_storage_observation_frame(empty_load).is_empty()
    assert facility_flow_storage_gas_date_options(empty_load) == (
        FACILITY_FLOW_STORAGE_GAS_DATE_FILTER_ALL,
    )
    assert facility_flow_storage_facility_options(empty_load) == (
        FACILITY_FLOW_STORAGE_FACILITY_FILTER_ALL,
    )
    assert facility_flow_storage_source_system_options(empty_load) == (
        FACILITY_FLOW_STORAGE_SOURCE_SYSTEM_FILTER_ALL,
    )
    assert facility_flow_storage_kpi_frame(
        partial_load,
        gas_date_filter="2024-01-05",
    ).is_empty()
    partial_coverage = facility_flow_storage_source_coverage_frame(partial_load)
    no_measure_values = {
        row["metric"]: row["value"]
        for row in facility_flow_storage_kpi_frame(no_measure_load).to_dicts()
    }
    empty_markdown = facility_flow_storage_empty_state_markdown(empty_load)
    error_markdown = facility_flow_storage_empty_state_markdown(error_load)
    filtered_markdown = facility_flow_storage_empty_state_markdown(partial_load)
    missing_load_markdown = facility_flow_storage_empty_state_markdown(None)
    empty_context_links = render_facility_flow_storage_context_links(entries=())

    assert partial_coverage.row(0, named=True)["source table"] == (
        "(empty source_table/source_tables value)"
    )
    assert no_measure_values["Demand"] == "unknown"
    assert no_measure_values["Held in storage"] == "unknown"
    assert "No facility flow or storage data is available" in empty_markdown
    assert "silver.gas_model.silver_gas_fact_facility_flow_storage" in empty_markdown
    assert "Bounded preview reads are capped at `6` rows per table" in empty_markdown
    assert "FileNotFoundError: no parquet files found" in error_markdown
    assert "current filters do not match" in filtered_markdown
    assert "did not receive a facility flow/storage load" in missing_load_markdown
    assert (
        "No Facility flow/storage, Facility, Flow, Capacity, map, source "
        "coverage, or table explorer entries are registered."
    ) in empty_context_links


def test_linepack_metadata_and_loader_use_recent_bounded_rows() -> None:
    entry = registry_entry_by_concept_id(LINEPACK_CONTEXT_ID)
    html = render_dashboard_context_panel(LINEPACK_CONTEXT_ID)
    context_links = render_linepack_context_links()
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "14",
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

    load = load_linepack_table(config, reader=reader)

    assert entry is not None
    assert entry.status is DashboardStatus.AVAILABLE
    assert entry.notebook_name == "linepack_adequacy"
    assert entry.notebook_route == "/marimo/linepack_adequacy/"
    assert "silver.gas_model.silver_gas_fact_linepack" in entry.backing_assets
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/linepack.md"
        in entry.generated_gold_paths
    )
    assert "chunk-gbb-procedures-linepack-capacity-adequacy" in (entry.source_chunk_ids)
    assert "Linepack Context" in html
    assert "chunk-gbb-procedures-linepack-capacity-adequacy" in html
    assert 'href="/marimo/linepack_adequacy/"' in context_links
    assert "Linepack Context" in context_links
    assert "Flow Context" in context_links
    assert "Capacity Context" in context_links
    assert "MOS Context" in context_links
    assert load.spec == LINEPACK_TABLE_SPEC
    assert captured == [
        (
            "s3://prod-energy-market-aemo/silver/gas_model/silver_gas_fact_linepack",
            14,
        )
    ]

    cache: GasModelSessionCache = {}
    cached_calls = 0

    def cached_reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        nonlocal cached_calls
        assert uri.endswith(f"/{LINEPACK_TABLE_NAME}")
        assert storage_options == config.storage_options()
        assert row_limit == 14
        cached_calls += 1
        return pl.DataFrame({"source_system": ["GBB"]})

    first_cached = cached_load_linepack_table(
        config,
        cache,
        reader=cached_reader,
        refresh_token="same",
    )
    second_cached = cached_load_linepack_table(
        config,
        cache,
        reader=cached_reader,
        refresh_token="same",
    )
    refreshed = cached_load_linepack_table(
        config,
        cache,
        reader=cached_reader,
        refresh_token="changed",
    )

    assert cached_calls == 2
    assert not first_cached.cache_hit
    assert second_cached.cache_hit
    assert not refreshed.cache_hit


def test_capacity_outlook_metadata_and_loader_use_recent_bounded_rows() -> None:
    entry = registry_entry_by_concept_id(CAPACITY_CONTEXT_ID)
    html = render_dashboard_context_panel(CAPACITY_CONTEXT_ID)
    context_links = render_capacity_outlook_context_links()
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "11",
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

    load = load_capacity_outlook_table(config, reader=reader)

    assert entry is not None
    assert entry.status is DashboardStatus.AVAILABLE
    assert entry.notebook_name == "capacity_outlook"
    assert entry.notebook_route == "/marimo/capacity_outlook/"
    assert entry.backing_assets == (
        "silver.gas_model.silver_gas_fact_capacity_outlook",
    )
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/capacity.md"
        in entry.generated_gold_paths
    )
    assert "chunk-gbb-procedures-capacity-outlooks" in entry.source_chunk_ids
    assert "Capacity Context" in html
    assert 'data-status="available"' in html
    assert 'href="/marimo/capacity_outlook/"' in context_links
    assert "Facility Context" in context_links
    assert "Flow Context" in context_links
    assert "Connection Point Context" in context_links
    assert load.spec == CAPACITY_OUTLOOK_TABLE_SPEC
    assert captured == [
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_capacity_outlook",
            11,
        )
    ]

    cache: GasModelSessionCache = {}
    cached_calls = 0

    def cached_reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        nonlocal cached_calls
        assert uri.endswith(f"/{CAPACITY_OUTLOOK_TABLE_NAME}")
        assert storage_options == config.storage_options()
        assert row_limit == 11
        cached_calls += 1
        return pl.DataFrame({"source_system": ["GBB"]})

    first_cached = cached_load_capacity_outlook_table(
        config,
        cache,
        reader=cached_reader,
        refresh_token="same",
    )
    second_cached = cached_load_capacity_outlook_table(
        config,
        cache,
        reader=cached_reader,
        refresh_token="same",
    )
    refreshed = cached_load_capacity_outlook_table(
        config,
        cache,
        reader=cached_reader,
        refresh_token="changed",
    )

    assert cached_calls == 2
    assert not first_cached.cache_hit
    assert second_cached.cache_hit
    assert not refreshed.cache_hit


def test_capacity_outlook_helpers_summarize_filters_and_source_coverage() -> None:
    source_tables = [
        "silver.gbb.silver_gasbb_short_term_capacity_outlook",
        "silver.gbb.silver_gasbb_medium_term_capacity_outlook",
        "silver.gbb.silver_gasbb_uncontracted_capacity",
        "silver.gbb.silver_gasbb_nameplate_rating",
        "silver.gbb.silver_gasbb_connection_point_nameplate",
    ]
    load = _capacity_outlook_load(
        pl.DataFrame(
            {
                "source_system": ["GBB", "GBB", "GBB", "GBB", "GBB"],
                "source_tables": [[table] for table in source_tables],
                "source_table": source_tables,
                "source_facility_id": ["F1", "F1", "F2", "F3", "F4"],
                "facility_name": [
                    "Pipeline A",
                    "Pipeline A",
                    "Pipeline B",
                    "Pipeline C",
                    "Connection Point D",
                ],
                "capacity_type": [
                    "MDQ",
                    "MDQ",
                    "MDQ",
                    "nameplate",
                    "connection_point_nameplate",
                ],
                "flow_direction": [
                    "RECEIPT",
                    "DELIVERY",
                    "RECEIPT",
                    "DELIVERY",
                    None,
                ],
                "from_gas_date": [
                    date(2024, 1, 1),
                    date(2024, 2, 1),
                    None,
                    date(2024, 1, 1),
                    date(2024, 3, 1),
                ],
                "to_gas_date": [None, date(2024, 2, 29), None, None, None],
                "outlook_month": [None, None, 4, None, None],
                "outlook_year": [None, None, 2024, None, None],
                "receipt_location_id": ["R1", "R2", "R3", "R4", "CP-D"],
                "delivery_location_id": ["D1", "D2", "D3", "D4", None],
                "capacity_quantity_tj": [10.0, 20.0, 30.0, 40.0, 50.0],
                "capacity_description": [
                    "Short outlook",
                    "Medium outlook",
                    "Uncontracted capacity",
                    "Nameplate rating",
                    "Connection point capacity",
                ],
                "source_surrogate_key": ["src-1", "src-2", "src-3", "src-4", "src-5"],
                "source_file": ["capacity.csv"] * 5,
                "source_last_updated_timestamp": [
                    datetime(2024, 1, 1, 8),
                    datetime(2024, 1, 2, 8),
                    datetime(2024, 1, 3, 8),
                    datetime(2024, 1, 4, 8),
                    datetime(2024, 1, 5, 8),
                ],
                "ingested_timestamp": [
                    datetime(2024, 1, 1, 9),
                    datetime(2024, 1, 2, 9),
                    datetime(2024, 1, 3, 9),
                    datetime(2024, 1, 4, 9),
                    datetime(2024, 1, 5, 9),
                ],
            }
        ),
        row_limit=5,
    )

    source_coverage = capacity_outlook_source_coverage_frame(load)
    summary = capacity_outlook_summary_frame(load)
    observations = capacity_outlook_observation_frame(load, preview_rows=10)
    kpi_values = {
        row["metric"]: row["value"]
        for row in capacity_outlook_kpi_frame(load).to_dicts()
    }
    coverage_labels = set(source_coverage["capacity source coverage"].to_list())
    filtered_kpis = capacity_outlook_kpi_frame(
        load,
        capacity_type_filter="MDQ",
        direction_filter="RECEIPT",
    )

    assert kpi_values["Loaded capacity rows"] == "5"
    assert kpi_values["Capacity source coverage"] == "5"
    assert kpi_values["Date ranges"] == "4"
    assert kpi_values["Capacity quantity"] == "150 TJ"
    assert {
        "Short-term capacity outlook",
        "Medium-term capacity outlook",
        "Uncontracted capacity",
        "Nameplate rating",
        "Connection-point nameplate",
    } == coverage_labels
    assert "2024-02-01 to 2024-02-29" in capacity_outlook_date_range_options(load)
    assert "2024-04" in capacity_outlook_date_range_options(load)
    assert "MDQ" in capacity_outlook_capacity_type_options(load)
    assert "RECEIPT" in capacity_outlook_direction_options(load)
    assert "F2" in capacity_outlook_facility_options(load)
    assert "Uncontracted capacity" in capacity_outlook_source_coverage_options(load)
    assert capacity_outlook_source_system_options(load) == (
        CAPACITY_OUTLOOK_SOURCE_SYSTEM_FILTER_ALL,
        "GBB",
    )
    assert filtered_kpis.row(0, named=True)["value"] == "2"
    assert (
        summary.select(
            "capacity source coverage",
            "source facility id",
            "facility",
            "capacity type",
            "direction",
            "date range",
            "total capacity tj",
        ).height
        == 5
    )
    assert (
        observations.select(
            "capacity source coverage",
            "from gas date",
            "to gas date",
            "outlook month",
            "outlook year",
            "capacity_quantity_tj",
        ).height
        == 5
    )


def test_capacity_outlook_helpers_cover_missing_data_and_empty_states() -> None:
    missing_columns_load = _capacity_outlook_load(
        pl.DataFrame(
            {
                "source_system": ["GBB"],
                "source_table": ["silver.gbb.silver_gasbb_nameplate_rating"],
                "source_facility_id": ["F1"],
            }
        ),
        row_limit=4,
    )
    unavailable_load = GasTableLoad(
        spec=CAPACITY_OUTLOOK_TABLE_SPEC,
        uri="s3://bucket/silver/gas_model/silver_gas_fact_capacity_outlook",
        dataframe=None,
        error="FileNotFoundError: no parquet files found",
        row_limit=4,
        load_duration_seconds=0.01,
        cache_hit=False,
    )
    empty_load = _capacity_outlook_load(pl.DataFrame(), row_limit=4)

    kpis = capacity_outlook_kpi_frame(missing_columns_load)
    coverage = capacity_outlook_source_coverage_frame(missing_columns_load)
    observations = capacity_outlook_observation_frame(missing_columns_load)
    filtered = capacity_outlook_summary_frame(
        missing_columns_load,
        facility_filter="missing",
    )
    unavailable_markdown = capacity_outlook_empty_state_markdown(unavailable_load)
    empty_markdown = capacity_outlook_empty_state_markdown(empty_load)
    filtered_markdown = capacity_outlook_empty_state_markdown(missing_columns_load)
    missing_load_markdown = capacity_outlook_empty_state_markdown(None)
    empty_context_links = render_capacity_outlook_context_links(entries=())

    assert kpis.row(0, named=True)["value"] == "1"
    assert coverage.row(0, named=True)["capacity source coverage"] == "Nameplate rating"
    assert observations.row(0, named=True)["capacity_quantity_tj"] is None
    assert filtered.is_empty()
    assert "No capacity outlook data is available" in unavailable_markdown
    assert "FileNotFoundError: no parquet files found" in unavailable_markdown
    assert "The table loaded successfully but returned no rows" in empty_markdown
    assert "current filters do not match" in filtered_markdown
    assert "did not receive a capacity outlook load" in missing_load_markdown
    assert (
        "No Capacity, Facility, Flow, Connection Point, Gas Day, map, "
        "source coverage, or table explorer entries are registered."
    ) in empty_context_links


def test_capacity_outlook_helpers_cover_fallback_classification_branches() -> None:
    load = _capacity_outlook_load(
        pl.DataFrame(
            [
                {
                    "source_system": "GBB",
                    "source_table": "custom.connection",
                    "source_facility_id": "F1",
                    "capacity_type": "connection_point_nameplate",
                    "flow_direction": "RECEIPT",
                    "to_gas_date": date(2024, 5, 1),
                },
                {
                    "source_system": "GBB",
                    "source_table": "custom.uncontracted",
                    "source_facility_id": "F2",
                    "capacity_description": "uncontracted capacity",
                    "outlook_year": 2025,
                },
                {
                    "source_system": "GBB",
                    "source_table": "custom.nameplate",
                    "source_facility_id": "F3",
                    "capacity_type": "nameplate",
                    "outlook_month": 7.0,
                    "outlook_year": 2026.0,
                },
                {
                    "source_system": "GBB",
                    "source_table": "custom.medium",
                    "source_facility_id": "F4",
                    "capacity_description": "medium-term capacity outlook",
                },
                {
                    "source_system": "GBB",
                    "source_table": "custom.short",
                    "source_facility_id": "F5",
                    "capacity_description": "short_term capacity outlook",
                    "outlook_month": "",
                    "outlook_year": "",
                },
                {
                    "source_system": "GBB",
                    "source_facility_id": "F6",
                    "capacity_type": "custom",
                    "capacity_description": "custom capacity",
                    "outlook_month": True,
                    "outlook_year": "not-a-year",
                },
            ]
        )
    )
    empty_load = _capacity_outlook_load(pl.DataFrame(), row_limit=3)

    coverage_labels = {
        row["capacity source coverage"]
        for row in capacity_outlook_source_coverage_frame(load).to_dicts()
    }
    date_range_options = capacity_outlook_date_range_options(load)
    filtered = capacity_outlook_summary_frame(
        load,
        date_range_filter="to 2024-05-01",
        source_coverage_filter="Connection-point nameplate",
        source_system_filter="GBB",
    )

    assert capacity_outlook_kpi_frame(empty_load).is_empty()
    assert capacity_outlook_source_coverage_frame(empty_load).is_empty()
    assert capacity_outlook_observation_frame(empty_load).is_empty()
    assert capacity_outlook_facility_options(empty_load) == (
        CAPACITY_OUTLOOK_FACILITY_FILTER_ALL,
    )
    assert {
        "Connection-point nameplate",
        "Uncontracted capacity",
        "Nameplate rating",
        "Medium-term capacity outlook",
        "Short-term capacity outlook",
        "Other capacity outlook",
    } == coverage_labels
    assert "to 2024-05-01" in date_range_options
    assert "2025" in date_range_options
    assert "2026-07" in date_range_options
    assert "(undated outlook period)" in date_range_options
    assert filtered.height == 1
    assert filtered.row(0, named=True)["capacity source coverage"] == (
        "Connection-point nameplate"
    )


def test_context_links_render_planned_entries_without_routes() -> None:
    planned_capacity = DashboardRegistryEntry(
        concept_id=CAPACITY_CONTEXT_ID,
        title="Capacity Context",
        description="Planned capacity context.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.PLANNED,
        notebook_name=None,
        backing_assets=("silver.gas_model.silver_gas_fact_capacity_outlook",),
        generated_gold_paths=(
            "tools/gas-market-knowledge-base/generated/gold/glossary/capacity.md",
        ),
        source_chunks=(),
    )

    capacity_links = render_capacity_outlook_context_links(entries=(planned_capacity,))
    facility_flow_links = render_facility_flow_storage_context_links(
        entries=(planned_capacity,)
    )
    facility_links = render_facility_context_links(entries=(planned_capacity,))
    connection_point_links = render_connection_point_context_links(
        entries=(planned_capacity,)
    )

    assert 'data-dashboard-status="planned"' in capacity_links
    assert "<span>Capacity Context</span>" in capacity_links
    assert "<span>Capacity Context</span>" in facility_flow_links
    assert "<span>Capacity Context</span>" in facility_links
    assert "<span>Capacity Context</span>" in connection_point_links


def test_capacity_auction_metadata_and_loader_use_recent_bounded_rows() -> None:
    entry = registry_entry_by_concept_id(CAPACITY_AUCTION_CONTEXT_ID)
    html = render_dashboard_context_panel(CAPACITY_AUCTION_CONTEXT_ID)
    context_links = render_capacity_auction_context_links()
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "13",
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

    load = load_capacity_auction_table(config, reader=reader)

    assert entry is not None
    assert entry.status is DashboardStatus.AVAILABLE
    assert entry.notebook_name == "capacity_auction"
    assert entry.notebook_route == "/marimo/capacity_auction/"
    assert entry.backing_assets == (
        "silver.gas_model.silver_gas_fact_capacity_auction",
    )
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/capacity.md"
        in entry.generated_gold_paths
    )
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/hub-zone.md"
        in entry.generated_gold_paths
    )
    assert "chunk-sttm-procedures-capacity-settlement" in entry.source_chunk_ids
    assert "Capacity Auctions" in html
    assert 'data-status="available"' in html
    assert 'href="/marimo/capacity_auction/"' in context_links
    assert 'href="/marimo/capacity_outlook/"' in context_links
    assert "Hub / Zone Context" in context_links
    assert "Gas Market Overview" in context_links
    assert load.spec == CAPACITY_AUCTION_TABLE_SPEC
    assert captured == [
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_capacity_auction",
            13,
        )
    ]

    cache: GasModelSessionCache = {}
    cached_calls = 0

    def cached_reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        nonlocal cached_calls
        assert uri.endswith(f"/{CAPACITY_AUCTION_TABLE_NAME}")
        assert storage_options == config.storage_options()
        assert row_limit == 13
        cached_calls += 1
        return pl.DataFrame({"source_system": ["VICGAS"]})

    first_cached = cached_load_capacity_auction_table(
        config,
        cache,
        reader=cached_reader,
        refresh_token="same",
    )
    second_cached = cached_load_capacity_auction_table(
        config,
        cache,
        reader=cached_reader,
        refresh_token="same",
    )
    refreshed = cached_load_capacity_auction_table(
        config,
        cache,
        reader=cached_reader,
        refresh_token="changed",
    )

    assert cached_calls == 2
    assert not first_cached.cache_hit
    assert second_cached.cache_hit
    assert not refreshed.cache_hit


def test_capacity_auction_helpers_summarize_filters_and_metrics() -> None:
    load = _capacity_auction_load(
        pl.DataFrame(
            {
                "source_system": ["VICGAS", "VICGAS", "VICGAS", "VICGAS"],
                "source_tables": [
                    ["silver.vicgas.silver_int339_v4_ccauction_bid_stack_1"],
                    ["silver.vicgas.silver_int353_v4_ccauction_qty_won_1"],
                    ["silver.vicgas.silver_int348_v4_cctransfer_1"],
                    [],
                ],
                "source_table": [
                    "silver.vicgas.silver_int339_v4_ccauction_bid_stack_1",
                    "silver.vicgas.silver_int353_v4_ccauction_qty_won_1",
                    "silver.vicgas.silver_int348_v4_cctransfer_1",
                    None,
                ],
                "auction_id": ["A1", "A1", "A2", None],
                "auction_date": [
                    date(2024, 1, 1),
                    date(2024, 1, 1),
                    date(2024, 2, 1),
                    None,
                ],
                "source_zone_id": ["Z1", "Z1", "Z2", None],
                "zone_name": ["Sydney", "Sydney", "Brisbane", None],
                "zone_type": ["STTM", "STTM", "STTM", None],
                "capacity_period": ["Apr-2026", "Apr-2026", None, None],
                "start_date": [
                    None,
                    date(2024, 4, 1),
                    date(2024, 3, 1),
                    None,
                ],
                "end_date": [
                    None,
                    date(2024, 4, 30),
                    date(2024, 3, 31),
                    None,
                ],
                "auction_metric": [
                    "bid_stack",
                    "quantity_won",
                    "transfer",
                    "zone_reference",
                ],
                "quantity_gj": [10.0, 20.0, 30.0, None],
                "price": [1.0, 7.0, None, None],
                "source_surrogate_key": ["src-1", "src-2", "src-3", "src-4"],
                "source_file": ["capacity-auction.csv"] * 4,
                "source_last_updated_timestamp": [
                    datetime(2024, 1, 1, 8),
                    datetime(2024, 1, 2, 8),
                    datetime(2024, 1, 3, 8),
                    datetime(2024, 1, 4, 8),
                ],
                "ingested_timestamp": [
                    datetime(2024, 1, 1, 9),
                    datetime(2024, 1, 2, 9),
                    datetime(2024, 1, 3, 9),
                    datetime(2024, 1, 4, 9),
                ],
            }
        ),
        row_limit=4,
    )

    kpi_values = {
        row["metric"]: row["value"]
        for row in capacity_auction_kpi_frame(load).to_dicts()
    }
    filtered_summary = capacity_auction_summary_frame(
        load,
        auction_date_filter="2024-01-01",
        zone_filter="Sydney (Z1)",
        capacity_period_filter="Apr-2026",
        metric_filter="quantity_won",
        source_system_filter="VICGAS",
    )
    metric_summary = capacity_auction_metric_frame(load)
    observations = capacity_auction_observation_frame(load, preview_rows=10)

    assert kpi_values["Loaded auction rows"] == "4"
    assert kpi_values["Auction IDs"] == "2"
    assert kpi_values["Capacity periods"] == "3"
    assert kpi_values["Quantity"] == "60 GJ"
    assert kpi_values["Price range"] == "1 to 7"
    assert "2024-01-01" in capacity_auction_auction_date_options(load)
    assert "(missing)" in capacity_auction_auction_date_options(load)
    assert "Sydney (Z1)" in capacity_auction_zone_options(load)
    assert "(missing Hub / Zone)" in capacity_auction_zone_options(load)
    assert "Apr-2026" in capacity_auction_capacity_period_options(load)
    assert "2024-03-01 to 2024-03-31" in (
        capacity_auction_capacity_period_options(load)
    )
    assert "quantity_won" in capacity_auction_metric_options(load)
    assert capacity_auction_source_system_options(load) == (
        CAPACITY_AUCTION_SOURCE_SYSTEM_FILTER_ALL,
        "VICGAS",
    )
    assert filtered_summary.height == 1
    assert filtered_summary.row(0, named=True)["auction metric"] == "quantity_won"
    assert filtered_summary.row(0, named=True)["total quantity gj"] == 20.0
    assert {row["auction metric"] for row in metric_summary.to_dicts()} == {
        "bid_stack",
        "quantity_won",
        "transfer",
        "zone_reference",
    }
    assert (
        observations.select(
            "auction id",
            "auction date",
            "zone",
            "capacity period",
            "auction metric",
            "quantity_gj",
            "price",
        ).height
        == 4
    )


def test_capacity_auction_helpers_cover_missing_data_and_empty_states() -> None:
    missing_columns_load = _capacity_auction_load(
        pl.DataFrame(
            {
                "source_system": ["VICGAS"],
                "auction_metric": ["system_capability"],
            }
        ),
        row_limit=4,
    )
    unavailable_load = GasTableLoad(
        spec=CAPACITY_AUCTION_TABLE_SPEC,
        uri="s3://bucket/silver/gas_model/silver_gas_fact_capacity_auction",
        dataframe=None,
        error="FileNotFoundError: no parquet files found",
        row_limit=4,
        load_duration_seconds=0.01,
        cache_hit=False,
    )
    empty_load = _capacity_auction_load(pl.DataFrame(), row_limit=4)
    fallback_load = _capacity_auction_load(
        pl.DataFrame(
            [
                {
                    "source_system": "VICGAS",
                    "zone_name": "Name Only",
                    "auction_metric": "start_only",
                    "start_date": date(2024, 5, 1),
                },
                {
                    "source_system": "VICGAS",
                    "source_zone_id": "Z9",
                    "auction_metric": "end_only",
                    "end_date": date(2024, 6, 1),
                },
            ]
        )
    )
    planned_capacity_auction = DashboardRegistryEntry(
        concept_id=CAPACITY_AUCTION_CONTEXT_ID,
        title="Capacity Auctions",
        description="Planned capacity auction dashboard.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.PLANNED,
        notebook_name=None,
        backing_assets=("silver.gas_model.silver_gas_fact_capacity_auction",),
        generated_gold_paths=(
            "tools/gas-market-knowledge-base/generated/gold/glossary/capacity.md",
        ),
        source_chunks=(),
    )

    kpis = capacity_auction_kpi_frame(missing_columns_load)
    summary = capacity_auction_summary_frame(missing_columns_load)
    observations = capacity_auction_observation_frame(missing_columns_load)
    filtered = capacity_auction_metric_frame(
        missing_columns_load,
        zone_filter="missing",
    )
    unavailable_markdown = capacity_auction_empty_state_markdown(unavailable_load)
    empty_markdown = capacity_auction_empty_state_markdown(empty_load)
    filtered_markdown = capacity_auction_empty_state_markdown(missing_columns_load)
    missing_load_markdown = capacity_auction_empty_state_markdown(None)
    empty_context_links = render_capacity_auction_context_links(entries=())
    planned_context_links = render_capacity_auction_context_links(
        entries=(planned_capacity_auction,)
    )
    fallback_zone_options = capacity_auction_zone_options(fallback_load)
    fallback_period_options = capacity_auction_capacity_period_options(fallback_load)

    assert kpis.row(0, named=True)["value"] == "1"
    assert summary.row(0, named=True)["auction metric"] == "system_capability"
    assert summary.row(0, named=True)["zone"] == "(missing Hub / Zone)"
    assert observations.row(0, named=True)["quantity_gj"] is None
    assert filtered.is_empty()
    assert capacity_auction_kpi_frame(empty_load).is_empty()
    assert capacity_auction_summary_frame(empty_load).is_empty()
    assert capacity_auction_observation_frame(empty_load).is_empty()
    assert capacity_auction_zone_options(empty_load) == ("All zones",)
    assert "Name Only" in fallback_zone_options
    assert "Z9" in fallback_zone_options
    assert "from 2024-05-01" in fallback_period_options
    assert "to 2024-06-01" in fallback_period_options
    assert "No capacity auction data is available" in unavailable_markdown
    assert "FileNotFoundError: no parquet files found" in unavailable_markdown
    assert "The table loaded successfully but returned no rows" in empty_markdown
    assert "current filters do not match" in filtered_markdown
    assert "did not receive a capacity auction load" in missing_load_markdown
    assert (
        "No Capacity Auction, Capacity, Hub / Zone, market overview, "
        "source coverage, source lineage, or table explorer entries are "
        "registered."
    ) in empty_context_links
    assert 'data-dashboard-status="planned"' in planned_context_links
    assert "<span>Capacity Auctions</span>" in planned_context_links


def test_capacity_transaction_metadata_and_loader_use_recent_bounded_rows() -> None:
    entry = registry_entry_by_concept_id(CAPACITY_TRANSACTION_CONTEXT_ID)
    html = render_dashboard_context_panel(CAPACITY_TRANSACTION_CONTEXT_ID)
    context_links = render_capacity_transaction_context_links()
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "17",
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

    load = load_capacity_transaction_table(config, reader=reader)

    assert entry is not None
    assert entry.status is DashboardStatus.AVAILABLE
    assert entry.notebook_name == "capacity_transactions"
    assert entry.notebook_route == "/marimo/capacity_transactions/"
    assert entry.backing_assets == (
        "silver.gas_model.silver_gas_fact_capacity_transaction",
    )
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/capacity.md"
        in entry.generated_gold_paths
    )
    assert "Capacity Transactions" in html
    assert 'data-status="available"' in html
    assert 'href="/marimo/capacity_transactions/"' in context_links
    assert 'href="/marimo/capacity_outlook/"' in context_links
    assert 'href="/marimo/capacity_auction/"' in context_links
    assert "Gas Market Overview" in context_links
    assert load.spec == CAPACITY_TRANSACTION_TABLE_SPEC
    assert captured == [
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_capacity_transaction",
            17,
        )
    ]

    cache: GasModelSessionCache = {}
    cached_calls = 0

    def cached_reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        nonlocal cached_calls
        assert uri.endswith(f"/{CAPACITY_TRANSACTION_TABLE_NAME}")
        assert storage_options == config.storage_options()
        assert row_limit == 17
        cached_calls += 1
        return pl.DataFrame({"source_system": ["GBB"]})

    first_cached = cached_load_capacity_transaction_table(
        config,
        cache,
        reader=cached_reader,
    )
    second_cached = cached_load_capacity_transaction_table(
        config,
        cache,
        reader=cached_reader,
    )
    refreshed = cached_load_capacity_transaction_table(
        config,
        cache,
        reader=cached_reader,
        refresh_token=1,
    )

    assert cached_calls == 2
    assert not first_cached.cache_hit
    assert second_cached.cache_hit
    assert not refreshed.cache_hit


def test_capacity_transaction_helpers_summarize_filters_sources_and_measures() -> None:
    lng_transaction_table = "silver.gbb.silver_gasbb_lng_transactions"
    lng_shipment_table = "silver.gbb.silver_gasbb_lng_shipments"
    short_transaction_table = "silver.gbb.silver_gasbb_short_term_transactions"
    swap_transaction_table = "silver.gbb.silver_gasbb_short_term_swap_transactions"
    load = _capacity_transaction_load(
        pl.DataFrame(
            {
                "source_system": ["GBB", "GBB", "GBB", "GBB"],
                "source_tables": [
                    [short_transaction_table],
                    [lng_transaction_table],
                    [lng_shipment_table],
                    [],
                ],
                "source_table": [
                    short_transaction_table,
                    lng_transaction_table,
                    lng_shipment_table,
                    swap_transaction_table,
                ],
                "transaction_type": [
                    "capacity",
                    "lng_transaction",
                    "lng_shipment",
                    "swap",
                ],
                "transaction_date": [
                    date(2024, 1, 1),
                    date(2024, 2, 1),
                    date(2024, 2, 15),
                    None,
                ],
                "supply_start_date": [
                    date(2024, 1, 1),
                    date(2024, 2, 1),
                    date(2024, 2, 15),
                    date(2024, 3, 1),
                ],
                "supply_end_date": [
                    date(2024, 1, 31),
                    date(2024, 2, 29),
                    date(2024, 2, 15),
                    None,
                ],
                "source_location_id": ["SA", None, None, "VIC"],
                "source_facility_id": [None, None, "LNG1", "F2"],
                "quantity_tj": [1.5, None, None, 2.5],
                "quantity_gj": [1500.0, None, None, 2500.0],
                "volume_pj": [None, 0.7, 0.8, None],
                "price": [7.5, 10.0, None, 5.0],
                "source_surrogate_key": ["src-1", "src-2", "src-3", "src-4"],
                "source_file": ["capacity-transaction.csv"] * 4,
                "source_last_updated_timestamp": [
                    datetime(2024, 1, 1, 8),
                    datetime(2024, 2, 1, 8),
                    datetime(2024, 2, 15, 8),
                    datetime(2024, 3, 1, 8),
                ],
                "ingested_timestamp": [
                    datetime(2024, 1, 1, 9),
                    datetime(2024, 2, 1, 9),
                    datetime(2024, 2, 15, 9),
                    datetime(2024, 3, 1, 9),
                ],
            }
        ),
        row_limit=4,
    )

    kpi_values = {
        row["metric"]: row["value"]
        for row in capacity_transaction_kpi_frame(load).to_dicts()
    }
    filtered_summary = capacity_transaction_summary_frame(
        load,
        transaction_type_filter="lng_transaction",
        transaction_date_filter="2024-02-01",
        location_filter="(missing source location)",
        facility_filter="(missing source facility)",
        source_system_filter="GBB",
    )
    source_coverage = capacity_transaction_source_coverage_frame(load)
    observations = capacity_transaction_observation_frame(load, preview_rows=10)

    assert kpi_values["Loaded transaction rows"] == "4"
    assert kpi_values["Transaction types"] == "4"
    assert kpi_values["Quantity TJ"] == "4 TJ"
    assert kpi_values["Quantity GJ"] == "4,000 GJ"
    assert kpi_values["Volume PJ"] == "1.5 PJ"
    assert kpi_values["Price range"] == "5 to 10"
    assert "lng_transaction" in capacity_transaction_type_options(load)
    assert "2024-02-01" in capacity_transaction_date_options(load)
    assert "(missing)" in capacity_transaction_date_options(load)
    assert "SA" in capacity_transaction_location_options(load)
    assert "(missing source location)" in capacity_transaction_location_options(load)
    assert "LNG1" in capacity_transaction_facility_options(load)
    assert "(missing source facility)" in capacity_transaction_facility_options(load)
    assert capacity_transaction_source_system_options(load) == (
        CAPACITY_TRANSACTION_SOURCE_SYSTEM_FILTER_ALL,
        "GBB",
    )
    assert filtered_summary.height == 1
    assert filtered_summary.row(0, named=True)["transaction type"] == (
        "lng_transaction"
    )
    assert filtered_summary.row(0, named=True)["total volume pj"] == 0.7
    assert {row["source table"] for row in source_coverage.to_dicts()} == {
        short_transaction_table,
        lng_transaction_table,
        lng_shipment_table,
        swap_transaction_table,
    }
    assert (
        observations.select(
            "transaction type",
            "transaction date",
            "source location",
            "source facility",
            "quantity_tj",
            "quantity_gj",
            "volume_pj",
            "price",
        ).height
        == 4
    )


def test_capacity_transaction_helpers_cover_missing_data_and_empty_states() -> None:
    missing_columns_load = _capacity_transaction_load(
        pl.DataFrame(
            {
                "source_system": ["GBB"],
                "transaction_type": ["lng_transaction"],
            }
        ),
        row_limit=4,
    )
    unavailable_load = GasTableLoad(
        spec=CAPACITY_TRANSACTION_TABLE_SPEC,
        uri="s3://bucket/silver/gas_model/silver_gas_fact_capacity_transaction",
        dataframe=None,
        error="FileNotFoundError: no parquet files found",
        row_limit=4,
        load_duration_seconds=0.01,
        cache_hit=False,
    )
    empty_load = _capacity_transaction_load(pl.DataFrame(), row_limit=4)
    fallback_load = _capacity_transaction_load(
        pl.DataFrame(
            [
                {
                    "source_system": "GBB",
                    "transaction_type": "start_only",
                    "supply_start_date": date(2024, 5, 1),
                    "source_location_id": "QLD",
                },
                {
                    "source_system": "GBB",
                    "transaction_type": "end_only",
                    "supply_end_date": date(2024, 6, 1),
                    "source_facility_id": "LNG2",
                },
            ]
        )
    )
    planned_capacity_transaction = DashboardRegistryEntry(
        concept_id=CAPACITY_TRANSACTION_CONTEXT_ID,
        title="Capacity Transactions",
        description="Planned capacity transaction dashboard.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.PLANNED,
        notebook_name=None,
        backing_assets=("silver.gas_model.silver_gas_fact_capacity_transaction",),
        generated_gold_paths=(
            "tools/gas-market-knowledge-base/generated/gold/glossary/capacity.md",
        ),
        source_chunks=(),
    )

    kpis = capacity_transaction_kpi_frame(missing_columns_load)
    summary = capacity_transaction_summary_frame(missing_columns_load)
    source_coverage = capacity_transaction_source_coverage_frame(missing_columns_load)
    observations = capacity_transaction_observation_frame(missing_columns_load)
    filtered = capacity_transaction_source_coverage_frame(
        missing_columns_load,
        location_filter="missing",
    )
    fallback_observations = capacity_transaction_observation_frame(fallback_load)
    unavailable_markdown = capacity_transaction_empty_state_markdown(unavailable_load)
    empty_markdown = capacity_transaction_empty_state_markdown(empty_load)
    filtered_markdown = capacity_transaction_empty_state_markdown(missing_columns_load)
    missing_load_markdown = capacity_transaction_empty_state_markdown(None)
    empty_context_links = render_capacity_transaction_context_links(entries=())
    planned_context_links = render_capacity_transaction_context_links(
        entries=(planned_capacity_transaction,)
    )

    assert kpis.row(0, named=True)["value"] == "1"
    assert summary.row(0, named=True)["transaction type"] == "lng_transaction"
    assert summary.row(0, named=True)["source location"] == (
        "(missing source location)"
    )
    assert source_coverage.row(0, named=True)["source table"] == (
        "(empty source_table/source_tables value)"
    )
    assert observations.row(0, named=True)["volume_pj"] is None
    assert filtered.is_empty()
    assert capacity_transaction_kpi_frame(empty_load).is_empty()
    assert capacity_transaction_summary_frame(empty_load).is_empty()
    assert capacity_transaction_observation_frame(empty_load).is_empty()
    assert capacity_transaction_type_options(empty_load) == ("All transaction types",)
    assert "from 2024-05-01" in set(
        fallback_observations.get_column("supply period").to_list()
    )
    assert "to 2024-06-01" in set(
        fallback_observations.get_column("supply period").to_list()
    )
    assert "No capacity transaction data is available" in unavailable_markdown
    assert "FileNotFoundError: no parquet files found" in unavailable_markdown
    assert "The table loaded successfully but returned no rows" in empty_markdown
    assert "current filters do not match" in filtered_markdown
    assert "did not receive a capacity transaction load" in missing_load_markdown
    assert (
        "No Capacity Transactions, Capacity, Capacity Auctions, market "
        "overview, source coverage, source lineage, or table explorer entries "
        "are registered."
    ) in empty_context_links
    assert 'data-dashboard-status="planned"' in planned_context_links
    assert "<span>Capacity Transactions</span>" in planned_context_links


def test_linepack_helpers_summarize_quantities_adequacy_and_sources() -> None:
    gbb_source_table = "silver.gbb.silver_gasbb_linepack_capacity_adequacy"
    vicgas_source_table = "silver.vicgas.silver_int128_v4_actual_linepack_1"
    load = _linepack_load(
        pl.DataFrame(
            {
                "source_system": ["GBB", "GBB", "VICGAS"],
                "source_tables": [[gbb_source_table], [gbb_source_table], []],
                "source_table": [None, None, vicgas_source_table],
                "facility_key": ["fac-1", "fac-1", "fac-2"],
                "zone_key": ["zone-1", "zone-1", "zone-2"],
                "gas_date": [
                    date(2024, 1, 2),
                    date(2024, 1, 3),
                    date(2024, 1, 3),
                ],
                "observation_timestamp": [
                    datetime(2024, 1, 2, 6),
                    datetime(2024, 1, 3, 6),
                    datetime(2024, 1, 3, 7),
                ],
                "source_facility_id": ["F1", "F1", "F2"],
                "actual_linepack_gj": [1000.0, 900.0, 700.0],
                "adequacy_flag": ["Green", "Red", None],
                "adequacy_description": ["Adequate", "Below minimum", None],
                "source_file": ["a.parquet", "b.parquet", "c.parquet"],
                "source_last_updated_timestamp": [
                    datetime(2024, 1, 2, 7),
                    datetime(2024, 1, 3, 7),
                    datetime(2024, 1, 3, 8),
                ],
                "ingested_timestamp": [
                    datetime(2024, 1, 2, 8),
                    datetime(2024, 1, 3, 8),
                    datetime(2024, 1, 3, 9),
                ],
            }
        ),
        row_limit=20,
    )

    kpis = linepack_kpi_frame(load)
    summary = linepack_summary_frame(load)
    source_coverage = linepack_source_coverage_frame(load)
    observations = linepack_observation_frame(load)
    filtered_kpis = linepack_kpi_frame(load, adequacy_flag_filter="Red")
    facility_filtered_kpis = linepack_kpi_frame(load, facility_filter="F1")
    zone_filtered_kpis = linepack_kpi_frame(load, zone_filter="zone-2")
    source_filtered_kpis = linepack_kpi_frame(load, source_system_filter="VICGAS")
    kpi_values = {row["metric"]: row["value"] for row in kpis.to_dicts()}
    filtered_kpi_values = {
        row["metric"]: row["value"] for row in filtered_kpis.to_dicts()
    }
    facility_filtered_kpi_values = {
        row["metric"]: row["value"] for row in facility_filtered_kpis.to_dicts()
    }
    zone_filtered_kpi_values = {
        row["metric"]: row["value"] for row in zone_filtered_kpis.to_dicts()
    }
    source_filtered_kpi_values = {
        row["metric"]: row["value"] for row in source_filtered_kpis.to_dicts()
    }

    assert linepack_gas_date_options(load) == (
        LINEPACK_GAS_DATE_FILTER_ALL,
        "2024-01-03",
        "2024-01-02",
    )
    assert linepack_facility_options(load) == (
        LINEPACK_FACILITY_FILTER_ALL,
        "F1",
        "F2",
    )
    assert linepack_zone_options(load) == (
        LINEPACK_ZONE_FILTER_ALL,
        "zone-1",
        "zone-2",
    )
    assert linepack_adequacy_flag_options(load) == (
        LINEPACK_ADEQUACY_FLAG_FILTER_ALL,
        "Green",
        "Red",
    )
    assert linepack_source_system_options(load) == (
        LINEPACK_SOURCE_SYSTEM_FILTER_ALL,
        "GBB",
        "VICGAS",
    )
    assert kpi_values["Loaded linepack rows"] == "3"
    assert kpi_values["Facility keys"] == "2"
    assert kpi_values["Zone keys"] == "2"
    assert kpi_values["Source facilities"] == "2"
    assert kpi_values["Source tables"] == "2"
    assert kpi_values["Latest gas date"] == "2024-01-03"
    assert kpi_values["Linepack quantity"] == "2,600 GJ"
    assert kpi_values["Adequacy flags"] == "2"
    assert filtered_kpi_values["Loaded linepack rows"] == "1"
    assert facility_filtered_kpi_values["Loaded linepack rows"] == "2"
    assert zone_filtered_kpi_values["Loaded linepack rows"] == "1"
    assert source_filtered_kpi_values["Loaded linepack rows"] == "1"
    assert summary.select(
        "source system",
        "source table",
        "facility key",
        "zone key",
        "source facility id",
        "adequacy flag",
        "adequacy description",
        "rows",
        "linepack rows",
        "latest linepack gj",
        "latest observation",
    ).to_dict(as_series=False) == {
        "source system": ["VICGAS", "GBB", "GBB"],
        "source table": [vicgas_source_table, gbb_source_table, gbb_source_table],
        "facility key": ["fac-2", "fac-1", "fac-1"],
        "zone key": ["zone-2", "zone-1", "zone-1"],
        "source facility id": ["F2", "F1", "F1"],
        "adequacy flag": [None, "Red", "Green"],
        "adequacy description": [None, "Below minimum", "Adequate"],
        "rows": [1, 1, 1],
        "linepack rows": [1, 1, 1],
        "latest linepack gj": [700.0, 900.0, 1000.0],
        "latest observation": [
            datetime(2024, 1, 3, 7),
            datetime(2024, 1, 3, 6),
            datetime(2024, 1, 2, 6),
        ],
    }
    assert source_coverage.select(
        "source system",
        "source table",
        "rows",
        "facility keys",
        "zone keys",
        "source facilities",
        "gas days",
        "linepack rows",
        "adequacy flags",
        "latest gas date",
    ).to_dict(as_series=False) == {
        "source system": ["GBB", "VICGAS"],
        "source table": [gbb_source_table, vicgas_source_table],
        "rows": [2, 1],
        "facility keys": [1, 1],
        "zone keys": [1, 1],
        "source facilities": [1, 1],
        "gas days": [2, 1],
        "linepack rows": [2, 1],
        "adequacy flags": [2, 0],
        "latest gas date": [date(2024, 1, 3), date(2024, 1, 3)],
    }
    assert observations.select(
        "gas date",
        "source system",
        "source facility id",
        "zone key",
        "actual_linepack_gj",
        "adequacy flag",
    ).to_dicts()[:2] == [
        {
            "gas date": date(2024, 1, 3),
            "source system": "VICGAS",
            "source facility id": "F2",
            "zone key": "zone-2",
            "actual_linepack_gj": 700.0,
            "adequacy flag": None,
        },
        {
            "gas date": date(2024, 1, 3),
            "source system": "GBB",
            "source facility id": "F1",
            "zone key": "zone-1",
            "actual_linepack_gj": 900.0,
            "adequacy flag": "Red",
        },
    ]


def test_linepack_helpers_cover_missing_data_behavior() -> None:
    empty_load = _linepack_load(pl.DataFrame(), row_limit=6)
    partial_load = _linepack_load(
        pl.DataFrame(
            {
                "source_system": ["GBB"],
                "actual_linepack_gj": [321.0],
            }
        ),
        row_limit=6,
    )
    error_load = GasTableLoad(
        spec=LINEPACK_TABLE_SPEC,
        uri="s3://bucket/silver/gas_model/silver_gas_fact_linepack",
        dataframe=None,
        error="FileNotFoundError: no parquet files found",
        row_limit=6,
        load_duration_seconds=0.01,
        cache_hit=False,
    )

    assert linepack_kpi_frame(empty_load).is_empty()
    assert linepack_summary_frame(empty_load).is_empty()
    assert linepack_source_coverage_frame(empty_load).is_empty()
    assert linepack_observation_frame(empty_load).is_empty()
    assert linepack_gas_date_options(empty_load) == (LINEPACK_GAS_DATE_FILTER_ALL,)
    assert linepack_facility_options(empty_load) == (LINEPACK_FACILITY_FILTER_ALL,)
    assert linepack_zone_options(empty_load) == (LINEPACK_ZONE_FILTER_ALL,)
    assert linepack_adequacy_flag_options(empty_load) == (
        LINEPACK_ADEQUACY_FLAG_FILTER_ALL,
    )
    assert linepack_source_system_options(empty_load) == (
        LINEPACK_SOURCE_SYSTEM_FILTER_ALL,
    )
    assert linepack_kpi_frame(
        partial_load,
        gas_date_filter="2024-01-05",
    ).is_empty()
    partial_summary = linepack_summary_frame(partial_load)
    partial_coverage = linepack_source_coverage_frame(partial_load)
    empty_markdown = linepack_empty_state_markdown(empty_load)
    error_markdown = linepack_empty_state_markdown(error_load)
    filtered_markdown = linepack_empty_state_markdown(partial_load)
    missing_load_markdown = linepack_empty_state_markdown(None)
    empty_context_links = render_linepack_context_links(entries=())

    assert partial_summary.row(0, named=True)["source table"] == (
        "(empty source_table/source_tables value)"
    )
    assert partial_summary.row(0, named=True)["facility key"] is None
    assert partial_summary.row(0, named=True)["zone key"] is None
    assert partial_summary.row(0, named=True)["latest linepack gj"] == 321.0
    assert partial_coverage.row(0, named=True)["linepack rows"] == 1
    assert "No linepack data is available" in empty_markdown
    assert "silver.gas_model.silver_gas_fact_linepack" in empty_markdown
    assert "Bounded preview reads are capped at `6` rows per table" in empty_markdown
    assert "FileNotFoundError: no parquet files found" in error_markdown
    assert "current filters do not match" in filtered_markdown
    assert "did not receive a linepack load result" in missing_load_markdown
    assert (
        "No Linepack, Flow, Capacity, MOS, Facility, Hub / Zone, source "
        "coverage, or table explorer entries are registered."
    ) in empty_context_links


def test_nomination_forecast_metadata_and_loader_use_recent_bounded_rows() -> None:
    entry = registry_entry_by_concept_id(NOMINATION_FORECAST_CONTEXT_ID)
    html = render_dashboard_context_panel(NOMINATION_FORECAST_CONTEXT_ID)
    context_links = render_nomination_forecast_context_links()
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "17",
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

    load = load_nomination_forecast_table(config, reader=reader)

    assert entry is not None
    assert entry.status is DashboardStatus.AVAILABLE
    assert entry.notebook_name == "nomination_demand_forecast"
    assert entry.notebook_route == "/marimo/nomination_demand_forecast/"
    assert entry.backing_assets == (
        "silver.gas_model.silver_gas_fact_nomination_forecast",
    )
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/flow.md"
        in entry.generated_gold_paths
    )
    assert "chunk-gbb-guide-flow-report" in entry.source_chunk_ids
    assert "Nomination And Demand Forecast" in html
    assert "chunk-gbb-guide-flow-report" in html
    assert 'href="/marimo/nomination_demand_forecast/"' in context_links
    assert "Flow Context" in context_links
    assert "Facility Context" in context_links
    assert "Gas Day Context" in context_links
    assert load.spec == NOMINATION_FORECAST_TABLE_SPEC
    assert captured == [
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_nomination_forecast",
            17,
        )
    ]

    cache: GasModelSessionCache = {}
    cached_calls = 0

    def cached_reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        nonlocal cached_calls
        assert uri.endswith(f"/{NOMINATION_FORECAST_TABLE_NAME}")
        assert storage_options == config.storage_options()
        assert row_limit == 17
        cached_calls += 1
        return pl.DataFrame({"source_system": ["GBB"]})

    first_cached = cached_load_nomination_forecast_table(
        config,
        cache,
        reader=cached_reader,
        refresh_token="same",
    )
    second_cached = cached_load_nomination_forecast_table(
        config,
        cache,
        reader=cached_reader,
        refresh_token="same",
    )
    refreshed = cached_load_nomination_forecast_table(
        config,
        cache,
        reader=cached_reader,
        refresh_token="changed",
    )

    assert cached_calls == 2
    assert not first_cached.cache_hit
    assert second_cached.cache_hit
    assert not refreshed.cache_hit


def test_nomination_forecast_helpers_summarize_filters_and_horizon() -> None:
    gbb_source_table = "silver.gbb.silver_gasbb_nomination_and_forecast"
    vicgas_source_table = "silver.vicgas.silver_int153_v4_demand_forecast_rpt_1"
    load = _nomination_forecast_load(
        pl.DataFrame(
            {
                "source_system": ["GBB", "GBB", "VICGAS"],
                "source_table": [
                    gbb_source_table,
                    gbb_source_table,
                    vicgas_source_table,
                ],
                "source_tables": [
                    [gbb_source_table],
                    [gbb_source_table],
                    [vicgas_source_table],
                ],
                "facility_key": ["fac-1", "fac-1", None],
                "location_key": ["loc-1", "loc-1", "loc-2"],
                "gas_date": [
                    date(2024, 1, 2),
                    date(2024, 1, 3),
                    date(2024, 1, 4),
                ],
                "forecast_type": [
                    "gbb_nomination_forecast",
                    "gbb_nomination_forecast",
                    "interval_demand",
                ],
                "forecast_version": ["v1", "v1", "42"],
                "gas_interval": [1, 2, 12],
                "source_facility_id": ["F1", "F1", None],
                "source_location_id": ["L1", "L1", "L2"],
                "demand_forecast_gj": [1000.0, 1100.0, 900.0],
                "supply_forecast_gj": [500.0, None, None],
                "transfer_in_forecast_gj": [100.0, 150.0, None],
                "transfer_out_forecast_gj": [20.0, 25.0, None],
                "override_quantity_gj": [950.0, None, None],
                "source_file": ["a.parquet", "b.parquet", "c.parquet"],
                "source_last_updated_timestamp": [
                    datetime(2024, 1, 2, 6),
                    datetime(2024, 1, 3, 6),
                    datetime(2024, 1, 4, 5),
                ],
                "ingested_timestamp": [
                    datetime(2024, 1, 2, 8),
                    datetime(2024, 1, 3, 8),
                    datetime(2024, 1, 4, 6),
                ],
            }
        ),
        row_limit=20,
    )
    as_of_date = date(2024, 1, 3)

    kpis = nomination_forecast_kpi_frame(load, as_of_date=as_of_date)
    summary = nomination_forecast_summary_frame(load, as_of_date=as_of_date)
    daily = nomination_forecast_daily_frame(load, as_of_date=as_of_date)
    source_coverage = nomination_forecast_source_coverage_frame(
        load,
        as_of_date=as_of_date,
    )
    observations = nomination_forecast_observation_frame(load, as_of_date=as_of_date)
    facility_filtered_kpis = nomination_forecast_kpi_frame(
        load,
        facility_filter="F1",
        as_of_date=as_of_date,
    )
    location_filtered_kpis = nomination_forecast_kpi_frame(
        load,
        location_filter="L2",
        as_of_date=as_of_date,
    )
    source_filtered_kpis = nomination_forecast_kpi_frame(
        load,
        source_system_filter="VICGAS",
        as_of_date=as_of_date,
    )
    kpi_values = {row["metric"]: row["value"] for row in kpis.to_dicts()}
    facility_kpi_values = {
        row["metric"]: row["value"] for row in facility_filtered_kpis.to_dicts()
    }
    location_kpi_values = {
        row["metric"]: row["value"] for row in location_filtered_kpis.to_dicts()
    }
    source_kpi_values = {
        row["metric"]: row["value"] for row in source_filtered_kpis.to_dicts()
    }

    assert nomination_forecast_gas_date_options(load) == (
        NOMINATION_FORECAST_GAS_DATE_FILTER_ALL,
        "2024-01-04",
        "2024-01-03",
        "2024-01-02",
    )
    assert nomination_forecast_source_system_options(load) == (
        NOMINATION_FORECAST_SOURCE_SYSTEM_FILTER_ALL,
        "GBB",
        "VICGAS",
    )
    assert nomination_forecast_facility_options(load) == (
        NOMINATION_FORECAST_FACILITY_FILTER_ALL,
        "F1",
    )
    assert nomination_forecast_location_options(load) == (
        NOMINATION_FORECAST_LOCATION_FILTER_ALL,
        "L1",
        "L2",
    )
    assert kpi_values["Loaded forecast rows"] == "3"
    assert kpi_values["Forecast type/version pairs"] == "2"
    assert kpi_values["Current/future forecasts"] == "2"
    assert kpi_values["Historical forecasts"] == "1"
    assert kpi_values["Source systems"] == "2"
    assert kpi_values["Source tables"] == "2"
    assert kpi_values["Facilities"] == "1"
    assert kpi_values["Locations"] == "2"
    assert kpi_values["Latest gas date"] == "2024-01-04"
    assert kpi_values["Demand forecast"] == "3,000 GJ"
    assert kpi_values["Supply forecast"] == "500 GJ"
    assert kpi_values["Transfer in forecast"] == "250 GJ"
    assert kpi_values["Transfer out forecast"] == "45 GJ"
    assert kpi_values["Override quantity"] == "950 GJ"
    assert facility_kpi_values["Loaded forecast rows"] == "2"
    assert location_kpi_values["Loaded forecast rows"] == "1"
    assert source_kpi_values["Demand forecast"] == "900 GJ"
    assert summary.select(
        "forecast type",
        "forecast version",
        "forecast horizon",
        "rows",
        "total demand forecast gj",
        "latest gas date",
    ).to_dicts() == [
        {
            "forecast type": "interval_demand",
            "forecast version": "42",
            "forecast horizon": "Current/future forecast",
            "rows": 1,
            "total demand forecast gj": 900.0,
            "latest gas date": date(2024, 1, 4),
        },
        {
            "forecast type": "gbb_nomination_forecast",
            "forecast version": "v1",
            "forecast horizon": "Current/future forecast",
            "rows": 1,
            "total demand forecast gj": 1100.0,
            "latest gas date": date(2024, 1, 3),
        },
        {
            "forecast type": "gbb_nomination_forecast",
            "forecast version": "v1",
            "forecast horizon": "Historical forecast",
            "rows": 1,
            "total demand forecast gj": 1000.0,
            "latest gas date": date(2024, 1, 2),
        },
    ]
    assert daily.select(
        "gas date",
        "forecast horizon",
        "rows",
        "total demand forecast gj",
        "total override quantity gj",
    ).to_dicts() == [
        {
            "gas date": date(2024, 1, 4),
            "forecast horizon": "Current/future forecast",
            "rows": 1,
            "total demand forecast gj": 900.0,
            "total override quantity gj": 0.0,
        },
        {
            "gas date": date(2024, 1, 3),
            "forecast horizon": "Current/future forecast",
            "rows": 1,
            "total demand forecast gj": 1100.0,
            "total override quantity gj": 0.0,
        },
        {
            "gas date": date(2024, 1, 2),
            "forecast horizon": "Historical forecast",
            "rows": 1,
            "total demand forecast gj": 1000.0,
            "total override quantity gj": 950.0,
        },
    ]
    assert source_coverage.select(
        "source system",
        "source table",
        "rows",
        "forecast types",
        "forecast versions",
        "gas days",
        "measure rows",
        "latest gas date",
    ).to_dicts() == [
        {
            "source system": "GBB",
            "source table": gbb_source_table,
            "rows": 2,
            "forecast types": 1,
            "forecast versions": 1,
            "gas days": 2,
            "measure rows": 2,
            "latest gas date": date(2024, 1, 3),
        },
        {
            "source system": "VICGAS",
            "source table": vicgas_source_table,
            "rows": 1,
            "forecast types": 1,
            "forecast versions": 1,
            "gas days": 1,
            "measure rows": 1,
            "latest gas date": date(2024, 1, 4),
        },
    ]
    assert observations.select(
        "gas date",
        "forecast horizon",
        "forecast type",
        "demand_forecast_gj",
        "override_quantity_gj",
    ).to_dicts()[:2] == [
        {
            "gas date": date(2024, 1, 4),
            "forecast horizon": "Current/future forecast",
            "forecast type": "interval_demand",
            "demand_forecast_gj": 900.0,
            "override_quantity_gj": None,
        },
        {
            "gas date": date(2024, 1, 3),
            "forecast horizon": "Current/future forecast",
            "forecast type": "gbb_nomination_forecast",
            "demand_forecast_gj": 1100.0,
            "override_quantity_gj": None,
        },
    ]


def test_nomination_forecast_helpers_cover_empty_state_behavior() -> None:
    empty_load = _nomination_forecast_load(pl.DataFrame(), row_limit=6)
    partial_load = _nomination_forecast_load(
        pl.DataFrame(
            {
                "source_system": ["GBB"],
                "gas_date": [date(2024, 1, 4)],
                "source_facility_id": ["F1"],
                "demand_forecast_gj": [10.0],
            }
        ),
        row_limit=6,
    )
    no_measure_load = _nomination_forecast_load(
        pl.DataFrame(
            {
                "source_system": ["GBB"],
                "gas_date": [date(2024, 1, 4)],
                "source_facility_id": ["F1"],
            }
        ),
        row_limit=6,
    )
    unknown_gas_date_load = _nomination_forecast_load(
        pl.DataFrame(
            {
                "source_system": ["GBB"],
                "gas_date": [None],
                "demand_forecast_gj": [5.0],
            }
        ),
        row_limit=6,
    )
    error_load = GasTableLoad(
        spec=NOMINATION_FORECAST_TABLE_SPEC,
        uri="s3://bucket/silver/gas_model/silver_gas_fact_nomination_forecast",
        dataframe=None,
        error="FileNotFoundError: no parquet files found",
        row_limit=6,
        load_duration_seconds=0.01,
        cache_hit=False,
    )

    assert nomination_forecast_kpi_frame(empty_load).is_empty()
    assert nomination_forecast_summary_frame(empty_load).is_empty()
    assert nomination_forecast_daily_frame(empty_load).is_empty()
    assert nomination_forecast_source_coverage_frame(empty_load).is_empty()
    assert nomination_forecast_observation_frame(empty_load).is_empty()
    assert nomination_forecast_gas_date_options(empty_load) == (
        NOMINATION_FORECAST_GAS_DATE_FILTER_ALL,
    )
    assert nomination_forecast_source_system_options(empty_load) == (
        NOMINATION_FORECAST_SOURCE_SYSTEM_FILTER_ALL,
    )
    assert nomination_forecast_facility_options(empty_load) == (
        NOMINATION_FORECAST_FACILITY_FILTER_ALL,
    )
    assert nomination_forecast_location_options(empty_load) == (
        NOMINATION_FORECAST_LOCATION_FILTER_ALL,
    )
    assert nomination_forecast_kpi_frame(
        partial_load,
        gas_date_filter="2024-01-05",
    ).is_empty()
    partial_coverage = nomination_forecast_source_coverage_frame(partial_load)
    no_measure_values = {
        row["metric"]: row["value"]
        for row in nomination_forecast_kpi_frame(no_measure_load).to_dicts()
    }
    unknown_horizon_observation = nomination_forecast_observation_frame(
        unknown_gas_date_load,
        as_of_date=date(2024, 1, 4),
    )
    empty_markdown = nomination_forecast_empty_state_markdown(empty_load)
    error_markdown = nomination_forecast_empty_state_markdown(error_load)
    filtered_markdown = nomination_forecast_empty_state_markdown(partial_load)
    missing_load_markdown = nomination_forecast_empty_state_markdown(None)
    empty_context_links = render_nomination_forecast_context_links(entries=())

    assert partial_coverage.row(0, named=True)["source table"] == (
        "(empty source_table/source_tables value)"
    )
    assert no_measure_values["Demand forecast"] == "unknown"
    assert no_measure_values["Override quantity"] == "unknown"
    assert (
        unknown_horizon_observation.row(0, named=True)["forecast horizon"]
        == "Unknown Gas Day forecast"
    )
    assert "No nomination or demand forecast data is available" in empty_markdown
    assert "silver.gas_model.silver_gas_fact_nomination_forecast" in empty_markdown
    assert "Bounded preview reads are capped at `6` rows per table" in empty_markdown
    assert "FileNotFoundError: no parquet files found" in error_markdown
    assert "current filters do not match" in filtered_markdown
    assert "did not receive a nomination forecast load" in missing_load_markdown
    assert (
        "No Nomination forecast, Flow, Facility, Gas Day, map, source coverage, "
        "or table explorer entries are registered."
    ) in empty_context_links


def test_forecast_actual_metadata_and_loader_use_recent_bounded_rows() -> None:
    entry = registry_entry_by_concept_id(FORECAST_ACTUAL_CONTEXT_ID)
    html = render_dashboard_context_panel(FORECAST_ACTUAL_CONTEXT_ID)
    context_links = render_forecast_actual_context_links()
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "19",
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

    loads = load_forecast_actual_tables(config, reader=reader)

    assert entry is not None
    assert entry.status is DashboardStatus.AVAILABLE
    assert entry.notebook_name == "forecast_vs_actual"
    assert entry.notebook_route == "/marimo/forecast_vs_actual/"
    assert entry.backing_assets == (
        "silver.gas_model.silver_gas_fact_nomination_forecast",
        "silver.gas_model.silver_gas_fact_facility_flow_storage",
    )
    assert "Forecast Vs Actual Flow And Storage" in html
    assert "chunk-gbb-procedures-daily-flow-storage" in html
    assert 'href="/marimo/forecast_vs_actual/"' in context_links
    assert "Nomination And Demand Forecast" in context_links
    assert "Facility Flow And Storage" in context_links
    assert [load.spec for load in loads] == list(FORECAST_ACTUAL_TABLE_SPECS)
    assert captured == [
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_nomination_forecast",
            19,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_facility_flow_storage",
            19,
        ),
    ]

    cache: GasModelSessionCache = {}
    cached_calls = 0

    def cached_reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        nonlocal cached_calls
        assert storage_options == config.storage_options()
        assert row_limit == 19
        cached_calls += 1
        return pl.DataFrame({"source_system": ["GBB"]})

    first_cached = cached_load_forecast_actual_tables(
        config,
        cache,
        reader=cached_reader,
        refresh_token="same",
    )
    second_cached = cached_load_forecast_actual_tables(
        config,
        cache,
        reader=cached_reader,
        refresh_token="same",
    )
    refreshed = cached_load_forecast_actual_tables(
        config,
        cache,
        reader=cached_reader,
        refresh_token="changed",
    )

    assert cached_calls == 4
    assert [load.cache_hit for load in first_cached] == [False, False]
    assert [load.cache_hit for load in second_cached] == [True, True]
    assert [load.cache_hit for load in refreshed] == [False, False]


def test_forecast_actual_helpers_compare_matched_bounded_data() -> None:
    forecast_load = _nomination_forecast_load(
        pl.DataFrame(
            {
                "source_system": ["GBB", "GBB"],
                "source_table": [
                    "silver.gbb.silver_gasbb_nomination_and_forecast",
                    "silver.gbb.silver_gasbb_nomination_and_forecast",
                ],
                "source_tables": [
                    ["silver.gbb.silver_gasbb_nomination_and_forecast"],
                    ["silver.gbb.silver_gasbb_nomination_and_forecast"],
                ],
                "gas_date": [date(2024, 1, 4), date(2024, 1, 4)],
                "forecast_type": ["gbb_nomination_forecast", "gbb_nomination_forecast"],
                "forecast_version": ["v1", "v1"],
                "source_facility_id": ["F1", "F1"],
                "source_location_id": ["L1", "L1"],
                "demand_forecast_gj": [600.0, 400.0],
                "supply_forecast_gj": [500.0, None],
                "transfer_in_forecast_gj": [100.0, 50.0],
                "transfer_out_forecast_gj": [20.0, 30.0],
                "source_last_updated_timestamp": [
                    datetime(2024, 1, 4, 5),
                    datetime(2024, 1, 4, 6),
                ],
                "ingested_timestamp": [
                    datetime(2024, 1, 4, 7),
                    datetime(2024, 1, 4, 8),
                ],
            }
        ),
        row_limit=12,
    )
    actual_load = _facility_flow_storage_load(
        pl.DataFrame(
            {
                "source_system": ["GBB"],
                "source_tables": [["silver.gbb.silver_gasbb_actual_flow_storage"]],
                "gas_date": [date(2024, 1, 4)],
                "source_facility_id": ["F1"],
                "source_location_id": ["L1"],
                "demand_tj": [1.2],
                "supply_tj": [0.4],
                "transfer_in_tj": [0.1],
                "transfer_out_tj": [0.05],
                "held_in_storage_tj": [5.0],
                "cushion_gas_storage_tj": [1.0],
                "source_last_updated_timestamp": [datetime(2024, 1, 4, 9)],
                "ingested_timestamp": [datetime(2024, 1, 4, 10)],
            }
        ),
        row_limit=12,
    )
    loads = (forecast_load, actual_load)

    kpis = forecast_actual_kpi_frame(loads, as_of_date=date(2024, 1, 4))
    comparison = forecast_actual_comparison_frame(
        loads,
        as_of_date=date(2024, 1, 4),
    )
    storage = forecast_actual_storage_frame(loads, as_of_date=date(2024, 1, 4))
    kpi_values = {row["metric"]: row["value"] for row in kpis.to_dicts()}
    comparison_row = comparison.row(0, named=True)
    storage_row = storage.row(0, named=True)

    assert forecast_actual_gas_date_options(loads) == (
        FORECAST_ACTUAL_GAS_DATE_FILTER_ALL,
        "2024-01-04",
    )
    assert forecast_actual_facility_options(loads) == (
        FORECAST_ACTUAL_FACILITY_FILTER_ALL,
        "F1",
    )
    assert forecast_actual_source_system_options(loads) == (
        FORECAST_ACTUAL_SOURCE_SYSTEM_FILTER_ALL,
        "GBB",
    )
    assert kpi_values["Forecast rows"] == "2"
    assert kpi_values["Actual rows"] == "1"
    assert kpi_values["Matched facility days"] == "1"
    assert kpi_values["Comparable flow measures"] == "4"
    assert comparison_row["match status"] == "Matched forecast and actual"
    assert comparison_row["forecast rows"] == 2
    assert comparison_row["actual rows"] == 1
    assert comparison_row["forecast demand gj"] == 1000.0
    assert comparison_row["actual demand gj"] == 1200.0
    assert comparison_row["demand delta gj"] == 200.0
    assert comparison_row["demand delta pct"] == 20.0
    assert comparison_row["forecast supply gj"] == 500.0
    assert comparison_row["actual supply gj"] == 400.0
    assert comparison_row["supply delta gj"] == -100.0
    assert storage_row["forecast coverage"] == "Matched forecast row in bounded view"
    assert storage_row["held in storage tj"] == 5.0
    assert storage_row["cushion gas storage tj"] == 1.0
    assert "loaded `2` bounded rows" in forecast_actual_empty_state_markdown(loads)


def test_forecast_actual_helpers_degrade_with_missing_forecast_data() -> None:
    loads = (
        _nomination_forecast_load(pl.DataFrame(), row_limit=6),
        _facility_flow_storage_load(
            pl.DataFrame(
                {
                    "source_system": ["GBB"],
                    "source_tables": [["silver.gbb.silver_gasbb_actual_flow_storage"]],
                    "gas_date": [date(2024, 1, 5)],
                    "source_facility_id": ["F2"],
                    "source_location_id": ["L2"],
                    "demand_tj": [2.0],
                    "held_in_storage_tj": [7.0],
                }
            ),
            row_limit=6,
        ),
    )

    comparison = forecast_actual_comparison_frame(loads)
    storage = forecast_actual_storage_frame(loads)
    kpi_values = {
        row["metric"]: row["value"]
        for row in forecast_actual_kpi_frame(loads).to_dicts()
    }

    assert comparison.row(0, named=True)["match status"] == "Actual only"
    assert comparison.row(0, named=True)["forecast rows"] == 0
    assert comparison.row(0, named=True)["actual demand gj"] == 2000.0
    assert storage.row(0, named=True)["forecast coverage"] == (
        "No matching forecast row in bounded view"
    )
    assert kpi_values["Forecast rows"] == "0"
    assert kpi_values["Actual-only groups"] == "1"


def test_forecast_actual_helpers_degrade_with_missing_actual_data() -> None:
    loads = (
        _nomination_forecast_load(
            pl.DataFrame(
                {
                    "source_system": ["VICGAS"],
                    "source_table": [
                        "silver.vicgas.silver_int153_v4_demand_forecast_rpt_1"
                    ],
                    "gas_date": [date(2024, 1, 6)],
                    "forecast_type": ["interval_demand"],
                    "forecast_version": ["42"],
                    "source_facility_id": ["F3"],
                    "source_location_id": ["L3"],
                    "demand_forecast_gj": [900.0],
                }
            ),
            row_limit=6,
        ),
        _facility_flow_storage_load(pl.DataFrame(), row_limit=6),
    )

    comparison = forecast_actual_comparison_frame(loads)
    storage = forecast_actual_storage_frame(loads)
    kpi_values = {
        row["metric"]: row["value"]
        for row in forecast_actual_kpi_frame(loads).to_dicts()
    }

    assert comparison.row(0, named=True)["match status"] == "Forecast only"
    assert comparison.row(0, named=True)["forecast demand gj"] == 900.0
    assert comparison.row(0, named=True)["actual demand gj"] is None
    assert storage.is_empty()
    assert kpi_values["Actual rows"] == "0"
    assert kpi_values["Forecast-only groups"] == "1"


def test_forecast_actual_helpers_make_bounded_messaging_explicit() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "7",
        }
    )
    loads = (
        _nomination_forecast_load(pl.DataFrame(), row_limit=7),
        _facility_flow_storage_load(pl.DataFrame(), row_limit=7),
    )
    local_config = discover_dashboard_config({})
    unavailable_loads = (
        GasTableLoad(
            spec=NOMINATION_FORECAST_TABLE_SPEC,
            uri=f"s3://bucket/silver/gas_model/{NOMINATION_FORECAST_TABLE_NAME}",
            dataframe=None,
            error="FileNotFoundError: no parquet files found",
            row_limit=7,
            load_duration_seconds=0.01,
            cache_hit=False,
        ),
    )
    unknown_date_loads = (
        _nomination_forecast_load(
            pl.DataFrame(
                {
                    "source_system": ["GBB"],
                    "gas_date": [None],
                    "demand_forecast_gj": [5.0],
                }
            ),
            row_limit=7,
        ),
        _facility_flow_storage_load(pl.DataFrame(), row_limit=7),
    )

    bounded_markdown = forecast_actual_bounded_scope_markdown(config, loads)
    local_markdown = forecast_actual_bounded_scope_markdown(local_config, ())
    empty_markdown = forecast_actual_empty_state_markdown(loads)
    missing_load_markdown = forecast_actual_empty_state_markdown(())
    unavailable_markdown = forecast_actual_empty_state_markdown(unavailable_loads)
    unknown_date_kpis = {
        row["metric"]: row["value"]
        for row in forecast_actual_kpi_frame(unknown_date_loads).to_dicts()
    }

    assert "AWS mode uses sampled/recent-only bounded reads" in bounded_markdown
    assert "Bounded preview reads are capped at `7` rows per table" in bounded_markdown
    assert "forecast-only or actual-only" in bounded_markdown
    assert "Local mode uses the configured gas dashboard read policy" in local_markdown
    assert forecast_actual_kpi_frame(loads).is_empty()
    assert forecast_actual_comparison_frame(loads).is_empty()
    assert forecast_actual_facility_options(loads) == (
        FORECAST_ACTUAL_FACILITY_FILTER_ALL,
    )
    assert "No forecast-vs-actual" in render_forecast_actual_context_links(entries=())
    assert "No forecast-vs-actual comparison rows are available" in empty_markdown
    assert "silver_gas_fact_nomination_forecast" in empty_markdown
    assert "silver_gas_fact_facility_flow_storage" in empty_markdown
    assert "not requested by this dashboard run" in missing_load_markdown
    assert "unavailable:" in unavailable_markdown
    assert "FileNotFoundError: no parquet files found" in unavailable_markdown
    assert unknown_date_kpis["Latest Gas Day"] == "unknown"


def test_forecast_actual_numeric_and_timestamp_edges() -> None:
    current = datetime(2024, 1, 5, 12)
    older = datetime(2024, 1, 5, 11)
    newer = datetime(2024, 1, 5, 13)

    assert _optional_float(None) is None
    assert _optional_float(True) is None
    assert _optional_float(object()) is None
    assert _optional_float("not-a-number") is None
    assert _optional_float(float("nan")) is None
    assert _optional_float("1.5") == 1.5
    assert _latest_datetime(None, None) is None
    assert _latest_datetime(None, current) == current
    assert _latest_datetime(current, None) == current
    assert _latest_datetime(current, older) == current
    assert _latest_datetime(current, newer) == newer


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


def test_sttm_contingency_gas_table_loader_uses_bounded_recent_view() -> None:
    captured: list[int | None] = []
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "13",
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
            "silver_gas_fact_sttm_contingency_gas_call"
        )
        assert storage_options == config.storage_options()
        return pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 1), date(2024, 1, 3)],
                "contingency_call_id": ["older", "newer"],
            }
        )

    load = load_sttm_contingency_gas_table(config, reader=reader)

    assert captured == [13]
    assert load.spec == STTM_CONTINGENCY_GAS_TABLE_SPEC
    assert load.row_limit == 13
    assert load.dataframe is not None
    assert load.dataframe["contingency_call_id"].to_list() == ["newer", "older"]


def test_cached_sttm_contingency_gas_table_loader_reuses_session_cache() -> None:
    calls: list[int] = []
    config = _dashboard_config()
    cache: GasModelSessionCache = {}

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        calls.append(len(calls) + 1)
        return pl.DataFrame({"contingency_call_id": [f"call-{calls[-1]}"]})

    first_load = cached_load_sttm_contingency_gas_table(config, cache, reader=reader)
    cached_load = cached_load_sttm_contingency_gas_table(config, cache, reader=reader)
    refreshed_load = cached_load_sttm_contingency_gas_table(
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
    assert cached_load.dataframe["contingency_call_id"].to_list() == ["call-1"]
    assert refreshed_load.dataframe is not None
    assert refreshed_load.dataframe["contingency_call_id"].to_list() == ["call-2"]


def test_sttm_contingency_gas_summaries_filters_and_context_links() -> None:
    int661_table = (
        "silver.sttm.silver_int661_v1_contingency_gas_called_scheduled_bid_offer_rpt_1"
    )
    int673_table = "silver.sttm.silver_int673_v1_total_contingency_bid_offer_rpt_1"
    load = _sttm_contingency_gas_load(
        pl.DataFrame(
            {
                "gas_date": ["2024-01-03", "2024-01-03", "2024-01-02"],
                "source_system": ["STTM", "STTM", "STTM"],
                "source_table": [int661_table, int661_table, int673_table],
                "source_report_id": ["INT661", "INT661", "INT673"],
                "contingency_grain": [
                    "bid_offer_step",
                    "bid_offer_step",
                    "hub_total",
                ],
                "quantity_type": [
                    "called_step_quantity",
                    "confirmed_step_quantity",
                    "total_contingency_gas_offer_qty",
                ],
                "source_hub_id": ["SYD", "SYD", "BNE"],
                "source_hub_name": ["Sydney", "Sydney", "Brisbane"],
                "source_facility_id": ["FAC1", "FAC1", None],
                "facility_name": ["Pipeline A", "Pipeline A", None],
                "flow_direction": ["inject", "inject", None],
                "bid_offer_type": ["offer", "offer", "offer"],
                "participant_id": ["P1", "P1", None],
                "participant_name": ["Participant One", "Participant One", None],
                "contingency_call_id": ["CALL-1", "CALL-1", None],
                "contingency_bid_offer_id": ["CG-1", "CG-1", None],
                "bid_step": [1, 2, None],
                "bid_price": [18.5, 20.0, None],
                "bid_qty_gj": [100.0, 120.0, None],
                "quantity_gj": [40.0, 80.0, 300.0],
                "approval_timestamp": [
                    "2024-01-02 06:00:00",
                    "2024-01-02 07:30:00",
                    None,
                ],
                "source_last_updated_timestamp": [
                    "2024-01-02 08:00:00",
                    "2024-01-02 08:10:00",
                    "2024-01-01 09:00:00",
                ],
                "source_surrogate_key": ["src-1", "src-2", "src-3"],
                "source_file": ["int661.csv", "int661.csv", "int673.csv"],
                "ingested_timestamp": [
                    datetime(2024, 1, 2, 8),
                    datetime(2024, 1, 2, 8, 10),
                    datetime(2024, 1, 1, 9),
                ],
            }
        )
    )

    kpis = sttm_contingency_gas_kpi_frame(load)
    grain_summary = sttm_contingency_gas_grain_summary_frame(load)
    bid_offer_summary = sttm_contingency_gas_bid_offer_summary_frame(
        load,
        "bid_offer_step",
        STTM_CONTINGENCY_GAS_QUANTITY_TYPE_FILTER_ALL,
        "SYD",
        "STTM",
    )
    source_summary = sttm_contingency_gas_source_summary_frame(load)
    observations = sttm_contingency_gas_observation_frame(
        load,
        "bid_offer_step",
        STTM_CONTINGENCY_GAS_QUANTITY_TYPE_FILTER_ALL,
        "SYD",
        "STTM",
    )
    context_links = render_sttm_contingency_gas_context_links()

    assert sttm_contingency_gas_grain_options(load) == (
        STTM_CONTINGENCY_GAS_GRAIN_FILTER_ALL,
        "bid_offer_step",
        "hub_total",
    )
    assert sttm_contingency_gas_quantity_type_options(load) == (
        STTM_CONTINGENCY_GAS_QUANTITY_TYPE_FILTER_ALL,
        "called_step_quantity",
        "confirmed_step_quantity",
        "total_contingency_gas_offer_qty",
    )
    assert sttm_contingency_gas_hub_options(load) == (
        STTM_CONTINGENCY_GAS_HUB_FILTER_ALL,
        "BNE",
        "SYD",
    )
    assert sttm_contingency_gas_source_system_options(load) == (
        STTM_CONTINGENCY_GAS_SOURCE_SYSTEM_FILTER_ALL,
        "STTM",
    )
    assert kpis.select("metric", "value", "detail").to_dict(as_series=False) == {
        "metric": [
            "Loaded contingency gas rows",
            "Gas Days",
            "Contingency grains",
            "Quantity types",
            "Hubs",
            "Facilities",
            "Participants",
            "Bid / Offer identifiers",
            "Rows with Bid / Offer context",
            "Loaded contingency quantity",
            "Contingency quantity range",
            "Latest Gas Day",
            "Latest approval",
            "Accepted source identifiers",
        ],
        "value": [
            "3",
            "2",
            "2",
            "3",
            "2",
            "1",
            "1",
            "1",
            "2",
            "420 GJ",
            "40 to 300",
            "2024-01-03",
            "2024-01-02 07:30:00",
            "3",
        ],
        "detail": [
            "Full table scan",
            "Distinct gas_date values represented",
            "Distinct contingency_grain values represented",
            "Distinct quantity_type values represented",
            "Distinct source_hub_id values represented",
            "Distinct source_facility_id values represented",
            "Distinct participant_id values represented",
            "Distinct contingency_bid_offer_id values represented",
            "Rows carrying bid/offer id, step, price, or quantity fields",
            "Sum of quantity_gj in loaded bounded rows",
            "Minimum and maximum quantity_gj in the current view",
            "Maximum gas_date in the loaded bounded rows",
            "Maximum approval_timestamp in the loaded bounded rows",
            "Distinct source_surrogate_key values represented",
        ],
    }
    assert grain_summary.sort(["contingency grain", "quantity type"]).select(
        "contingency grain",
        "quantity type",
        "hub",
        "rows",
        "gas days",
        "facilities",
        "participants",
        "bid/offer ids",
        "total quantity gj",
        "max quantity gj",
        "latest gas date",
    ).to_dict(as_series=False) == {
        "contingency grain": [
            "bid_offer_step",
            "bid_offer_step",
            "hub_total",
        ],
        "quantity type": [
            "called_step_quantity",
            "confirmed_step_quantity",
            "total_contingency_gas_offer_qty",
        ],
        "hub": ["SYD", "SYD", "BNE"],
        "rows": [1, 1, 1],
        "gas days": [1, 1, 1],
        "facilities": [1, 1, 0],
        "participants": [1, 1, 0],
        "bid/offer ids": [1, 1, 0],
        "total quantity gj": [40.0, 80.0, 300.0],
        "max quantity gj": [40.0, 80.0, 300.0],
        "latest gas date": [date(2024, 1, 3), date(2024, 1, 3), date(2024, 1, 2)],
    }
    assert bid_offer_summary.select(
        "gas date",
        "hub",
        "facility",
        "participant",
        "bid/offer type",
        "bid/offer id",
        "bid step",
        "quantity type",
        "bid price",
        "bid quantity gj",
        "contingency quantity gj",
    ).to_dict(as_series=False) == {
        "gas date": [date(2024, 1, 3), date(2024, 1, 3)],
        "hub": ["SYD", "SYD"],
        "facility": ["FAC1", "FAC1"],
        "participant": ["P1", "P1"],
        "bid/offer type": ["offer", "offer"],
        "bid/offer id": ["CG-1", "CG-1"],
        "bid step": [2, 1],
        "quantity type": ["confirmed_step_quantity", "called_step_quantity"],
        "bid price": [20.0, 18.5],
        "bid quantity gj": [120.0, 100.0],
        "contingency quantity gj": [80.0, 40.0],
    }
    assert source_summary.select(
        "source system",
        "source table",
        "source report",
        "rows",
        "contingency grains",
        "quantity types",
        "hubs",
        "source identifiers",
        "source files",
        "latest gas date",
    ).to_dict(as_series=False) == {
        "source system": ["STTM", "STTM"],
        "source table": [int661_table, int673_table],
        "source report": ["INT661", "INT673"],
        "rows": [2, 1],
        "contingency grains": [1, 1],
        "quantity types": [2, 1],
        "hubs": [1, 1],
        "source identifiers": [2, 1],
        "source files": [1, 1],
        "latest gas date": [date(2024, 1, 3), date(2024, 1, 2)],
    }
    assert observations.select(
        "gas date",
        "source system",
        "source table",
        "contingency grain",
        "quantity type",
        "hub",
        "facility",
        "participant",
        "bid/offer id",
        "bid step",
        "bid price",
        "bid quantity gj",
        "quantity gj",
        "accepted source identifier",
    ).to_dict(as_series=False) == {
        "gas date": [date(2024, 1, 3), date(2024, 1, 3)],
        "source system": ["STTM", "STTM"],
        "source table": [int661_table, int661_table],
        "contingency grain": ["bid_offer_step", "bid_offer_step"],
        "quantity type": ["confirmed_step_quantity", "called_step_quantity"],
        "hub": ["SYD", "SYD"],
        "facility": ["FAC1", "FAC1"],
        "participant": ["P1", "P1"],
        "bid/offer id": ["CG-1", "CG-1"],
        "bid step": [2, 1],
        "bid price": [20.0, 18.5],
        "bid quantity gj": [120.0, 100.0],
        "quantity gj": [80.0, 40.0],
        "accepted source identifier": ["src-2", "src-1"],
    }
    assert 'href="/marimo/gas_sttm_contingency_gas/"' in context_links
    assert 'href="/marimo/gas_bid_offer_stack/"' in context_links
    assert "Schedule Context" in context_links
    assert 'href="/marimo/gas_settlement_activity/"' in context_links
    assert 'href="/marimo/gas_day_explainer/"' in context_links


def test_sttm_contingency_gas_helpers_cover_missing_data_and_filter_empty_state() -> (
    None
):
    empty_load = _sttm_contingency_gas_load(pl.DataFrame(), row_limit=4)
    populated_load = _sttm_contingency_gas_load(
        pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 3)],
                "source_system": ["STTM"],
                "contingency_grain": ["hub_total"],
                "quantity_type": ["total_contingency_gas_offer_qty"],
                "source_hub_id": ["SYD"],
                "quantity_gj": [300.0],
                "source_surrogate_key": ["src-1"],
            }
        )
    )
    no_bid_offer_context_load = _sttm_contingency_gas_load(
        pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 3)],
                "source_system": ["STTM"],
                "contingency_grain": ["hub_total"],
                "quantity_type": ["total_contingency_gas_offer_qty"],
                "source_hub_id": ["SYD"],
                "quantity_gj": [300.0],
            }
        )
    )
    missing_date_load = _sttm_contingency_gas_load(
        pl.DataFrame(
            {
                "source_system": ["STTM"],
                "contingency_grain": ["hub_total"],
                "quantity_type": ["total_contingency_gas_offer_qty"],
                "source_hub_id": ["SYD"],
                "quantity_gj": [300.0],
            }
        )
    )
    error_load = GasTableLoad(
        spec=STTM_CONTINGENCY_GAS_TABLE_SPEC,
        uri=("s3://bucket/silver/gas_model/silver_gas_fact_sttm_contingency_gas_call"),
        dataframe=None,
        error="FileNotFoundError: no parquet files found",
        row_limit=4,
        load_duration_seconds=0.01,
        cache_hit=False,
    )

    assert sttm_contingency_gas_kpi_frame(empty_load).is_empty()
    assert sttm_contingency_gas_grain_summary_frame(empty_load).is_empty()
    assert sttm_contingency_gas_bid_offer_summary_frame(empty_load).is_empty()
    assert sttm_contingency_gas_source_summary_frame(empty_load).is_empty()
    assert sttm_contingency_gas_observation_frame(empty_load).is_empty()
    assert sttm_contingency_gas_grain_options(empty_load) == (
        STTM_CONTINGENCY_GAS_GRAIN_FILTER_ALL,
    )
    assert sttm_contingency_gas_quantity_type_options(empty_load) == (
        STTM_CONTINGENCY_GAS_QUANTITY_TYPE_FILTER_ALL,
    )
    assert sttm_contingency_gas_hub_options(empty_load) == (
        STTM_CONTINGENCY_GAS_HUB_FILTER_ALL,
    )
    assert sttm_contingency_gas_source_system_options(empty_load) == (
        STTM_CONTINGENCY_GAS_SOURCE_SYSTEM_FILTER_ALL,
    )
    assert sttm_contingency_gas_kpi_frame(
        populated_load,
        hub_filter="missing-hub",
    ).is_empty()
    assert (
        sttm_contingency_gas_kpi_frame(
            populated_load,
            quantity_type_filter="total_contingency_gas_offer_qty",
        ).height
        == 14
    )
    assert sttm_contingency_gas_bid_offer_summary_frame(
        no_bid_offer_context_load
    ).is_empty()
    assert sttm_contingency_gas_kpi_frame(missing_date_load).row(11, named=True) == {
        "metric": "Latest Gas Day",
        "value": "unknown",
        "detail": "Maximum gas_date in the loaded bounded rows",
    }

    empty_markdown = sttm_contingency_gas_empty_state_markdown(empty_load)
    error_markdown = sttm_contingency_gas_empty_state_markdown(error_load)
    filtered_markdown = sttm_contingency_gas_empty_state_markdown(populated_load)
    missing_load_markdown = sttm_contingency_gas_empty_state_markdown(None)
    empty_context_links = render_sttm_contingency_gas_context_links(entries=())
    unmounted_entry = DashboardRegistryEntry(
        concept_id="sttm-contingency-gas",
        title="Unmounted STTM Contingency Gas",
        description="Available entry without a mounted notebook route.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.AVAILABLE,
        notebook_name=None,
        backing_assets=("silver.gas_model.silver_gas_fact_sttm_contingency_gas_call",),
        generated_gold_paths=(),
        source_chunks=(),
    )
    unmounted_context_links = render_sttm_contingency_gas_context_links(
        entries=(unmounted_entry,)
    )

    assert "No STTM contingency gas data is available" in empty_markdown
    assert "silver.gas_model.silver_gas_fact_sttm_contingency_gas_call" in (
        empty_markdown
    )
    assert "Bounded preview reads are capped at `4` rows per table" in empty_markdown
    assert "FileNotFoundError: no parquet files found" in error_markdown
    assert "current filters do not match" in filtered_markdown
    assert "did not receive a contingency gas load result" in missing_load_markdown
    assert "No STTM contingency gas, Bid / Offer, Schedule" in empty_context_links
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


def test_heating_value_pressure_metadata_and_loader_use_bounded_recent_rows() -> None:
    entry = registry_entry_by_concept_id(HEATING_VALUE_PRESSURE_CONTEXT_ID)
    html = render_dashboard_context_panel(HEATING_VALUE_PRESSURE_CONTEXT_ID)
    context_links = render_heating_value_pressure_context_links()
    captured: list[tuple[str, int | None]] = []
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
        captured.append((uri, row_limit))
        assert storage_options == config.storage_options()
        if uri.endswith(f"/{HEATING_VALUE_TABLE_NAME}"):
            return pl.DataFrame(
                {
                    "gas_date": [date(2024, 1, 1), date(2024, 1, 3)],
                    "source_zone_id": ["older", "newer"],
                }
            )
        return pl.DataFrame(
            {
                "measurement_timestamp": [
                    datetime(2024, 1, 2),
                    datetime(2024, 1, 4),
                ],
                "source_node_id": ["older", "newer"],
            }
        )

    loads = load_heating_value_pressure_tables(config, reader=reader)

    assert entry is not None
    assert entry.status is DashboardStatus.AVAILABLE
    assert entry.notebook_name == "heating_value_pressure"
    assert entry.notebook_route == "/marimo/heating_value_pressure/"
    assert entry.backing_assets == (
        "silver.gas_model.silver_gas_fact_heating_value",
        "silver.gas_model.silver_gas_fact_scada_pressure",
    )
    assert "Heating Value And SCADA Pressure" in html
    assert "silver.gas_model.silver_gas_fact_heating_value" in html
    assert 'href="/marimo/heating_value_pressure/"' in context_links
    assert "Gas Quality And Composition" in context_links
    assert "Gas System Notices" in context_links
    assert [load.spec for load in loads] == [
        HEATING_VALUE_TABLE_SPEC,
        SCADA_PRESSURE_TABLE_SPEC,
    ]
    assert captured == [
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_heating_value",
            8,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_scada_pressure",
            8,
        ),
    ]
    assert loads[0].dataframe is not None
    assert loads[0].dataframe["source_zone_id"].to_list() == ["newer", "older"]
    assert loads[1].dataframe is not None
    assert loads[1].dataframe["source_node_id"].to_list() == ["newer", "older"]


def test_cached_heating_value_pressure_tables_reuse_session_cache() -> None:
    calls: list[str] = []
    config = _dashboard_config()
    cache: GasModelSessionCache = {}

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        calls.append(uri.rsplit("/", maxsplit=1)[-1])
        return pl.DataFrame({"source_system": [f"VICGAS-{len(calls)}"]})

    first_loads = cached_load_heating_value_pressure_tables(
        config, cache, reader=reader
    )
    cached_loads = cached_load_heating_value_pressure_tables(
        config, cache, reader=reader
    )
    refreshed_loads = cached_load_heating_value_pressure_tables(
        config,
        cache,
        reader=reader,
        refresh_token=1,
    )

    assert calls == [
        HEATING_VALUE_TABLE_NAME,
        SCADA_PRESSURE_TABLE_NAME,
        HEATING_VALUE_TABLE_NAME,
        SCADA_PRESSURE_TABLE_NAME,
    ]
    assert all(not load.cache_hit for load in first_loads)
    assert all(load.cache_hit for load in cached_loads)
    assert all(not load.cache_hit for load in refreshed_loads)
    assert cached_loads[0].dataframe is not None
    assert cached_loads[0].dataframe["source_system"].to_list() == ["VICGAS-1"]
    assert refreshed_loads[0].dataframe is not None
    assert refreshed_loads[0].dataframe["source_system"].to_list() == ["VICGAS-3"]


def test_heating_value_pressure_summaries_and_source_identifier_rendering() -> None:
    loads = _heating_value_pressure_loads(
        heating_dataframe=pl.DataFrame(
            {
                "gas_date": ["2024-01-02", "2024-01-01"],
                "gas_interval": ["1", None],
                "source_zone_id": ["400", "VIC"],
                "zone_name": ["Dandenong", "Victoria"],
                "heating_value": [39.2, 40.0],
                "initial_heating_value": [38.9, None],
                "heating_value_unit": ["GJ/1000m3", "declared"],
                "source_system": ["VICGAS", "VICGAS"],
                "source_table": [
                    "silver.vicgas.silver_int047_v4_heating_values_1",
                    "silver.vicgas.silver_int139_v4_declared_daily_state_"
                    "heating_value_1",
                ],
                "source_last_updated_timestamp": [
                    "2024-01-02 01:00:00",
                    "2024-01-01 01:00:00",
                ],
                "ingested_timestamp": [
                    datetime(2024, 1, 2, 3),
                    datetime(2024, 1, 1, 3),
                ],
            }
        ),
        pressure_dataframe=pl.DataFrame(
            {
                "measurement_timestamp": [
                    "2024-01-02 02:00:00",
                    "2024-01-02 01:00:00",
                ],
                "pressure_offset_hour": [0, 1],
                "source_node_id": ["MCE-A", "MCE-A"],
                "node_name": ["Node A", "Node A"],
                "pressure_kpa": [521.0, 519.0],
                "source_system": ["VICGAS", "VICGAS"],
                "source_table": [
                    "silver.vicgas.silver_int276_v4_hourly_scada_pressures_at_"
                    "mce_nodes_1",
                    "silver.vicgas.silver_int276_v4_hourly_scada_pressures_at_"
                    "mce_nodes_1",
                ],
                "source_last_updated_timestamp": [
                    "2024-01-02 02:30:00",
                    "2024-01-02 02:30:00",
                ],
                "ingested_timestamp": [
                    datetime(2024, 1, 2, 4),
                    datetime(2024, 1, 2, 4),
                ],
            }
        ),
    )

    kpis = heating_value_pressure_kpi_frame(loads)
    field_summary = heating_value_pressure_field_summary_frame(loads)
    identifiers = heating_value_pressure_identifier_frame(loads)
    source_coverage = heating_value_pressure_source_coverage_frame(loads)
    heating_observations = heating_value_observation_frame(
        loads,
        identifier_filter="Heating value zone 400",
    )
    heating_table_filter_observations = heating_value_observation_frame(
        loads,
        source_table_filter="silver.vicgas.silver_int047_v4_heating_values_1",
    )
    pressure_observations = scada_pressure_observation_frame(
        loads,
        identifier_filter="SCADA node MCE-A",
    )
    pressure_table_filter_observations = scada_pressure_observation_frame(
        loads,
        source_table_filter=(
            "silver.vicgas.silver_int276_v4_hourly_scada_pressures_at_mce_nodes_1"
        ),
    )

    assert heating_value_pressure_source_system_options(loads) == (
        HEATING_VALUE_PRESSURE_SOURCE_SYSTEM_FILTER_ALL,
        "VICGAS",
    )
    assert heating_value_pressure_identifier_options(loads) == (
        HEATING_VALUE_PRESSURE_IDENTIFIER_FILTER_ALL,
        "Heating value zone 400",
        "Heating value zone VIC",
        "SCADA node MCE-A",
    )
    assert kpis.to_dict(as_series=False) == {
        "metric": [
            "Loaded observations",
            "Heating value observations",
            "SCADA pressure observations",
            "Source-qualified identifiers",
            "Source tables",
            "Latest gas date",
            "Latest pressure measurement",
            "Latest ingest",
        ],
        "value": [
            "4",
            "2",
            "2",
            "3",
            "3",
            "2024-01-02",
            "2024-01-02 02:00:00",
            "2024-01-02 04:00:00",
        ],
        "detail": [
            "Bounded preview: 100 rows max",
            "Rows from silver_gas_fact_heating_value",
            "Rows from silver_gas_fact_scada_pressure",
            "Distinct source zone and source node identifiers",
            "Distinct source_table values represented",
            "Maximum gas_date in loaded heating value rows",
            "Maximum measurement_timestamp in loaded pressure rows",
            "Latest ingested_timestamp across loaded rows",
        ],
    }
    assert field_summary.select("field", "available rows").to_dict(as_series=False) == {
        "field": [
            "gas_date",
            "gas_interval",
            "source_zone_id",
            "zone_name",
            "heating_value",
            "initial_heating_value",
            "heating_value_unit",
            "measurement_timestamp",
            "pressure_offset_hour",
            "source_node_id",
            "node_name",
            "pressure_kpa",
        ],
        "available rows": [2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2],
    }
    assert identifiers.select(
        "fact",
        "identifier role",
        "source-qualified identifier",
        "observations",
        "relationship status",
    ).to_dict(as_series=False) == {
        "fact": ["Heating value", "Heating value", "SCADA pressure"],
        "identifier role": ["source_zone_id", "source_zone_id", "source_node_id"],
        "source-qualified identifier": ["400", "VIC", "MCE-A"],
        "observations": [1, 1, 2],
        "relationship status": [
            "Source-qualified identifier only; no conformed dimension key in fact schema",
            "Source-qualified identifier only; no conformed dimension key in fact schema",
            "Source-qualified identifier only; no conformed dimension key in fact schema",
        ],
    }
    assert source_coverage.select(
        "fact",
        "observations",
        "source-qualified identifiers",
        "measure values",
    ).to_dict(as_series=False) == {
        "fact": ["Heating value", "Heating value", "SCADA pressure"],
        "observations": [1, 1, 2],
        "source-qualified identifiers": [1, 1, 1],
        "measure values": [1, 1, 2],
    }
    assert heating_observations.select(
        "gas date",
        "source-qualified zone id",
        "heating value",
        "relationship status",
    ).to_dict(as_series=False) == {
        "gas date": [date(2024, 1, 2)],
        "source-qualified zone id": ["400"],
        "heating value": [39.2],
        "relationship status": [
            "Source-qualified identifier only; no conformed dimension key in fact schema"
        ],
    }
    assert heating_table_filter_observations["source-qualified zone id"].to_list() == [
        "400"
    ]
    assert pressure_observations.select(
        "measurement timestamp",
        "source-qualified node id",
        "pressure offset hour",
        "pressure kpa",
    ).to_dict(as_series=False) == {
        "measurement timestamp": [
            datetime(2024, 1, 2, 2),
            datetime(2024, 1, 2, 1),
        ],
        "source-qualified node id": ["MCE-A", "MCE-A"],
        "pressure offset hour": [0, 1],
        "pressure kpa": [521.0, 519.0],
    }
    assert pressure_table_filter_observations["pressure offset hour"].to_list() == [
        0,
        1,
    ]
    assert heating_value_observation_frame(
        loads,
        source_system_filter="OTHER",
    ).is_empty()
    assert scada_pressure_observation_frame(
        loads,
        source_system_filter="OTHER",
    ).is_empty()


def test_heating_value_pressure_helpers_cover_missing_data_and_empty_states() -> None:
    empty_loads = _heating_value_pressure_loads(
        heating_dataframe=pl.DataFrame(),
        pressure_dataframe=pl.DataFrame(),
        row_limit=6,
    )
    populated_loads = _heating_value_pressure_loads(
        heating_dataframe=pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 2)],
                "source_zone_id": ["400"],
                "heating_value": [39.2],
            }
        ),
        pressure_dataframe=pl.DataFrame(),
    )
    error_loads = [
        GasTableLoad(
            spec=HEATING_VALUE_TABLE_SPEC,
            uri=f"s3://bucket/silver/gas_model/{HEATING_VALUE_TABLE_NAME}",
            dataframe=None,
            error="FileNotFoundError: no parquet files found",
            row_limit=6,
            load_duration_seconds=0.01,
            cache_hit=False,
        ),
        _scada_pressure_load(pl.DataFrame(), row_limit=6),
    ]

    assert heating_value_pressure_kpi_frame(empty_loads).is_empty()
    assert heating_value_pressure_field_summary_frame(empty_loads).is_empty()
    assert heating_value_pressure_identifier_frame(empty_loads).is_empty()
    assert heating_value_pressure_source_coverage_frame(empty_loads).is_empty()
    assert _dataframe_min_value(pl.DataFrame(), "missing") is None
    assert heating_value_observation_frame(empty_loads).is_empty()
    assert scada_pressure_observation_frame(empty_loads).is_empty()
    assert heating_value_pressure_source_table_options(empty_loads) == (
        HEATING_VALUE_PRESSURE_SOURCE_TABLE_FILTER_ALL,
    )
    assert heating_value_pressure_identifier_options(empty_loads) == (
        HEATING_VALUE_PRESSURE_IDENTIFIER_FILTER_ALL,
    )
    assert heating_value_pressure_kpi_frame(populated_loads).row(6, named=True) == {
        "metric": "Latest pressure measurement",
        "value": "unknown",
        "detail": "Maximum measurement_timestamp in loaded pressure rows",
    }
    populated_field_summary = heating_value_pressure_field_summary_frame(
        populated_loads
    )

    empty_markdown = heating_value_pressure_empty_state_markdown(empty_loads)
    error_markdown = heating_value_pressure_empty_state_markdown(error_loads)
    filtered_markdown = heating_value_pressure_empty_state_markdown(populated_loads)
    missing_load_markdown = heating_value_pressure_empty_state_markdown(None)
    empty_context_links = render_heating_value_pressure_context_links(entries=())
    unmounted_entry = DashboardRegistryEntry(
        concept_id=HEATING_VALUE_PRESSURE_CONTEXT_ID,
        title="Unmounted Heating Value And Pressure",
        description="Available entry without a mounted notebook route.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.AVAILABLE,
        notebook_name=None,
        backing_assets=("silver.gas_model.silver_gas_fact_heating_value",),
        generated_gold_paths=(),
        source_chunks=(),
    )
    unmounted_context_links = render_heating_value_pressure_context_links(
        entries=(unmounted_entry,)
    )

    assert (
        populated_field_summary.filter(pl.col("field") == "pressure_kpa").row(
            0, named=True
        )["available rows"]
        == 0
    )
    assert "No heating value or SCADA pressure data is available" in empty_markdown
    assert "silver.gas_model.silver_gas_fact_heating_value" in empty_markdown
    assert "silver.gas_model.silver_gas_fact_scada_pressure" in empty_markdown
    assert "Bounded preview reads are capped at `6` rows per table" in empty_markdown
    assert "source-qualified identifiers" in empty_markdown
    assert "conformed dimension keys" in empty_markdown
    assert "FileNotFoundError: no parquet files found" in error_markdown
    assert "current filters do not match" in filtered_markdown
    assert "did not receive heating value or SCADA pressure" in missing_load_markdown
    assert "No Heating value, SCADA pressure, Gas Quality" in empty_context_links
    assert "Unavailable dashboard" in unmounted_context_links


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


def test_participant_context_metadata_is_available_dashboard() -> None:
    entry = registry_entry_by_concept_id(PARTICIPANT_CONTEXT_ID)
    html = render_dashboard_context_panel(PARTICIPANT_CONTEXT_ID)
    context_links = render_participant_context_links()

    assert entry is not None
    assert entry.status is DashboardStatus.AVAILABLE
    assert entry.notebook_name == "participant_explainer"
    assert entry.notebook_route == "/marimo/participant_explainer/"
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/participant.md"
        in entry.generated_gold_paths
    )
    assert entry.source_chunk_ids == (
        "chunk-gbb-guide-participants-report",
        "chunk-gbb-procedures-registration",
        "chunk-sttm-procedures-settlement-terms",
    )
    assert "silver.gas_model.silver_gas_dim_participant" in entry.backing_assets
    assert (
        "silver.gas_model.silver_gas_participant_market_membership"
        in entry.backing_assets
    )
    assert "silver.gas_model.silver_gas_fact_bid_stack" in entry.backing_assets
    assert (
        "silver.gas_model.silver_gas_fact_settlement_activity" in entry.backing_assets
    )
    assert "Participant Context" in html
    assert "chunk-gbb-guide-participants-report" in html
    assert 'data-status="available"' in html
    assert 'href="/marimo/participant_explainer/"' in context_links
    assert 'href="/marimo/gas_bid_offer_stack/"' in context_links
    assert 'href="/marimo/gas_settlement_activity/"' in context_links
    assert 'href="/marimo/facility_explainer/"' in context_links


def test_participant_table_specs_and_loader_use_bounded_samples() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "6",
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

    specs = participant_table_specs()
    loads = load_participant_context_tables(config, reader=reader)

    assert specs == PARTICIPANT_TABLE_SPECS
    assert tuple(spec.table_name for spec in specs) == (
        PARTICIPANT_DIM_TABLE_NAME,
        PARTICIPANT_MARKET_MEMBERSHIP_TABLE_NAME,
        FACILITY_DIM_TABLE_NAME,
        BID_STACK_TABLE_NAME,
        SETTLEMENT_ACTIVITY_TABLE_NAME,
    )
    assert len(loads) == len(specs)
    assert {row_limit for _, row_limit in captured} == {6}
    assert captured[0][0] == (
        "s3://prod-energy-market-aemo/silver/gas_model/silver_gas_dim_participant"
    )

    cache: GasModelSessionCache = {}
    cached_calls = 0

    def cached_reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        nonlocal cached_calls
        assert uri.endswith(f"/{PARTICIPANT_DIM_TABLE_NAME}")
        assert storage_options == config.storage_options()
        assert row_limit == 6
        cached_calls += 1
        return pl.DataFrame({"source_systems": [["GBB"]]})

    first_cached = cached_load_participant_context_tables(
        config,
        cache,
        specs=(PARTICIPANT_TABLE_SPECS[0],),
        reader=cached_reader,
        refresh_token="same",
    )
    second_cached = cached_load_participant_context_tables(
        config,
        cache,
        specs=(PARTICIPANT_TABLE_SPECS[0],),
        reader=cached_reader,
        refresh_token="same",
    )
    refreshed = cached_load_participant_context_tables(
        config,
        cache,
        specs=(PARTICIPANT_TABLE_SPECS[0],),
        reader=cached_reader,
        refresh_token="changed",
    )

    assert cached_calls == 2
    assert not first_cached[0].cache_hit
    assert second_cached[0].cache_hit
    assert not refreshed[0].cache_hit


def test_participant_metadata_helpers_extract_dimension_memberships_and_facts() -> None:
    participant_load = _participant_load(
        PARTICIPANT_TABLE_SPECS[0],
        pl.DataFrame(
            {
                "surrogate_key": ["participant-key-1", "participant-key-2"],
                "participant_identity_source": ["gbb_company_id", "sttm_code"],
                "participant_identity_value": ["P1", "BETA"],
                "canonical_participant_name": ["Alpha Energy", "Beta Gas"],
                "registered_name": ["Alpha Energy Pty Ltd", "Beta Gas Ltd"],
                "participant_type": ["trader", "retailer"],
                "participant_status": ["active", "active"],
                "source_systems": [["GBB", "STTM"], ["STTM"]],
                "source_tables": [
                    [
                        "silver.gbb.silver_gasbb_participants_list",
                        "silver.sttm.silver_int670_v1_registered_participants_rpt_1",
                    ],
                    ["silver.sttm.silver_int670_v1_registered_participants_rpt_1"],
                ],
                "source_company_ids": [["P1", "ALPHA"], ["BETA"]],
                "ingested_timestamp": [
                    datetime(2024, 1, 1, 8),
                    datetime(2024, 1, 1, 9),
                ],
            }
        ),
    )
    membership_load = _participant_load(
        PARTICIPANT_TABLE_SPECS[1],
        pl.DataFrame(
            {
                "participant_key": [
                    "participant-key-1",
                    "participant-key-1",
                    "participant-key-2",
                ],
                "source_system": ["GBB", "STTM", "STTM"],
                "source_tables": [
                    ["silver.gbb.silver_gasbb_participants_list"],
                    ["silver.sttm.silver_int670_v1_registered_participants_rpt_1"],
                    ["silver.sttm.silver_int670_v1_registered_participants_rpt_1"],
                ],
                "market_code": ["BB", "STTM", "STTM"],
                "source_company_id": ["P1", "ALPHA", "BETA"],
                "source_company_code": ["P1", "ALP", "BET"],
                "source_hub_id": [None, "SYD", "ADL"],
                "source_hub_name": [None, "Sydney", "Adelaide"],
                "registration_type": ["BB Participant", "Trader", "Retailer"],
                "registered_capacity": [None, "100", "50"],
                "membership_status": ["active", "active", "active"],
                "participant_identity_source": [
                    "gbb_company_id",
                    "sttm_code",
                    "sttm_code",
                ],
                "participant_identity_value": ["P1", "ALPHA", "BETA"],
                "ingested_timestamp": [
                    datetime(2024, 1, 2, 8),
                    datetime(2024, 1, 2, 9),
                    datetime(2024, 1, 2, 10),
                ],
            }
        ),
    )
    facility_load = _participant_load(
        PARTICIPANT_TABLE_SPECS[2],
        pl.DataFrame(
            {
                "participant_key": ["participant-key-1", "unknown-key", None],
                "source_system": ["GBB", "GBB", "STTM"],
                "source_facility_id": ["FAC1", "FAC2", "FAC3"],
                "facility_name": ["Facility One", "Facility Two", "Facility Three"],
            }
        ),
    )
    bid_stack_load = _participant_load(
        PARTICIPANT_TABLE_SPECS[3],
        pl.DataFrame(
            {
                "participant_id": ["P1", "UNKNOWN"],
                "participant_name": ["Alpha Energy", "Unknown Trading"],
                "source_system": ["STTM", "STTM"],
            }
        ),
    )
    settlement_load = _participant_load(
        PARTICIPANT_TABLE_SPECS[4],
        pl.DataFrame(
            {
                "participant_name": [
                    "Alpha Energy",
                    "Beta Gas Ltd",
                    "Unknown Trading",
                ],
                "amount_gst_ex": [100.0, 50.0, 25.0],
                "source_system": ["STTM", "STTM", "STTM"],
            }
        ),
    )
    loads = (
        participant_load,
        membership_load,
        facility_load,
        bid_stack_load,
        settlement_load,
    )

    coverage = participant_dimension_coverage_frame(participant_load)
    memberships = participant_membership_coverage_frame(membership_load)
    relationships = participant_related_market_fact_frame(loads)
    participant_preview = participant_dimension_preview_frame(participant_load)
    membership_preview = participant_membership_preview_frame(membership_load)
    coverage_values = {row["metric"]: row["value"] for row in coverage.to_dicts()}
    membership_rows = {
        (row["source system"], row["market code"], row["registration type"]): row
        for row in memberships.to_dicts()
    }
    relationship_rows = {
        row["related surface"]: row for row in relationships.to_dicts()
    }

    assert coverage_values == {
        "Participant dimension rows": "2",
        "Identity sources": "2",
        "Canonical participants": "2",
        "Registered names": "2",
        "Participant types": "2",
        "Participant statuses": "1",
        "Source systems": "2",
        "Source tables": "2",
        "Source company ids": "3",
    }
    assert membership_rows[("GBB", "BB", "BB Participant")]["rows"] == 1
    assert membership_rows[("STTM", "STTM", "Trader")]["participant keys"] == 1
    assert membership_rows[("STTM", "STTM", "Retailer")]["hub ids"] == 1
    assert relationship_rows["Market membership"]["matched participants"] == 2
    assert relationship_rows["Facility"]["available rows"] == 2
    assert relationship_rows["Facility"]["matched participants"] == 1
    assert relationship_rows["Bid / Offer"]["participant references"] == 4
    assert relationship_rows["Bid / Offer"]["matched participants"] == 2
    assert relationship_rows["Settlement"]["participant references"] == 3
    assert relationship_rows["Settlement"]["matched participants"] == 2
    assert participant_preview.select(
        "identity source",
        "identity value",
        "participant",
        "registered name",
        "participant type",
        "participant status",
        "source systems",
        "source tables",
        "source company ids",
    ).to_dict(as_series=False) == {
        "identity source": ["gbb_company_id", "sttm_code"],
        "identity value": ["P1", "BETA"],
        "participant": ["Alpha Energy", "Beta Gas"],
        "registered name": ["Alpha Energy Pty Ltd", "Beta Gas Ltd"],
        "participant type": ["trader", "retailer"],
        "participant status": ["active", "active"],
        "source systems": ["GBB, STTM", "STTM"],
        "source tables": [
            (
                "silver.gbb.silver_gasbb_participants_list, "
                "silver.sttm.silver_int670_v1_registered_participants_rpt_1"
            ),
            "silver.sttm.silver_int670_v1_registered_participants_rpt_1",
        ],
        "source company ids": ["P1, ALPHA", "BETA"],
    }
    assert membership_preview.select(
        "source system",
        "market code",
        "participant key",
        "company id",
        "company code",
        "hub",
        "registration type",
        "membership status",
    ).to_dict(as_series=False) == {
        "source system": ["GBB", "STTM", "STTM"],
        "market code": ["BB", "STTM", "STTM"],
        "participant key": [
            "participant-key-1",
            "participant-key-1",
            "participant-key-2",
        ],
        "company id": ["P1", "ALPHA", "BETA"],
        "company code": ["P1", "ALP", "BET"],
        "hub": [None, "Sydney", "Adelaide"],
        "registration type": ["BB Participant", "Trader", "Retailer"],
        "membership status": ["active", "active", "active"],
    }


def test_participant_helpers_cover_empty_state_behavior() -> None:
    unavailable_load = _participant_load(
        PARTICIPANT_TABLE_SPECS[0],
        None,
        error="FileNotFoundError: no parquet files found",
        row_limit=4,
    )
    empty_membership_load = _participant_load(
        PARTICIPANT_TABLE_SPECS[1],
        pl.DataFrame(),
        row_limit=4,
    )
    loads = (unavailable_load, empty_membership_load)
    partial_membership_load = _participant_load(
        PARTICIPANT_TABLE_SPECS[1],
        pl.DataFrame(
            {
                "participant_key": ["orphan-participant-key"],
                "source_system": [None],
                "market_code": [None],
                "registration_type": [None],
                "membership_status": [None],
            }
        ),
        row_limit=4,
    )
    planned_entry = DashboardRegistryEntry(
        concept_id=PARTICIPANT_CONTEXT_ID,
        title="Participant Context",
        description="Planned Participant context entry.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.PLANNED,
        notebook_name=None,
        backing_assets=(),
        generated_gold_paths=(),
        source_chunks=(),
    )

    assert participant_dimension_coverage_frame(unavailable_load).is_empty()
    assert participant_membership_coverage_frame(empty_membership_load).is_empty()
    assert participant_dimension_preview_frame(unavailable_load).is_empty()
    assert participant_membership_preview_frame(empty_membership_load).is_empty()
    assert participant_related_market_fact_frame(loads).is_empty()
    partial_membership = participant_membership_coverage_frame(partial_membership_load)
    partial_relationships = participant_related_market_fact_frame(
        (partial_membership_load,)
    )

    markdown = participant_context_empty_state_markdown(loads)
    empty_markdown = participant_context_empty_state_markdown(())
    empty_context_links = render_participant_context_links(entries=())
    planned_context_links = render_participant_context_links(entries=(planned_entry,))

    assert partial_membership.row(0, named=True) == {
        "source system": None,
        "market code": None,
        "registration type": None,
        "membership status": None,
        "rows": 1,
        "participant keys": 1,
        "source company ids": 0,
        "source company codes": 0,
        "hub ids": 0,
        "source tables": 0,
        "latest ingest": None,
    }
    assert partial_relationships.row(0, named=True)["matched participants"] == 0
    assert "No Participant metadata, membership, or related fact rows" in markdown
    assert "`1` reads were unavailable and `1` reads returned no rows" in markdown
    assert "Bounded preview reads are capped at `4` rows per table" in markdown
    assert "No Participant context tables were requested" in empty_markdown
    assert (
        "No Participant, bid, settlement, facility, or table explorer entries "
        "are registered."
    ) in empty_context_links
    assert "<span>Participant Context</span>" in planned_context_links


def test_facility_context_metadata_is_available_dashboard() -> None:
    entry = registry_entry_by_concept_id(FACILITY_CONTEXT_ID)
    html = render_dashboard_context_panel(FACILITY_CONTEXT_ID)
    context_links = render_facility_context_links()

    assert entry is not None
    assert entry.status is DashboardStatus.AVAILABLE
    assert entry.notebook_name == "facility_explainer"
    assert entry.notebook_route == "/marimo/facility_explainer/"
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/facility.md"
        in entry.generated_gold_paths
    )
    assert entry.source_chunk_ids == (
        "chunk-gbb-guide-nodes-facilities",
        "chunk-gbb-procedures-facility-nameplate",
    )
    assert "silver.gas_model.silver_gas_dim_facility" in entry.backing_assets
    assert "Facility Context" in html
    assert "chunk-gbb-guide-nodes-facilities" in html
    assert 'data-status="available"' in html
    assert 'href="/marimo/facility_explainer/"' in context_links
    assert "GBB Interactive Map" in context_links
    assert "Capacity Context" in context_links


def test_facility_table_specs_and_loader_use_bounded_samples() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "5",
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

    specs = facility_table_specs()
    loads = load_facility_context_tables(config, reader=reader)

    assert specs == FACILITY_TABLE_SPECS
    assert tuple(spec.table_name for spec in specs) == (
        FACILITY_DIM_TABLE_NAME,
        FACILITY_FLOW_STORAGE_TABLE_NAME,
        FACILITY_CAPACITY_OUTLOOK_TABLE_NAME,
    )
    assert len(loads) == len(specs)
    assert {row_limit for _, row_limit in captured} == {5}
    assert captured[0][0] == (
        "s3://prod-energy-market-aemo/silver/gas_model/silver_gas_dim_facility"
    )

    cache: GasModelSessionCache = {}
    cached_calls = 0

    def cached_reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        nonlocal cached_calls
        assert uri.endswith(f"/{FACILITY_DIM_TABLE_NAME}")
        assert storage_options == config.storage_options()
        assert row_limit == 5
        cached_calls += 1
        return pl.DataFrame({"source_system": ["GBB"]})

    first_cached = cached_load_facility_context_tables(
        config,
        cache,
        specs=(FACILITY_TABLE_SPECS[0],),
        reader=cached_reader,
        refresh_token="same",
    )
    second_cached = cached_load_facility_context_tables(
        config,
        cache,
        specs=(FACILITY_TABLE_SPECS[0],),
        reader=cached_reader,
        refresh_token="same",
    )
    refreshed = cached_load_facility_context_tables(
        config,
        cache,
        specs=(FACILITY_TABLE_SPECS[0],),
        reader=cached_reader,
        refresh_token="changed",
    )

    assert cached_calls == 2
    assert not first_cached[0].cache_hit
    assert second_cached[0].cache_hit
    assert not refreshed[0].cache_hit


def test_facility_metadata_helpers_extract_dimension_and_relationships() -> None:
    facility_load = _facility_load(
        FACILITY_TABLE_SPECS[0],
        pl.DataFrame(
            {
                "surrogate_key": ["facility-key-1", "facility-key-2"],
                "participant_key": ["participant-key-1", None],
                "zone_key": ["zone-key-1", "zone-key-2"],
                "source_system": ["GBB", "STTM"],
                "source_tables": [
                    ["silver.gbb.silver_gasbb_facilities"],
                    ["silver.sttm.silver_int671_v1_hub_facility_definition_rpt_1"],
                ],
                "source_facility_id": ["10", "20"],
                "facility_name": [
                    "Carpentaria Gas Pipeline",
                    "Sydney Hub Facility",
                ],
                "facility_short_name": ["CGP", "SYD"],
                "facility_type": ["PIPE", "HUB"],
                "operator_name": ["APA Group", None],
                "capacity_effective_from_date": [date(2024, 1, 1), None],
                "capacity_effective_to_date": [None, None],
                "default_capacity": [45.0, None],
                "maximum_capacity": [90.0, None],
                "ingested_timestamp": [
                    datetime(2024, 1, 1, 8),
                    datetime(2024, 1, 1, 9),
                ],
            }
        ),
    )
    flow_load = _facility_load(
        FACILITY_TABLE_SPECS[1],
        pl.DataFrame(
            {
                "facility_key": [
                    "facility-key-1",
                    "facility-key-1",
                    None,
                    "facility-key-2",
                ],
                "source_system": ["GBB", "GBB", "GBB", "GBB"],
                "gas_date": [
                    date(2024, 1, 2),
                    date(2024, 1, 2),
                    date(2024, 1, 2),
                    date(2024, 1, 2),
                ],
                "source_facility_id": ["10", "10", "99", None],
                "demand_tj": [12.0, None, 3.0, 4.0],
                "supply_tj": [None, None, None, None],
                "transfer_in_tj": [None, None, None, None],
                "transfer_out_tj": [None, None, None, None],
                "held_in_storage_tj": [None, 8.0, None, None],
            }
        ),
    )
    capacity_load = _facility_load(
        FACILITY_TABLE_SPECS[2],
        pl.DataFrame(
            {
                "source_system": ["GBB", "GBB", "GBB"],
                "source_table": [
                    "silver.gbb.capacity",
                    "silver.gbb.capacity",
                    "silver.gbb.capacity",
                ],
                "source_facility_id": ["10", "20", "99"],
                "facility_name": [
                    "Carpentaria Gas Pipeline",
                    "Sydney Hub Facility",
                    "Unmatched Facility",
                ],
                "capacity_type": ["nameplate", "nameplate", "nameplate"],
                "flow_direction": ["north", "injection", "south"],
                "capacity_quantity_tj": [14.0, None, 20.0],
            }
        ),
    )

    coverage = facility_dimension_coverage_frame(facility_load)
    relationships = facility_relationship_frame(
        (facility_load, flow_load, capacity_load)
    )
    preview = facility_dimension_preview_frame(facility_load)
    coverage_values = {row["metric"]: row["value"] for row in coverage.to_dicts()}
    relationship_rows = {row["relationship"]: row for row in relationships.to_dicts()}

    assert coverage_values == {
        "Facility dimension rows": "2",
        "Source systems": "2",
        "Source tables": "2",
        "Facility types": "2",
        "Operators": "1",
        "Participant links": "1",
        "Zone links": "2",
        "Capacity metadata rows": "1",
    }
    assert relationship_rows["Participant"]["available rows"] == 1
    assert relationship_rows["Zone"]["available rows"] == 2
    assert relationship_rows["Flow"]["available rows"] == 3
    assert relationship_rows["Flow"]["matched facilities"] == 2
    assert relationship_rows["Storage"]["available rows"] == 1
    assert relationship_rows["Storage"]["matched facilities"] == 1
    assert relationship_rows["Capacity"]["available rows"] == 2
    assert relationship_rows["Capacity"]["matched facilities"] == 1
    assert (
        "1 facility dimension rows also carry standing capacity metadata"
        in relationship_rows["Capacity"]["detail"]
    )
    assert preview.select(
        "source system",
        "source facility id",
        "facility",
        "facility type",
        "operator",
        "participant key",
        "zone key",
        "default capacity",
        "maximum capacity",
        "source tables",
    ).to_dict(as_series=False) == {
        "source system": ["GBB", "STTM"],
        "source facility id": ["10", "20"],
        "facility": ["Carpentaria Gas Pipeline", "Sydney Hub Facility"],
        "facility type": ["PIPE", "HUB"],
        "operator": ["APA Group", None],
        "participant key": ["participant-key-1", None],
        "zone key": ["zone-key-1", "zone-key-2"],
        "default capacity": [45.0, None],
        "maximum capacity": [90.0, None],
        "source tables": [
            "silver.gbb.silver_gasbb_facilities",
            "silver.sttm.silver_int671_v1_hub_facility_definition_rpt_1",
        ],
    }


def test_facility_helpers_cover_empty_state_behavior() -> None:
    unavailable_load = _facility_load(
        FACILITY_TABLE_SPECS[0],
        None,
        error="FileNotFoundError: no parquet files found",
        row_limit=4,
    )
    empty_flow_load = _facility_load(
        FACILITY_TABLE_SPECS[1],
        pl.DataFrame(),
        row_limit=4,
    )
    empty_capacity_load = _facility_load(
        FACILITY_TABLE_SPECS[2],
        pl.DataFrame(),
        row_limit=4,
    )
    loads = (unavailable_load, empty_flow_load, empty_capacity_load)

    assert facility_dimension_coverage_frame(unavailable_load).is_empty()
    assert facility_relationship_frame(loads).is_empty()
    assert facility_dimension_preview_frame(unavailable_load).is_empty()

    markdown = facility_context_empty_state_markdown(loads)
    empty_markdown = facility_context_empty_state_markdown(())
    empty_context_links = render_facility_context_links(entries=())

    assert "No Facility metadata or relationship rows are available" in markdown
    assert "`1` reads were unavailable and `2` reads returned no rows" in markdown
    assert "Bounded preview reads are capped at `4` rows per table" in markdown
    assert "No Facility context tables were requested" in empty_markdown
    assert (
        "No Facility, flow, capacity, participant, zone, or table explorer entries "
        "are registered."
    ) in empty_context_links


def test_connection_point_context_metadata_is_available_dashboard() -> None:
    entry = registry_entry_by_concept_id(CONNECTION_POINT_CONTEXT_ID)
    html = render_dashboard_context_panel(CONNECTION_POINT_CONTEXT_ID)
    context_links = render_connection_point_context_links()

    assert entry is not None
    assert entry.status is DashboardStatus.AVAILABLE
    assert entry.notebook_name == "connection_point_explainer"
    assert entry.notebook_route == "/marimo/connection_point_explainer/"
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/connection-point.md"
    ) in entry.generated_gold_paths
    assert entry.source_chunk_ids == (
        "chunk-gbb-guide-connection-point-identifiers",
        "chunk-gbb-guide-flow-report",
    )
    assert "silver.gas_model.silver_gas_dim_connection_point" in entry.backing_assets
    assert "silver.gas_model.silver_gas_dim_facility" in entry.backing_assets
    assert "silver.gas_model.silver_gas_dim_location" in entry.backing_assets
    assert "silver.gas_model.silver_gas_dim_zone" in entry.backing_assets
    assert "silver.gas_model.silver_gas_fact_connection_point_flow" in (
        entry.backing_assets
    )
    assert "Connection Point Context" in html
    assert "chunk-gbb-guide-connection-point-identifiers" in html
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/connection-point.md"
    ) in html
    assert 'data-status="available"' in html
    assert 'href="/marimo/connection_point_explainer/"' in context_links
    assert "Facility Context" in context_links
    assert "Hub / Zone Context" in context_links
    assert "Capacity Context" in context_links


def test_connection_point_table_specs_and_loader_use_bounded_samples() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "9",
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

    specs = connection_point_table_specs()
    loads = load_connection_point_context_tables(config, reader=reader)

    assert specs == CONNECTION_POINT_TABLE_SPECS
    assert tuple(spec.table_name for spec in specs) == (
        CONNECTION_POINT_DIM_TABLE_NAME,
        FACILITY_DIM_TABLE_NAME,
        LOCATION_DIM_TABLE_NAME,
        HUB_ZONE_DIM_TABLE_NAME,
        CONNECTION_POINT_FLOW_TABLE_NAME,
        FACILITY_CAPACITY_OUTLOOK_TABLE_NAME,
    )
    assert len(loads) == 6
    assert captured == [
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_dim_connection_point",
            9,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/silver_gas_dim_facility",
            9,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/silver_gas_dim_location",
            9,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/silver_gas_dim_zone",
            9,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_connection_point_flow",
            9,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_capacity_outlook",
            9,
        ),
    ]

    cache: GasModelSessionCache = {}
    cached_calls = 0

    def cached_reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        nonlocal cached_calls
        assert storage_options == config.storage_options()
        assert row_limit == 9
        cached_calls += 1
        return pl.DataFrame({"source_system": ["GBB"]})

    first_cached = cached_load_connection_point_context_tables(
        config,
        cache,
        specs=(CONNECTION_POINT_TABLE_SPECS[0],),
        reader=cached_reader,
        refresh_token="same",
    )
    second_cached = cached_load_connection_point_context_tables(
        config,
        cache,
        specs=(CONNECTION_POINT_TABLE_SPECS[0],),
        reader=cached_reader,
        refresh_token="same",
    )
    refreshed = cached_load_connection_point_context_tables(
        config,
        cache,
        specs=(CONNECTION_POINT_TABLE_SPECS[0],),
        reader=cached_reader,
        refresh_token="changed",
    )

    assert cached_calls == 2
    assert not first_cached[0].cache_hit
    assert second_cached[0].cache_hit
    assert not refreshed[0].cache_hit


def test_connection_point_metadata_helpers_extract_relationships() -> None:
    connection_point_load = _facility_load(
        CONNECTION_POINT_TABLE_SPECS[0],
        pl.DataFrame(
            {
                "surrogate_key": ["cp-key-1", "cp-key-2", "cp-key-3"],
                "facility_key": ["facility-key-1", "facility-key-2", None],
                "location_key": ["location-key-1", None, None],
                "zone_key": ["zone-key-1", "zone-key-2", None],
                "source_system": ["GBB", "GBB", "STTM"],
                "source_tables": [
                    ["silver.gbb.silver_gasbb_nodes_connection_points"],
                    ["silver.gbb.silver_gasbb_nodes_connection_points"],
                    ["silver.sttm.silver_int691_v1_sttm_ctp_register_rpt_1"],
                ],
                "source_hub_id": [None, None, "SYD"],
                "source_hub_name": [None, None, "Sydney Hub"],
                "source_facility_id": ["10", "10", "20"],
                "source_connection_point_id": ["1001", "1002", "CTP1"],
                "source_location_id": ["L1", "L2", None],
                "connection_point_name": [
                    "Receipt Point",
                    "Delivery Point",
                    "Sydney CTP",
                ],
                "flow_direction": ["RECEIPT", "DELIVERY", "not_applicable"],
                "facility_name": [
                    "Carpentaria Gas Pipeline",
                    "Carpentaria Gas Pipeline",
                    "Sydney Hub Facility",
                ],
                "location_name": ["Longford", "Wallumbilla", None],
                "state": ["Queensland", "Queensland", None],
                "exempt": [False, True, None],
                "ingested_timestamp": [
                    datetime(2024, 1, 1, 8),
                    datetime(2024, 1, 1, 9),
                    datetime(2024, 1, 1, 10),
                ],
            }
        ),
    )
    facility_load = _facility_load(
        CONNECTION_POINT_TABLE_SPECS[1],
        pl.DataFrame(
            {
                "surrogate_key": ["facility-key-1", "facility-key-2"],
                "source_system": ["GBB", "STTM"],
                "source_tables": [
                    ["silver.gbb.silver_gasbb_facilities"],
                    ["silver.sttm.silver_int671_v1_hub_facility_definition_rpt_1"],
                ],
                "source_facility_id": ["10", "20"],
                "facility_name": [
                    "Carpentaria Gas Pipeline",
                    "Sydney Hub Facility",
                ],
                "ingested_timestamp": [
                    datetime(2024, 1, 1, 8),
                    datetime(2024, 1, 1, 9),
                ],
            }
        ),
    )
    location_load = _facility_load(
        CONNECTION_POINT_TABLE_SPECS[2],
        pl.DataFrame(
            {
                "surrogate_key": ["location-key-1"],
                "source_system": ["GBB"],
                "source_tables": [["silver.gbb.silver_gasbb_locations_list"]],
                "source_location_id": ["L1"],
                "location_name": ["Longford"],
                "state": ["Victoria"],
            }
        ),
    )
    zone_load = _facility_load(
        CONNECTION_POINT_TABLE_SPECS[3],
        pl.DataFrame(
            {
                "surrogate_key": ["zone-key-1", "zone-key-2"],
                "source_system": ["GBB", "STTM"],
                "source_tables": [
                    [
                        "silver.gbb.silver_gasbb_demand_zones_and_pipeline_connectionpoint_mapping"
                    ],
                    ["silver.sttm.silver_int671_v1_hub_facility_definition_rpt_1"],
                ],
                "zone_type": ["demand_zone", "sttm_hub"],
                "source_zone_id": ["DZ1", "SYD"],
                "zone_name": ["Demand Zone 1", "Sydney Hub"],
            }
        ),
    )
    flow_load = _facility_load(
        CONNECTION_POINT_TABLE_SPECS[4],
        pl.DataFrame(
            {
                "connection_point_key": ["cp-key-1", None, None],
                "source_system": ["GBB", "GBB", "GBB"],
                "gas_date": [
                    date(2024, 1, 2),
                    date(2024, 1, 2),
                    date(2024, 1, 2),
                ],
                "source_facility_id": ["10", "10", "99"],
                "source_connection_point_id": ["1001", "1002", "9999"],
                "flow_direction": ["RECEIPT", "DELIVERY", "RECEIPT"],
                "actual_quantity_tj": [5.0, 7.0, 3.0],
            }
        ),
    )
    capacity_load = _facility_load(
        CONNECTION_POINT_TABLE_SPECS[5],
        pl.DataFrame(
            {
                "source_system": ["GBB", "GBB", "STTM", "GBB"],
                "source_table": [
                    "silver.gbb.capacity",
                    "silver.gbb.capacity",
                    "silver.sttm.capacity",
                    "silver.gbb.capacity",
                ],
                "source_facility_id": ["10", "10", "20", "99"],
                "facility_name": [
                    "Carpentaria Gas Pipeline",
                    "Carpentaria Gas Pipeline",
                    "Sydney Hub Facility",
                    "Unmatched Facility",
                ],
                "capacity_type": ["nameplate", "nameplate", "nameplate", "nameplate"],
                "flow_direction": [
                    "RECEIPT",
                    "DELIVERY",
                    "not_applicable",
                    "RECEIPT",
                ],
                "capacity_quantity_tj": [100.0, None, 90.0, 80.0],
            }
        ),
    )

    loads = (
        connection_point_load,
        facility_load,
        location_load,
        zone_load,
        flow_load,
        capacity_load,
    )
    coverage = connection_point_dimension_coverage_frame(connection_point_load)
    sources = connection_point_source_system_frame(connection_point_load)
    relationships = connection_point_relationship_frame(loads)
    preview = connection_point_dimension_preview_frame(connection_point_load)
    coverage_values = {row["metric"]: row["value"] for row in coverage.to_dicts()}
    source_rows = {row["source system"]: row for row in sources.to_dicts()}
    relationship_rows = {row["relationship"]: row for row in relationships.to_dicts()}

    assert coverage_values == {
        "Connection point dimension rows": "3",
        "Source systems": "2",
        "Source tables": "2",
        "Connection point IDs": "3",
        "Facility links": "2",
        "Location links": "1",
        "Zone links": "2",
        "Flow directions": "3",
        "Data exemption rows": "1",
    }
    assert source_rows["GBB"]["rows"] == 2
    assert source_rows["GBB"]["connection points"] == 2
    assert source_rows["GBB"]["facilities"] == 1
    assert source_rows["GBB"]["locations"] == 2
    assert source_rows["STTM"]["flow directions"] == 1
    assert relationship_rows["Facility"]["available rows"] == 2
    assert relationship_rows["Facility"]["matched connection points"] == 2
    assert relationship_rows["Location"]["available rows"] == 1
    assert relationship_rows["Location"]["matched connection points"] == 1
    assert relationship_rows["Zone"]["available rows"] == 2
    assert relationship_rows["Zone"]["matched connection points"] == 2
    assert relationship_rows["Flow direction"]["available rows"] == 3
    assert relationship_rows["Actual flow"]["available rows"] == 3
    assert relationship_rows["Actual flow"]["matched connection points"] == 2
    assert relationship_rows["Capacity"]["available rows"] == 3
    assert relationship_rows["Capacity"]["matched connection points"] == 2
    assert (
        "do not carry a direct connection_point_key"
        in relationship_rows["Capacity"]["detail"]
    )
    assert preview.select(
        "source-qualified identifier",
        "source system",
        "source facility id",
        "source connection point id",
        "connection point",
        "flow direction",
        "facility",
        "location",
        "hub",
        "source tables",
    ).to_dict(as_series=False) == {
        "source-qualified identifier": [
            "GBB:10:1001:RECEIPT",
            "GBB:10:1002:DELIVERY",
            "STTM:20:CTP1:not_applicable",
        ],
        "source system": ["GBB", "GBB", "STTM"],
        "source facility id": ["10", "10", "20"],
        "source connection point id": ["1001", "1002", "CTP1"],
        "connection point": ["Receipt Point", "Delivery Point", "Sydney CTP"],
        "flow direction": ["RECEIPT", "DELIVERY", "not_applicable"],
        "facility": [
            "Carpentaria Gas Pipeline",
            "Carpentaria Gas Pipeline",
            "Sydney Hub Facility",
        ],
        "location": ["Longford", "Wallumbilla", None],
        "hub": [None, None, "Sydney Hub (SYD)"],
        "source tables": [
            "silver.gbb.silver_gasbb_nodes_connection_points",
            "silver.gbb.silver_gasbb_nodes_connection_points",
            "silver.sttm.silver_int691_v1_sttm_ctp_register_rpt_1",
        ],
    }


def test_connection_point_helpers_handle_partial_identifiers_and_hubs() -> None:
    connection_point_load = _facility_load(
        CONNECTION_POINT_TABLE_SPECS[0],
        pl.DataFrame(
            {
                "surrogate_key": ["cp-fallback", "cp-name", "cp-id"],
                "facility_key": ["facility-key-1", None, None],
                "source_system": [None, "GBB", "GBB"],
                "source_facility_id": [None, "10", "20"],
                "source_connection_point_id": [None, "1001", "1002"],
                "flow_direction": [None, "RECEIPT", "DELIVERY"],
                "source_hub_name": [None, "Sydney Hub", None],
                "source_hub_id": [None, None, "BRI"],
                "source_tables": [[], [], []],
                "ingested_timestamp": [None, None, None],
            }
        ),
    )
    facility_load = _facility_load(
        CONNECTION_POINT_TABLE_SPECS[1],
        pl.DataFrame(
            {
                "surrogate_key": ["facility-key-1"],
                "source_facility_id": ["10"],
            }
        ),
    )
    flow_only_load = _facility_load(
        CONNECTION_POINT_TABLE_SPECS[4],
        pl.DataFrame(
            {
                "source_system": ["GBB"],
                "source_facility_id": ["99"],
                "source_connection_point_id": ["9999"],
                "flow_direction": ["RECEIPT"],
                "actual_quantity_tj": [1.0],
            }
        ),
    )

    relationships = connection_point_relationship_frame(
        (connection_point_load, facility_load)
    )
    flow_only_relationships = connection_point_relationship_frame((flow_only_load,))
    preview = connection_point_dimension_preview_frame(connection_point_load)
    relationship_rows = {row["relationship"]: row for row in relationships.to_dicts()}
    flow_only_rows = {
        row["relationship"]: row for row in flow_only_relationships.to_dicts()
    }

    assert relationship_rows["Facility"]["matched connection points"] == 1
    assert flow_only_rows["Actual flow"]["available rows"] == 1
    assert flow_only_rows["Actual flow"]["matched connection points"] == 0
    assert preview.select("source-qualified identifier", "hub").to_dict(
        as_series=False
    ) == {
        "source-qualified identifier": [
            "GBB:10:1001:RECEIPT",
            "GBB:20:1002:DELIVERY",
            "",
        ],
        "hub": ["Sydney Hub", "BRI", None],
    }


def test_connection_point_helpers_cover_empty_state_behavior() -> None:
    unavailable_load = _facility_load(
        CONNECTION_POINT_TABLE_SPECS[0],
        None,
        error="FileNotFoundError: no parquet files found",
        row_limit=5,
    )
    loads = (
        unavailable_load,
        *(
            _facility_load(spec, pl.DataFrame(), row_limit=5)
            for spec in CONNECTION_POINT_TABLE_SPECS[1:]
        ),
    )

    assert connection_point_dimension_coverage_frame(unavailable_load).is_empty()
    assert connection_point_source_system_frame(unavailable_load).is_empty()
    assert connection_point_relationship_frame(loads).is_empty()
    assert connection_point_dimension_preview_frame(unavailable_load).is_empty()

    markdown = connection_point_context_empty_state_markdown(loads)
    empty_markdown = connection_point_context_empty_state_markdown(())
    empty_context_links = render_connection_point_context_links(entries=())

    assert "No Connection Point metadata or relationship rows are available" in markdown
    assert "`1` reads were unavailable and `5` reads returned no rows" in markdown
    assert "Bounded preview reads are capped at `5` rows per table" in markdown
    assert "No Connection Point context tables were requested" in empty_markdown
    assert (
        "No Connection Point, Facility, Hub / Zone, flow, capacity, map, or "
        "table explorer entries are registered."
    ) in empty_context_links


def test_flow_context_metadata_is_available_dashboard() -> None:
    entry = registry_entry_by_concept_id(FLOW_CONTEXT_ID)
    html = render_dashboard_context_panel(FLOW_CONTEXT_ID)
    context_links = render_flow_context_links()

    assert entry is not None
    assert entry.status is DashboardStatus.AVAILABLE
    assert entry.notebook_name == "flow_operations"
    assert entry.notebook_route == "/marimo/flow_operations/"
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/flow.md"
        in entry.generated_gold_paths
    )
    assert entry.source_chunk_ids == (
        "chunk-gbb-guide-flow-report",
        "chunk-gbb-procedures-scheduled-flow",
        "chunk-sttm-procedures-settlement-terms",
    )
    assert "silver.gas_model.silver_gas_fact_connection_point_flow" in (
        entry.backing_assets
    )
    assert "silver.gas_model.silver_gas_fact_facility_flow_storage" in (
        entry.backing_assets
    )
    assert "silver.gas_model.silver_gas_fact_nomination_forecast" in (
        entry.backing_assets
    )
    assert "silver.gas_model.silver_gas_fact_operational_meter_flow" in (
        entry.backing_assets
    )
    assert "Flow Context" in html
    assert "chunk-gbb-guide-flow-report" in html
    assert 'data-status="available"' in html
    assert 'href="/marimo/flow_operations/"' in context_links
    assert "Facility Context" in context_links
    assert "Connection Point Context" in context_links
    assert "Gas Day Context" in context_links


def test_flow_table_specs_and_loader_use_bounded_recent_samples() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "11",
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

    specs = flow_table_specs()
    loads = load_flow_context_tables(config, reader=reader)

    assert specs == FLOW_TABLE_SPECS
    assert tuple(spec.table_name for spec in specs) == (
        CONNECTION_POINT_FLOW_TABLE_NAME,
        FACILITY_FLOW_STORAGE_TABLE_NAME,
        NOMINATION_FORECAST_TABLE_NAME,
        OPERATIONAL_METER_FLOW_TABLE_NAME,
    )
    assert len(loads) == 4
    assert captured == [
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_connection_point_flow",
            11,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_facility_flow_storage",
            11,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_nomination_forecast",
            11,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_operational_meter_flow",
            11,
        ),
    ]

    cache: GasModelSessionCache = {}
    cached_calls = 0

    def cached_reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        nonlocal cached_calls
        assert uri.endswith(f"/{CONNECTION_POINT_FLOW_TABLE_NAME}")
        assert storage_options == config.storage_options()
        assert row_limit == 11
        cached_calls += 1
        return pl.DataFrame({"source_system": ["GBB"]})

    first_cached = cached_load_flow_context_tables(
        config,
        cache,
        specs=(FLOW_TABLE_SPECS[0],),
        reader=cached_reader,
        refresh_token="same",
    )
    second_cached = cached_load_flow_context_tables(
        config,
        cache,
        specs=(FLOW_TABLE_SPECS[0],),
        reader=cached_reader,
        refresh_token="same",
    )
    refreshed = cached_load_flow_context_tables(
        config,
        cache,
        specs=(FLOW_TABLE_SPECS[0],),
        reader=cached_reader,
        refresh_token="changed",
    )

    assert cached_calls == 2
    assert not first_cached[0].cache_hit
    assert second_cached[0].cache_hit
    assert not refreshed[0].cache_hit


def test_flow_summary_helpers_extract_sources_and_recent_observations() -> None:
    connection_point_load = _facility_load(
        FLOW_TABLE_SPECS[0],
        pl.DataFrame(
            {
                "source_system": ["GBB", "GBB"],
                "source_tables": [
                    ["silver.gbb.silver_gasbb_pipeline_connection_flow_v2"],
                    ["silver.gbb.silver_gasbb_pipeline_connection_flow_v2"],
                ],
                "gas_date": [date(2024, 1, 2), date(2024, 1, 3)],
                "source_facility_id": ["10", "10"],
                "source_connection_point_id": ["1001", "1002"],
                "flow_direction": ["RECEIPT", "DELIVERY"],
                "actual_quantity_tj": [5.0, None],
                "source_last_updated_timestamp": [
                    datetime(2024, 1, 2, 6),
                    datetime(2024, 1, 3, 6),
                ],
                "ingested_timestamp": [
                    datetime(2024, 1, 2, 8),
                    datetime(2024, 1, 3, 8),
                ],
            }
        ),
        row_limit=20,
    )
    facility_load = _facility_load(
        FLOW_TABLE_SPECS[1],
        pl.DataFrame(
            {
                "source_system": ["GBB"],
                "source_tables": [["silver.gbb.silver_gasbb_actual_flow_storage"]],
                "gas_date": [date(2024, 1, 3)],
                "source_facility_id": ["20"],
                "source_location_id": ["L1"],
                "demand_tj": [12.5],
                "supply_tj": [None],
                "held_in_storage_tj": [7.0],
                "source_last_updated_timestamp": [datetime(2024, 1, 3, 7)],
                "ingested_timestamp": [datetime(2024, 1, 3, 9)],
            }
        ),
        row_limit=20,
    )
    nomination_load = _facility_load(
        FLOW_TABLE_SPECS[2],
        pl.DataFrame(
            {
                "source_system": ["VICGAS"],
                "source_table": [
                    "silver.vicgas.silver_int153_v4_demand_forecast_rpt_1"
                ],
                "source_tables": [
                    ["silver.vicgas.silver_int153_v4_demand_forecast_rpt_1"]
                ],
                "gas_date": [date(2024, 1, 4)],
                "forecast_type": ["interval_demand"],
                "forecast_version": ["42"],
                "gas_interval": [12],
                "demand_forecast_gj": [1000.0],
                "override_quantity_gj": [900.0],
                "source_last_updated_timestamp": [datetime(2024, 1, 4, 5)],
                "ingested_timestamp": [datetime(2024, 1, 4, 6)],
            }
        ),
        row_limit=20,
    )
    meter_load = _facility_load(
        FLOW_TABLE_SPECS[3],
        pl.DataFrame(
            {
                "source_system": ["VICGAS"],
                "source_table": [
                    "silver.vicgas.silver_int236_v4_operational_meter_readings_1"
                ],
                "gas_date": [date(2024, 1, 4)],
                "gas_interval": ["13"],
                "point_type": ["direction_code_name"],
                "source_point_id": ["Dandenong"],
                "flow_direction": ["WITHDRAWAL"],
                "quantity_gj": [70.0],
                "commencement_timestamp": [datetime(2024, 1, 4, 13)],
                "source_last_updated_timestamp": [datetime(2024, 1, 4, 7)],
                "ingested_timestamp": [datetime(2024, 1, 4, 8)],
            }
        ),
        row_limit=20,
    )
    loads = (connection_point_load, facility_load, nomination_load, meter_load)

    kpis = flow_kpi_frame(loads)
    source_summary = flow_source_summary_frame(loads)
    observations = flow_recent_observation_frame(loads)
    kpi_values = {row["metric"]: row["value"] for row in kpis.to_dicts()}
    source_rows = {
        (row["fact"], row["source system"], row["source table"]): row
        for row in source_summary.to_dicts()
    }

    assert kpi_values["Flow facts checked"] == "4"
    assert kpi_values["Loaded facts"] == "4"
    assert kpi_values["Source systems"] == "2"
    assert kpi_values["Source tables"] == "4"
    assert kpi_values["Flow measure rows"] == "4"
    assert kpi_values["Latest Gas Day"] == "2024-01-04"
    assert kpi_values["Recent/sample observations"] == "6"
    assert (
        source_rows[
            (
                "Connection point flow",
                "GBB",
                "silver.gbb.silver_gasbb_pipeline_connection_flow_v2",
            )
        ]["measure rows"]
        == 1
    )
    assert (
        source_rows[
            (
                "Facility flow and storage",
                "GBB",
                "silver.gbb.silver_gasbb_actual_flow_storage",
            )
        ]["measure rows"]
        == 1
    )
    assert (
        source_rows[
            (
                "Nomination forecast",
                "VICGAS",
                "silver.vicgas.silver_int153_v4_demand_forecast_rpt_1",
            )
        ]["measure rows"]
        == 1
    )
    assert (
        source_rows[
            (
                "Operational meter flow",
                "VICGAS",
                "silver.vicgas.silver_int236_v4_operational_meter_readings_1",
            )
        ]["measure rows"]
        == 1
    )
    assert observations.select("fact", "measure", "quantity", "unit").to_dicts()[
        :3
    ] == [
        {
            "fact": "Operational meter flow",
            "measure": "quantity_gj",
            "quantity": 70.0,
            "unit": "GJ",
        },
        {
            "fact": "Nomination forecast",
            "measure": "demand_forecast_gj",
            "quantity": 1000.0,
            "unit": "GJ",
        },
        {
            "fact": "Nomination forecast",
            "measure": "override_quantity_gj",
            "quantity": 900.0,
            "unit": "GJ",
        },
    ]


def test_flow_helpers_cover_missing_columns_and_empty_state_behavior() -> None:
    partial_load = _facility_load(
        FLOW_TABLE_SPECS[0],
        pl.DataFrame(
            {
                "source_system": ["GBB"],
                "gas_date": [date(2024, 1, 5)],
            }
        ),
        row_limit=6,
    )
    null_gas_date_load = _facility_load(
        FLOW_TABLE_SPECS[0],
        pl.DataFrame(
            {
                "source_system": ["GBB"],
                "gas_date": [None],
            }
        ),
        row_limit=6,
    )
    unavailable_load = _facility_load(
        FLOW_TABLE_SPECS[1],
        None,
        error="FileNotFoundError: no parquet files found",
        row_limit=6,
    )
    empty_nomination_load = _facility_load(
        FLOW_TABLE_SPECS[2],
        pl.DataFrame(),
        row_limit=6,
    )
    empty_meter_load = _facility_load(
        FLOW_TABLE_SPECS[3],
        pl.DataFrame(),
        row_limit=6,
    )
    unknown_empty_load = _facility_load(
        GasTableSpec(
            section="Flow facts",
            label="Unmapped flow",
            table_name="silver_gas_fact_unmapped_flow",
        ),
        None,
        row_limit=6,
    )
    unknown_source_load = _facility_load(
        GasTableSpec(
            section="Flow facts",
            label="Unmapped flow rows",
            table_name="silver_gas_fact_unmapped_flow_rows",
        ),
        pl.DataFrame(
            {
                "source_system": [None, None],
                "gas_date": [
                    datetime(2024, 1, 6),
                    datetime(2024, 1, 5),
                ],
                "source_last_updated_timestamp": [
                    datetime(2024, 1, 7),
                    datetime(2024, 1, 6),
                ],
                "ingested_timestamp": [
                    datetime(2024, 1, 7, 1),
                    datetime(2024, 1, 6, 1),
                ],
            }
        ),
        row_limit=6,
    )
    loads = (
        partial_load,
        unavailable_load,
        empty_nomination_load,
        empty_meter_load,
    )

    source_summary = flow_source_summary_frame(loads)
    observations = flow_recent_observation_frame(loads)
    kpis = flow_kpi_frame(loads)
    markdown = flow_context_empty_state_markdown(loads)
    empty_markdown = flow_context_empty_state_markdown(())
    empty_context_links = render_flow_context_links(entries=())
    unknown_empty_summary = flow_source_summary_frame((unknown_empty_load,))
    unknown_source_summary = flow_source_summary_frame((unknown_source_load,))
    null_date_kpis = flow_kpi_frame((partial_load, null_gas_date_load))
    source_row = source_summary.row(0, named=True)
    unknown_source_row = unknown_source_summary.row(0, named=True)
    kpi_values = {row["metric"]: row["value"] for row in kpis.to_dicts()}
    null_date_kpi_values = {
        row["metric"]: row["value"] for row in null_date_kpis.to_dicts()
    }

    assert source_summary.height == 1
    assert source_row["source system"] == "GBB"
    assert source_row["source table"] == "(empty source_table/source_tables value)"
    assert source_row["measure rows"] == 0
    assert observations.is_empty()
    assert unknown_empty_summary.is_empty()
    assert unknown_source_row["rows"] == 2
    assert unknown_source_row["source system"] == "(empty source_system value)"
    assert (
        unknown_source_row["source table"] == "(empty source_table/source_tables value)"
    )
    assert unknown_source_row["latest gas date"] == date(2024, 1, 6)
    assert unknown_source_row["latest source update"] == datetime(2024, 1, 7)
    assert unknown_source_row["latest ingest"] == datetime(2024, 1, 7, 1)
    assert (
        "silver_gas_fact_unmapped_flow_rows has no configured Flow measure columns"
        == unknown_source_row["detail"]
    )
    assert kpi_values["Flow measure rows"] == "0"
    assert null_date_kpi_values["Latest Gas Day"] == "2024-01-05"
    assert "No Flow source summaries or recent measure rows" in markdown
    assert "`1` reads were unavailable and `2` reads returned no rows" in markdown
    assert "Bounded preview reads are capped at `6` rows per table" in markdown
    assert "No Flow operations tables were requested" in empty_markdown
    assert (
        "No Flow, Facility, Connection Point, Gas Day, schedule, capacity, map, "
        "or table explorer entries are registered."
    ) in empty_context_links


def test_operational_meter_flow_metadata_is_available_dashboard() -> None:
    entry = registry_entry_by_concept_id(OPERATIONAL_METER_FLOW_CONTEXT_ID)
    html = render_dashboard_context_panel(OPERATIONAL_METER_FLOW_CONTEXT_ID)
    context_links = render_operational_meter_flow_context_links()

    assert entry is not None
    assert entry.status is DashboardStatus.AVAILABLE
    assert entry.notebook_name == "operational_meter_flow"
    assert entry.notebook_route == "/marimo/operational_meter_flow/"
    assert "silver.gas_model.silver_gas_fact_operational_meter_flow" in (
        entry.backing_assets
    )
    assert "silver.gas_model.silver_gas_dim_operational_point" in (entry.backing_assets)
    assert "silver.gas_model.silver_gas_dim_zone" in entry.backing_assets
    assert "silver.gas_model.silver_gas_dim_pipeline_segment" in (entry.backing_assets)
    assert "Operational Meter Flow" in html
    assert "chunk-gbb-guide-flow-report" in html
    assert 'data-status="available"' in html
    assert 'href="/marimo/operational_meter_flow/"' in context_links
    assert "Flow Context" in context_links
    assert "Pipeline and Connection Operations" in context_links
    assert "Hub / Zone Context" in context_links


def test_operational_meter_flow_table_specs_and_loader_use_bounded_recent_samples() -> (
    None
):
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "13",
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

    specs = operational_meter_flow_table_specs()
    loads = load_operational_meter_flow_tables(config, reader=reader)

    assert specs == OPERATIONAL_METER_FLOW_TABLE_SPECS
    assert tuple(spec.table_name for spec in specs) == (
        OPERATIONAL_METER_FLOW_TABLE_NAME,
        OPERATIONAL_POINT_DIM_TABLE_NAME,
        HUB_ZONE_DIM_TABLE_NAME,
        PIPELINE_SEGMENT_DIM_TABLE_NAME,
    )
    assert len(loads) == 4
    assert captured == [
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_operational_meter_flow",
            13,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_dim_operational_point",
            13,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/silver_gas_dim_zone",
            13,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_dim_pipeline_segment",
            13,
        ),
    ]

    cache: GasModelSessionCache = {}
    cached_calls = 0

    def cached_reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        nonlocal cached_calls
        assert uri.endswith(f"/{OPERATIONAL_METER_FLOW_TABLE_NAME}")
        assert storage_options == config.storage_options()
        assert row_limit == 13
        cached_calls += 1
        return pl.DataFrame({"source_system": ["VICGAS"]})

    first_cached = cached_load_operational_meter_flow_tables(
        config,
        cache,
        specs=(OPERATIONAL_METER_FLOW_TABLE_SPECS[0],),
        reader=cached_reader,
        refresh_token="same",
    )
    second_cached = cached_load_operational_meter_flow_tables(
        config,
        cache,
        specs=(OPERATIONAL_METER_FLOW_TABLE_SPECS[0],),
        reader=cached_reader,
        refresh_token="same",
    )
    refreshed = cached_load_operational_meter_flow_tables(
        config,
        cache,
        specs=(OPERATIONAL_METER_FLOW_TABLE_SPECS[0],),
        reader=cached_reader,
        refresh_token="changed",
    )

    assert cached_calls == 2
    assert not first_cached[0].cache_hit
    assert second_cached[0].cache_hit
    assert not refreshed[0].cache_hit


def test_operational_meter_flow_helpers_summarize_relationship_gaps() -> None:
    meter_flow_load = _facility_load(
        OPERATIONAL_METER_FLOW_TABLE_SPECS[0],
        pl.DataFrame(
            {
                "operational_point_key": ["op-key-1", None, "missing-key"],
                "zone_key": ["zone-key-1", None, "zone-key-1"],
                "pipeline_segment_key": ["pipe-key-1", None, "pipe-key-2"],
                "source_system": ["VICGAS", "VICGAS", "VICGAS"],
                "source_table": [
                    "silver.vicgas.silver_int236_v4_operational_meter_readings_1",
                    "silver.vicgas.silver_int313_v4_allocated_injections_withdrawals_1",
                    "silver.vicgas.silver_int236_v4_operational_meter_readings_1",
                ],
                "gas_date": [
                    date(2024, 1, 4),
                    date(2024, 1, 4),
                    date(2024, 1, 5),
                ],
                "gas_interval": ["13", "14", "15"],
                "point_type": ["direction_code_name", "phy_mirn", "meter"],
                "source_point_id": ["Dandenong", "MIRN-A", "Missing"],
                "flow_direction": ["WITHDRAWAL", "INJECTION", "WITHDRAWAL"],
                "quantity_gj": [70.0, 20.0, None],
                "source_last_updated_timestamp": [
                    datetime(2024, 1, 4, 7),
                    datetime(2024, 1, 4, 8),
                    datetime(2024, 1, 5, 8),
                ],
                "ingested_timestamp": [
                    datetime(2024, 1, 4, 9),
                    datetime(2024, 1, 4, 10),
                    datetime(2024, 1, 5, 10),
                ],
            }
        ),
    )
    operational_point_load = _facility_load(
        OPERATIONAL_METER_FLOW_TABLE_SPECS[1],
        pl.DataFrame(
            {
                "surrogate_key": ["op-key-1", "op-key-2"],
                "source_system": ["VICGAS", "VICGAS"],
                "source_tables": [
                    ["silver.vicgas.silver_int236_v4_operational_meter_readings_1"],
                    [
                        "silver.vicgas.silver_int313_v4_allocated_injections_withdrawals_1"
                    ],
                ],
                "point_type": ["direction_code_name", "phy_mirn"],
                "source_point_id": ["Dandenong", "MIRN-A"],
                "point_name": ["Dandenong Meter", "MIRN Site"],
                "source_zone_id": ["5", None],
                "zone_key": ["zone-key-1", None],
                "source_pipeline_id": ["VTS", None],
                "source_pipeline_segment_id": ["77", None],
                "pipeline_segment_key": ["pipe-key-1", None],
                "ingested_timestamp": [
                    datetime(2024, 1, 4, 9),
                    datetime(2024, 1, 4, 10),
                ],
            }
        ),
    )
    zone_load = _facility_load(
        OPERATIONAL_METER_FLOW_TABLE_SPECS[2],
        pl.DataFrame(
            {
                "surrogate_key": ["zone-key-1"],
                "source_system": ["VICGAS"],
                "zone_type": ["linepack_zone"],
                "source_zone_id": ["5"],
                "zone_name": ["Linepack 5"],
            }
        ),
    )
    pipeline_segment_load = _facility_load(
        OPERATIONAL_METER_FLOW_TABLE_SPECS[3],
        pl.DataFrame(
            {
                "surrogate_key": ["pipe-key-1"],
                "zone_key": ["zone-key-1"],
                "source_system": ["VICGAS"],
                "source_pipeline_id": ["VTS"],
                "source_pipe_segment_id": ["77"],
                "pipe_segment_name": ["Segment 77"],
            }
        ),
    )
    loads = (
        meter_flow_load,
        operational_point_load,
        zone_load,
        pipeline_segment_load,
    )

    kpis = operational_meter_flow_kpi_frame(loads)
    summary = operational_meter_flow_summary_frame(loads)
    point_context = operational_meter_flow_point_context_frame(loads)
    gaps = operational_meter_flow_relationship_gap_frame(loads)
    kpi_values = {row["metric"]: row["value"] for row in kpis.to_dicts()}
    summary_rows = {
        (row["point type"], row["source point id"]): row for row in summary.to_dicts()
    }
    point_rows = {
        (row["point type"], row["source point id"]): row
        for row in point_context.to_dicts()
    }
    gap_rows = {row["relationship"]: row for row in gaps.to_dicts()}

    assert kpi_values["Operational tables checked"] == "4"
    assert kpi_values["Loaded tables"] == "4"
    assert kpi_values["Meter flow rows"] == "3"
    assert kpi_values["Rows with quantity"] == "2"
    assert kpi_values["Total quantity GJ"] == "90"
    assert kpi_values["Operational points"] == "2"
    assert kpi_values["Gas intervals"] == "3"
    assert kpi_values["Relationship gap rows"] == "6"
    assert kpi_values["Latest Gas Day"] == "2024-01-05"

    dandenong = summary_rows[("direction_code_name", "Dandenong")]
    assert dandenong["operational point"] == "Dandenong Meter"
    assert dandenong["flow direction"] == "WITHDRAWAL"
    assert dandenong["gas intervals"] == 1
    assert dandenong["total quantity gj"] == 70.0
    assert dandenong["zone"] == "Linepack 5 (5)"
    assert dandenong["pipeline segment"] == "Segment 77 (77)"
    assert dandenong["relationship status"] == "Conformed Operational Point match"
    assert dandenong["coverage gap"] == "Covered"

    mirn = summary_rows[("phy_mirn", "MIRN-A")]
    assert mirn["relationship status"] == "Source-qualified Operational Point match"
    assert mirn["coverage gap"] == "Missing operational_point_key"
    assert mirn["total quantity gj"] == 20.0

    missing = summary_rows[("meter", "Missing")]
    assert missing["relationship status"] == "Relationship gap"
    assert missing["coverage gap"] == "Unmatched operational_point_key"

    assert (
        point_rows[("direction_code_name", "Dandenong")]["relationship status"]
        == "Operational dimensions available"
    )
    assert point_rows[("direction_code_name", "Dandenong")]["coverage gap"] == (
        "Covered"
    )
    assert point_rows[("phy_mirn", "MIRN-A")]["coverage gap"] == (
        "Missing zone_key, Missing pipeline_segment_key"
    )

    assert gap_rows["Operational meter flow -> Operational Point"]["gap rows"] == 1
    assert gap_rows["Operational meter flow -> Zone"]["gap rows"] == 1
    assert gap_rows["Operational meter flow -> Pipeline segment"]["gap rows"] == 2
    assert gap_rows["Operational Point -> Zone"]["gap rows"] == 1
    assert gap_rows["Operational Point -> Pipeline segment"]["gap rows"] == 1


def test_operational_meter_flow_helpers_cover_gap_classification_branches() -> None:
    meter_flow_load = _facility_load(
        OPERATIONAL_METER_FLOW_TABLE_SPECS[0],
        pl.DataFrame(
            {
                "operational_point_key": ["wrong-op-key", None],
                "source_system": ["VICGAS", "VICGAS"],
                "gas_date": [date(2024, 1, 6), date(2024, 1, 6)],
                "point_type": ["meter", "meter"],
                "source_point_id": ["OP1", "Missing"],
                "flow_direction": ["WITHDRAWAL", "INJECTION"],
                "quantity_gj": [5.0, 6.0],
            }
        ),
    )
    empty_meter_flow_load = _facility_load(
        OPERATIONAL_METER_FLOW_TABLE_SPECS[0],
        pl.DataFrame(),
    )
    operational_point_load = _facility_load(
        OPERATIONAL_METER_FLOW_TABLE_SPECS[1],
        pl.DataFrame(
            {
                "surrogate_key": ["op-key-1", "op-key-2", "op-key-3", "op-key-4"],
                "source_system": ["VICGAS", "VICGAS", "VICGAS", "VICGAS"],
                "point_type": ["meter", "meter", "meter", "meter"],
                "source_point_id": ["OP1", "OP2", "OP3", "OP4"],
                "point_name": ["Point 1", "Point 2", "Point 3", "Point 4"],
                "zone_key": [
                    "zone-name-only",
                    "zone-id-only",
                    "zone-empty",
                    "unmatched-zone",
                ],
                "pipeline_segment_key": [
                    "pipe-name-only",
                    "pipe-id-only",
                    "pipe-empty",
                    "unmatched-pipe",
                ],
            }
        ),
    )
    empty_operational_point_load = _facility_load(
        OPERATIONAL_METER_FLOW_TABLE_SPECS[1],
        pl.DataFrame(),
    )
    zone_load = _facility_load(
        OPERATIONAL_METER_FLOW_TABLE_SPECS[2],
        pl.DataFrame(
            {
                "surrogate_key": ["zone-name-only", "zone-id-only", "zone-empty"],
                "zone_name": ["Name Only", None, None],
                "source_zone_id": [None, "6", None],
            }
        ),
    )
    empty_zone_load = _facility_load(
        OPERATIONAL_METER_FLOW_TABLE_SPECS[2],
        pl.DataFrame(),
    )
    pipeline_segment_load = _facility_load(
        OPERATIONAL_METER_FLOW_TABLE_SPECS[3],
        pl.DataFrame(
            {
                "surrogate_key": ["pipe-name-only", "pipe-id-only", "pipe-empty"],
                "pipe_segment_name": ["Pipe Name Only", None, None],
                "source_pipe_segment_id": [None, "88", None],
            }
        ),
    )
    empty_pipeline_segment_load = _facility_load(
        OPERATIONAL_METER_FLOW_TABLE_SPECS[3],
        pl.DataFrame(),
    )
    loads = (
        meter_flow_load,
        operational_point_load,
        zone_load,
        pipeline_segment_load,
    )

    summary = operational_meter_flow_summary_frame(loads)
    point_context = operational_meter_flow_point_context_frame(loads)
    summary_rows = {
        row["source point id"]: row
        for row in summary.sort("source point id").to_dicts()
    }
    point_rows = {
        row["source point id"]: row
        for row in point_context.sort("source point id").to_dicts()
    }

    assert summary_rows["OP1"]["coverage gap"] == "Unmatched operational_point_key"
    assert summary_rows["OP1"]["source table"] == (
        "(empty source_table/source_tables value)"
    )
    assert summary_rows["Missing"]["coverage gap"] == (
        "Missing Operational Point dimension match"
    )
    assert point_rows["OP1"]["zone"] == "Name Only"
    assert point_rows["OP1"]["pipeline segment"] == "Pipe Name Only"
    assert point_rows["OP2"]["zone"] == "6"
    assert point_rows["OP2"]["pipeline segment"] == "88"
    assert point_rows["OP3"]["zone"] is None
    assert point_rows["OP3"]["pipeline segment"] is None
    assert point_rows["OP4"]["coverage gap"] == (
        "Unmatched zone_key, Unmatched pipeline_segment_key"
    )

    missing_dimension_rows = operational_meter_flow_point_context_frame(
        (
            empty_meter_flow_load,
            operational_point_load,
            empty_zone_load,
            empty_pipeline_segment_load,
        )
    )
    missing_dimension_gap_rows = operational_meter_flow_relationship_gap_frame(
        (
            empty_meter_flow_load,
            operational_point_load,
            empty_zone_load,
            empty_pipeline_segment_load,
        )
    )
    missing_point_gap_rows = operational_meter_flow_relationship_gap_frame(
        (
            meter_flow_load,
            empty_operational_point_load,
            empty_zone_load,
            empty_pipeline_segment_load,
        )
    )
    empty_meter_kpis = operational_meter_flow_kpi_frame(
        (
            empty_meter_flow_load,
            operational_point_load,
            empty_zone_load,
            empty_pipeline_segment_load,
        )
    )

    assert {row["coverage gap"] for row in missing_dimension_rows.to_dicts()} == {
        "Unmatched zone_key, Unmatched pipeline_segment_key"
    }
    assert {row["coverage gap"] for row in missing_dimension_gap_rows.to_dicts()} >= {
        "No source rows loaded"
    }
    assert missing_point_gap_rows.row(0, named=True)["coverage gap"] == (
        "Meter flow rows have missing or unmatched operational_point_key values "
        "and no source-qualified Operational Point row was loaded."
    )
    assert {row["metric"]: row["value"] for row in empty_meter_kpis.to_dicts()}[
        "Gas intervals"
    ] == "0"


def test_operational_meter_flow_helpers_cover_empty_state_behavior() -> None:
    unavailable_load = _facility_load(
        OPERATIONAL_METER_FLOW_TABLE_SPECS[0],
        None,
        error="FileNotFoundError: no parquet files found",
        row_limit=5,
    )
    loads = (
        unavailable_load,
        *(
            _facility_load(spec, pl.DataFrame(), row_limit=5)
            for spec in OPERATIONAL_METER_FLOW_TABLE_SPECS[1:]
        ),
    )

    assert operational_meter_flow_summary_frame(loads).is_empty()
    assert operational_meter_flow_point_context_frame(loads).is_empty()
    assert operational_meter_flow_relationship_gap_frame(loads).is_empty()

    markdown = operational_meter_flow_empty_state_markdown(loads)
    empty_markdown = operational_meter_flow_empty_state_markdown(())
    empty_context_links = render_operational_meter_flow_context_links(entries=())

    assert "No Operational Meter Flow rows or dimension context" in markdown
    assert "`1` reads were unavailable and `3` reads returned no rows" in markdown
    assert "Bounded preview reads are capped at `5` rows per table" in markdown
    assert "No Operational Meter Flow tables were requested" in empty_markdown
    assert (
        "No Operational Meter Flow, Flow, Pipeline, Hub / Zone, source coverage, "
        "or table explorer entries are registered."
    ) in empty_context_links


def test_pipeline_connection_operations_metadata_is_available_dashboard() -> None:
    entry = registry_entry_by_concept_id(PIPELINE_CONNECTION_OPERATIONS_CONTEXT_ID)
    html = render_dashboard_context_panel(PIPELINE_CONNECTION_OPERATIONS_CONTEXT_ID)
    context_links = render_pipeline_connection_operations_context_links()

    assert entry is not None
    assert entry.status is DashboardStatus.AVAILABLE
    assert entry.notebook_name == "pipeline_connection_operations"
    assert entry.notebook_route == "/marimo/pipeline_connection_operations/"
    assert "silver.gas_model.silver_gas_dim_connection_point" in (entry.backing_assets)
    assert "silver.gas_model.silver_gas_dim_pipeline_segment" in (entry.backing_assets)
    assert "silver.gas_model.silver_gas_fact_connection_point_flow" in (
        entry.backing_assets
    )
    assert "silver.gas_model.silver_gas_fact_operational_meter_flow" in (
        entry.backing_assets
    )
    assert "silver.gas_model.silver_gas_fact_capacity_outlook" in (entry.backing_assets)
    assert "Pipeline and Connection Operations" in html
    assert "chunk-gbb-guide-connection-point-identifiers" in html
    assert 'data-status="available"' in html
    assert 'href="/marimo/pipeline_connection_operations/"' in context_links
    assert "Connection Point Context" in context_links
    assert "Facility Context" in context_links
    assert "Flow Context" in context_links
    assert "Capacity Context" in context_links


def test_pipeline_connection_operations_table_specs_and_loader_use_bounded_rows() -> (
    None
):
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "12",
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

    specs = pipeline_connection_operations_table_specs()
    loads = load_pipeline_connection_operations_tables(config, reader=reader)

    assert specs == PIPELINE_CONNECTION_OPERATIONS_TABLE_SPECS
    assert tuple(spec.table_name for spec in specs) == (
        CONNECTION_POINT_DIM_TABLE_NAME,
        FACILITY_DIM_TABLE_NAME,
        PIPELINE_SEGMENT_DIM_TABLE_NAME,
        HUB_ZONE_DIM_TABLE_NAME,
        CONNECTION_POINT_FLOW_TABLE_NAME,
        OPERATIONAL_METER_FLOW_TABLE_NAME,
        FACILITY_CAPACITY_OUTLOOK_TABLE_NAME,
    )
    assert len(loads) == 7
    assert captured == [
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_dim_connection_point",
            12,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/silver_gas_dim_facility",
            12,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_dim_pipeline_segment",
            12,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/silver_gas_dim_zone",
            12,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_connection_point_flow",
            12,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_operational_meter_flow",
            12,
        ),
        (
            "s3://prod-energy-market-aemo/silver/gas_model/"
            "silver_gas_fact_capacity_outlook",
            12,
        ),
    ]

    cache: GasModelSessionCache = {}
    cached_calls = 0

    def cached_reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        nonlocal cached_calls
        assert uri.endswith(f"/{PIPELINE_SEGMENT_DIM_TABLE_NAME}")
        assert storage_options == config.storage_options()
        assert row_limit == 12
        cached_calls += 1
        return pl.DataFrame({"source_system": ["VICGAS"]})

    first_cached = cached_load_pipeline_connection_operations_tables(
        config,
        cache,
        specs=(PIPELINE_CONNECTION_OPERATIONS_TABLE_SPECS[2],),
        reader=cached_reader,
        refresh_token="same",
    )
    second_cached = cached_load_pipeline_connection_operations_tables(
        config,
        cache,
        specs=(PIPELINE_CONNECTION_OPERATIONS_TABLE_SPECS[2],),
        reader=cached_reader,
        refresh_token="same",
    )
    refreshed = cached_load_pipeline_connection_operations_tables(
        config,
        cache,
        specs=(PIPELINE_CONNECTION_OPERATIONS_TABLE_SPECS[2],),
        reader=cached_reader,
        refresh_token="changed",
    )

    assert cached_calls == 2
    assert not first_cached[0].cache_hit
    assert second_cached[0].cache_hit
    assert not refreshed[0].cache_hit


def test_pipeline_connection_operations_helpers_show_relationship_gaps() -> None:
    connection_point_load = _facility_load(
        PIPELINE_CONNECTION_OPERATIONS_TABLE_SPECS[0],
        pl.DataFrame(
            {
                "surrogate_key": ["cp-key-1", "cp-key-2"],
                "facility_key": ["facility-key-1", None],
                "location_key": ["location-key-1", None],
                "zone_key": ["zone-key-1", None],
                "source_system": ["GBB", "GBB"],
                "source_tables": [
                    ["silver.gbb.silver_gasbb_nodes_connection_points"],
                    ["silver.gbb.silver_gasbb_nodes_connection_points"],
                ],
                "source_facility_id": ["10", "20"],
                "source_connection_point_id": ["1001", "2002"],
                "connection_point_name": ["Receipt Point", "Delivery Point"],
                "flow_direction": ["RECEIPT", "DELIVERY"],
                "facility_name": ["Matched Facility", "Unmatched Facility"],
                "location_name": ["Longford", None],
                "state": ["Victoria", "Queensland"],
                "exempt": [False, True],
                "effective_date": [date(2024, 1, 1), None],
                "exemption_description": [None, "test exemption"],
                "source_last_updated_timestamp": [
                    datetime(2024, 1, 1, 6),
                    datetime(2024, 1, 2, 6),
                ],
                "ingested_timestamp": [
                    datetime(2024, 1, 1, 8),
                    datetime(2024, 1, 2, 8),
                ],
            }
        ),
    )
    facility_load = _facility_load(
        PIPELINE_CONNECTION_OPERATIONS_TABLE_SPECS[1],
        pl.DataFrame(
            {
                "surrogate_key": ["facility-key-1"],
                "source_system": ["GBB"],
                "source_facility_id": ["10"],
                "facility_name": ["Matched Facility"],
            }
        ),
    )
    pipeline_segment_load = _facility_load(
        PIPELINE_CONNECTION_OPERATIONS_TABLE_SPECS[2],
        pl.DataFrame(
            {
                "surrogate_key": ["pipe-key-1", "pipe-key-2"],
                "zone_key": ["zone-key-1", None],
                "source_system": ["VICGAS", "VICGAS"],
                "source_tables": [
                    ["silver.vicgas.silver_int259_v4_pipe_segment_1"],
                    ["silver.vicgas.silver_int259_v4_pipe_segment_1"],
                ],
                "source_pipeline_id": ["VTS", "VTS"],
                "source_pipe_segment_id": ["77", "78"],
                "pipe_segment_name": ["Segment 77", "Segment 78"],
                "source_linepack_zone_id": ["5", "6"],
                "source_origin_node_name": ["Origin A", "Origin B"],
                "source_destination_node_name": ["Destination A", "Destination B"],
                "reverse_flow": ["Y", None],
                "compressor": ["N", "Y"],
                "commencement_date": [date(2020, 1, 1), None],
                "termination_date": [None, date(2025, 1, 1)],
                "source_last_updated_timestamp": [
                    datetime(2024, 1, 3, 6),
                    datetime(2024, 1, 4, 6),
                ],
                "ingested_timestamp": [
                    datetime(2024, 1, 3, 8),
                    datetime(2024, 1, 4, 8),
                ],
            }
        ),
    )
    zone_load = _facility_load(
        PIPELINE_CONNECTION_OPERATIONS_TABLE_SPECS[3],
        pl.DataFrame(
            {
                "surrogate_key": ["zone-key-1"],
                "source_system": ["VICGAS"],
                "zone_type": ["linepack_zone"],
                "source_zone_id": ["5"],
                "zone_name": ["Linepack 5"],
            }
        ),
    )
    flow_load = _facility_load(
        PIPELINE_CONNECTION_OPERATIONS_TABLE_SPECS[4],
        pl.DataFrame(
            {
                "connection_point_key": ["cp-key-1", None, None],
                "source_system": ["GBB", "GBB", "GBB"],
                "gas_date": [
                    date(2024, 1, 3),
                    date(2024, 1, 4),
                    date(2024, 1, 4),
                ],
                "source_facility_id": ["10", "20", "99"],
                "source_connection_point_id": ["1001", "2002", "9999"],
                "flow_direction": ["RECEIPT", "DELIVERY", "RECEIPT"],
                "actual_quantity_tj": [5.0, 7.0, 3.0],
                "quality": ["actual", "actual", "estimated"],
                "source_last_updated_timestamp": [
                    datetime(2024, 1, 3, 7),
                    datetime(2024, 1, 4, 7),
                    datetime(2024, 1, 4, 8),
                ],
                "ingested_timestamp": [
                    datetime(2024, 1, 3, 9),
                    datetime(2024, 1, 4, 9),
                    datetime(2024, 1, 4, 10),
                ],
            }
        ),
    )
    meter_flow_load = _facility_load(
        PIPELINE_CONNECTION_OPERATIONS_TABLE_SPECS[5],
        pl.DataFrame(
            {
                "source_system": ["VICGAS", "VICGAS"],
                "source_table": [
                    "silver.vicgas.silver_int236_v4_operational_meter_readings_1",
                    "silver.vicgas.silver_int236_v4_operational_meter_readings_1",
                ],
                "gas_date": [date(2024, 1, 4), date(2024, 1, 4)],
                "pipeline_segment_key": ["pipe-key-1", None],
                "point_type": ["meter", "meter"],
                "source_point_id": ["OP1", "OP2"],
                "flow_direction": ["WITHDRAWAL", "INJECTION"],
                "quantity_gj": [70.0, 20.0],
            }
        ),
    )
    capacity_load = _facility_load(
        PIPELINE_CONNECTION_OPERATIONS_TABLE_SPECS[6],
        pl.DataFrame(
            {
                "source_system": ["GBB", "GBB"],
                "source_table": ["silver.gbb.capacity", "silver.gbb.capacity"],
                "source_facility_id": ["10", "99"],
                "facility_name": ["Matched Facility", "Missing Facility"],
                "capacity_type": ["nameplate", "nameplate"],
                "flow_direction": ["RECEIPT", "RECEIPT"],
                "capacity_quantity_tj": [100.0, 50.0],
            }
        ),
    )
    loads = (
        connection_point_load,
        facility_load,
        pipeline_segment_load,
        zone_load,
        flow_load,
        meter_flow_load,
        capacity_load,
    )

    kpis = pipeline_connection_operations_kpi_frame(loads)
    flow_summary = pipeline_connection_flow_summary_frame(loads)
    metadata = pipeline_connection_metadata_frame(loads)
    gaps = pipeline_connection_relationship_gap_frame(loads)
    kpi_values = {row["metric"]: row["value"] for row in kpis.to_dicts()}
    flow_rows = {
        (row["source facility id"], row["source connection point id"]): row
        for row in flow_summary.to_dicts()
    }
    metadata_rows = {
        (row["metadata kind"], row["source identifier"]): row
        for row in metadata.to_dicts()
    }
    gap_rows = {row["relationship"]: row for row in gaps.to_dicts()}

    assert kpi_values["Operation tables checked"] == "7"
    assert kpi_values["Loaded tables"] == "7"
    assert kpi_values["Connection points"] == "2"
    assert kpi_values["Pipeline segments"] == "2"
    assert kpi_values["Connection point flow rows"] == "3"
    assert kpi_values["Operational meter flow rows"] == "2"
    assert kpi_values["Capacity rows"] == "2"
    assert kpi_values["Relationship gap rows"] == "5"
    assert kpi_values["Latest Gas Day"] == "2024-01-04"

    assert flow_rows[("10", "1001")]["relationship status"] == (
        "Conformed Connection Point match"
    )
    assert flow_rows[("20", "2002")]["coverage gap"] == "Missing connection_point_key"
    assert flow_rows[("99", "9999")]["relationship status"] == "Relationship gap"
    assert flow_rows[("99", "9999")]["coverage gap"] == (
        "Missing Connection Point dimension match"
    )
    assert flow_rows[("20", "2002")]["connection point"] == "Delivery Point"
    assert flow_rows[("20", "2002")]["total actual quantity tj"] == 7.0

    assert metadata_rows[("Connection Point", "1001")]["operational status"] == (
        "not exempt; effective from 2024-01-01"
    )
    assert metadata_rows[("Connection Point", "2002")]["coverage gap"] == (
        "Missing facility_key, location_key, zone_key"
    )
    assert (
        "reverse flow: Y"
        in metadata_rows[("Pipeline segment", "77")]["operational status"]
    )
    assert metadata_rows[("Pipeline segment", "78")]["coverage gap"] == (
        "Missing zone_key"
    )

    assert gap_rows["Connection Point -> Facility"]["gap rows"] == 1
    assert gap_rows["Connection Point flow -> Connection Point"]["gap rows"] == 1
    assert gap_rows["Capacity -> Connection Point"]["gap rows"] == 1
    assert gap_rows["Operational meter flow -> Pipeline segment"]["gap rows"] == 1
    assert gap_rows["Pipeline segment -> Zone"]["gap rows"] == 1
    assert (
        "connection_point_key"
        in gap_rows["Capacity -> Connection Point"]["coverage gap"]
    )


def test_pipeline_connection_operations_helpers_cover_gap_classification_branches() -> (
    None
):
    connection_point_load = _facility_load(
        PIPELINE_CONNECTION_OPERATIONS_TABLE_SPECS[0],
        pl.DataFrame(
            {
                "surrogate_key": ["cp-key-1"],
                "facility_key": ["facility-key-1"],
                "location_key": ["location-key-1"],
                "zone_key": ["zone-key-1"],
                "source_system": ["GBB"],
                "source_facility_id": ["10"],
                "source_connection_point_id": ["1001"],
                "connection_point_name": ["Receipt Point"],
                "flow_direction": ["RECEIPT"],
                "facility_name": ["Matched Facility"],
                "effective_date": [datetime(2024, 1, 1, 0)],
                "effective_to_date": [date(2024, 12, 31)],
            }
        ),
    )
    facility_load = _facility_load(
        PIPELINE_CONNECTION_OPERATIONS_TABLE_SPECS[1],
        pl.DataFrame(
            {
                "surrogate_key": ["facility-key-1"],
                "source_facility_id": ["10"],
            }
        ),
    )
    empty_pipeline_segment_load = _facility_load(
        PIPELINE_CONNECTION_OPERATIONS_TABLE_SPECS[2],
        pl.DataFrame(),
    )
    empty_zone_load = _facility_load(
        PIPELINE_CONNECTION_OPERATIONS_TABLE_SPECS[3],
        pl.DataFrame(),
    )
    flow_load = _facility_load(
        PIPELINE_CONNECTION_OPERATIONS_TABLE_SPECS[4],
        pl.DataFrame(
            {
                "connection_point_key": ["wrong-key", "missing-key", "cp-key-1"],
                "source_system": ["GBB", "GBB", "GBB"],
                "gas_date": [date(2024, 1, 5), date(2024, 1, 5), date(2024, 1, 5)],
                "source_facility_id": ["10", "99", "10"],
                "source_connection_point_id": ["1001", "9999", "1001"],
                "flow_direction": ["RECEIPT", "RECEIPT", "RECEIPT"],
                "actual_quantity_tj": [4.0, 2.0, None],
            }
        ),
    )
    empty_meter_flow_load = _facility_load(
        PIPELINE_CONNECTION_OPERATIONS_TABLE_SPECS[5],
        pl.DataFrame(),
    )
    capacity_load = _facility_load(
        PIPELINE_CONNECTION_OPERATIONS_TABLE_SPECS[6],
        pl.DataFrame(
            {
                "source_facility_id": ["10"],
                "flow_direction": ["RECEIPT"],
                "capacity_quantity_tj": [100.0],
            }
        ),
    )
    loads = (
        connection_point_load,
        facility_load,
        empty_pipeline_segment_load,
        empty_zone_load,
        flow_load,
        empty_meter_flow_load,
        capacity_load,
    )

    metadata = pipeline_connection_metadata_frame(loads)
    flow_summary = pipeline_connection_flow_summary_frame(loads)
    gaps = pipeline_connection_relationship_gap_frame(loads)
    metadata_row = metadata.row(0, named=True)
    flow_rows = flow_summary.to_dicts()
    matched_flow_row = next(
        row
        for row in flow_rows
        if (
            row["source facility id"],
            row["source connection point id"],
            row["coverage gap"],
        )
        == ("10", "1001", "Unmatched connection_point_key")
    )
    direct_flow_row = next(
        row
        for row in flow_rows
        if (
            row["source facility id"],
            row["source connection point id"],
            row["coverage gap"],
        )
        == ("10", "1001", "Covered")
    )
    missing_flow_row = next(
        row
        for row in flow_rows
        if (row["source facility id"], row["source connection point id"])
        == ("99", "9999")
    )
    gap_rows = {row["relationship"]: row for row in gaps.to_dicts()}

    assert "effective from 2024-01-01" in metadata_row["operational status"]
    assert "effective to 2024-12-31" in metadata_row["operational status"]
    assert matched_flow_row["flow rows"] == 1
    assert matched_flow_row["flow rows with quantity"] == 1
    assert direct_flow_row["flow rows"] == 1
    assert direct_flow_row["flow rows with quantity"] == 0
    assert missing_flow_row["coverage gap"] == "Unmatched connection_point_key"
    assert gap_rows["Connection Point -> Facility"]["coverage gap"] == "Covered"
    assert gap_rows["Capacity -> Connection Point"]["coverage gap"] == (
        "No direct connection_point_key; source-qualified comparison only"
    )
    assert gap_rows["Operational meter flow -> Pipeline segment"]["coverage gap"] == (
        "No source rows loaded"
    )
    assert gap_rows["Pipeline segment -> Zone"]["coverage gap"] == (
        "No source rows loaded"
    )


def test_pipeline_connection_operations_helpers_cover_empty_state_behavior() -> None:
    unavailable_load = _facility_load(
        PIPELINE_CONNECTION_OPERATIONS_TABLE_SPECS[0],
        None,
        error="FileNotFoundError: no parquet files found",
        row_limit=5,
    )
    loads = (
        unavailable_load,
        *(
            _facility_load(spec, pl.DataFrame(), row_limit=5)
            for spec in PIPELINE_CONNECTION_OPERATIONS_TABLE_SPECS[1:]
        ),
    )

    assert pipeline_connection_flow_summary_frame(loads).is_empty()
    assert pipeline_connection_metadata_frame(loads).is_empty()
    assert pipeline_connection_relationship_gap_frame(loads).is_empty()

    markdown = pipeline_connection_operations_empty_state_markdown(loads)
    empty_markdown = pipeline_connection_operations_empty_state_markdown(())
    empty_context_links = render_pipeline_connection_operations_context_links(
        entries=()
    )

    assert "No Pipeline and Connection operations rows are available" in markdown
    assert "`1` reads were unavailable and `6` reads returned no rows" in markdown
    assert "Bounded preview reads are capped at `5` rows per table" in markdown
    assert (
        "No Pipeline and Connection operations tables were requested" in empty_markdown
    )
    assert (
        "No Pipeline, Connection Point, Facility, Flow, Capacity, Hub / Zone, "
        "map, source coverage, or table explorer entries are registered."
    ) in empty_context_links


def test_hub_zone_context_metadata_is_available_dashboard() -> None:
    entry = registry_entry_by_concept_id(HUB_ZONE_CONTEXT_ID)
    html = render_dashboard_context_panel(HUB_ZONE_CONTEXT_ID)
    context_links = render_hub_zone_context_links()

    assert entry is not None
    assert entry.status is DashboardStatus.AVAILABLE
    assert entry.notebook_name == "hub_zone_explainer"
    assert entry.notebook_route == "/marimo/hub_zone_explainer/"
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/hub-zone.md"
        in entry.generated_gold_paths
    )
    assert entry.source_chunk_ids == (
        "chunk-sttm-procedures-definitions",
        "chunk-sttm-procedures-settlement-terms",
        "chunk-dwgm-operations-glossary-schedule",
        "chunk-dwgm-operations-capacity-certificates-modelling",
    )
    assert "silver.gas_model.silver_gas_dim_zone" in entry.backing_assets
    assert "Hub / Zone Context" in html
    assert "chunk-sttm-procedures-definitions" in html
    assert "tools/gas-market-knowledge-base/generated/gold/glossary/hub-zone.md" in html
    assert 'data-status="available"' in html
    assert 'href="/marimo/hub_zone_explainer/"' in context_links
    assert "Source Coverage Matrix" in context_links
    assert "Bid / Offer Stack" in context_links


def test_hub_zone_table_specs_and_loader_use_bounded_samples() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "7",
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

    specs = hub_zone_table_specs()
    loads = load_hub_zone_context_tables(config, reader=reader)

    assert specs == HUB_ZONE_TABLE_SPECS
    assert tuple(spec.table_name for spec in specs) == (HUB_ZONE_DIM_TABLE_NAME,)
    assert len(loads) == 1
    assert captured == [
        (
            "s3://prod-energy-market-aemo/silver/gas_model/silver_gas_dim_zone",
            7,
        )
    ]

    cache: GasModelSessionCache = {}
    cached_calls = 0

    def cached_reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        nonlocal cached_calls
        assert uri.endswith(f"/{HUB_ZONE_DIM_TABLE_NAME}")
        assert storage_options == config.storage_options()
        assert row_limit == 7
        cached_calls += 1
        return pl.DataFrame({"source_system": ["STTM"]})

    first_cached = cached_load_hub_zone_context_tables(
        config,
        cache,
        reader=cached_reader,
        refresh_token="same",
    )
    second_cached = cached_load_hub_zone_context_tables(
        config,
        cache,
        reader=cached_reader,
        refresh_token="same",
    )
    refreshed = cached_load_hub_zone_context_tables(
        config,
        cache,
        reader=cached_reader,
        refresh_token="changed",
    )

    assert cached_calls == 2
    assert not first_cached[0].cache_hit
    assert second_cached[0].cache_hit
    assert not refreshed[0].cache_hit


def test_hub_zone_metadata_helpers_extract_source_qualified_identifiers() -> None:
    load = _facility_load(
        HUB_ZONE_TABLE_SPECS[0],
        pl.DataFrame(
            {
                "surrogate_key": ["zone-key-1", "zone-key-2", "zone-key-3"],
                "source_system": ["STTM", "VICGAS", "GBB"],
                "source_tables": [
                    ["silver.sttm.silver_int671_v1_hub_facility_definition_rpt_1"],
                    ["silver.vicgas.silver_int259_v4_pipe_segment_1"],
                    [
                        "silver.gbb.silver_gasbb_demand_zones_and_pipeline_connectionpoint_mapping"
                    ],
                ],
                "zone_type": ["sttm_hub", "linepack_zone", "demand_zone"],
                "source_zone_id": ["SYD", "5", "DZ1"],
                "zone_name": ["Sydney Hub", "Linepack 5", "Demand Zone 1"],
                "zone_description": ["Sydney Hub", None, "GBB demand zone"],
                "source_surrogate_keys": [["sttm-1"], ["vic-1"], ["gbb-1", "gbb-2"]],
                "source_files": [
                    ["sttm.csv"],
                    ["vicgas.csv"],
                    ["gbb.csv", "gbb-extra.csv"],
                ],
                "ingested_timestamp": [
                    datetime(2024, 1, 1, 8),
                    datetime(2024, 1, 1, 10),
                    datetime(2024, 1, 1, 9),
                ],
            }
        ),
    )

    coverage = hub_zone_dimension_coverage_frame(load)
    sources = hub_zone_source_system_frame(load)
    preview = hub_zone_identifier_preview_frame(load)
    coverage_values = {row["metric"]: row["value"] for row in coverage.to_dicts()}
    source_rows = {row["source system"]: row for row in sources.to_dicts()}

    assert coverage_values == {
        "Zone dimension rows": "3",
        "Source systems": "3",
        "Source tables": "3",
        "Zone types": "3",
        "STTM hubs": "1",
        "DWGM/GBB zone rows": "2",
        "Source-qualified identifiers": "3",
        "Source files": "4",
    }
    assert source_rows["GBB"]["source zone ids"] == 1
    assert source_rows["GBB"]["source files"] == 2
    assert source_rows["STTM"]["zone types"] == 1
    assert source_rows["VICGAS"]["source tables"] == 1
    assert preview.select(
        "source-qualified identifier",
        "source system",
        "zone type",
        "source zone id",
        "zone name",
        "source tables",
        "source files",
    ).to_dict(as_series=False) == {
        "source-qualified identifier": [
            "GBB:demand_zone:DZ1",
            "STTM:sttm_hub:SYD",
            "VICGAS:linepack_zone:5",
        ],
        "source system": ["GBB", "STTM", "VICGAS"],
        "zone type": ["demand_zone", "sttm_hub", "linepack_zone"],
        "source zone id": ["DZ1", "SYD", "5"],
        "zone name": ["Demand Zone 1", "Sydney Hub", "Linepack 5"],
        "source tables": [
            "silver.gbb.silver_gasbb_demand_zones_and_pipeline_connectionpoint_mapping",
            "silver.sttm.silver_int671_v1_hub_facility_definition_rpt_1",
            "silver.vicgas.silver_int259_v4_pipe_segment_1",
        ],
        "source files": ["gbb.csv, gbb-extra.csv", "sttm.csv", "vicgas.csv"],
    }


def test_hub_zone_helpers_fill_missing_columns_and_partial_identifiers() -> None:
    load = _facility_load(
        HUB_ZONE_TABLE_SPECS[0],
        pl.DataFrame(
            {
                "source_system": ["STTM", "STTM"],
                "zone_type": ["sttm_hub", "sttm_hub"],
                "source_zone_id": ["", "SYD"],
                "ingested_timestamp": [None, None],
            }
        ),
    )

    coverage = hub_zone_dimension_coverage_frame(load)
    sources = hub_zone_source_system_frame(load)
    preview = hub_zone_identifier_preview_frame(load)
    coverage_values = {row["metric"]: row["value"] for row in coverage.to_dicts()}

    assert coverage_values["Source tables"] == "0"
    assert coverage_values["Source files"] == "0"
    assert coverage_values["Source-qualified identifiers"] == "1"
    assert sources.to_dicts() == [
        {
            "source system": "STTM",
            "rows": 2,
            "zone types": 1,
            "source zone ids": 1,
            "source tables": 0,
            "source files": 0,
            "latest ingest": None,
        }
    ]
    assert preview.select(
        "source-qualified identifier",
        "source system",
        "zone type",
        "source zone id",
    ).to_dict(as_series=False) == {
        "source-qualified identifier": ["", "STTM:sttm_hub:SYD"],
        "source system": ["STTM", "STTM"],
        "zone type": ["sttm_hub", "sttm_hub"],
        "source zone id": ["", "SYD"],
    }


def test_hub_zone_helpers_cover_empty_state_behavior() -> None:
    unavailable_load = _facility_load(
        HUB_ZONE_TABLE_SPECS[0],
        None,
        error="FileNotFoundError: no parquet files found",
        row_limit=4,
    )
    empty_load = _facility_load(
        HUB_ZONE_TABLE_SPECS[0],
        pl.DataFrame(),
        row_limit=4,
    )

    assert hub_zone_dimension_coverage_frame(unavailable_load).is_empty()
    assert hub_zone_source_system_frame(unavailable_load).is_empty()
    assert hub_zone_identifier_preview_frame(unavailable_load).is_empty()

    unavailable_markdown = hub_zone_context_empty_state_markdown((unavailable_load,))
    empty_markdown = hub_zone_context_empty_state_markdown((empty_load,))
    no_table_markdown = hub_zone_context_empty_state_markdown(())
    empty_context_links = render_hub_zone_context_links(entries=())

    assert "No Hub / Zone metadata rows are available" in unavailable_markdown
    assert "`1` reads were unavailable and `0` reads returned no rows" in (
        unavailable_markdown
    )
    assert "Bounded preview reads are capped at `4` rows per table" in (
        unavailable_markdown
    )
    assert "`0` reads were unavailable and `1` reads returned no rows" in empty_markdown
    assert "No Hub / Zone context tables were requested" in no_table_markdown
    assert (
        "No Hub / Zone, Facility, flow, capacity, schedule, bid, or table "
        "explorer entries are registered."
    ) in empty_context_links


def test_gas_day_context_metadata_is_available_dashboard() -> None:
    entry = registry_entry_by_concept_id(GAS_DAY_CONTEXT_ID)
    html = render_dashboard_context_panel(GAS_DAY_CONTEXT_ID)

    assert entry is not None
    assert entry.status is DashboardStatus.AVAILABLE
    assert entry.notebook_name == "gas_day_explainer"
    assert entry.notebook_route == "/marimo/gas_day_explainer/"
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/gas-day.md"
        in entry.generated_gold_paths
    )
    assert entry.source_chunk_ids == ("chunk-gbb-guide-gas-day",)
    assert "Gas Day Context" in html
    assert "tools/gas-market-knowledge-base/generated/gold/glossary/gas-day.md" in html
    assert "chunk-gbb-guide-gas-day" in html
    assert 'data-status="available"' in html


def test_gas_day_table_specs_use_current_registry_assets_and_known_dates() -> None:
    specs = gas_day_table_specs()
    specs_by_table = {spec.table_name: spec for spec in specs}

    assert "silver_gas_dim_date" in specs_by_table
    assert specs_by_table["silver_gas_fact_schedule_run"].date_columns == (
        "gas_date",
        "gas_start_timestamp",
        "bid_cutoff_timestamp",
        "creation_timestamp",
        "approval_timestamp",
        "source_last_updated_timestamp",
        "ingested_timestamp",
    )
    assert specs_by_table["silver_gas_fact_capacity_outlook"].date_columns == (
        "from_gas_date",
        "to_gas_date",
    )
    assert specs_by_table["silver_gas_fact_customer_transfer"].date_columns == (
        "gas_date",
        "ingested_timestamp",
    )


def test_gas_day_loaders_force_bounded_samples_and_cache_reads() -> None:
    config = _dashboard_config()
    specs = (
        GasTableSpec(
            section="Facts",
            label="Schedule runs",
            table_name="silver_gas_fact_schedule_run",
            date_columns=("gas_date",),
        ),
    )
    captured: list[int | None] = []
    calls: list[int] = []
    cache: GasModelSessionCache = {}

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        assert uri == (
            "s3://dev-energy-market-aemo/silver/gas_model/silver_gas_fact_schedule_run"
        )
        assert storage_options == config.storage_options()
        captured.append(row_limit)
        calls.append(len(calls) + 1)
        return pl.DataFrame(
            {
                "gas_date": [date(2024, 1, calls[-1])],
                "source_system": ["STTM"],
            }
        )

    direct = load_gas_day_tables(config, specs=specs, reader=reader)
    first_cached = cached_load_gas_day_tables(config, cache, specs=specs, reader=reader)
    second_cached = cached_load_gas_day_tables(
        config, cache, specs=specs, reader=reader
    )
    refreshed = cached_load_gas_day_tables(
        config,
        cache,
        specs=specs,
        reader=reader,
        refresh_token=1,
    )

    assert captured == [100, 100, 100]
    assert calls == [1, 2, 3]
    assert direct[0].row_limit == 100
    assert not first_cached[0].cache_hit
    assert second_cached[0].cache_hit
    assert not refreshed[0].cache_hit
    assert second_cached[0].dataframe is not None
    assert second_cached[0].dataframe["gas_date"].to_list() == [date(2024, 1, 2)]
    assert refreshed[0].dataframe is not None
    assert refreshed[0].dataframe["gas_date"].to_list() == [date(2024, 1, 3)]


def test_gas_day_field_discovery_finds_gas_date_and_date_fields() -> None:
    schedule_load = _source_coverage_load(
        "silver_gas_fact_schedule_run",
        pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 2), date(2024, 1, 3)],
                "gas_start_timestamp": [
                    datetime(2024, 1, 2, 6),
                    datetime(2024, 1, 3, 6),
                ],
                "source_system": ["STTM", "STTM"],
                "source_table": ["silver.sttm.schedule", "silver.sttm.schedule"],
            }
        ),
    )
    capacity_load = GasTableLoad(
        spec=GasTableSpec(
            section="Facts",
            label="Capacity outlook",
            table_name="silver_gas_fact_capacity_outlook",
            date_columns=("from_gas_date", "to_gas_date"),
        ),
        uri="s3://bucket/silver/gas_model/silver_gas_fact_capacity_outlook",
        dataframe=pl.DataFrame(
            {
                "from_gas_date": [date(2024, 2, 1)],
                "to_gas_date": [date(2024, 2, 3)],
                "source_table": ["silver.gbb.capacity"],
            }
        ),
        error=None,
        row_limit=100,
        load_duration_seconds=0.01,
        cache_hit=False,
    )
    unavailable_load = GasTableLoad(
        spec=CUSTOMER_TRANSFER_TABLE_SPEC,
        uri="s3://bucket/silver/gas_model/silver_gas_fact_customer_transfer",
        dataframe=None,
        error="FileNotFoundError: no parquet files found",
        row_limit=100,
        load_duration_seconds=0.01,
        cache_hit=False,
    )

    discovery = gas_day_field_discovery_frame(
        (schedule_load, capacity_load, unavailable_load)
    )
    rows = {
        (row["table"], row["field"]): row
        for row in discovery.to_dicts()
        if row["field"]
    }

    assert rows[("silver_gas_fact_schedule_run", "gas_date")] == {
        "asset": "silver.gas_model.silver_gas_fact_schedule_run",
        "section": "Facts",
        "table": "silver_gas_fact_schedule_run",
        "field": "gas_date",
        "field role": "Gas Day field",
        "dtype": "Date",
        "status": "Discovered",
        "rows loaded": 2,
        "populated values": 2,
        "first value": "2024-01-02",
        "latest value": "2024-01-03",
        "row limit": "Bounded preview: 100 rows max",
        "table explorer": (
            "/marimo/table_explorer/?search=silver_gas_fact_schedule_run"
        ),
        "uri": "s3://bucket/silver/gas_model/silver_gas_fact_schedule_run",
        "detail": "Field is present in the bounded table read.",
    }
    assert (
        rows[("silver_gas_fact_schedule_run", "gas_start_timestamp")]["field role"]
        == "Timestamp field"
    )
    assert (
        rows[("silver_gas_fact_capacity_outlook", "from_gas_date")]["field role"]
        == "Gas Day field"
    )
    assert rows[("silver_gas_fact_customer_transfer", "gas_date")]["status"] == (
        "Unavailable"
    )
    assert (
        "FileNotFoundError: no parquet files found"
        in rows[("silver_gas_fact_customer_transfer", "gas_date")]["detail"]
    )


def test_gas_day_field_discovery_handles_empty_declared_and_missing_fields() -> None:
    missing_load = _source_coverage_load(
        "silver_gas_fact_fieldless",
        pl.DataFrame({"source_system": ["GBB"]}),
    )
    empty_fieldless_load = _source_coverage_load(
        "silver_gas_fact_empty_fieldless",
        pl.DataFrame(),
    )
    date_field_load = _source_coverage_load(
        "silver_gas_fact_report_dates",
        pl.DataFrame({"report_date": [date(2024, 1, 4)]}),
    )
    empty_declared_load = GasTableLoad(
        spec=GasTableSpec(
            section="Facts",
            label="Declared empty",
            table_name="silver_gas_fact_declared_empty",
            date_columns=("date_key",),
        ),
        uri="s3://bucket/silver/gas_model/silver_gas_fact_declared_empty",
        dataframe=pl.DataFrame(schema={"source_system": pl.String}),
        error=None,
        row_limit=100,
        load_duration_seconds=0.01,
        cache_hit=False,
    )
    declared_only_load = GasTableLoad(
        spec=GasTableSpec(
            section="Facts",
            label="Declared only",
            table_name="silver_gas_fact_declared_only",
            date_columns=("delivery_gas_date",),
        ),
        uri="s3://bucket/silver/gas_model/silver_gas_fact_declared_only",
        dataframe=pl.DataFrame({"source_system": ["STTM"]}),
        error=None,
        row_limit=100,
        load_duration_seconds=0.01,
        cache_hit=False,
    )
    empty_value_load = _source_coverage_load(
        "silver_gas_fact_empty_values",
        pl.DataFrame({"gas_date": [None]}, schema={"gas_date": pl.Date}),
    )
    unavailable_fieldless_load = _source_coverage_load(
        "silver_gas_fact_missing_prefix",
        None,
        error="FileNotFoundError: no parquet files found",
    )

    empty_discovery = gas_day_field_discovery_frame(())
    discovery = gas_day_field_discovery_frame(
        (
            missing_load,
            empty_fieldless_load,
            date_field_load,
            empty_declared_load,
            declared_only_load,
            empty_value_load,
            unavailable_fieldless_load,
        )
    )
    rows = {(row["table"], row["field role"]): row for row in discovery.to_dicts()}

    assert empty_discovery.is_empty()
    assert rows[("silver_gas_fact_fieldless", "No date field found")]["status"] == (
        "Loaded"
    )
    assert (
        rows[("silver_gas_fact_empty_fieldless", "No date field found")]["status"]
        == "Empty"
    )
    assert rows[("silver_gas_fact_report_dates", "Date field")]["field"] == (
        "report_date"
    )
    assert rows[("silver_gas_fact_declared_empty", "Date key")]["status"] == "Empty"
    assert rows[("silver_gas_fact_declared_empty", "Date key")]["detail"] == (
        "The table read returned no rows; field presence came from metadata."
    )
    assert rows[("silver_gas_fact_declared_only", "Gas Day field")]["status"] == (
        "Declared only"
    )
    assert rows[("silver_gas_fact_declared_only", "Gas Day field")]["detail"] == (
        "delivery_gas_date is declared for this dashboard but absent from loaded rows."
    )
    assert rows[("silver_gas_fact_empty_values", "Gas Day field")]["first value"] == ""
    assert rows[("silver_gas_fact_empty_values", "Gas Day field")]["latest value"] == ""
    assert (
        rows[("silver_gas_fact_missing_prefix", "No date field found")]["status"]
        == "Unavailable"
    )


def test_gas_day_bounded_examples_and_kpis_use_loaded_rows() -> None:
    load = _source_coverage_load(
        "silver_gas_fact_schedule_run",
        pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 2), date(2024, 1, 3)],
                "source_system": ["STTM", "VICGAS"],
                "source_table": ["silver.sttm.schedule", "silver.vicgas.schedule"],
                "schedule_type_id": ["ex_ante", "pricing"],
                "transmission_id": ["S-1", "V-1"],
                "ingested_timestamp": [
                    datetime(2024, 1, 2, 8),
                    datetime(2024, 1, 3, 8),
                ],
            }
        ),
    )

    examples = gas_day_bounded_examples_frame((load,), examples_per_field=1)
    discovery = gas_day_field_discovery_frame((load,))
    kpis = gas_day_kpi_frame((load,), discovery, examples)
    kpi_rows = {row["metric"]: row for row in kpis.to_dicts()}

    assert examples.select(
        "table",
        "field",
        "field role",
        "value",
        "source system",
        "source table",
        "context",
    ).to_dict(as_series=False) == {
        "table": ["silver_gas_fact_schedule_run"],
        "field": ["gas_date"],
        "field role": ["Gas Day field"],
        "value": ["2024-01-03"],
        "source system": ["VICGAS"],
        "source table": ["silver.vicgas.schedule"],
        "context": [
            (
                "schedule_type_id=pricing; transmission_id=V-1; "
                "ingested_timestamp=2024-01-03 08:00:00"
            )
        ],
    }
    assert kpi_rows["Gas Day fields"]["value"] == "1"
    assert kpi_rows["Date fields with values"]["value"] == "2"
    assert kpi_rows["Bounded examples"]["value"] == "1"
    assert kpi_rows["Latest Gas Day"]["value"] == "2024-01-03"


def test_gas_day_examples_fall_back_to_date_fields_and_source_tables() -> None:
    timestamp_load = _source_coverage_load(
        "silver_gas_fact_timestamps",
        pl.DataFrame(
            {
                "ingested_timestamp": [
                    datetime(2024, 1, 2, 8),
                    datetime(2024, 1, 3, 8),
                ],
                "source_tables": [
                    ["silver.gbb.old", "silver.gbb.extra"],
                    ["silver.gbb.latest"],
                ],
                "quality_type": ["old", "latest"],
            }
        ),
    )
    missing_declared_load = GasTableLoad(
        spec=GasTableSpec(
            section="Facts",
            label="Missing declared field",
            table_name="silver_gas_fact_missing_declared",
            date_columns=("gas_date",),
        ),
        uri="s3://bucket/silver/gas_model/silver_gas_fact_missing_declared",
        dataframe=pl.DataFrame({"source_system": ["STTM"]}),
        error=None,
        row_limit=100,
        load_duration_seconds=0.01,
        cache_hit=False,
    )

    examples = gas_day_bounded_examples_frame(
        (timestamp_load, missing_declared_load),
        examples_per_field=1,
    )
    empty_kpis = gas_day_kpi_frame(
        (),
        gas_day_field_discovery_frame(()),
        gas_day_bounded_examples_frame(()),
    )

    assert examples.select(
        "table",
        "field",
        "field role",
        "value",
        "source table",
        "context",
    ).to_dict(as_series=False) == {
        "table": ["silver_gas_fact_timestamps"],
        "field": ["ingested_timestamp"],
        "field role": ["Timestamp field"],
        "value": ["2024-01-03 08:00:00"],
        "source table": ["silver.gbb.latest"],
        "context": ["quality_type=latest"],
    }
    assert empty_kpis.row(5, named=True) == {
        "metric": "Latest Gas Day",
        "value": "unknown",
        "detail": "Maximum loaded value across populated Gas Day fields",
    }


def test_gas_day_examples_empty_state_covers_absent_data() -> None:
    unavailable_load = _source_coverage_load(
        "silver_gas_fact_schedule_run",
        None,
        error="FileNotFoundError: no parquet files found",
    )
    empty_load = _source_coverage_load(
        "silver_gas_fact_customer_transfer",
        pl.DataFrame(schema={"gas_date": pl.Date}),
    )

    examples = gas_day_bounded_examples_frame((unavailable_load, empty_load))
    markdown = gas_day_examples_empty_state_markdown((unavailable_load, empty_load))

    assert examples.is_empty()
    assert "No Gas Day tables were requested" in gas_day_examples_empty_state_markdown(
        ()
    )
    assert "No bounded Gas Day examples are available" in markdown
    assert "`1` reads were unavailable and `1` reads returned" in markdown
    assert "no rows or no populated date fields" in markdown
    assert "Bounded preview reads are capped at `100` rows per table" in markdown


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


def test_source_lineage_explorer_extracts_lineage_fields_and_registry_links() -> None:
    table_name = "silver_gas_fact_market_price"
    load = _source_coverage_load(
        table_name,
        pl.DataFrame(
            {
                "source_system": ["STTM", "STTM", "VICGAS"],
                "source_table": [
                    "silver.sttm.price_report",
                    "silver.sttm.price_report",
                    "silver.vicgas.price_report",
                ],
                "source_file": ["price-a.csv", "price-b.csv", "vicgas.csv"],
                "source_surrogate_key": ["src-1", "src-2", "src-vic"],
                "source_last_updated_timestamp": [
                    datetime(2024, 1, 1),
                    datetime(2024, 1, 2),
                    datetime(2024, 1, 3),
                ],
            }
        ),
    )
    entry = DashboardRegistryEntry(
        concept_id="custom-lineage-context",
        title="Custom Lineage",
        description="Custom lineage mapping.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.AVAILABLE,
        notebook_name="custom_lineage",
        backing_assets=(f"silver.gas_model.{table_name}",),
        generated_gold_paths=(
            "tools/gas-market-knowledge-base/generated/gold/glossary/schedule.md",
        ),
        source_chunks=(SourceChunkReference("chunk-custom-lineage"),),
    )

    lineage = source_lineage_frame((load,), entries=(entry,))
    rows = {
        row["source system"]: row for row in lineage.sort("source system").to_dicts()
    }
    sttm_row = rows["STTM"]
    kpis = source_lineage_kpi_frame((load,), lineage)
    values = {row["metric"]: row["value"] for row in kpis.to_dicts()}

    assert sttm_row["source table"] == "silver.sttm.price_report"
    assert sttm_row["coverage state"] == SOURCE_COVERAGE_STATE_COVERED
    assert sttm_row["rows loaded"] == 2
    assert sttm_row["lineage fields"] == (
        "source_file, source_surrogate_key, source_last_updated_timestamp"
    )
    assert "source_file: price-a.csv, price-b.csv" in sttm_row["lineage examples"]
    assert "source_surrogate_key: src-1, src-2" in sttm_row["lineage examples"]
    assert sttm_row["concept cards"] == (
        "Custom Lineage -> /marimo#concept-custom-lineage-context"
    )
    assert sttm_row["dashboard routes"] == ("Custom Lineage -> /marimo/custom_lineage/")
    assert sttm_row["Market context paths"] == (
        "tools/gas-market-knowledge-base/generated/gold/glossary/schedule.md"
    )
    assert sttm_row["source chunk ids"] == "chunk-custom-lineage"
    assert values["Source systems"] == "2"
    assert values["Source tables"] == "2"
    assert values["Registry mapped assets"] == "1"
    assert values["Lineage field groups"] == "1"


def test_source_lineage_explorer_handles_list_fields_and_missing_metadata() -> None:
    list_load = _source_coverage_load(
        "silver_gas_dim_zone",
        pl.DataFrame(
            {
                "source_systems": [["GBB"]],
                "source_tables": [["silver.gbb.zone_report"]],
                "source_surrogate_keys": [["gbb-zone-1", "gbb-zone-2"]],
            }
        ),
    )
    missing_load = _source_coverage_load(
        "silver_gas_dim_date",
        pl.DataFrame({"date_id": [20240101]}),
    )
    empty_value_load = _source_coverage_load(
        "silver_gas_fact_schedule_run",
        pl.DataFrame({"source_system": [""], "source_table": [None]}),
    )
    empty_read_load = _source_coverage_load(
        "silver_gas_fact_linepack",
        pl.DataFrame(),
    )
    unavailable_load = _source_coverage_load(
        "silver_gas_fact_capacity_outlook",
        None,
        error="RuntimeError: missing parquet",
    )

    lineage = source_lineage_frame(
        (
            list_load,
            missing_load,
            empty_value_load,
            empty_read_load,
            unavailable_load,
        ),
        entries=(),
    )
    rows = {
        row["table"]: row
        for row in lineage.select(
            "table",
            "source system",
            "source table",
            "coverage state",
            "source fields",
            "lineage fields",
            "lineage examples",
            "concept cards",
            "detail",
        ).to_dicts()
    }
    empty_markdown = source_lineage_empty_state_markdown((unavailable_load,))

    assert rows["silver_gas_dim_zone"]["source system"] == "GBB"
    assert rows["silver_gas_dim_zone"]["source table"] == "silver.gbb.zone_report"
    assert rows["silver_gas_dim_zone"]["coverage state"] == (
        SOURCE_COVERAGE_STATE_COVERED
    )
    assert rows["silver_gas_dim_zone"]["source fields"] == (
        "source_systems, source_tables, source_surrogate_keys"
    )
    assert rows["silver_gas_dim_zone"]["lineage examples"] == (
        "source_surrogate_keys: gbb-zone-1, gbb-zone-2"
    )
    assert rows["silver_gas_dim_date"]["source system"] == (
        "(missing source_system/source_systems column)"
    )
    assert rows["silver_gas_dim_date"]["source table"] == (
        "(missing source_table/source_tables column)"
    )
    assert rows["silver_gas_dim_date"]["coverage state"] == SOURCE_COVERAGE_STATE_GAP
    assert rows["silver_gas_dim_date"]["lineage fields"] == (
        "(no additional source lineage fields)"
    )
    assert rows["silver_gas_dim_date"]["concept cards"] == "(no mapped concept card)"
    assert (
        "Missing source_system/source_systems columns"
        in (rows["silver_gas_dim_date"]["detail"])
    )
    assert rows["silver_gas_fact_schedule_run"]["source system"] == (
        "(empty source_system/source_systems value)"
    )
    assert rows["silver_gas_fact_schedule_run"]["source table"] == (
        "(empty source_table/source_tables value)"
    )
    assert rows["silver_gas_fact_linepack"]["coverage state"] == (
        SOURCE_COVERAGE_STATE_EMPTY
    )
    assert rows["silver_gas_fact_linepack"]["detail"] == (
        "The table read succeeded but returned no rows."
    )
    assert rows["silver_gas_fact_capacity_outlook"]["coverage state"] == (
        SOURCE_COVERAGE_STATE_UNAVAILABLE
    )
    assert "1` reads were unavailable" in empty_markdown


def test_render_source_lineage_explorer_html_links_and_escapes_values() -> None:
    table_name = "silver_gas_fact_market_price"
    load = _source_coverage_load(
        table_name,
        pl.DataFrame(
            {
                "source_system": ["STTM"],
                "source_table": ["silver.sttm.price_report"],
                "source_file": ["price.csv"],
            }
        ),
    )
    entry = DashboardRegistryEntry(
        concept_id="custom-lineage-context",
        title="Custom Lineage",
        description="Custom lineage mapping.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.AVAILABLE,
        notebook_name="custom_lineage",
        backing_assets=(f"silver.gas_model.{table_name}",),
        generated_gold_paths=(
            "tools/gas-market-knowledge-base/generated/gold/glossary/schedule.md",
        ),
        source_chunks=(SourceChunkReference("chunk-custom-lineage"),),
    )

    lineage = source_lineage_frame((load,), entries=(entry,))
    html = render_source_lineage_explorer_html(lineage)
    unsafe_html = render_source_lineage_explorer_html(
        pl.DataFrame(
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
                    "lineage fields": "source_file",
                    "lineage examples": "source_file: 1 < 2.csv",
                    "concept cards": "Unsafe -> javascript:alert(1)",
                    "dashboard routes": "Unsafe -> javascript:alert(1)",
                    "Market context paths": "tools/<unsafe>.md",
                    "source chunk ids": "chunk-unsafe",
                    "table explorer": "javascript:alert(1)",
                    "asset metadata": "",
                    "uri": "s3://bucket/<unsafe>",
                    "detail": "1 < 2",
                }
            ]
        )
    )

    assert 'data-link-target="concept-card"' in html
    assert 'href="/marimo#concept-custom-lineage-context"' in html
    assert 'data-link-target="dashboard-route"' in html
    assert 'href="/marimo/custom_lineage/"' in html
    assert 'data-link-target="table-explorer"' in html
    assert (
        'data-market-context-path="tools/gas-market-knowledge-base/generated/gold/'
        'glossary/schedule.md"'
    ) in html
    assert "<button" not in html.lower()
    assert "&lt;unsafe&gt;" in unsafe_html
    assert "1 &lt; 2" in unsafe_html
    assert "javascript:alert" not in unsafe_html


def test_source_lineage_explorer_empty_and_overflow_states() -> None:
    empty_lineage = source_lineage_frame(())
    empty_kpis = source_lineage_kpi_frame((), empty_lineage)
    empty_markdown = source_lineage_empty_state_markdown(())
    empty_html = render_source_lineage_explorer_html(empty_lineage)
    overflow_html = render_source_lineage_explorer_html(
        pl.DataFrame(
            [
                {
                    "asset": "silver.gas_model.first",
                    "section": "Facts",
                    "table": "first",
                    "source system": "GBB",
                    "source table": "silver.gbb.first",
                    "coverage state": SOURCE_COVERAGE_STATE_COVERED,
                    "rows loaded": 1234,
                    "row limit": "100 rows",
                    "source fields": "source_system, source_table",
                    "lineage fields": "source_file",
                    "lineage examples": "source_file: first.csv",
                    "concept cards": "/marimo#concept-first",
                    "dashboard routes": "/marimo/first/",
                    "Market context paths": None,
                    "source chunk ids": "chunk-first",
                    "table explorer": None,
                    "asset metadata": None,
                    "uri": "",
                    "detail": None,
                },
                {
                    "asset": "silver.gas_model.second",
                    "section": "Facts",
                    "table": "second",
                    "source system": "STTM",
                    "source table": "silver.sttm.second",
                    "coverage state": SOURCE_COVERAGE_STATE_COVERED,
                    "rows loaded": 1,
                    "row limit": "100 rows",
                    "source fields": "source_system, source_table",
                    "lineage fields": "source_file",
                    "lineage examples": "source_file: second.csv",
                    "concept cards": "/marimo#concept-second",
                    "dashboard routes": "/marimo/second/",
                    "Market context paths": "tools/gold.md",
                    "source chunk ids": "chunk-second",
                    "table explorer": "/marimo/table_explorer/?search=second",
                    "asset metadata": "",
                    "uri": "s3://bucket/silver/gas_model/second",
                    "detail": "Covered",
                },
            ]
        ),
        max_rows=1,
    )
    kpi_values = {row["metric"]: row["value"] for row in empty_kpis.to_dicts()}

    assert empty_lineage.is_empty()
    assert "No source lineage tables were requested" in empty_markdown
    assert "No source lineage rows match the current filters." in empty_html
    assert kpi_values["Requested assets"] == "0"
    assert kpi_values["Source systems"] == "0"
    assert 'data-row-count="2"' in overflow_html
    assert 'data-rendered-row-count="1"' in overflow_html
    assert "1 additional rows are hidden by the dashboard display limit." in (
        overflow_html
    )
    assert ">1,234</td>" in overflow_html
    assert 'href="/marimo#concept-first"' in overflow_html
    assert "source_file: second.csv" not in overflow_html


def test_source_lineage_examples_limit_duplicates_and_empty_values() -> None:
    repeated_load = _source_coverage_load(
        "silver_gas_fact_market_price",
        pl.DataFrame(
            {
                "source_system": ["GBB"] * 5,
                "source_table": ["silver.gbb.price_report"] * 5,
                "source_file": [
                    "same.csv",
                    "same.csv",
                    "two.csv",
                    "three.csv",
                    "four.csv",
                ],
                "source_empty_field": [None] * 5,
            }
        ),
    )
    empty_lineage_value_load = _source_coverage_load(
        "silver_gas_fact_schedule_run",
        pl.DataFrame(
            {
                "source_system": ["STTM"],
                "source_table": [float("nan")],
                "source_file": [float("nan")],
            }
        ),
    )

    lineage = source_lineage_frame(
        (repeated_load, empty_lineage_value_load),
        entries=(),
    )
    rows = {row["table"]: row for row in lineage.to_dicts()}

    assert rows["silver_gas_fact_market_price"]["lineage examples"] == (
        "source_file: same.csv, two.csv, three.csv"
    )
    assert "four.csv" not in rows["silver_gas_fact_market_price"]["lineage examples"]
    assert rows["silver_gas_fact_schedule_run"]["source table"] == (
        "(empty source_table/source_tables value)"
    )
    assert rows["silver_gas_fact_schedule_run"]["coverage state"] == (
        SOURCE_COVERAGE_STATE_GAP
    )
    assert rows["silver_gas_fact_schedule_run"]["lineage examples"] == (
        "(no populated source lineage values)"
    )
    assert (
        "source_table/source_tables columns are present but empty"
        in (rows["silver_gas_fact_schedule_run"]["detail"])
    )


def test_source_lineage_explorer_uses_catalogue_link_contexts() -> None:
    asset_table = "silver_gas_fact_market_price"
    storage_table = "silver_gas_fact_schedule_run"
    dotted_table = "silver_gas_fact_capacity_outlook"
    loads = (
        _source_coverage_load(
            asset_table,
            pl.DataFrame(
                {
                    "source_system": ["STTM"],
                    "source_table": ["silver.sttm.price_report"],
                }
            ),
        ),
        _source_coverage_load(
            storage_table,
            pl.DataFrame(
                {
                    "source_system": ["STTM"],
                    "source_table": ["silver.sttm.schedule_report"],
                }
            ),
        ),
        _source_coverage_load(
            dotted_table,
            pl.DataFrame(
                {
                    "source_system": ["GBB"],
                    "source_table": ["silver.gbb.capacity_report"],
                }
            ),
        ),
    )
    asset_row = CataloguedTable(
        entry_id=f"asset:silver/gas_model/{asset_table}",
        status=TableAvailability.LIVE,
        asset=DagsterTableAsset(
            asset_key=("silver", "gas_model", asset_table),
            group_name="gas_model",
            kinds=("python", "parquet"),
            description=None,
            uri=f"s3://bucket/silver/gas_model/{asset_table}",
            columns=(),
            is_materializable=True,
            is_executable=True,
            latest_materialization_timestamp=None,
        ),
        table=None,
    )
    duplicate_asset_row = CataloguedTable(
        entry_id=f"asset:silver/gas_model/{asset_table}",
        status=TableAvailability.LIVE,
        asset=None,
        table=TablePrefix(
            bucket="bucket",
            prefix=f"silver/gas_model/{asset_table}",
            table_format=TableFormat.PARQUET,
            parquet_files=(f"silver/gas_model/{asset_table}/part-000.parquet",),
        ),
    )
    storage_row = CataloguedTable(
        entry_id=f"storage:bucket/silver/gas_model/{storage_table}",
        status=TableAvailability.LIVE,
        asset=None,
        table=TablePrefix(
            bucket="bucket",
            prefix=f"silver/gas_model/{storage_table}",
            table_format=TableFormat.PARQUET,
            parquet_files=(f"silver/gas_model/{storage_table}/part-000.parquet",),
        ),
    )
    dotted_row = SimpleNamespace(
        entry_id=123,
        asset=None,
        table=None,
        uri=f"silver.gas_model.{dotted_table}",
    )
    ignored_rows = (
        SimpleNamespace(uri=123),
        SimpleNamespace(uri="s3://bucket/bronze/raw"),
        SimpleNamespace(uri="s3://bucket/silver/gas_model/"),
    )

    lineage = source_lineage_frame(
        loads,
        (*ignored_rows, asset_row, duplicate_asset_row, storage_row, dotted_row),
        entries=(),
    )
    rows = {row["table"]: row for row in lineage.to_dicts()}

    assert rows[asset_table]["table explorer"] == (
        "/marimo/table_explorer/?table=asset%3Asilver%2Fgas_model%2F"
        "silver_gas_fact_market_price"
    )
    assert rows[asset_table]["asset metadata"] == (
        "/marimo/table_explorer/?asset=asset%3Asilver%2Fgas_model%2F"
        "silver_gas_fact_market_price"
    )
    assert rows[asset_table]["uri"] == (
        "s3://bucket/silver/gas_model/silver_gas_fact_market_price"
    )
    assert rows[storage_table]["table explorer"] == (
        "/marimo/table_explorer/?table=storage%3Abucket%2Fsilver%2Fgas_model"
        "%2Fsilver_gas_fact_schedule_run"
    )
    assert rows[storage_table]["asset metadata"] == ""
    assert rows[dotted_table]["table explorer"] == "/marimo/table_explorer/"
    assert rows[dotted_table]["uri"] == f"silver.gas_model.{dotted_table}"


def test_render_dashboard_context_panel_covers_complete_concept() -> None:
    html = render_dashboard_context_panel("gas-market-overview")
    no_related_html = render_dashboard_context_panel(
        "gas-market-overview",
        related_limit=0,
    )

    assert "Gas Market Overview" in html
    assert "generated-gold paths" in html
    assert "source chunk IDs" in html
    assert "silver chunk paths" in html
    assert "source hashes" in html
    assert "backing assets" in html
    assert "tools/gas-market-knowledge-base/generated/gold/glossary/gas-day.md" in html
    assert "chunk-gbb-guide-gas-day" in html
    assert "chunk-gbb-guide-gas-day.md" in html
    assert "9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410" in html
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
    assert "No silver chunk paths recorded in the Marimo registry." in html
    assert "No source hashes recorded in the Marimo registry." in html
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


def _participant_load(
    spec: GasTableSpec,
    dataframe: pl.DataFrame | None,
    *,
    error: str | None = None,
    row_limit: int | None = 100,
) -> GasTableLoad:
    return GasTableLoad(
        spec=spec,
        uri=f"s3://bucket/silver/gas_model/{spec.table_name}",
        dataframe=dataframe,
        error=error,
        row_limit=row_limit,
        load_duration_seconds=0.01,
        cache_hit=False,
    )


def _facility_load(
    spec: GasTableSpec,
    dataframe: pl.DataFrame | None,
    *,
    error: str | None = None,
    row_limit: int | None = 100,
) -> GasTableLoad:
    return GasTableLoad(
        spec=spec,
        uri=f"s3://bucket/silver/gas_model/{spec.table_name}",
        dataframe=dataframe,
        error=error,
        row_limit=row_limit,
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


def _heating_value_load(
    dataframe: pl.DataFrame,
    *,
    row_limit: int | None = 100,
) -> GasTableLoad:
    return GasTableLoad(
        spec=HEATING_VALUE_TABLE_SPEC,
        uri=f"s3://bucket/silver/gas_model/{HEATING_VALUE_TABLE_NAME}",
        dataframe=dataframe,
        error=None,
        row_limit=row_limit,
        load_duration_seconds=0.01,
        cache_hit=False,
    )


def _scada_pressure_load(
    dataframe: pl.DataFrame,
    *,
    row_limit: int | None = 100,
) -> GasTableLoad:
    return GasTableLoad(
        spec=SCADA_PRESSURE_TABLE_SPEC,
        uri=f"s3://bucket/silver/gas_model/{SCADA_PRESSURE_TABLE_NAME}",
        dataframe=dataframe,
        error=None,
        row_limit=row_limit,
        load_duration_seconds=0.01,
        cache_hit=False,
    )


def _heating_value_pressure_loads(
    *,
    heating_dataframe: pl.DataFrame,
    pressure_dataframe: pl.DataFrame,
    row_limit: int | None = 100,
) -> list[GasTableLoad]:
    return [
        _heating_value_load(heating_dataframe, row_limit=row_limit),
        _scada_pressure_load(pressure_dataframe, row_limit=row_limit),
    ]


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


def _facility_flow_storage_load(
    dataframe: pl.DataFrame,
    *,
    row_limit: int | None = None,
) -> GasTableLoad:
    return GasTableLoad(
        spec=FACILITY_FLOW_STORAGE_TABLE_SPEC,
        uri=f"s3://bucket/silver/gas_model/{FACILITY_FLOW_STORAGE_TABLE_NAME}",
        dataframe=dataframe,
        error=None,
        row_limit=row_limit,
        load_duration_seconds=0.01,
        cache_hit=False,
    )


def _linepack_load(
    dataframe: pl.DataFrame,
    *,
    row_limit: int | None = None,
) -> GasTableLoad:
    return GasTableLoad(
        spec=LINEPACK_TABLE_SPEC,
        uri=f"s3://bucket/silver/gas_model/{LINEPACK_TABLE_NAME}",
        dataframe=dataframe,
        error=None,
        row_limit=row_limit,
        load_duration_seconds=0.01,
        cache_hit=False,
    )


def _capacity_outlook_load(
    dataframe: pl.DataFrame,
    *,
    row_limit: int | None = None,
) -> GasTableLoad:
    return GasTableLoad(
        spec=CAPACITY_OUTLOOK_TABLE_SPEC,
        uri=f"s3://bucket/silver/gas_model/{CAPACITY_OUTLOOK_TABLE_NAME}",
        dataframe=dataframe,
        error=None,
        row_limit=row_limit,
        load_duration_seconds=0.01,
        cache_hit=False,
    )


def _capacity_auction_load(
    dataframe: pl.DataFrame,
    *,
    row_limit: int | None = None,
) -> GasTableLoad:
    return GasTableLoad(
        spec=CAPACITY_AUCTION_TABLE_SPEC,
        uri=f"s3://bucket/silver/gas_model/{CAPACITY_AUCTION_TABLE_NAME}",
        dataframe=dataframe,
        error=None,
        row_limit=row_limit,
        load_duration_seconds=0.01,
        cache_hit=False,
    )


def _capacity_transaction_load(
    dataframe: pl.DataFrame,
    *,
    row_limit: int | None = None,
) -> GasTableLoad:
    return GasTableLoad(
        spec=CAPACITY_TRANSACTION_TABLE_SPEC,
        uri=f"s3://bucket/silver/gas_model/{CAPACITY_TRANSACTION_TABLE_NAME}",
        dataframe=dataframe,
        error=None,
        row_limit=row_limit,
        load_duration_seconds=0.01,
        cache_hit=False,
    )


def _nomination_forecast_load(
    dataframe: pl.DataFrame,
    *,
    row_limit: int | None = None,
) -> GasTableLoad:
    return GasTableLoad(
        spec=NOMINATION_FORECAST_TABLE_SPEC,
        uri=f"s3://bucket/silver/gas_model/{NOMINATION_FORECAST_TABLE_NAME}",
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


def _sttm_market_settlement_load(
    dataframe: pl.DataFrame,
    *,
    row_limit: int | None = None,
) -> GasTableLoad:
    return GasTableLoad(
        spec=STTM_MARKET_SETTLEMENT_TABLE_SPEC,
        uri=f"s3://bucket/silver/gas_model/{STTM_MARKET_SETTLEMENT_TABLE_NAME}",
        dataframe=dataframe,
        error=None,
        row_limit=row_limit,
        load_duration_seconds=0.01,
        cache_hit=False,
    )


def _sttm_capacity_settlement_load(
    dataframe: pl.DataFrame,
    *,
    row_limit: int | None = None,
) -> GasTableLoad:
    return GasTableLoad(
        spec=STTM_CAPACITY_SETTLEMENT_TABLE_SPEC,
        uri=f"s3://bucket/silver/gas_model/{STTM_CAPACITY_SETTLEMENT_TABLE_NAME}",
        dataframe=dataframe,
        error=None,
        row_limit=row_limit,
        load_duration_seconds=0.01,
        cache_hit=False,
    )


def _sttm_mos_allocation_loads(
    *,
    mos_stack: pl.DataFrame,
    allocation_quantity: pl.DataFrame,
    allocation_limit: pl.DataFrame,
    default_notice: pl.DataFrame,
    row_limit: int | None = None,
) -> list[GasTableLoad]:
    return [
        GasTableLoad(
            spec=STTM_MOS_STACK_TABLE_SPEC,
            uri=f"s3://bucket/silver/gas_model/{STTM_MOS_STACK_TABLE_NAME}",
            dataframe=mos_stack,
            error=None,
            row_limit=row_limit,
            load_duration_seconds=0.01,
            cache_hit=False,
        ),
        GasTableLoad(
            spec=STTM_ALLOCATION_QUANTITY_TABLE_SPEC,
            uri=f"s3://bucket/silver/gas_model/{STTM_ALLOCATION_QUANTITY_TABLE_NAME}",
            dataframe=allocation_quantity,
            error=None,
            row_limit=row_limit,
            load_duration_seconds=0.01,
            cache_hit=False,
        ),
        GasTableLoad(
            spec=STTM_ALLOCATION_LIMIT_TABLE_SPEC,
            uri=f"s3://bucket/silver/gas_model/{STTM_ALLOCATION_LIMIT_TABLE_NAME}",
            dataframe=allocation_limit,
            error=None,
            row_limit=row_limit,
            load_duration_seconds=0.01,
            cache_hit=False,
        ),
        GasTableLoad(
            spec=STTM_DEFAULT_ALLOCATION_NOTICE_TABLE_SPEC,
            uri=(
                "s3://bucket/silver/gas_model/"
                f"{STTM_DEFAULT_ALLOCATION_NOTICE_TABLE_NAME}"
            ),
            dataframe=default_notice,
            error=None,
            row_limit=row_limit,
            load_duration_seconds=0.01,
            cache_hit=False,
        ),
    ]


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


def _sttm_contingency_gas_load(
    dataframe: pl.DataFrame,
    *,
    row_limit: int | None = None,
) -> GasTableLoad:
    return GasTableLoad(
        spec=STTM_CONTINGENCY_GAS_TABLE_SPEC,
        uri=f"s3://bucket/silver/gas_model/{STTM_CONTINGENCY_GAS_TABLE_NAME}",
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


def _scheduled_quantity_load(
    dataframe: pl.DataFrame,
    *,
    row_limit: int | None = None,
) -> GasTableLoad:
    return GasTableLoad(
        spec=SCHEDULED_QUANTITY_TABLE_SPEC,
        uri=f"s3://bucket/silver/gas_model/{SCHEDULED_QUANTITY_TABLE_NAME}",
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
