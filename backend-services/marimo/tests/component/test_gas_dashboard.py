"""Component tests for the gas market dashboard helper surface."""

from collections.abc import Mapping

import polars as pl
import pytest

from marimoserver.gas_dashboard import (
    GAS_MODEL_TABLES,
    GasDashboardConfig,
    GasTableSpec,
    discover_dashboard_config,
    load_gas_model_tables,
    read_delta_table,
    table_load_by_name,
)


def test_read_delta_table_delegates_to_polars(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[tuple[str, dict[str, str]]] = []

    def read_delta(uri: str, storage_options: dict[str, str]) -> pl.DataFrame:
        captured.append((uri, storage_options))
        return pl.DataFrame({"source_system": ["GBB"]})

    monkeypatch.setattr(pl, "read_delta", read_delta)

    dataframe = read_delta_table("s3://bucket/table", {"A": "B"})

    assert dataframe.to_dict(as_series=False) == {"source_system": ["GBB"]}
    assert captured == [("s3://bucket/table", {"A": "B"})]


def test_discover_dashboard_config_derives_default_aemo_bucket() -> None:
    config = discover_dashboard_config({})

    assert config.development_environment == "dev"
    assert config.name_prefix == "energy-market"
    assert config.aemo_bucket == "dev-energy-market-aemo"
    assert config.table_uri("silver_gas_fact_market_price") == (
        "s3://dev-energy-market-aemo/silver/gas_model/silver_gas_fact_market_price"
    )


def test_discover_dashboard_config_uses_explicit_environment() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_ENVIRONMENT": "LOCAL",
            "NAME_PREFIX": "market-lab",
            "AEMO_BUCKET": "custom-aemo",
            "AWS_ENDPOINT_URL": "http://localhost:4566",
            "AWS_DEFAULT_REGION": "ap-southeast-2",
            "AWS_ACCESS_KEY_ID": "local",
            "AWS_SECRET_ACCESS_KEY": "secret",
            "AWS_ALLOW_HTTP": "false",
        }
    )

    assert config.development_environment == "local"
    assert config.name_prefix == "market-lab"
    assert config.aemo_bucket == "custom-aemo"
    assert config.storage_options() == {
        "AWS_ENDPOINT_URL": "http://localhost:4566",
        "AWS_REGION": "ap-southeast-2",
        "AWS_ACCESS_KEY_ID": "local",
        "AWS_SECRET_ACCESS_KEY": "secret",
        "AWS_ALLOW_HTTP": "false",
        "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
    }


def test_discover_dashboard_config_treats_blank_values_as_unset() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_ENVIRONMENT": "",
            "NAME_PREFIX": "",
            "AWS_ENDPOINT_URL": "",
        }
    )

    assert config.development_environment == "dev"
    assert config.name_prefix == "energy-market"
    assert config.aemo_bucket == "dev-energy-market-aemo"
    assert config.aws_endpoint_url == "http://localstack:4566"


def test_gas_model_specs_cover_required_dashboard_sections() -> None:
    sections = {spec.section for spec in GAS_MODEL_TABLES}
    table_names = {spec.table_name for spec in GAS_MODEL_TABLES}

    assert {"Prices", "Schedules", "Flow and capacity"} <= sections
    assert "silver_gas_fact_market_price" in table_names
    assert "silver_gas_fact_schedule_run" in table_names
    assert "silver_gas_fact_scheduled_quantity" in table_names
    assert "silver_gas_fact_connection_point_flow" in table_names
    assert "silver_gas_fact_capacity_outlook" in table_names


def test_load_gas_model_tables_passes_configured_uri_and_storage() -> None:
    captured: list[tuple[str, Mapping[str, str]]] = []
    config = _dashboard_config()
    specs = [
        GasTableSpec(
            section="Prices",
            label="Market prices",
            table_name="silver_gas_fact_market_price",
        )
    ]

    def reader(uri: str, storage_options: Mapping[str, str]) -> pl.DataFrame:
        captured.append((uri, storage_options))
        return pl.DataFrame({"source_system": ["STTM"]})

    loads = load_gas_model_tables(config, specs=specs, reader=reader)

    assert len(loads) == 1
    assert loads[0].available
    assert loads[0].error is None
    assert captured == [
        (
            "s3://dev-energy-market-aemo/silver/gas_model/silver_gas_fact_market_price",
            config.storage_options(),
        )
    ]


def test_load_gas_model_tables_returns_empty_state_detail_on_read_error() -> None:
    config = _dashboard_config()
    specs = [
        GasTableSpec(
            section="Prices",
            label="Market prices",
            table_name="silver_gas_fact_market_price",
        )
    ]

    def reader(uri: str, storage_options: Mapping[str, str]) -> pl.DataFrame:
        raise RuntimeError("no delta log found\ntraceback detail")

    loads = load_gas_model_tables(config, specs=specs, reader=reader)

    assert len(loads) == 1
    assert not loads[0].available
    assert loads[0].dataframe is None
    assert loads[0].error == "RuntimeError: no delta log found"
    assert "\n" not in loads[0].error


def test_load_gas_model_tables_handles_empty_exception_message() -> None:
    config = _dashboard_config()
    specs = [
        GasTableSpec(
            section="Prices",
            label="Market prices",
            table_name="silver_gas_fact_market_price",
        )
    ]

    class EmptyMessageError(Exception):
        def __str__(self) -> str:
            return ""

    def reader(uri: str, storage_options: Mapping[str, str]) -> pl.DataFrame:
        raise EmptyMessageError

    loads = load_gas_model_tables(config, specs=specs, reader=reader)

    assert loads[0].error == "EmptyMessageError"


def test_table_load_by_name_returns_matching_load() -> None:
    config = _dashboard_config()
    specs = [
        GasTableSpec(section="Prices", label="Market prices", table_name="prices"),
        GasTableSpec(section="Schedules", label="Schedules", table_name="schedules"),
    ]

    def reader(uri: str, storage_options: Mapping[str, str]) -> pl.DataFrame:
        return pl.DataFrame({"source_system": ["STTM"]})

    loads = load_gas_model_tables(config, specs=specs, reader=reader)

    assert table_load_by_name(loads, "schedules") == loads[1]
    assert table_load_by_name(loads, "missing") is None


def _dashboard_config() -> GasDashboardConfig:
    return discover_dashboard_config(
        {
            "DEVELOPMENT_ENVIRONMENT": "dev",
            "NAME_PREFIX": "energy-market",
            "AWS_ENDPOINT_URL": "http://localstack:4566",
            "AWS_DEFAULT_REGION": "ap-southeast-4",
            "AWS_ACCESS_KEY_ID": "test",
            "AWS_SECRET_ACCESS_KEY": "test",
            "AWS_ALLOW_HTTP": "true",
        }
    )
