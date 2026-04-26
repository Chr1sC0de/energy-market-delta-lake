from dagster import AssetKey, AssetsDefinition, Definitions
from polars import String

from aemo_etl.factories.df_from_s3_keys.definitions import (
    df_from_s3_keys_definitions_factory,
)


def test_df_from_s3_keys_definitions_factory_returns_definitions() -> None:
    schema = {
        "col1": String,
    }
    defs = df_from_s3_keys_definitions_factory(
        domain="gbb",
        name_suffix="test_table",
        glob_pattern="test*",
        schema=schema,
        schema_descriptions={"col1": "test column"},
        surrogate_key_sources=["col1"],
        description="A test table",
    )
    assert isinstance(defs, Definitions)


def test_df_from_s3_keys_definitions_factory_wires_bronze_and_silver() -> None:
    defs = df_from_s3_keys_definitions_factory(
        domain="gbb",
        name_suffix="test_table",
        glob_pattern="test*",
        schema={"col1": String},
        schema_descriptions={"col1": "test column"},
        surrogate_key_sources=["col1"],
        description="A test table",
    )

    assets = list(defs.assets or [])
    assert len(assets) == 2

    bronze_key = AssetKey(["bronze", "gbb", "bronze_test_table"])
    silver_key = AssetKey(["silver", "gbb", "silver_test_table"])
    assets_by_key: dict[AssetKey, AssetsDefinition] = {}
    for asset in assets:
        assert isinstance(asset, AssetsDefinition)
        assets_by_key[next(iter(asset.keys))] = asset

    assert set(assets_by_key) == {bronze_key, silver_key}
    assert (
        assets_by_key[bronze_key].get_io_manager_key_for_asset_key(bronze_key)
        == "aemo_deltalake_ingest_partitioned_append_io_manager"
    )
    assert (
        assets_by_key[silver_key].get_io_manager_key_for_asset_key(silver_key)
        == "aemo_deltalake_overwrite_io_manager"
    )
    assert assets_by_key[silver_key].keys_by_input_name == {"df": bronze_key}
    assert (
        assets_by_key[silver_key].metadata_by_key[silver_key]["dagster/table_name"]
        == "silver.gbb.silver_test_table"
    )


def test_df_from_s3_keys_definitions_factory_attaches_checks_to_silver() -> None:
    defs = df_from_s3_keys_definitions_factory(
        domain="gbb",
        name_suffix="test_table",
        glob_pattern="test*",
        schema={"col1": String},
        schema_descriptions={"col1": "test column"},
        surrogate_key_sources=["col1"],
        description="A test table",
    )

    check_specs = [
        spec
        for asset_check in defs.asset_checks or []
        for spec in asset_check.check_specs
    ]

    assert len(check_specs) == 5
    assert {(spec.asset_key, spec.name) for spec in check_specs} == {
        (AssetKey(["bronze", "gbb", "bronze_test_table"]), "check_schema_matches"),
        (AssetKey(["bronze", "gbb", "bronze_test_table"]), "check_schema_drift"),
        (AssetKey(["silver", "gbb", "silver_test_table"]), "check_for_duplicate_rows"),
        (AssetKey(["silver", "gbb", "silver_test_table"]), "check_schema_matches"),
        (AssetKey(["silver", "gbb", "silver_test_table"]), "check_schema_drift"),
    }


def test_df_from_s3_keys_definitions_factory_wires_step_op_tags() -> None:
    defs = df_from_s3_keys_definitions_factory(
        domain="gbb",
        name_suffix="test_table",
        glob_pattern="test*",
        schema={"col1": String},
        schema_descriptions={"col1": "test column"},
        surrogate_key_sources=["col1"],
        description="A test table",
        bronze_op_tags={"ecs/cpu": "512", "ecs/memory": "4096"},
        silver_op_tags={"ecs/cpu": "1024", "ecs/memory": "5120"},
    )

    assets_by_key = {
        next(iter(asset.keys)): asset
        for asset in defs.assets or []
        if isinstance(asset, AssetsDefinition)
    }

    assert assets_by_key[
        AssetKey(["bronze", "gbb", "bronze_test_table"])
    ].node_def.tags == {"ecs/cpu": "512", "ecs/memory": "4096"}
    assert assets_by_key[
        AssetKey(["silver", "gbb", "silver_test_table"])
    ].node_def.tags == {"ecs/cpu": "1024", "ecs/memory": "5120"}
