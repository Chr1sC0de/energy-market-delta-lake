"""Canonical Dagster asset group and tag organization for AEMO ETL."""

from collections.abc import Mapping
from typing import Final, Literal

SourceReportFamily = Literal[
    "market",
    "operations",
    "settlement_retail",
    "capacity",
    "quality",
    "reference",
    "notices",
]
SourceTableLayer = Literal["bronze", "source_silver"]
GasModelMart = Literal[
    "dimensions",
    "operations",
    "market",
    "capacity_settlement",
    "quality_status",
]

AEMO_ETL_LAYER_TAG: Final = "aemo_etl_layer"
AEMO_ETL_DOMAIN_TAG: Final = "aemo_etl_domain"
AEMO_ETL_ROLE_TAG: Final = "aemo_etl_role"
AEMO_ETL_REPORT_FAMILY_TAG: Final = "aemo_etl_report_family"
AEMO_ETL_MART_TAG: Final = "aemo_etl_mart"

LAYER_BRONZE: Final = "bronze"
LAYER_SOURCE_SILVER: Final = "source_silver"
LAYER_GAS_MODEL: Final = "gas_model"

ROLE_SOURCE_TABLE: Final = "source_table"
ROLE_GAS_MODEL: Final = "curated_gas_model"

SOURCE_REPORT_FAMILIES: Final[tuple[SourceReportFamily, ...]] = (
    "market",
    "operations",
    "settlement_retail",
    "capacity",
    "quality",
    "reference",
    "notices",
)

GAS_INGESTION_DISCOVERY_GROUP: Final = "gas_ingestion_discovery"
GAS_INGESTION_UNZIP_GROUP: Final = "gas_ingestion_unzip"
GAS_AEMO_GAS_DOCUMENTS_GROUP: Final = "gas_aemo_gas_documents"
GAS_AEMO_MAJOR_PUBLICATIONS_GROUP: Final = "gas_aemo_major_publications"
GAS_METADATA_GROUP: Final = "gas_metadata"

GAS_MODEL_DIMENSIONS_GROUP: Final = "gas_model_dimensions"
GAS_MODEL_OPERATIONS_GROUP: Final = "gas_model_operations"
GAS_MODEL_MARKET_GROUP: Final = "gas_model_market"
GAS_MODEL_CAPACITY_SETTLEMENT_GROUP: Final = "gas_model_capacity_settlement"
GAS_MODEL_QUALITY_STATUS_GROUP: Final = "gas_model_quality_status"
GAS_MODEL_TARGET_SELECTOR: Final = f"tag:{AEMO_ETL_LAYER_TAG}={LAYER_GAS_MODEL}"

_GAS_MODEL_GROUP_BY_MART: Final[Mapping[GasModelMart, str]] = {
    "dimensions": GAS_MODEL_DIMENSIONS_GROUP,
    "operations": GAS_MODEL_OPERATIONS_GROUP,
    "market": GAS_MODEL_MARKET_GROUP,
    "capacity_settlement": GAS_MODEL_CAPACITY_SETTLEMENT_GROUP,
    "quality_status": GAS_MODEL_QUALITY_STATUS_GROUP,
}

