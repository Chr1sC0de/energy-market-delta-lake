from collections.abc import Callable
from datetime import datetime, timezone
from typing import Protocol, cast

import polars as pl
from dagster import (
    AssetCheckResult,
    AssetChecksDefinition,
    AssetKey,
    AssetsDefinition,
    Definitions,
    MaterializeResult,
)

from aemo_etl.defs.gas_model import silver_gas_fact_sttm_allocation_limit as limit
from aemo_etl.defs.gas_model import silver_gas_fact_sttm_allocation_quantity as alloc
from aemo_etl.defs.gas_model import silver_gas_fact_sttm_capacity_settlement as cap
from aemo_etl.defs.gas_model import (
    silver_gas_fact_sttm_default_allocation_notice as notice,
)
from aemo_etl.defs.gas_model import silver_gas_fact_sttm_market_parameter as param
from aemo_etl.defs.gas_model import silver_gas_fact_sttm_market_settlement as settle
from aemo_etl.defs.gas_model import silver_gas_fact_sttm_mos_stack as mos


class _DecoratedComputeFn(Protocol):
    decorated_fn: Callable[..., object]


def _ingested() -> datetime:
    return datetime(2024, 1, 2, tzinfo=timezone.utc)


def _source(source_key: str, **values: object) -> pl.LazyFrame:
    source_values = dict(values)
    source_values.setdefault("surrogate_key", source_key)
    source_values.setdefault("source_file", f"s3://archive/{source_key}.csv")
    source_values.setdefault("ingested_timestamp", _ingested())
    return pl.LazyFrame({key: [value] for key, value in source_values.items()})


def _participants() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "surrogate_key": ["participant-tp-1"],
            "participant_identity_source": ["company_id"],
            "participant_identity_value": ["TP-1"],
        }
    )


def _facilities() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "surrogate_key": ["facility-syd-fac-1"],
            "source_system": ["STTM"],
            "source_hub_id": ["SYD"],
            "source_facility_id": ["FAC-1"],
        }
    )


def _zones() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "surrogate_key": ["zone-syd"],
            "source_system": ["STTM"],
            "zone_type": ["sttm_hub"],
            "source_zone_id": ["SYD"],
        }
    )


def _collect(result: MaterializeResult[pl.LazyFrame]) -> pl.DataFrame:
    assert "dagster/column_lineage" in (result.metadata or {})
    return result.value.collect()


def _dagster_fn(
    definition: AssetsDefinition | AssetChecksDefinition,
) -> Callable[..., object]:
    return cast(_DecoratedComputeFn, definition.op.compute_fn).decorated_fn


def _check_passed(
    check_definition: AssetChecksDefinition, input_df: pl.LazyFrame
) -> bool:
    return cast(AssetCheckResult, _dagster_fn(check_definition)(input_df)).passed


def test_sttm_allocation_quantity_transform_and_checks() -> None:
    result = cast(
        MaterializeResult[pl.LazyFrame],
        _dagster_fn(alloc.silver_gas_fact_sttm_allocation_quantity)(
            _source(
                "int658",
                gas_date="01 Jan 2024",
                hub_identifier="SYD",
                hub_name="Sydney",
                facility_identifier="FAC-1",
                facility_name="Facility 1",
                allocation_qty_inc_mos="10.5",
                flow_direction="T",
                report_datetime="01 Jan 2024 01:00:00",
            ),
            _source(
                "int689",
                gas_date="01 Jan 2024",
                hub_identifier="SYD",
                hub_name="Sydney",
                facility_identifier="FAC-1",
                facility_name="Facility 1",
                allocation_qty_inc_mos="11.5",
                allocation_qty_quality_type="WH",
                flow_direction="F",
                report_datetime="01 Jan 2024 02:00:00",
            ),
            _facilities(),
            _zones(),
        ),
    )
    rows = _collect(result).sort("source_report_id")

    assert rows["source_report_id"].to_list() == ["INT658", "INT689"]
    assert rows["facility_key"].to_list() == ["facility-syd-fac-1"] * 2
    assert rows["zone_key"].to_list() == ["zone-syd"] * 2
    assert rows["allocation_version"].to_list() == ["latest", "ex_post"]
    assert rows["allocation_qty_quality_type"].to_list() == [None, "WH"]
    assert rows["allocation_qty_inc_mos_gj"].to_list() == [10.5, 11.5]
    assert _check_passed(
        alloc.silver_gas_fact_sttm_allocation_quantity_required_fields,
        result.value,
    )
    assert _check_passed(
        alloc.silver_gas_fact_sttm_allocation_quantity_duplicate_row_check,
        result.value,
    )


