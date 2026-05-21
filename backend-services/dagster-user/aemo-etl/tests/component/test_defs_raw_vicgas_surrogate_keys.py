from importlib import import_module

import pytest
from dagster import AssetsDefinition


@pytest.mark.parametrize(
    ("module_name", "surrogate_key_sources"),
    [
        (
            "int039b_v4_indicative_locational_price_1",
            ["node_name", "ti", "transmission_id"],
        ),
        ("int111_v5_sdpc_1", ["gas_date", "ti", "sdpc_id"]),
        (
            "int112_v4_dfpc_1",
            ["dfpc_id", "ti", "commencement_date", "termination_date"],
        ),
        (
            "int117b_v4_ancillary_payments_1",
            ["ap_run_id", "gas_date", "schedule_no"],
        ),
        (
            "int131_v4_bids_at_bid_cutoff_times_prev_2_1",
            [
                "gas_date",
                "type_1",
                "type_2",
                "participant_id",
                "code",
                "offer_type",
                "bid_id",
                "schedule_type",
                "bid_cutoff_time",
            ],
        ),
        (
            "int236_v4_operational_meter_readings_1",
            ["direction_code_name", "direction", "commencement_datetime"],
        ),
        ("int276_v4_hourly_scada_pressures_at_mce_nodes_1", ["node_id"]),
        ("int311_v5_customer_transfers_1", ["gas_date", "market_code"]),
        (
            "int314_v4_bid_stack_1",
            ["bid_id", "gas_date", "market_participant_id", "mirn", "bid_step"],
        ),
        (
            "int381_v4_tie_breaking_event_1",
            ["schedule_interval", "transmission_id", "mirn"],
        ),
        ("int538_v4_settlement_versions_1", ["version_id"]),
        (
            "int583_v4_monthly_cumulative_imb_pos_1",
            ["version_id", "fro_name", "distributor_name", "withdrawal_zone"],
        ),
        (
            "int597_v4_injection_scaling_factors_1",
            ["version_id", "gas_date", "distributor_name", "withdrawal_zone"],
        ),
        (
            "int898_v1_newstreetlisting_1",
            [
                "distributor",
                "street_name",
                "street_id",
                "street_suffix",
                "suburb_or_place_or_locality",
            ],
        ),
        (
            "int871_v1_erftdailynslrpt_1",
            ["network_id", "gas_date", "gas_date_historical"],
        ),
        ("int891_v1_eddact_1", ["edd_update", "edd_date", "edd_type"]),
    ],
)
def test_vicgas_mibb_surrogate_key_sources(
    module_name: str, surrogate_key_sources: list[str]
) -> None:
    module = import_module(f"aemo_etl.defs.raw.vicgas.{module_name}")
    defs = module.defs

    for asset in defs.assets or []:
        assert isinstance(asset, AssetsDefinition)
        for asset_key in asset.keys:
            assert (
                asset.metadata_by_key[asset_key]["surrogate_key_sources"]
                == surrogate_key_sources
            )