SOURCE_TABLE_REPORT_FAMILY_BY_DOMAIN: Final[
    Mapping[str, Mapping[str, SourceReportFamily]]
] = {
    "gbb": {
        "gasbb_2p_sensitivities": "capacity",
        "gasbb_actual_flow_storage": "operations",
        "gasbb_basins": "reference",
        "gasbb_connection_point_nameplate": "capacity",
        "gasbb_contacts": "reference",
        "gasbb_demand_zones_and_pipeline_connectionpoint_mapping": "reference",
        "gasbb_facilities": "reference",
        "gasbb_facility_developments": "capacity",
        "gasbb_field_interest": "reference",
        "gasbb_field_interest_v2": "reference",
        "gasbb_forecast_utilisation": "capacity",
        "gasbb_gsh_gas_trades": "market",
        "gasbb_late_actual_flow_storage": "operations",
        "gasbb_late_nomination_forecast": "operations",
        "gasbb_linepack_capacity_adequacy": "capacity",
        "gasbb_linepack_zones": "reference",
        "gasbb_lng_shipments": "capacity",
        "gasbb_lng_transactions": "capacity",
        "gasbb_locations_list": "reference",
        "gasbb_medium_term_capacity_outlook": "capacity",
        "gasbb_missing_actual_flow_storage": "operations",
        "gasbb_missing_nomination_forecast": "operations",
        "gasbb_nameplate_rating": "capacity",
        "gasbb_nodes_connection_points": "reference",
        "gasbb_nomination_and_forecast": "operations",
        "gasbb_nt_lng_flow": "operations",
        "gasbb_participants_list": "reference",
        "gasbb_pipeline_connection_flow_history": "operations",
        "gasbb_pipeline_connection_flow_v1": "operations",
        "gasbb_pipeline_connection_flow_v2": "operations",
        "gasbb_pipeline_nil_quality": "quality",
        "gasbb_reserves_resources": "capacity",
        "gasbb_shippers_list": "reference",
        "gasbb_short_term_capacity_outlook": "capacity",
        "gasbb_short_term_swap_transactions": "market",
        "gasbb_short_term_transactions": "market",
        "gasbb_uncontracted_capacity": "capacity",
    },
    "sttm": {
        "int651_v1_ex_ante_market_price_rpt_1": "market",
        "int652_v1_ex_ante_schedule_quantity_rpt_1": "market",
        "int653_v3_ex_ante_pipeline_price_rpt_1": "market",
        "int654_v1_provisional_market_price_rpt_1": "market",
        "int655_v1_provisional_schedule_quantity_rpt_1": "market",
        "int656_v2_provisional_pipeline_data_rpt_1": "market",
        "int657_v2_ex_post_market_data_rpt_1": "market",
        "int658_v1_latest_allocation_quantity_rpt_1": "settlement_retail",
        "int659_v1_bid_offer_rpt_1": "market",
        "int660_v1_contingency_gas_bids_and_offers_rpt_1": "market",
        "int661_v1_contingency_gas_called_scheduled_bid_offer_rpt_1": "market",
        "int662_v1_provisional_deviation_rpt_1": "settlement_retail",
        "int663_v1_provisional_variation_rpt_1": "settlement_retail",
        "int664_v1_daily_provisional_mos_allocation_rpt_1": "settlement_retail",
        "int665_v1_mos_stack_data_rpt_1": "settlement_retail",
        "int666_v1_market_notice_rpt_1": "notices",
        "int667_v1_market_parameters_rpt_1": "market",
        "int668_v1_schedule_log_rpt_1": "market",
        "int669_v1_settlement_version_rpt_1": "settlement_retail",
        "int670_v1_registered_participants_rpt_1": "reference",
        "int671_v1_hub_facility_definition_rpt_1": "reference",
        "int672_v1_cumulative_price_rpt_1": "market",
        "int673_v1_total_contingency_bid_offer_rpt_1": "market",
        "int674_v1_total_contingency_gas_schedules_rpt_1": "market",
        "int675_v1_default_allocation_notice_rpt_1": "settlement_retail",
        "int676_v1_rolling_average_price_rpt_1": "market",
        "int677_v1_contingency_gas_price_rpt_1": "market",
        "int678_v1_net_market_balance_daily_amounts_rpt_1": "settlement_retail",
        "int679_v1_net_market_balance_settlement_amounts_rpt_1": "settlement_retail",
        "int680_v1_dp_flag_data_rpt_1": "reference",
        "int681_v1_daily_provisional_capacity_data_rpt_1": "capacity",
        "int682_v1_settlement_mos_and_capacity_data_rpt_1": "settlement_retail",
        "int683_v1_provisional_used_mos_steps_rpt_1": "settlement_retail",
        "int684_v1_settlement_used_mos_steps_rpt_1": "settlement_retail",
        "int687_v1_facility_hub_capacity_data_rpt_1": "capacity",
        "int688_v1_allocation_warning_limit_thresholds_rpt_1": "capacity",
        "int689_v1_expost_allocation_quantity_rpt_1": "settlement_retail",
        "int690_v1_deviation_price_data_rpt_1": "market",
        "int691_v1_sttm_ctp_register_rpt_1": "reference",
    },
    "vicgas": {
        "int029a_v4_system_notices_1": "notices",
        "int037b_v4_indicative_mkt_price_1": "market",
        "int037c_v4_indicative_price_1": "market",
        "int039b_v4_indicative_locational_price_1": "market",
        "int041_v4_market_and_reference_prices_1": "market",
        "int042_v4_weighted_average_daily_prices_1": "market",
        "int047_v4_heating_values_1": "quality",
        "int050_v4_sched_withdrawals_1": "market",
        "int079_v4_total_gas_withdrawn_1": "settlement_retail",
        "int089_v4_linepack_balance_1": "operations",
        "int091_v4_eddact_1": "settlement_retail",
        "int108_v4_scheduled_run_log_7_1": "market",
        "int111_v5_sdpc_1": "market",
        "int112_v4_dfpc_1": "market",
        "int112b_v4_nftc_1": "market",
        "int112b_v5_nftc_1": "market",
        "int112c_v4_ssc_1": "market",
        "int112d_v4_zftc_1": "market",
        "int117a_v4_est_ancillary_payments_1": "settlement_retail",
        "int117b_v4_ancillary_payments_1": "settlement_retail",
        "int125_v8_details_of_organisations_1": "reference",
        "int126_v4_dfs_data_1": "reference",
        "int128_v4_actual_linepack_1": "operations",
        "int131_v4_bids_at_bid_cutoff_times_prev_2_1": "market",
        "int135_v4_uplift_cap_1": "settlement_retail",
        "int138_v4_settlement_version_1": "settlement_retail",
        "int139_v4_declared_daily_state_heating_value_1": "quality",
        "int139a_v4_daily_zonal_heating_1": "quality",
        "int140_v5_gas_quality_data_1": "quality",
        "int150_v4_public_metering_data_1": "operations",
        "int152_v4_sched_min_qty_linepack_1": "market",
        "int153_v4_demand_forecast_rpt_1": "operations",
        "int171_v4_latest_nsl_1": "settlement_retail",
        "int176_v4_gas_composition_data_1": "quality",
        "int188_v4_ctm_to_hv_zone_mapping_1": "reference",
        "int199_v4_cumulative_price_1": "market",
        "int235_v4_sched_system_total_1": "market",
        "int236_v4_operational_meter_readings_1": "operations",
        "int256_v4_mce_factor_1": "market",
        "int257_v4_linepack_with_zones_1": "operations",
        "int258_v4_mce_nodes_1": "market",
        "int259_v4_pipe_segment_1": "reference",
        "int260_v4_compressor_char_1": "reference",
        "int261_v4_agg_amdq_transferred_1": "settlement_retail",
        "int262_v4_spare_capacity_limits_1": "capacity",
        "int263_v4_lng_monitor_1": "capacity",
        "int271_v4_latest_total_hourly_nsl_1": "settlement_retail",
        "int276_v4_hourly_scada_pressures_at_mce_nodes_1": "operations",
        "int284_v4_tuos_zone_postcode_map_1": "reference",
        "int287_v4_gas_consumption_1": "settlement_retail",
        "int291_v4_out_of_merit_order_gas_1": "settlement_retail",
        "int310_v1_price_and_withdrawals_rpt_1": "market",
        "int310_v4_price_and_withdrawals_1": "market",
        "int311_v5_customer_transfers_1": "settlement_retail",
        "int312_v4_settlements_activity_1": "settlement_retail",
        "int313_v4_allocated_injections_withdrawals_1": "settlement_retail",
        "int314_v4_bid_stack_1": "market",
        "int316_v4_operational_gas_1": "operations",
        "int322a_v4_uplift_breakdown_sett_1": "settlement_retail",
        "int322b_v4_uplift_breakdown_prud_1": "settlement_retail",
        "int339_v4_ccauction_bid_stack_1": "capacity",
        "int342_v4_ccauction_sys_capability_1": "capacity",
        "int343_v4_ccauction_auction_qty_1": "capacity",
        "int345_v4_ccauction_zone_1": "capacity",
        "int348_v4_cctransfer_1": "settlement_retail",
        "int351_v4_ccregistry_summary_1": "capacity",
        "int353_v4_ccauction_qty_won_1": "capacity",
        "int353_v4_ccauction_qty_won_all_1": "capacity",
        "int381_v4_tie_breaking_event_1": "market",
        "int438_v4_bmp_version_non_pts_1": "settlement_retail",
        "int439_v4_published_daily_heating_value_non_pts_1": "quality",
        "int471_v4_latest_nsl_non_pts_rpt_1": "settlement_retail",
        "int538_v4_settlement_versions_1": "settlement_retail",
        "int539_v4_daily_zonal_hv_1": "quality",
        "int571_v4_latest_nsl_1": "settlement_retail",
        "int583_v4_monthly_cumulative_imb_pos_1": "settlement_retail",
        "int597_v4_injection_scaling_factors_1": "settlement_retail",
        "int839a_v1_daily_zonal_hv_1": "quality",
        "int871_v1_erftdailynslrpt_1": "settlement_retail",
        "int891_v1_eddact_1": "settlement_retail",
        "int898_v1_newstreetlisting_1": "settlement_retail",
        "int929a_v4_system_notices_1": "notices",
        "int934_v4_ecgs_contacts_1": "reference",
    },
}