def test_sttm_market_settlement_transform_and_checks() -> None:
    result = cast(
        MaterializeResult[pl.LazyFrame],
        _dagster_fn(settle.silver_gas_fact_sttm_market_settlement)(
            _source(
                "int662",
                gas_date="01 Jan 2024",
                hub_identifier="SYD",
                hub_name="Sydney",
                facility_identifier="FAC-1",
                facility_name="Facility 1",
                total_deviation_qty="1.0",
                net_deviation_qty="-0.5",
                deviation_charge="2.0",
                deviation_payment="3.0",
                report_datetime="01 Jan 2024 03:00:00",
            ),
            _source(
                "int663",
                gas_date="01 Jan 2024",
                hub_identifier="SYD",
                hub_name="Sydney",
                variation_qty="4.0",
                variation_charge="5.0",
                mos_capacity_payment="6.0",
                mos_cashout_payment="7.0",
                mos_cashout_charge="8.0",
                report_datetime="01 Jan 2024 03:00:00",
            ),
            _source(
                "int678",
                period_start_date="01 Jan 2024",
                period_end_date="31 Jan 2024",
                hub_identifier="SYD",
                hub_name="Sydney",
                net_market_balance="9.0",
                total_deviation_qty="10.0",
                total_withdrawals="11.0",
                total_variation_charges="12.0",
                report_datetime="01 Feb 2024 01:00:00",
            ),
            _source(
                "int679",
                settlement_run_identifier="SET-1",
                period_start_date="01 Jan 2024",
                period_end_date="31 Jan 2024",
                hub_identifier="SYD",
                hub_name="Sydney",
                net_market_balance="13.0",
                total_deviation_qty="14.0",
                total_withdrawals="15.0",
                total_variation_charges="16.0",
                report_datetime="01 Feb 2024 02:00:00",
            ),
            _facilities(),
            _zones(),
        ),
    )
    rows = _collect(result)

    assert rows.height == 17
    assert set(rows["source_report_id"]) == {"INT662", "INT663", "INT678", "INT679"}
    assert rows.filter(pl.col("settlement_component") == "net_market_balance")[
        "amount"
    ].to_list() == [9.0, 13.0]
    assert rows.filter(pl.col("settlement_component") == "total_withdrawals")[
        "quantity_gj"
    ].to_list() == [11.0, 15.0]
    nmb_row = rows.filter(pl.col("source_report_id") == "INT678").row(0, named=True)
    assert nmb_row["date_key"] is None
    assert nmb_row["period_start_date_key"] is not None
    assert _check_passed(
        settle.silver_gas_fact_sttm_market_settlement_required_fields,
        result.value,
    )
    assert _check_passed(
        settle.silver_gas_fact_sttm_market_settlement_duplicate_row_check,
        result.value,
    )


