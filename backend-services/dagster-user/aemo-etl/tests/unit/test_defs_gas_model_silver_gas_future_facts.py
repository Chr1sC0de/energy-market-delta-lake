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

from aemo_etl.defs.gas_model import silver_gas_fact_bid_stack as bid_stack
from aemo_etl.defs.gas_model import silver_gas_fact_capacity_auction as capacity_auction
from aemo_etl.defs.gas_model import silver_gas_fact_capacity_outlook as capacity_outlook
from aemo_etl.defs.gas_model import (
    silver_gas_fact_capacity_transaction as capacity_transaction,
)
from aemo_etl.defs.gas_model import (
    silver_gas_fact_customer_transfer as customer_transfer,
)
from aemo_etl.defs.gas_model import silver_gas_fact_gas_quality as gas_quality
from aemo_etl.defs.gas_model import silver_gas_fact_heating_value as heating_value
from aemo_etl.defs.gas_model import silver_gas_fact_linepack_balance as linepack_balance
from aemo_etl.defs.gas_model import silver_gas_fact_market_price as market_price
from aemo_etl.defs.gas_model import silver_gas_fact_scada_pressure as scada_pressure
from aemo_etl.defs.gas_model import silver_gas_fact_schedule_run as schedule_run
from aemo_etl.defs.gas_model import (
    silver_gas_fact_scheduled_quantity as scheduled_quantity,
)
from aemo_etl.defs.gas_model import silver_gas_fact_settlement_activity as settlement
from aemo_etl.defs.gas_model import silver_gas_fact_system_notice as system_notice


class _DecoratedComputeFn(Protocol):
    decorated_fn: Callable[..., object]


def _ingested() -> datetime:
    return datetime(2024, 1, 2, tzinfo=timezone.utc)


def _row(**values: object) -> pl.LazyFrame:
    return pl.LazyFrame({key: [value] for key, value in values.items()})


