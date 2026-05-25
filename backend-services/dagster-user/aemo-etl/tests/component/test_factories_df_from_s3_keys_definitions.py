from typing import cast

from dagster import AssetKey, AssetsDefinition, Definitions
from dagster._core.definitions.unresolved_asset_job_definition import (
    UnresolvedAssetJobDefinition,
)
from polars import String

from aemo_etl.asset_organization import (
    AEMO_ETL_DOMAIN_TAG,
    AEMO_ETL_LAYER_TAG,
    AEMO_ETL_REPORT_FAMILY_TAG,
    AEMO_ETL_ROLE_TAG,
    LAYER_BRONZE,
    LAYER_SOURCE_SILVER,
    ROLE_SOURCE_TABLE,
)
from aemo_etl.defs.resources import SOURCE_TABLE_BRONZE_READ_IO_MANAGER_KEY
from aemo_etl.factories.df_from_s3_keys.assets import (
    SKIPPED_S3_KEYS_CHECK_NAME,
    SOURCE_CONTENT_HASH_COLUMN,
)
from aemo_etl.factories.df_from_s3_keys.definitions import (
    df_from_s3_keys_definitions_factory,
)


def test_df_from_s3_keys_definitions_factory_returns_definitions() -> None:
    schema = {
        "col1": String,
    }
    defs = df_from_s3_keys_definitions_factory(
        domain="test",
        name_suffix="test_table",
        glob_pattern="test*",
        schema=schema,
        schema_descriptions={"col1": "test column"},
        surrogate_key_sources=["col1"],
        description="A test table",
        report_family="reference",
    )
    assert isinstance(defs, Definitions)


def test_df_from_s3_keys_definitions_factory_wires_bronze_and_silver() -> None:
    defs = df_from_s3_keys_definitions_factory(
        domain="test",
        name_suffix="test_table",
        glob_pattern="test*",
        schema={"col1": String},
        schema_descriptions={"col1": "test column"},
        surrogate_key_sources=["col1"],
        description="A test table",
        report_family="reference",
    )

    assets = list(defs.assets or [])
    assert len(assets) == 2

    bronze_key = AssetKey(["bronze", "test", "bronze_test_table"])
    silver_key = AssetKey(["silver", "test", "silver_test_table"])
    assets_by_key: dict[AssetKey, AssetsDefinition] = {}
    for asset in assets:
        assert isinstance(asset, AssetsDefinition)
        assets_by_key[next(iter(asset.keys))] = asset

    assert set(assets_by_key) == {bronze_key, silver_key}
    assert (
        assets_by_key[bronze_key].get_io_manager_key_for_asset_key(bronze_key)
        == SOURCE_TABLE_BRONZE_READ_IO_MANAGER_KEY
    )
    assert (
        assets_by_key[silver_key].get_io_manager_key_for_asset_key(silver_key)
        == "aemo_parquet_overwrite_io_manager"
    )
    assert assets_by_key[silver_key].keys_by_input_name == {"df": bronze_key}
    assert assets_by_key[bronze_key].group_names_by_key[bronze_key] == (
        "gas_test_reference"
    )
    assert assets_by_key[silver_key].group_names_by_key[silver_key] == (
        "gas_test_reference"
    )
    assert {
        AEMO_ETL_DOMAIN_TAG: "test",
        AEMO_ETL_LAYER_TAG: LAYER_BRONZE,
        AEMO_ETL_REPORT_FAMILY_TAG: "reference",
        AEMO_ETL_ROLE_TAG: ROLE_SOURCE_TABLE,
    }.items() <= assets_by_key[bronze_key].tags_by_key[bronze_key].items()
    assert {
        AEMO_ETL_DOMAIN_TAG: "test",
        AEMO_ETL_LAYER_TAG: LAYER_SOURCE_SILVER,
        AEMO_ETL_REPORT_FAMILY_TAG: "reference",
        AEMO_ETL_ROLE_TAG: ROLE_SOURCE_TABLE,
    }.items() <= assets_by_key[silver_key].tags_by_key[silver_key].items()
    assert (
        assets_by_key[silver_key].metadata_by_key[silver_key]["dagster/table_name"]
        == "silver.test.silver_test_table"
    )
    assert assets_by_key[bronze_key].metadata_by_key[bronze_key][
        "source_content_hash_sources"
    ] == ["col1"]
    assert {
        (spec.asset_key, spec.name) for spec in assets_by_key[bronze_key].check_specs
    } == {(bronze_key, SKIPPED_S3_KEYS_CHECK_NAME)}
    column_names = [
        column.name
        for column in assets_by_key[bronze_key]
        .metadata_by_key[bronze_key]["dagster/column_schema"]
        .columns
    ]
    assert SOURCE_CONTENT_HASH_COLUMN in column_names


def test_df_from_s3_keys_definitions_factory_attaches_checks_to_silver() -> None:
    defs = df_from_s3_keys_definitions_factory(
        domain="test",
        name_suffix="test_table",
        glob_pattern="test*",
        schema={"col1": String},
        schema_descriptions={"col1": "test column"},
        surrogate_key_sources=["col1"],
        description="A test table",
        report_family="reference",
    )

    check_specs = [
        spec
        for asset_check in defs.asset_checks or []
        for spec in asset_check.check_specs
    ]

    assert len(check_specs) == 5
    assert {(spec.asset_key, spec.name) for spec in check_specs} == {
        (AssetKey(["bronze", "test", "bronze_test_table"]), "check_schema_matches"),
        (AssetKey(["bronze", "test", "bronze_test_table"]), "check_schema_drift"),
        (AssetKey(["silver", "test", "silver_test_table"]), "check_for_duplicate_rows"),
        (AssetKey(["silver", "test", "silver_test_table"]), "check_schema_matches"),
        (AssetKey(["silver", "test", "silver_test_table"]), "check_schema_drift"),
    }


def test_df_from_s3_keys_definitions_factory_wires_asset_job() -> None:
    defs = df_from_s3_keys_definitions_factory(
        domain="test",
        name_suffix="test_table",
        glob_pattern="test*",
        schema={"col1": String},
        schema_descriptions={"col1": "test column"},
        surrogate_key_sources=["col1"],
        description="A test table",
        job_tags={"ecs/cpu": "1024", "ecs/memory": "5120"},
        report_family="reference",
    )

    jobs = list(defs.jobs or [])
    assert len(jobs) == 1

    job = cast(UnresolvedAssetJobDefinition, jobs[0])
    assets = [
        asset for asset in defs.assets or [] if isinstance(asset, AssetsDefinition)
    ]
    assert job.name == "test_table_job"
    assert job.tags == {"ecs/cpu": "1024", "ecs/memory": "5120"}
    assert job.selection.resolve(assets) == {
        AssetKey(["bronze", "test", "bronze_test_table"]),
        AssetKey(["silver", "test", "silver_test_table"]),
    }
