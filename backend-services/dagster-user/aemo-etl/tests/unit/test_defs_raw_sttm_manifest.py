import pytest
from polars import Datetime, String

from aemo_etl.defs.raw.sttm._manifest import (
    get_sttm_report_manifest,
    load_sttm_source_tables_manifest,
    sttm_landing_only_gap_report_ids,
    sttm_report_schema,
    sttm_report_schema_descriptions,
)


def test_sttm_manifest_defines_int651_from_public_reports_spec() -> None:
    report = get_sttm_report_manifest("int651")

    assert report["report_id"] == "INT651"
    assert report["report_name"] == "Ex Ante Market Price"
    assert report["name_suffix"] == "int651_v1_ex_ante_market_price_rpt_1"
    assert report["glob_pattern"] == "int651_v1_ex_ante_market_price_rpt_1*"
    assert report["surrogate_key_sources"] == ["gas_date", "hub_identifier"]
    assert [column["name"] for column in report["source_columns"]] == [
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
    ]


def test_sttm_manifest_rejects_unknown_report() -> None:
    with pytest.raises(KeyError, match="unknown STTM report: INT685"):
        get_sttm_report_manifest("INT685")


def test_sttm_manifest_keeps_all_source_columns_as_string() -> None:
    report = get_sttm_report_manifest("INT651")
    schema = sttm_report_schema(report)

    for column in report["source_columns"]:
        assert schema[column["name"]] == String

    assert schema["ingested_timestamp"] == Datetime("us", time_zone="UTC")
    assert schema["ingested_date"] == Datetime("us", time_zone="UTC")
    assert schema["surrogate_key"] == String
    assert schema["source_file"] == String


def test_sttm_manifest_includes_descriptions_for_all_schema_columns() -> None:
    report = get_sttm_report_manifest("INT651")

    assert set(sttm_report_schema_descriptions(report)) == set(
        sttm_report_schema(report)
    )


def test_int685_and_int685b_are_landing_only_gaps() -> None:
    manifest = load_sttm_source_tables_manifest()
    report_ids = {report["report_id"] for report in manifest["reports"]}

    assert sttm_landing_only_gap_report_ids() == ("INT685", "INT685B")
    assert "INT685" not in report_ids
    assert "INT685B" not in report_ids
