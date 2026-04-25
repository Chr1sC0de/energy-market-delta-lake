from datetime import datetime, timezone
from typing import cast

import polars as pl
from dagster import AssetKey, AssetsDefinition, Definitions, MaterializeResult

from aemo_etl.defs.gas_model.silver_gas_dim_participant import (
    silver_gas_dim_participant,
)
from aemo_etl.defs.gas_model.silver_gas_participant_market_membership import (
    SOURCE_TABLES,
    defs,
    silver_gas_participant_market_membership,
)


def _gbb_participants() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "CompanyName": ["GBB Participant"],
            "CompanyId": [1],
            "OrganisationTypeName": ["Retailer"],
            "ABN": ["11 222 333 444"],
            "CompanyPhone": ["1"],
            "Locale": ["Melbourne"],
            "LastUpdated": ["01 Jan 2024 00:00:00"],
            "AddressType": ["Postal"],
            "Address": ["1 Street"],
            "State": ["VIC"],
            "Postcode": ["3000"],
            "CompanyFax": ["2"],
            "ingested_timestamp": [datetime(2024, 1, 1, tzinfo=timezone.utc)],
            "surrogate_key": ["gbb-key"],
            "source_file": ["s3://gbb"],
        }
    )


def _vicgas_organisations() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "company_id": [1],
            "company_name": ["VICGAS Participant"],
            "registered_name": ["Registered VICGAS Participant"],
            "acn": ["123 456 789"],
            "abn": ["11222333444"],
            "organization_class_name": ["Participant"],
            "organization_type_name": ["Retailer"],
            "organization_status_name": ["Active"],
            "line_1": ["1 Street"],
            "line_2": [None],
            "line_3": [None],
            "province_id": ["VIC"],
            "city": ["Melbourne"],
            "postal_code": ["3000"],
            "phone": ["1"],
            "fax": ["2"],
            "market_code": ["VICGAS"],
            "company_code": ["ABC"],
            "current_date": ["01 Jan 2024 00:00:00"],
            "ingested_timestamp": [datetime(2024, 1, 2, tzinfo=timezone.utc)],
            "surrogate_key": ["vic-key"],
            "source_file": ["s3://vic"],
        }
    )


def _participants() -> pl.LazyFrame:
    fn = silver_gas_dim_participant.op.compute_fn.decorated_fn  # type: ignore[union-attr]
    result = cast(
        MaterializeResult[pl.LazyFrame],
        fn(_gbb_participants(), _vicgas_organisations()),
    )
    return result.value


def test_silver_gas_participant_market_membership_transform() -> None:
    fn = silver_gas_participant_market_membership.op.compute_fn.decorated_fn  # type: ignore[union-attr]

    result = cast(
        MaterializeResult[pl.LazyFrame],
        fn(_gbb_participants(), _vicgas_organisations(), _participants()),
    )
    collected = result.value.collect()

    assert "dagster/column_lineage" in (result.metadata or {})
    assert collected.height == 2
    assert set(collected["market_code"]) == {"NATGASBB", "VICGAS"}
    assert collected["participant_key"].null_count() == 0
    assert collected["surrogate_key"].n_unique() == collected.height
    assert set(collected["source_surrogate_key"]) == {"gbb-key", "vic-key"}


def test_required_fields_check_fails_for_null_required_field() -> None:
    from aemo_etl.defs.gas_model.silver_gas_participant_market_membership import (
        silver_gas_participant_market_membership_required_fields,
    )

    check_fn = silver_gas_participant_market_membership_required_fields.op.compute_fn.decorated_fn  # type: ignore[union-attr]
    result = check_fn(
        pl.LazyFrame(
            {
                "surrogate_key": ["key-1"],
                "participant_key": [None],
                "source_system": ["GBB"],
                "market_code": ["NATGASBB"],
            }
        )
    )

    assert not result.passed


def test_defs_returns_asset_and_checks() -> None:
    result = defs()
    asset_key = AssetKey(
        ["silver", "gas_model", "silver_gas_participant_market_membership"]
    )
    assets = list(result.assets or [])
    asset_checks = list(result.asset_checks or [])

    assert isinstance(result, Definitions)
    assert len(assets) == 1
    assert len(asset_checks) == 4

    asset_def = cast(AssetsDefinition, assets[0])
    assert asset_def.metadata_by_key[asset_key]["dagster/table_name"] == (
        "silver.gas_model.silver_gas_participant_market_membership"
    )
    assert asset_def.metadata_by_key[asset_key]["source_tables"] == SOURCE_TABLES
