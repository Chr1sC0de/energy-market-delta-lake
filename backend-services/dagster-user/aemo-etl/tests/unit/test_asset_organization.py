import pytest

from aemo_etl.asset_organization import (
    AEMO_ETL_DOMAIN_TAG,
    AEMO_ETL_LAYER_TAG,
    AEMO_ETL_REPORT_FAMILY_TAG,
    AEMO_ETL_ROLE_TAG,
    LAYER_BRONZE,
    ROLE_SOURCE_TABLE,
    gas_model_mart,
    source_table_asset_tags,
    source_table_report_family,
)


def test_source_table_asset_tags_include_family_and_role() -> None:
    assert source_table_asset_tags(
        domain="sttm",
        name_suffix="int651_v1_ex_ante_market_price_rpt_1",
        layer=LAYER_BRONZE,
    ) == {
        AEMO_ETL_LAYER_TAG: LAYER_BRONZE,
        AEMO_ETL_DOMAIN_TAG: "sttm",
        AEMO_ETL_ROLE_TAG: ROLE_SOURCE_TABLE,
        AEMO_ETL_REPORT_FAMILY_TAG: "market",
    }


def test_unknown_source_table_domain_fails_clearly() -> None:
    with pytest.raises(ValueError, match="unknown source-table domain: electric"):
        source_table_report_family(domain="electric", name_suffix="some_report")


def test_unknown_source_table_name_fails_clearly() -> None:
    with pytest.raises(ValueError, match="unknown sttm source table: int999"):
        source_table_report_family(domain="sttm", name_suffix="int999")


def test_unknown_gas_model_asset_fails_clearly() -> None:
    with pytest.raises(
        ValueError, match="unknown gas_model asset: silver_gas_fact_unknown"
    ):
        gas_model_mart("silver_gas_fact_unknown")