def _source(**values: object) -> pl.LazyFrame:
    return _row(
        **values,
        surrogate_key=values.get("surrogate_key", "source-key"),
        source_file=values.get("source_file", "s3://archive/source.csv"),
        ingested_timestamp=values.get("ingested_timestamp", _ingested()),
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


def test_market_price_transform_and_required_check() -> None:
    fn = _dagster_fn(market_price.silver_gas_fact_market_price)
    result = cast(
        MaterializeResult[pl.LazyFrame],
        fn(
            _source(
                demand_type_name="Normal",
                price_value_gst_ex=1.0,
                transmission_group_id=1,
                schedule_type_id="MS",
                transmission_id=10,
                gas_date="01 Jan 2024",
                approval_datetime="01 Jan 2024 01:00:00",
                current_date="01 Jan 2024 02:00:00",
            ),
            _source(
                demand_type_name="Normal",
                price_value_gst_ex=2.0,
                transmission_group_id=1,
                schedule_type_id="OS",
                transmission_id=11,
                gas_date="01 Jan 2024",
                approval_datetime="01 Jan 2024 01:00:00",
                current_date="01 Jan 2024 02:00:00",
            ),
            _source(
                gas_date="01 Jan 2024",
                node_name="Node",
                ti=1,
                nodal_price_value_gst_ex=3.0,
                transmission_id=12,
                current_date="01 Jan 2024 02:00:00",
            ),
            _source(
                gas_date="01 Jan 2024",
                price_bod_gst_ex=4.0,
                price_10am_gst_ex=4.1,
                price_2pm_gst_ex=4.2,
                price_6pm_gst_ex=4.3,
                price_10pm_gst_ex=4.4,
                imb_wtd_ave_price_gst_ex=4.5,
                imb_inj_wtd_ave_price_gst_ex=4.6,
                imb_wdr_wtd_ave_price_gst_ex=4.7,
                current_date="01 Jan 2024 02:00:00",
            ),
            _source(
                gas_date="01 Jan 2024",
                imb_dev_wa_dly_price_gst_ex=5.0,
                current_date="01 Jan 2024 02:00:00",
            ),
            _source(
                transmission_id=13,
                gas_date="01 Jan 2024",
                schedule_interval=1,
                cumulative_price=6.0,
                cpt_exceeded_flag="N",
                schedule_type_id="MS",
                transmission_doc_id=130,
                approval_datetime="01 Jan 2024 01:00:00",
                current_date="01 Jan 2024 02:00:00",
            ),
            _source(
                gas_date="01 Jan 2024",
                gas_hour="06:00:00",
                transmission_id=14,
                ctm_d1_inj=1.0,
                ctm_d1_wdl=1.0,
                price_value=7.0,
                administered_price=0.0,
                total_gas_withdrawals=1.0,
                total_gas_injections=1.0,
            ),
            _source(
                gas_date="01 Jan 2024",
                schedule_interval=1,
                transmission_id=15,
                sched_inj_gj=1.0,
                sched_wdl_gj=1.0,
                price_value=8.0,
                administered_price=0.0,
                actual_wdl_gj=1.0,
                actual_inj_gj=1.0,
            ),
            _source(
                transmission_id=16,
                gas_date="01 Jan 2024",
                flag="MS",
                day_in_advance="D-0",
                data_type="MKT PRICE",
                detail="ACTUAL",
                transmission_doc_id=160,
                id="SYSTEM",
                value=9.0,
                current_date="01 Jan 2024 02:00:00",
            ),
        ),
    )
    collected = _collect(result)

    assert collected.height == 9
    assert _check_passed(
        market_price.silver_gas_fact_market_price_required_fields, result.value
    )


def test_scheduling_transforms() -> None:
    schedule_result = cast(
        MaterializeResult[pl.LazyFrame],
        _dagster_fn(schedule_run.silver_gas_fact_schedule_run)(
            _source(
                transmission_id=1,
                transmission_document_id=2,
                transmission_group_id=3,
                gas_start_datetime="01 Jan 2024 06:00:00",
                bid_cutoff_datetime="01 Jan 2024 05:00:00",
                schedule_type_id="OS",
                creation_datetime="01 Jan 2024 04:00:00",
                forecast_demand_version="7",
                dfs_interface_audit_id=8,
                last_os_for_gas_day_tdoc_id=9,
                os_prior_gas_day_tdoc_id=10,
                approval_datetime="01 Jan 2024 06:30:00",
                demand_type_id=0,
                objective_function_value=1.5,
                current_date="01 Jan 2024 07:00:00",
            )
        ),
    )
    quantity_result = cast(
        MaterializeResult[pl.LazyFrame],
        _dagster_fn(scheduled_quantity.silver_gas_fact_scheduled_quantity)(
            _source(
                gas_date="01 Jan 2024",
                withdrawal_zone_name="Zone",
                scheduled_qty=10.0,
                transmission_id=1,
                current_date="01 Jan 2024 07:00:00",
            ),
            _source(
                transmission_id=2,
                gas_date="01 Jan 2024",
                flag="OS",
                day_in_advance="D-0",
                data_type="CTLD WDLS",
                detail="DAILY",
                transmission_doc_id=20,
                id="SYSTEM",
                value=11.0,
                current_date="01 Jan 2024 07:00:00",
            ),
            _source(
                gas_date="01 Jan 2024",
                statement_version_id=1,
                ancillary_amt_gst_ex=12.0,
                scheduled_out_of_merit_gj=13.0,
                current_date="01 Jan 2024 07:00:00",
            ),
            _source(
                gas_date="01 Jan 2024",
                hv_zone=400,
                hv_zone_desc="HV",
                energy_gj=14.0,
                volume_kscm=15.0,
                current_date="01 Jan 2024 07:00:00",
            ),
        ),
    )
    bid_result = cast(
        MaterializeResult[pl.LazyFrame],
        _dagster_fn(bid_stack.silver_gas_fact_bid_stack)(
            _source(
                gas_date="01 Jan 2024",
                type_1="I",
                type_2="X",
                participant_id=1,
                participant_name="P",
                code="MIRN",
                name="N",
                offer_type="O",
                step1=1,
                step2=2,
                step3=3,
                step4=4,
                step5=5,
                step6=6,
                step7=7,
                step8=8,
                step9=9,
                step10=10,
                min_daily_qty=100.0,
                bid_id=1,
                bid_cutoff_time="01 Jan 2024 05:00:00",
                schedule_type="OS",
                schedule_time="06:00",
                current_date="01 Jan 2024 07:00:00",
            ),
            _source(
                bid_id=2,
                gas_date="01 Jan 2024",
                market_participant_id=2,
                company_name="Company",
                mirn="MIRN2",
                bid_step=1,
                bid_price=3.0,
                bid_qty_gj=4.0,
                step_qty_gj=5.0,
                inject_withdraw="W",
                current_date="01 Jan 2024 07:00:00",
            ),
        ),
    )

    assert _collect(schedule_result).height == 1
    assert _collect(quantity_result).height == 4
    assert _collect(bid_result).height == 2
    assert _check_passed(
        schedule_run.silver_gas_fact_schedule_run_required_fields, schedule_result.value
    )
    assert _check_passed(
        scheduled_quantity.silver_gas_fact_scheduled_quantity_required_fields,
        quantity_result.value,
    )
    assert _check_passed(
        bid_stack.silver_gas_fact_bid_stack_required_fields, bid_result.value
    )


def test_quality_transforms() -> None:
    heating_result = cast(
        MaterializeResult[pl.LazyFrame],
        _dagster_fn(heating_value.silver_gas_fact_heating_value)(
            _source(
                version_id=1,
                gas_date="01 Jan 2024",
                event_datetime="01 Jan 2024 06:00:00",
                event_interval=1,
                heating_value_zone=400,
                heating_value_zone_desc="HV",
                initial_heating_value=1.0,
                current_heating_value=2.0,
                current_date="01 Jan 2024 07:00:00",
            ),
            _source(
                gas_date="01 Jan 2024",
                declared_heating_value=3.0,
                current_date="01 Jan 2024 07:00:00",
            ),
            _source(
                gas_date="01 Jan 2024",
                hv_zone=400,
                hv_zone_desc="HV",
                heating_value=4.0,
                current_date="01 Jan 2024 07:00:00",
            ),
            _source(
                network_name="N",
                gas_day="01 Jan 2024",
                heating_value=5.0,
                current_date="01 Jan 2024 07:00:00",
            ),
            _source(
                gas_date="01 Jan 2024",
                hv_zone=400,
                hv_zone_desc="HV",
                heating_value_mj=6.0,
                current_date="01 Jan 2024 07:00:00",
            ),
            _source(
                gas_date="01 Jan 2024",
                hv_zone=400,
                hv_zone_description="HV",
                heating_value_mj=7.0,
                current_date="01 Jan 2024 07:00:00",
            ),
        ),
    )
    quality_result = cast(
        MaterializeResult[pl.LazyFrame],
        _dagster_fn(gas_quality.silver_gas_fact_gas_quality)(
            _source(
                mirn="MIRN",
                gas_date="01 Jan 2024",
                ti=1,
                quality_type="Heating value",
                unit="MJ",
                quantity=1.0,
                meter_no="M",
                site_company="Site",
                current_date="01 Jan 2024 07:00:00",
            ),
            _source(
                hv_zone=400,
                hv_zone_desc="HV",
                gas_date="01 Jan 2024",
                methane=1.0,
                ethane=2.0,
                propane=3.0,
                butane_i=4.0,
                butane_n=5.0,
                pentane_i=6.0,
                pentane_n=7.0,
                pentane_neo=8.0,
                hexane=9.0,
                nitrogen=10.0,
                carbon_dioxide=11.0,
                hydrogen=12.0,
                spec_gravity=13.0,
                current_date="01 Jan 2024 07:00:00",
            ),
        ),
    )
    pressure_values = {column: 1.0 for column in scada_pressure.PRESSURE_COLUMNS}
    pressure_result = cast(
        MaterializeResult[pl.LazyFrame],
        _dagster_fn(scada_pressure.silver_gas_fact_scada_pressure)(
            _source(
                node_id=1,
                node_name="Node",
                measurement_datetime="01 Jan 2024 07:00:00",
                current_date="01 Jan 2024 07:00:00",
                **pressure_values,
            )
        ),
    )
    linepack_result = cast(
        MaterializeResult[pl.LazyFrame],
        _dagster_fn(linepack_balance.silver_gas_fact_linepack_balance)(
            _source(
                gas_date="01 Jan 2024",
                total_imb_pmt=1.0,
                total_dev_pmt=2.0,
                linepack_acct_pmt_gst_ex=3.0,
                linepack_acct_bal_gst_ex=4.0,
                current_date="01 Jan 2024 07:00:00",
            ),
            _source(
                gas_date="01 Jan 2024",
                type="MIN",
                linepack_id="L",
                linepack_zone_id="Z",
                commencement_datetime="01 Jan 2024 06:00:00",
                ti=1,
                termination_datetime="01 Jan 2024 07:00:00",
                unit_id="GJ",
                linepack_zone_name="Zone",
                transmission_document_id=1,
                quantity=5.0,
                current_date="01 Jan 2024 07:00:00",
                approval_date="01 Jan 2024 07:00:00",
            ),
            _source(
                linepack_zone_id="Z",
                linepack_zone_name="Zone",
                last_mod_date="01 Jan 2024 07:00:00",
                current_date="01 Jan 2024 07:00:00",
            ),
        ),
    )

    assert _collect(heating_result).height == 6
    assert _collect(quality_result).height == 14
    assert _collect(pressure_result).height == 25
    assert _collect(linepack_result).height == 3
    assert _check_passed(
        heating_value.silver_gas_fact_heating_value_required_fields,
        heating_result.value,
    )
    assert _check_passed(
        gas_quality.silver_gas_fact_gas_quality_required_fields, quality_result.value
    )
    assert _check_passed(
        scada_pressure.silver_gas_fact_scada_pressure_required_fields,
        pressure_result.value,
    )
    assert _check_passed(
        linepack_balance.silver_gas_fact_linepack_balance_required_fields,
        linepack_result.value,
    )


def test_capacity_and_settlement_transforms() -> None:
    outlook_result = cast(
        MaterializeResult[pl.LazyFrame],
        _dagster_fn(capacity_outlook.silver_gas_fact_capacity_outlook)(
            _source(
                GasDate="01 Jan 2024",
                FacilityId=1,
                FacilityName="F",
                CapacityType="MDQ",
                CapacityTypeDescription="MDQ",
                OutlookQuantity=1.0,
                FlowDirection="RECEIPT",
                CapacityDescription="C",
                ReceiptLocation=10,
                DeliveryLocation=20,
                ReceiptLocationName="R",
                DeliveryLocationName="D",
                Description="Desc",
                LastUpdated="01 Jan 2024 01:00:00",
            ),
            _source(
                FacilityId=1,
                FacilityName="F",
                FromGasDate="01 Jan 2024",
                ToGasDate="02 Jan 2024",
                CapacityType="MDQ",
                OutlookQuantity=2.0,
                FlowDirection="RECEIPT",
                CapacityDescription="C",
                ReceiptLocation=10,
                DeliveryLocation=20,
                ReceiptLocationName="R",
                DeliveryLocationName="D",
                Description="Desc",
                LastUpdated="01 Jan 2024 01:00:00",
            ),
            _source(
                FacilityId=1,
                FacilityName="F",
                FacilityType="PIPE",
                OutlookMonth=1,
                OutlookYear=2024,
                CapacityType="MDQ",
                OutlookQuantity=3.0,
                FlowDirection="RECEIPT",
                CapacityDescription="C",
                ReceiptLocation=10,
                ReceiptLocationName="R",
                DeliveryLocation=20,
                DeliveryLocationName="D",
                Description="Desc",
                LastUpdated="01 Jan 2024 01:00:00",
            ),
            _source(
                facilityname="F",
                facilityid=1,
                facilitytype="PIPE",
                capacitytype="MDQ",
                capacityquantity=4.0,
                flowdirection="RECEIPT",
                capacitydescription="C",
                receiptlocation=10,
                receiptlocationname="R",
                deliverylocation=20,
                deliverylocationname="D",
                effectivedate="01 Jan 2024",
                description="Desc",
                lastupdated="01 Jan 2024 01:00:00",
            ),
            _source(
                ConnectionPointName="CP",
                ConnectionPointId=10,
                FacilityName="F",
                FacilityId=1,
                FacilityType="PIPE",
                OwnerName="O",
                OwnerId=2,
                OperatorName="Op",
                OperatorId=3,
                CapacityQuantity=5.0,
                EffectiveDate="01 Jan 2024",
                Description="Desc",
                LastUpdated="01 Jan 2024 01:00:00",
            ),
        ),
    )
    transaction_result = cast(
        MaterializeResult[pl.LazyFrame],
        _dagster_fn(capacity_transaction.silver_gas_fact_capacity_transaction)(
            pl.concat(
                [
                    _source(
                        **{
                            "PeriodID": "P",
                            "State": "VIC",
                            "Quantity (TJ)": 1.0,
                            "VolumeWeightedPrice ($)": 2.0,
                            "TransactionType": "T",
                            "SupplyPeriodStart": "01 Jan 2024",
                            "SupplyPeriodEnd": "02 Jan 2024",
                        }
                    ),
                    _source(
                        **{
                            "PeriodID": "P",
                            "State": "VIC",
                            "Quantity (TJ)": None,
                            "VolumeWeightedPrice ($)": None,
                            "TransactionType": None,
                            "SupplyPeriodStart": None,
                            "SupplyPeriodEnd": None,
                        }
                    ),
                ],
                how="diagonal_relaxed",
            ),
            _source(
                **{
                    "PeriodID": "P",
                    "State": "VIC",
                    "Quantity (TJ)": 1.0,
                    "VolumeWeightedPrice ($)": 2.0,
                    "TransactionType": "S",
                    "SupplyPeriodStart": "01 Jan 2024",
                    "SupplyPeriodEnd": "02 Jan 2024",
                }
            ),
            pl.concat(
                [
                    _source(
                        TRADE_DATE="01 Jan 2024",
                        TYPE="GSH",
                        PRODUCT="P",
                        LOCATION="L",
                        TRADE_PRICE=3.0,
                        DAILY_QTY_GJ=4.0,
                        START_DATE="01 Jan 2024",
                        END_DATE="02 Jan 2024",
                        MANUAL_TRADE="N",
                    ),
                    _source(
                        TRADE_DATE="01 Jan 2024",
                        TYPE=None,
                        PRODUCT=None,
                        LOCATION=None,
                        TRADE_PRICE=None,
                        DAILY_QTY_GJ=None,
                        START_DATE=None,
                        END_DATE=None,
                        MANUAL_TRADE=None,
                    ),
                ],
                how="diagonal_relaxed",
            ),
            _source(
                TransactionMonth="01 Jan 2024",
                VolWeightPrice=5.0,
                Volume=6.0,
                VolumePJ=7.0,
                SupplyStartDate="01 Jan 2024",
                SupplyEndDate="02 Jan 2024",
            ),
            _source(
                TransactionId=1,
                FacilityId=1,
                FacilityName="F",
                VolumePJ=8.0,
                ShipmentDate="01 Jan 2024",
                VersionDateTime="01 Jan 2024 01:00:00",
            ),
        ),
    )
    auction_result = cast(
        MaterializeResult[pl.LazyFrame],
        _dagster_fn(capacity_auction.silver_gas_fact_capacity_auction)(
            _source(
                auction_id=1,
                auction_date="01 Jan 2024",
                bid_id=1,
                zone_id=1,
                zone_name="Z",
                start_period="01 Jan 2024",
                end_period="02 Jan 2024",
                step=1,
                bid_price=1.0,
                bid_quantity_gj=2.0,
                current_date="01 Jan 2024",
            ),
            _source(
                zone_id=1,
                zone_name="Z",
                zone_type="T",
                capacity_period="P",
                zone_capacity_gj=3.0,
                current_date="01 Jan 2024",
            ),
            _source(
                auction_id=1,
                zone_id=1,
                zone_name="Z",
                zone_type="T",
                capacity_period="P",
                auction_date="01 Jan 2024",
                available_capacity_gj=4.0,
                current_date="01 Jan 2024",
            ),
            _source(
                zone_id=1,
                zone_name="Z",
                zone_type="T",
                from_date="01 Jan 2024",
                to_date="02 Jan 2024",
                current_date="01 Jan 2024",
            ),
            _source(
                transfer_id=1,
                zone_id=1,
                zone_name="Z",
                start_date="01 Jan 2024",
                end_date="02 Jan 2024",
                transferred_qty_gj=5.0,
                current_date="01 Jan 2024",
            ),
            _source(
                zone_id=1,
                zone_name="Z",
                zone_type="T",
                start_date="01 Jan 2024",
                end_date="02 Jan 2024",
                total_holding_gj=6.0,
                source="S",
                current_date="01 Jan 2024",
            ),
            _source(
                auction_id=1,
                auction_date="01 Jan 2024",
                zone_id=1,
                zone_name="Z",
                zone_type="T",
                start_date="01 Jan 2024",
                end_date="02 Jan 2024",
                cc_period="P",
                clearing_price=7.0,
                quantities_won_gj=8.0,
                unallocated_qty=9.0,
                current_date="01 Jan 2024",
            ),
            _source(
                auction_id=1,
                auction_date="01 Jan 2024",
                zone_id=1,
                zone_name="Z",
                zone_type="T",
                start_date="01 Jan 2024",
                end_date="02 Jan 2024",
                cc_period="P",
                clearing_price=7.0,
                quantities_won_gj=8.0,
                unallocated_qty=9.0,
                current_date="01 Jan 2024",
            ),
            _source(
                gas_date="01 Jan 2024",
                schedule_interval=1,
                transmission_id=1,
                mirn="M",
                tie_breaking_event="T",
                cc_bids=1,
                non_cc_bids=2,
                part_cc_bids=3,
                gas_not_scheduled=4.0,
                current_date="01 Jan 2024",
            ),
        ),
    )
    settlement_result = cast(
        MaterializeResult[pl.LazyFrame],
        _dagster_fn(settlement.silver_gas_fact_settlement_activity)(
            _source(
                gas_date="01 Jan 2024",
                schedule_no=1,
                est_ancillary_amt_gst_ex=1.0,
                current_date="01 Jan 2024",
            ),
            _source(
                ap_run_id=1,
                gas_date="01 Jan 2024",
                schedule_no=1,
                ancillary_amt_gst_ex=2.0,
                current_date="01 Jan 2024",
            ),
            _source(
                statement_version_id=1,
                settlement_cat_type="C",
                version_from_date="01 Jan 2024",
                version_to_date="02 Jan 2024",
                interest_rate=0.1,
                issued_date="01 Jan 2024",
                version_desc="V",
                current_date="01 Jan 2024",
            ),
            _source(
                gas_date="01 Jan 2024",
                uafg_28_days_pct=0.1,
                total_scheduled_inj_gj=1.0,
                total_scheduled_wdl_gj=2.0,
                total_actual_inj_gj=3.0,
                total_actual_wdl_gj=4.0,
                total_uplift_amt=5.0,
                su_uplift_amt=1.0,
                cu_uplift_amt=1.0,
                vu_uplift_amt=1.0,
                tu_uplift_amt=1.0,
                ru_uplift_amt=1.0,
            ),
            _source(
                statement_version_id=1,
                gas_date="01 Jan 2024",
                sched_no=1,
                total_uplift_amt=1.0,
                tuq_qty=1.0,
                dts_uplift_amt=1.0,
                final_qds_gj=1.0,
                event_cap_rate=1.0,
                event_liability_amt=1.0,
                event_liability_qty=1.0,
                annual_cap_limit=1.0,
                annual_liability_amt=1.0,
                annual_liability_qty=1.0,
                net_dts_uplift_amt=1.0,
                modified_surprise_uplift_amt=1.0,
                modified_surprise_uplift_qty=1.0,
                common_uplift_amt=1.0,
                common_uplift_qty=1.0,
                current_date="01 Jan 2024",
            ),
            _source(
                gas_date="01 Jan 2024",
                sched_no=1,
                total_uplift_amt=1.0,
                tuq_qty=1.0,
                dts_uplift_amt=1.0,
                final_qds_gj=1.0,
                event_cap_rate=1.0,
                event_liability_amt=1.0,
                event_liability_qty=1.0,
                annual_cap_limit=1.0,
                annual_liability_amt=1.0,
                annual_liability_qty=1.0,
                net_dts_uplift_amt=1.0,
                modified_surprise_uplift_amt=1.0,
                modified_surprise_uplift_qty=1.0,
                common_uplift_amt=1.0,
                common_uplift_qty=1.0,
                current_date="01 Jan 2024",
            ),
            _source(
                network_name="N",
                version_id=1,
                extract_type="E",
                version_from_date="01 Jan 2024",
                version_to_date="02 Jan 2024",
                issued_date="01 Jan 2024",
                current_date="01 Jan 2024",
            ),
            _source(
                network_name="N",
                version_id=1,
                fro_name="FRO",
                distributor_name="D",
                withdrawal_zone="W",
                curr_cum_date="01 Jan 2024",
                curr_cum_imb_position="Surplus",
                current_date="01 Jan 2024",
            ),
        ),
    )

    assert _collect(outlook_result).height == 5
    transaction_df = _collect(transaction_result)
    settlement_df = _collect(settlement_result)

    assert transaction_df.height == 5
    assert _collect(auction_result).height == 9
    assert settlement_df.height == 8
    assert "monthly_cumulative_imbalance_position_surplus" in (
        settlement_df["activity_type"].to_list()
    )
    assert settlement_df.filter(
        pl.col("activity_type") == "monthly_cumulative_imbalance_position_surplus"
    )["amount_gst_ex"].to_list() == [None]
    assert _check_passed(
        capacity_outlook.silver_gas_fact_capacity_outlook_required_fields,
        outlook_result.value,
    )
    assert _check_passed(
        capacity_transaction.silver_gas_fact_capacity_transaction_required_fields,
        transaction_result.value,
    )
    assert _check_passed(
        capacity_auction.silver_gas_fact_capacity_auction_required_fields,
        auction_result.value,
    )
    assert _check_passed(
        settlement.silver_gas_fact_settlement_activity_required_fields,
        settlement_result.value,
    )


def test_admin_transforms_and_defs() -> None:
    customer_result = cast(
        MaterializeResult[pl.LazyFrame],
        _dagster_fn(customer_transfer.silver_gas_fact_customer_transfer)(
            _source(
                gas_date="01 Jan 2024",
                market_code="VIC",
                transfers_lodged=1,
                transfers_completed=2,
                transfers_cancelled=3,
                int_transfers_lodged=4,
                int_transfers_completed=5,
                int_transfers_cancelled=6,
                greenfields_received=7,
            )
        ),
    )
    notice_result = cast(
        MaterializeResult[pl.LazyFrame],
        _dagster_fn(system_notice.silver_gas_fact_system_notice)(
            _source(
                system_wide_notice_id=1,
                critical_notice_flag="Y",
                system_message="A",
                system_email_message="B",
                notice_start_date="01 Jan 2024 01:00:00",
                notice_end_date="01 Jan 2024 02:00:00",
                url_path="/a",
                current_date="01 Jan 2024 03:00:00",
            ),
            _source(
                system_wide_notice_id=2,
                critical_notice_flag="N",
                system_message="A",
                system_email_message="B",
                notice_start_date="01 Jan 2024 01:00:00",
                notice_end_date="01 Jan 2024 02:00:00",
                url_path="/b",
                current_date="01 Jan 2024 03:00:00",
            ),
        ),
    )

    assert _collect(customer_result).height == 1
    assert _collect(notice_result).height == 2
    assert _check_passed(
        customer_transfer.silver_gas_fact_customer_transfer_required_fields,
        customer_result.value,
    )
    assert _check_passed(
        system_notice.silver_gas_fact_system_notice_required_fields, notice_result.value
    )

    for module in [
        market_price,
        schedule_run,
        scheduled_quantity,
        bid_stack,
        heating_value,
        gas_quality,
        scada_pressure,
        linepack_balance,
        capacity_outlook,
        capacity_transaction,
        capacity_auction,
        settlement,
        customer_transfer,
        system_notice,
    ]:
        definitions = module.defs()
        asset_def = cast(AssetsDefinition, list(definitions.assets or [])[0])
        asset_key = AssetKey(["silver", "gas_model", module.TABLE_NAME])

        assert isinstance(definitions, Definitions)
        assert len(list(definitions.asset_checks or [])) == 4
        assert (
            asset_def.metadata_by_key[asset_key]["source_tables"]
            == module.SOURCE_TABLES
        )