GAS_MODEL_MART_BY_ASSET: Final[Mapping[str, GasModelMart]] = {
    "silver_gas_dim_connection_point": "dimensions",
    "silver_gas_dim_date": "dimensions",
    "silver_gas_dim_facility": "dimensions",
    "silver_gas_dim_location": "dimensions",
    "silver_gas_dim_operational_point": "dimensions",
    "silver_gas_dim_participant": "dimensions",
    "silver_gas_dim_pipeline_segment": "dimensions",
    "silver_gas_dim_zone": "dimensions",
    "silver_gas_participant_market_membership": "dimensions",
    "silver_gas_fact_bid_stack": "market",
    "silver_gas_fact_capacity_auction": "capacity_settlement",
    "silver_gas_fact_capacity_outlook": "capacity_settlement",
    "silver_gas_fact_capacity_transaction": "capacity_settlement",
    "silver_gas_fact_connection_point_flow": "operations",
    "silver_gas_fact_customer_transfer": "capacity_settlement",
    "silver_gas_fact_facility_flow_storage": "operations",
    "silver_gas_fact_gas_quality": "quality_status",
    "silver_gas_fact_heating_value": "quality_status",
    "silver_gas_fact_linepack": "operations",
    "silver_gas_fact_linepack_balance": "operations",
    "silver_gas_fact_market_price": "market",
    "silver_gas_fact_nomination_forecast": "operations",
    "silver_gas_fact_operational_meter_flow": "operations",
    "silver_gas_fact_scada_pressure": "operations",
    "silver_gas_fact_schedule_run": "operations",
    "silver_gas_fact_scheduled_quantity": "operations",
    "silver_gas_fact_settlement_activity": "capacity_settlement",
    "silver_gas_fact_sttm_allocation_limit": "capacity_settlement",
    "silver_gas_fact_sttm_allocation_quantity": "capacity_settlement",
    "silver_gas_fact_sttm_capacity_settlement": "capacity_settlement",
    "silver_gas_fact_sttm_contingency_gas_call": "market",
    "silver_gas_fact_sttm_default_allocation_notice": "capacity_settlement",
    "silver_gas_fact_sttm_market_parameter": "market",
    "silver_gas_fact_sttm_market_settlement": "capacity_settlement",
    "silver_gas_fact_sttm_mos_stack": "capacity_settlement",
    "silver_gas_fact_system_notice": "quality_status",
}


