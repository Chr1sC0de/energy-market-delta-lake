import pytest
from polars import Datetime, String

from aemo_etl.defs.raw.sttm._manifest import (
    get_sttm_report_manifest,
    load_sttm_source_tables_manifest,
    sttm_landing_only_gap_report_ids,
    sttm_report_schema,
    sttm_report_schema_descriptions,
)
from aemo_etl.utils import get_s3_object_keys_from_prefix_and_name_glob


EXPECTED_CORE_REPORT_COLUMNS = {
    "INT651": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "schedule_identifier",
        "ex_ante_market_price",
        "administered_price_period",
        "cap_applied",
        "administered_price_cap",
        "schedule_price",
        "approval_datetime",
        "report_datetime",
    ],
    "INT652": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "schedule_identifier",
        "facility_identifier",
        "facility_name",
        "scheduled_qty",
        "firm_gas_scheduled_qty",
        "as_available_scheduled_qty",
        "flow_direction",
        "price_taker_bid_qty",
        "price_taker_bid_not_sched_qty",
        "approval_datetime",
        "report_datetime",
    ],
    "INT653": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "schedule_identifier",
        "facility_identifier",
        "facility_name",
        "capacity_qty",
        "capacity_qty_quality_type",
        "capacity_qty_datetime",
        "ex_ante_capacity_price",
        "ex_ante_flow_direction_constraint_price",
        "schedule_capacity_price",
        "approval_datetime",
        "report_datetime",
    ],
    "INT654": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "schedule_identifier",
        "provisional_price",
        "provisional_schedule_type",
        "report_datetime",
    ],
    "INT655": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "schedule_identifier",
        "facility_identifier",
        "facility_name",
        "provisional_qty",
        "provisional_firm_gas_scheduled",
        "provisional_as_available_scheduled",
        "flow_direction",
        "price_taker_bid_provisional_not_sched_qty",
        "price_taker_bid_provisional_qty",
        "provisional_schedule_type",
        "report_datetime",
    ],
    "INT656": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "schedule_identifier",
        "facility_identifier",
        "facility_name",
        "provisional_capacity_qty",
        "prov_cap_qty_quality_type",
        "provisional_capacity_price",
        "provisional_flow_constraint_price",
        "provisional_schedule_type",
        "report_datetime",
    ],
    "INT657": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "schedule_identifier",
        "imbalance_qty",
        "ex_post_imbalance_price",
        "schedule_type_code",
        "imbalance_type",
        "schedule_imbalance_price",
        "approval_datetime",
        "report_datetime",
    ],
    "INT658": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "facility_identifier",
        "facility_name",
        "allocation_qty_inc_mos",
        "flow_direction",
        "report_datetime",
    ],
    "INT659": [
        "gas_date",
        "company_identifier",
        "company_name",
        "hub_identifier",
        "hub_name",
        "schedule_identifier",
        "facility_identifier",
        "facility_name",
        "bid_offer_identifier",
        "bid_offer_step_number",
        "step_price",
        "step_capped_cumulative_qty",
        "bid_offer_type",
        "report_datetime",
    ],
    "INT660": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "facility_identifier",
        "facility_name",
        "flow_direction",
        "contingency_gas_bid_offer_type",
        "company_identifier",
        "company_name",
        "contingency_gas_bid_offer_identifier",
        "contingency_gas_bid_offer_step_number",
        "contingency_gas_bid_offer_step_price",
        "contingency_gas_bid_offer_step_quantity",
        "report_datetime",
    ],
    "INT661": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "facility_identifier",
        "facility_name",
        "contingency_gas_called_identifier",
        "flow_direction",
        "contingency_gas_bid_offer_type",
        "company_identifier",
        "company_name",
        "contingency_gas_bid_offer_identifier",
        "contingency_gas_bid_offer_step_number",
        "contingency_gas_bid_offer_step_price",
        "contingency_gas_bid_offer_step_quantity",
        "contingency_gas_bid_offer_confirmed_step_quantity",
        "contingency_gas_bid_offer_called_step_quantity",
        "approval_datetime",
        "report_datetime",
    ],
    "INT662": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "facility_identifier",
        "facility_name",
        "total_deviation_qty",
        "net_deviation_qty",
        "deviation_charge",
        "deviation_payment",
        "report_datetime",
    ],
    "INT663": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "variation_qty",
        "variation_charge",
        "mos_capacity_payment",
        "mos_cashout_payment",
        "mos_cashout_charge",
        "report_datetime",
    ],
    "INT664": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "facility_identifier",
        "facility_name",
        "mos_allocated_qty",
        "mos_overrun_qty",
        "report_datetime",
    ],
    "INT665": [
        "effective_from_date",
        "effective_to_date",
        "stack_identifier",
        "hub_identifier",
        "hub_name",
        "facility_identifier",
        "facility_name",
        "stack_type",
        "estimated_maximum_quantity",
        "stack_step_identifier",
        "trading_participant_identifier",
        "trading_participant_name",
        "step_quantity",
        "step_price",
        "report_datetime",
    ],
    "INT666": [
        "market_notice_identifier",
        "critical_notice_flag",
        "market_message",
        "notice_start_date",
        "notice_end_date",
        "url_path",
        "report_datetime",
    ],
    "INT667": [
        "effective_from_date",
        "effective_to_date",
        "parameter_code",
        "parameter_description",
        "parameter_value",
        "last_update_datetime",
        "report_datetime",
    ],
    "INT668": [
        "schedule_identifier",
        "gas_date",
        "hub_identifier",
        "hub_name",
        "schedule_type",
        "schedule_day",
        "creation_datetime",
        "bid_offer_cut_off_datetime",
        "facility_hub_capacity_cut_off_datetime",
        "pipeline_allocation_cut_off_datetime",
        "approval_datetime",
        "report_datetime",
    ],
    "INT669": [
        "settlement_run_identifier",
        "settlement_cat_type",
        "version_from_date",
        "version_to_date",
        "interest_rate",
        "issued_datetime",
        "settlement_run_desc",
        "report_datetime",
    ],
    "INT670": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "company_identifier",
        "company_name",
        "abn",
        "acn",
        "organisation_registration_type",
        "registered_capacity",
        "registered_capacity_status",
        "line_1",
        "line_2",
        "line_3",
        "state_id",
        "city",
        "postal_code",
        "phone",
        "fax",
        "last_update_datetime",
        "registration_status",
        "report_datetime",
    ],
    "INT671": [
        "hub_identifier",
        "hub_name",
        "facility_identifier",
        "facility_name",
        "facility_type",
        "last_update_datetime",
        "report_datetime",
    ],
    "INT672": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "cumulative_price",
        "cumulative_price_threshold",
        "report_datetime",
    ],
    "INT673": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "total_contingency_gas_bid_qty",
        "total_contingency_gas_offer_qty",
        "report_datetime",
    ],
    "INT674": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "facility_identifier",
        "facility_name",
        "contingency_gas_called_identifier",
        "flow_direction",
        "contingency_gas_bid_offer_type",
        "contingency_gas_bid_offer_called_quantity",
        "approval_datetime",
        "report_datetime",
    ],
    "INT675": [
        "notice_identifier",
        "gas_date",
        "hub_identifier",
        "hub_name",
        "facility_identifier",
        "facility_name",
        "notice_message",
        "report_datetime",
    ],
    "INT676": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "rolling_average",
        "report_datetime",
    ],
    "INT677": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "contingency_gas_called_identifier",
        "high_contingency_gas_price",
        "low_contingency_gas_price",
        "schedule_high_contingency_gas_price",
        "schedule_low_contingency_gas_price",
        "approval_datetime",
        "report_datetime",
    ],
    "INT678": [
        "period_start_date",
        "period_end_date",
        "hub_identifier",
        "hub_name",
        "net_market_balance",
        "total_deviation_qty",
        "total_withdrawals",
        "total_variation_charges",
        "report_datetime",
    ],
    "INT679": [
        "settlement_run_identifier",
        "period_start_date",
        "period_end_date",
        "hub_identifier",
        "hub_name",
        "net_market_balance",
        "total_deviation_qty",
        "total_withdrawals",
        "total_variation_charges",
        "report_datetime",
    ],
    "INT680": [
        "hub_identifier",
        "hub_name",
        "effective_from_date",
        "effective_to_date",
        "dp_flag",
        "report_datetime",
    ],
    "INT681": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "facility_identifier",
        "facility_name",
        "firm_not_flowed",
        "as_available_flowed",
        "report_datetime",
    ],
    "INT682": [
        "settlement_run_identifier",
        "gas_date",
        "hub_identifier",
        "hub_name",
        "facility_identifier",
        "facility_name",
        "mos_allocated_qty",
        "mos_overrun_qty",
        "firm_not_flowed",
        "as_available_flowed",
        "report_datetime",
    ],
    "INT683": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "facility_identifier",
        "facility_name",
        "stack_identifier",
        "stack_type",
        "stack_step_identifier",
        "report_datetime",
    ],
    "INT684": [
        "settlement_run_identifier",
        "gas_date",
        "hub_identifier",
        "hub_name",
        "facility_identifier",
        "facility_name",
        "stack_identifier",
        "stack_type",
        "stack_step_identifier",
        "report_datetime",
    ],
    "INT687": [
        "effective_from_date",
        "effective_to_date",
        "hub_identifier",
        "hub_name",
        "facility_identifier",
        "facility_name",
        "default_capacity",
        "maximum_capacity",
        "high_capacity_threshold",
        "low_capacity_threshold",
        "last_update_datetime",
        "report_datetime",
    ],
    "INT688": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "facility_identifier",
        "facility_name",
        "upper_warning_limit",
        "lower_warning_limit",
        "last_update_datetime",
        "report_datetime",
    ],
    "INT689": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "facility_identifier",
        "facility_name",
        "allocation_qty_inc_mos",
        "allocation_qty_quality_type",
        "flow_direction",
        "report_datetime",
    ],
    "INT690": [
        "gas_date",
        "hub_identifier",
        "hub_name",
        "positive_deviation_price",
        "negative_deviation_price",
        "ex_ante_market_price",
        "ex_post_imbalance_price",
        "low_contingency_gas_price",
        "high_contingency_gas_price",
        "mos_increase_cost",
        "mos_decrease_cost",
        "last_update_datetime",
        "report_datetime",
    ],
    "INT691": [
        "hub_identifier",
        "hub_name",
        "facility_identifier",
        "facility_name",
        "facility_type",
        "ctp_identifier",
        "ctp_name",
        "effective_from_date",
        "effective_to_date",
        "last_update_datetime",
        "report_datetime",
    ],
}