def test_sttm_capacity_settlement_transform_and_checks() -> None:
    result = cast(
        MaterializeResult[pl.LazyFrame],
        _dagster_fn(cap.silver_gas_fact_sttm_capacity_settlement)(
            _source(
                "int664",
                gas_date="01 Jan 2024",
                hub_identifier="SYD",
                hub_name="Sydney",
                facility_identifier="FAC-1",
                facility_name="Facility 1",
                mos_allocated_qty="1.0",
                mos_overrun_qty="2.0",
                report_datetime="01 Jan 2024 03:00:00",
            ),
            _source(
                "int681",
                gas_date="01 Jan 2024",
                hub_identifier="SYD",
                hub_name="Sydney",
                facility_identifier="FAC-1",
                facility_name="Facility 1",
                firm_not_flowed="3.0",
                as_available_flowed="4.0",
                report_datetime="01 Jan 2024 03:00:00",
            ),
            _source(
                "int682",
                settlement_run_identifier="SET-1",
                gas_date="01 Jan 2024",
                hub_identifier="SYD",
                hub_name="Sydney",
                facility_identifier="FAC-1",
                facility_name="Facility 1",
                mos_allocated_qty="5.0",
                mos_overrun_qty="6.0",
                firm_not_flowed="7.0",
                as_available_flowed="8.0",
                report_datetime="01 Feb 2024 02:00:00",
            ),
            _facilities(),
            _zones(),
        ),
    )
    rows = _collect(result)

    assert rows.height == 8
    assert set(rows["capacity_settlement_component"]) == {
        "mos_allocated_qty",
        "mos_overrun_qty",
        "firm_not_flowed",
        "as_available_flowed",
    }
    assert (
        rows.filter(pl.col("source_report_id") == "INT682")[
            "settlement_run_id"
        ].to_list()
        == ["SET-1"] * 4
    )
    assert rows["facility_key"].unique().to_list() == ["facility-syd-fac-1"]
    assert _check_passed(
        cap.silver_gas_fact_sttm_capacity_settlement_required_fields,
        result.value,
    )
    assert _check_passed(
        cap.silver_gas_fact_sttm_capacity_settlement_duplicate_row_check,
        result.value,
    )


def test_sttm_mos_stack_transform_and_checks() -> None:
    result = cast(
        MaterializeResult[pl.LazyFrame],
        _dagster_fn(mos.silver_gas_fact_sttm_mos_stack)(
            _source(
                "int665",
                effective_from_date="01 Jan 2024",
                effective_to_date="31 Jan 2024",
                stack_identifier="STACK-1",
                hub_identifier="SYD",
                hub_name="Sydney",
                facility_identifier="FAC-1",
                facility_name="Facility 1",
                stack_type="I",
                estimated_maximum_quantity="1.0",
                stack_step_identifier="STEP-1",
                trading_participant_identifier="TP-1",
                trading_participant_name="Participant 1",
                step_quantity="2.0",
                step_price="3.0",
                report_datetime="01 Jan 2024 01:00:00",
            ),
            _source(
                "int683",
                gas_date="02 Jan 2024",
                hub_identifier="SYD",
                hub_name="Sydney",
                facility_identifier="FAC-1",
                facility_name="Facility 1",
                stack_identifier="STACK-1",
                stack_type="I",
                stack_step_identifier="STEP-1",
                report_datetime="02 Jan 2024 01:00:00",
            ),
            _source(
                "int684",
                settlement_run_identifier="SET-1",
                gas_date="02 Jan 2024",
                hub_identifier="SYD",
                hub_name="Sydney",
                facility_identifier="FAC-1",
                facility_name="Facility 1",
                stack_identifier="STACK-1",
                stack_type="I",
                stack_step_identifier="STEP-1",
                report_datetime="02 Feb 2024 01:00:00",
            ),
            _participants(),
            _facilities(),
            _zones(),
        ),
    )
    rows = _collect(result).sort("source_report_id")

    assert rows["source_report_id"].to_list() == ["INT665", "INT683", "INT684"]
    registered = rows.filter(pl.col("source_report_id") == "INT665").row(0, named=True)
    assert registered["participant_key"] == "participant-tp-1"
    assert registered["effective_from_date_key"] is not None
    assert registered["step_quantity_gj"] == 2.0
    used = rows.filter(pl.col("source_report_id") == "INT683").row(0, named=True)
    assert used["mos_stack_context"] == "provisional_used_step"
    assert used["step_quantity_gj"] is None
    assert _check_passed(
        mos.silver_gas_fact_sttm_mos_stack_required_fields, result.value
    )
    assert _check_passed(
        mos.silver_gas_fact_sttm_mos_stack_duplicate_row_check,
        result.value,
    )