def source_table_report_family(
    *,
    domain: str,
    name_suffix: str,
) -> SourceReportFamily:
    """Return the Source report family for a typed source-table asset."""
    domain_mapping = SOURCE_TABLE_REPORT_FAMILY_BY_DOMAIN.get(domain)
    if domain_mapping is None:
        raise ValueError(f"unknown source-table domain: {domain}")
    family = domain_mapping.get(name_suffix)
    if family is None:
        raise ValueError(f"unknown {domain} source table: {name_suffix}")
    return family


def source_table_group_name(*, domain: str, name_suffix: str) -> str:
    """Return the visual Dagster group for a typed source-table asset pair."""
    family = source_table_report_family(domain=domain, name_suffix=name_suffix)
    return f"gas_{domain}_{family}"


def source_table_asset_tags(
    *,
    domain: str,
    name_suffix: str,
    layer: SourceTableLayer,
    report_family: SourceReportFamily | None = None,
) -> dict[str, str]:
    """Return structured Dagster tags for a source-table bronze or silver asset."""
    family = report_family or source_table_report_family(
        domain=domain,
        name_suffix=name_suffix,
    )
    return {
        AEMO_ETL_LAYER_TAG: layer,
        AEMO_ETL_DOMAIN_TAG: domain,
        AEMO_ETL_ROLE_TAG: ROLE_SOURCE_TABLE,
        AEMO_ETL_REPORT_FAMILY_TAG: family,
    }


def gas_model_mart(asset_name: str) -> GasModelMart:
    """Return the curated gas-model mart assignment for one asset name."""
    mart = GAS_MODEL_MART_BY_ASSET.get(asset_name)
    if mart is None:
        raise ValueError(f"unknown gas_model asset: {asset_name}")
    return mart


def gas_model_group_name(asset_name: str) -> str:
    """Return the visual Dagster group for one curated gas-model asset."""
    return _GAS_MODEL_GROUP_BY_MART[gas_model_mart(asset_name)]


def gas_model_asset_tags(asset_name: str) -> dict[str, str]:
    """Return structured Dagster tags for one curated gas-model asset."""
    mart = gas_model_mart(asset_name)
    return {
        AEMO_ETL_LAYER_TAG: LAYER_GAS_MODEL,
        AEMO_ETL_DOMAIN_TAG: "gas",
        AEMO_ETL_ROLE_TAG: ROLE_GAS_MODEL,
        AEMO_ETL_MART_TAG: mart,
    }