def test_sttm_manifest_defines_int651_from_public_reports_spec() -> None:
    report = get_sttm_report_manifest("int651")

    assert report["report_id"] == "INT651"
    assert report["report_name"] == "Ex Ante Market Price"
    assert report["name_suffix"] == "int651_v1_ex_ante_market_price_rpt_1"
    assert report["glob_pattern"] == "int651_v1_ex_ante_market_price_rpt_1*"
    assert report["surrogate_key_sources"] == ["gas_date", "hub_identifier"]
    assert [column["name"] for column in report["source_columns"]] == [
        *EXPECTED_CORE_REPORT_COLUMNS["INT651"],
    ]


def test_sttm_manifest_defines_public_report_batches() -> None:
    manifest = load_sttm_source_tables_manifest()

    assert [report["report_id"] for report in manifest["reports"]] == [
        *EXPECTED_CORE_REPORT_COLUMNS,
    ]


@pytest.mark.parametrize("report_id", EXPECTED_CORE_REPORT_COLUMNS)
def test_sttm_manifest_preserves_columns_and_primary_keys(report_id: str) -> None:
    report = get_sttm_report_manifest(report_id)

    primary_key_columns = [
        column["name"] for column in report["source_columns"] if column["primary_key"]
    ]

    assert [column["name"] for column in report["source_columns"]] == (
        EXPECTED_CORE_REPORT_COLUMNS[report_id]
    )
    assert report["surrogate_key_sources"] == primary_key_columns


