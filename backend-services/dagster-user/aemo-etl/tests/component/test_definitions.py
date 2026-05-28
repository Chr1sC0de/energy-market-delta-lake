"""Unit tests for the root aemo_etl/definitions.py module."""

from dagster import AssetKey, Definitions
from pytest_mock import MockerFixture


def test_root_defs_function(mocker: MockerFixture) -> None:
    """defs() merges resources, loaded definitions, and maintenance definitions."""
    mocker.patch(
        "aemo_etl.definitions.load_from_defs_folder",
        return_value=Definitions(),
    )
    from aemo_etl.definitions import defs
    from aemo_etl.maintenance.delta_tables import DELTA_TABLE_VACUUM_JOB_NAME

    result = defs()
    assert isinstance(result, Definitions)
    assert [job.name for job in result.jobs or []] == [DELTA_TABLE_VACUUM_JOB_NAME]


def test_root_defs_registers_manual_vicgas_report_job() -> None:
    from aemo_etl.definitions import defs

    result = defs()
    job_names = {job.name for job in result.jobs or []}

    assert "download_vicgas_public_report_zip_files_job" in job_names
    assert "download_sttm_day_zip_files_job" in job_names


def test_root_defs_apply_asset_organization_contract() -> None:
    from aemo_etl.asset_organization import (
        AEMO_ETL_DOMAIN_TAG,
        AEMO_ETL_LAYER_TAG,
        AEMO_ETL_MART_TAG,
        AEMO_ETL_REPORT_FAMILY_TAG,
        AEMO_ETL_ROLE_TAG,
        GAS_AEMO_GAS_DOCUMENTS_GROUP,
        GAS_AEMO_MAJOR_PUBLICATIONS_GROUP,
        GAS_INGESTION_DISCOVERY_GROUP,
        GAS_INGESTION_UNZIP_GROUP,
        GAS_METADATA_GROUP,
        GAS_MODEL_MART_BY_ASSET,
        LAYER_BRONZE,
        LAYER_GAS_MODEL,
        LAYER_SOURCE_SILVER,
        ROLE_GAS_MODEL,
        ROLE_SOURCE_TABLE,
        SOURCE_TABLE_REPORT_FAMILY_BY_DOMAIN,
        gas_model_group_name,
        source_table_group_name,
    )
    from aemo_etl.definitions import defs
    from aemo_etl.factories.df_from_s3_keys.source_tables import (
        load_source_table_specs,
    )

    repository_def = defs().get_repository_def()
    assets_by_key = repository_def.assets_defs_by_key

    helper_group_by_key = {
        AssetKey(["bronze", "gbb", "bronze_nemweb_public_files_gbb"]): (
            GAS_INGESTION_DISCOVERY_GROUP
        ),
        AssetKey(["bronze", "sttm", "bronze_nemweb_public_files_sttm"]): (
            GAS_INGESTION_DISCOVERY_GROUP
        ),
        AssetKey(["bronze", "vicgas", "bronze_nemweb_public_files_vicgas"]): (
            GAS_INGESTION_DISCOVERY_GROUP
        ),
        AssetKey(["bronze", "gbb", "unzipper_gbb"]): GAS_INGESTION_UNZIP_GROUP,
        AssetKey(["bronze", "sttm", "unzipper_sttm"]): GAS_INGESTION_UNZIP_GROUP,
        AssetKey(["bronze", "vicgas", "unzipper_vicgas"]): GAS_INGESTION_UNZIP_GROUP,
        AssetKey(
            ["bronze", "aemo_gas_documents", "bronze_aemo_gas_document_sources"]
        ): GAS_AEMO_GAS_DOCUMENTS_GROUP,
        AssetKey(
            [
                "bronze",
                "aemo_major_publications",
                "bronze_aemo_major_publications_hub_downloads",
            ]
        ): GAS_AEMO_MAJOR_PUBLICATIONS_GROUP,
        AssetKey(["bronze", "metadata", "bronze_table_metadata"]): GAS_METADATA_GROUP,
    }
    for asset_key, expected_group in helper_group_by_key.items():
        assert assets_by_key[asset_key].group_names_by_key[asset_key] == expected_group

    specs = [
        spec
        for spec in load_source_table_specs()
        if spec.domain in SOURCE_TABLE_REPORT_FAMILY_BY_DOMAIN
    ]
    for spec in specs:
        expected_group_name = source_table_group_name(
            domain=spec.domain,
            name_suffix=spec.name_suffix,
        )
        bronze_key = AssetKey(["bronze", spec.domain, spec.bronze_table_name])
        silver_key = AssetKey(["silver", spec.domain, f"silver_{spec.name_suffix}"])

        bronze_def = assets_by_key[bronze_key]
        silver_def = assets_by_key[silver_key]
        assert bronze_def.group_names_by_key[bronze_key] == expected_group_name
        assert silver_def.group_names_by_key[silver_key] == expected_group_name
        assert {
            AEMO_ETL_DOMAIN_TAG: spec.domain,
            AEMO_ETL_LAYER_TAG: LAYER_BRONZE,
            AEMO_ETL_REPORT_FAMILY_TAG: spec.report_family,
            AEMO_ETL_ROLE_TAG: ROLE_SOURCE_TABLE,
        }.items() <= bronze_def.tags_by_key[bronze_key].items()
        assert {
            AEMO_ETL_DOMAIN_TAG: spec.domain,
            AEMO_ETL_LAYER_TAG: LAYER_SOURCE_SILVER,
            AEMO_ETL_REPORT_FAMILY_TAG: spec.report_family,
            AEMO_ETL_ROLE_TAG: ROLE_SOURCE_TABLE,
        }.items() <= silver_def.tags_by_key[silver_key].items()

    curated_gas_model_keys = {
        AssetKey(["silver", "gas_model", asset_name])
        for asset_name in GAS_MODEL_MART_BY_ASSET
    }
    assert len(curated_gas_model_keys) == 36
    for asset_key in curated_gas_model_keys:
        asset_def = assets_by_key[asset_key]
        asset_name = asset_key.path[-1]
        assert asset_def.group_names_by_key[asset_key] == gas_model_group_name(
            asset_name
        )
        assert {
            AEMO_ETL_DOMAIN_TAG: "gas",
            AEMO_ETL_LAYER_TAG: LAYER_GAS_MODEL,
            AEMO_ETL_MART_TAG: GAS_MODEL_MART_BY_ASSET[asset_name],
            AEMO_ETL_ROLE_TAG: ROLE_GAS_MODEL,
        }.items() <= asset_def.tags_by_key[asset_key].items()

    silver_metadata_key = AssetKey(["silver", "metadata", "silver_table_metadata"])
    silver_metadata_def = assets_by_key[silver_metadata_key]
    assert silver_metadata_def.group_names_by_key[silver_metadata_key] == (
        GAS_METADATA_GROUP
    )
    assert AEMO_ETL_LAYER_TAG not in silver_metadata_def.tags_by_key.get(
        silver_metadata_key,
        {},
    )