def test_sttm_notice_limit_and_parameter_transforms_and_checks() -> None:
    notice_result = cast(
        MaterializeResult[pl.LazyFrame],
        _dagster_fn(notice.silver_gas_fact_sttm_default_allocation_notice)(
            _source(
                "int675",
                notice_identifier="NOTICE-1",
                gas_date="01 Jan 2024",
                hub_identifier="SYD",
                hub_name="Sydney",
                facility_identifier="FAC-1",
                facility_name="Facility 1",
                notice_message="Default allocation applied",
                report_datetime="01 Jan 2024 04:00:00",
            ),
            _facilities(),
            _zones(),
        ),
    )
    limit_result = cast(
        MaterializeResult[pl.LazyFrame],
        _dagster_fn(limit.silver_gas_fact_sttm_allocation_limit)(
            _source(
                "int688",
                gas_date="01 Jan 2024",
                hub_identifier="SYD",
                hub_name="Sydney",
                facility_identifier="FAC-1",
                facility_name="Facility 1",
                upper_warning_limit="20.0",
                lower_warning_limit="5.0",
                last_update_datetime="01 Jan 2024 01:00:00",
                report_datetime="01 Jan 2024 04:00:00",
            ),
            _facilities(),
            _zones(),
        ),
    )
    param_result = cast(
        MaterializeResult[pl.LazyFrame],
        _dagster_fn(param.silver_gas_fact_sttm_market_parameter)(
            _source(
                "int680",
                hub_identifier="SYD",
                hub_name="Sydney",
                effective_from_date="01 Jan 2024",
                effective_to_date=None,
                dp_flag="1",
                report_datetime="01 Jan 2024 04:00:00",
            ),
            _zones(),
        ),
    )

    notice_row = _collect(notice_result).row(0, named=True)
    limit_row = _collect(limit_result).row(0, named=True)
    param_row = _collect(param_result).row(0, named=True)

    assert notice_row["notice_id"] == "NOTICE-1"
    assert notice_row["facility_key"] == "facility-syd-fac-1"
    assert limit_row["upper_warning_limit_gj"] == 20.0
    assert limit_row["source_report_timestamp"] is not None
    assert param_row["parameter_type"] == "dp_flag"
    assert param_row["dp_flag"] == "1"
    assert param_row["effective_to_date_key"] is None

    assert _check_passed(
        notice.silver_gas_fact_sttm_default_allocation_notice_required_fields,
        notice_result.value,
    )
    assert _check_passed(
        notice.silver_gas_fact_sttm_default_allocation_notice_duplicate_row_check,
        notice_result.value,
    )
    assert _check_passed(
        limit.silver_gas_fact_sttm_allocation_limit_required_fields,
        limit_result.value,
    )
    assert _check_passed(
        limit.silver_gas_fact_sttm_allocation_limit_duplicate_row_check,
        limit_result.value,
    )
    assert _check_passed(
        param.silver_gas_fact_sttm_market_parameter_required_fields,
        param_result.value,
    )
    assert _check_passed(
        param.silver_gas_fact_sttm_market_parameter_duplicate_row_check,
        param_result.value,
    )


def test_sttm_capacity_settlement_fact_defs() -> None:
    for module in [alloc, settle, cap, mos, notice, limit, param]:
        definitions = module.defs()
        asset_def = cast(AssetsDefinition, list(definitions.assets or [])[0])
        asset_key = AssetKey(["silver", "gas_model", module.TABLE_NAME])

        assert isinstance(definitions, Definitions)
        assert len(list(definitions.asset_checks or [])) == 4
        assert (
            asset_def.metadata_by_key[asset_key]["source_tables"]
            == module.SOURCE_TABLES
        )