def test_sttm_manifest_rejects_unknown_report() -> None:
    with pytest.raises(KeyError, match="unknown STTM report: INT685"):
        get_sttm_report_manifest("INT685")


@pytest.mark.parametrize("report_id", EXPECTED_CORE_REPORT_COLUMNS)
def test_sttm_manifest_keeps_all_source_columns_as_string(report_id: str) -> None:
    report = get_sttm_report_manifest(report_id)
    schema = sttm_report_schema(report)

    for column in report["source_columns"]:
        assert schema[column["name"]] == String

    assert schema["ingested_timestamp"] == Datetime("us", time_zone="UTC")
    assert schema["ingested_date"] == Datetime("us", time_zone="UTC")
    assert schema["surrogate_key"] == String
    assert schema["source_file"] == String


def test_sttm_manifest_includes_descriptions_for_all_schema_columns() -> None:
    report = get_sttm_report_manifest("INT659")

    assert set(sttm_report_schema_descriptions(report)) == set(
        sttm_report_schema(report)
    )


@pytest.mark.parametrize(
    ("report_id", "matching_key", "non_matching_key"),
    [
        (
            "INT653",
            "bronze/sttm/INT653_V3_EX_ANTE_PIPELINE_PRICE_RPT_1.CSV",
            "bronze/sttm/int653_v2_ex_ante_pipeline_price_rpt_1.csv",
        ),
        (
            "INT659",
            "bronze/sttm/int659_v1_bid_offer_rpt_1~20260506090010.csv",
            "bronze/sttm/int659_v1_bid_offer_other_shape.csv",
        ),
        (
            "INT660",
            "bronze/sttm/INT660_V1_CONTINGENCY_GAS_BIDS_AND_OFFERS_RPT_1.CSV",
            "bronze/sttm/int660_v1_contingency_gas_bid_offer_rpt_1.csv",
        ),
        (
            "INT661",
            "bronze/sttm/int661_v1_contingency_gas_called_scheduled_bid_offer_rpt_1~20260506110000.csv",
            "bronze/sttm/int661_v1_contingency_gas_called_schedule_rpt_1.csv",
        ),
        (
            "INT667",
            "bronze/sttm/int667_v1_market_parameters_rpt_1~20260506090000.csv",
            "bronze/sttm/int667_v1_allocation_quantity_rpt_1~20260506090000.csv",
        ),
        (
            "INT668",
            "bronze/sttm/int668_v1_schedule_log_rpt_1~20260506133141.csv",
            "bronze/sttm/int668_v1_schedule_log_other_shape.csv",
        ),
        (
            "INT669",
            "bronze/sttm/INT669_V1_SETTLEMENT_VERSION_RPT_1.CSV",
            "bronze/sttm/int669_v1_settlement_run_rpt_1.csv",
        ),
        (
            "INT670",
            "bronze/sttm/int670_v1_registered_participants_rpt_1~20260506070000.csv",
            "bronze/sttm/int670_v1_participant_register_rpt_1~20260506070000.csv",
        ),
        (
            "INT674",
            "bronze/sttm/INT674_V1_TOTAL_CONTINGENCY_GAS_SCHEDULES_RPT_1.CSV",
            "bronze/sttm/int674_v1_total_contingency_schedule_rpt_1.csv",
        ),
        (
            "INT678",
            "bronze/sttm/int678_v1_net_market_balance_daily_amounts_rpt_1~20260506160000.csv",
            "bronze/sttm/int678_v1_net_market_balance_amounts_rpt_1~20260506160000.csv",
        ),
        (
            "INT679",
            "bronze/sttm/int679_v1_net_market_balance_settlement_amounts_rpt_1~20260506170000.csv",
            "bronze/sttm/int679_v1_net_market_balance_settlement_rpt_1~20260506170000.csv",
        ),
        (
            "INT680",
            "bronze/sttm/int680_v1_dp_flag_data_rpt_1~20260506160000.csv",
            "bronze/sttm/int680_v1_dp_flags_rpt_1~20260506160000.csv",
        ),
        (
            "INT681",
            "bronze/sttm/int681_v1_daily_provisional_capacity_data_rpt_1~20260506160000.csv",
            "bronze/sttm/int681_v1_provisional_capacity_data_rpt_1~20260506160000.csv",
        ),
        (
            "INT682",
            "bronze/sttm/int682_v1_settlement_mos_and_capacity_data_rpt_1~20260506160000.csv",
            "bronze/sttm/int682_v1_settlement_capacity_data_rpt_1~20260506160000.csv",
        ),
        (
            "INT683",
            "bronze/sttm/int683_v1_provisional_used_mos_steps_rpt_1~20260506113000.csv",
            "bronze/sttm/int683_v1_provisional_used_mos_step_rpt_1~20260506113000.csv",
        ),
        (
            "INT684",
            "bronze/sttm/int684_v1_settlement_used_mos_steps_rpt_1~20260506160000.csv",
            "bronze/sttm/int684_v1_settlement_used_mos_step_rpt_1~20260506160000.csv",
        ),
        (
            "INT687",
            "bronze/sttm/int687_v1_facility_hub_capacity_data_rpt_1~20260506090000.csv",
            "bronze/sttm/int687_v1_facility_capacity_data_rpt_1~20260506090000.csv",
        ),
        (
            "INT688",
            "bronze/sttm/int688_v1_allocation_warning_limit_thresholds_rpt_1~20260506113000.csv",
            "bronze/sttm/int688_v1_allocation_warning_thresholds_rpt_1~20260506113000.csv",
        ),
        (
            "INT689",
            "bronze/sttm/int689_v1_expost_allocation_quantity_rpt_1~20260506113000.csv",
            "bronze/sttm/int689_v1_ex_post_allocation_quantity_rpt_1~20260506113000.csv",
        ),
        (
            "INT690",
            "bronze/sttm/int690_v1_deviation_price_data_rpt_1~20260506113800.csv",
            "bronze/sttm/int690_v1_deviation_prices_data_rpt_1~20260506113800.csv",
        ),
        (
            "INT691",
            "bronze/sttm/int691_v1_sttm_ctp_register_rpt_1~20260506060000.csv",
            "bronze/sttm/int691_v1_sttm_custody_transfer_point_register_rpt_1~20260506060000.csv",
        ),
    ],
)
def test_sttm_manifest_glob_patterns_match_representative_keys(
    report_id: str,
    matching_key: str,
    non_matching_key: str,
) -> None:
    report = get_sttm_report_manifest(report_id)

    assert get_s3_object_keys_from_prefix_and_name_glob(
        "bronze/sttm",
        report["glob_pattern"],
        [non_matching_key, matching_key, "bronze/vicgas/unrelated.csv"],
    ) == [matching_key]


def test_int685_and_int685b_are_landing_only_gaps() -> None:
    manifest = load_sttm_source_tables_manifest()
    report_ids = {report["report_id"] for report in manifest["reports"]}

    assert sttm_landing_only_gap_report_ids() == ("INT685", "INT685B")
    assert "INT685" not in report_ids
    assert "INT685B" not in report_ids
