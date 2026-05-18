"""Component tests for the gas market dashboard helper surface."""

from collections.abc import Mapping
from typing import Self

import polars as pl
import pytest

from marimoserver.gas_dashboard import (
    GAS_MODEL_TABLES,
    GasDashboardConfig,
    GasTableLoad,
    GasTableSpec,
    cached_load_gas_model_tables,
    discover_dashboard_config,
    gas_table_load_status_frame,
    gas_table_load_status_message,
    load_gas_model_tables,
    read_parquet_table,
    render_dashboard_context_panel,
    table_load_by_name,
)
from marimoserver.dashboard_registry import (
    DashboardAudience,
    DashboardRegistryEntry,
    DashboardRegistryError,
    DashboardStatus,
)
from marimoserver.gas_model_loader import (
    GasModelSessionCache,
    GasModelReadRequest,
    GasModelTableRead,
    GasModelTableView,
    cache_status_label,
    format_load_duration,
    format_row_limit,
    refresh_token_from_control,
    load_gas_model_read_request,
    load_gas_model_read_requests,
    row_limit_message,
)


def test_read_parquet_table_delegates_to_polars(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[tuple[str, dict[str, str]]] = []

    class FakeLazyFrame:
        def collect(self) -> pl.DataFrame:
            return pl.DataFrame({"source_system": ["GBB"]})

    def scan_parquet(uri: str, storage_options: dict[str, str]) -> FakeLazyFrame:
        captured.append((uri, storage_options))
        return FakeLazyFrame()

    monkeypatch.setattr(pl, "scan_parquet", scan_parquet)

    dataframe = read_parquet_table("s3://bucket/table", {"A": "B"})

    assert dataframe.to_dict(as_series=False) == {"source_system": ["GBB"]}
    assert captured == [("s3://bucket/table/*.parquet", {"A": "B"})]


def test_read_parquet_table_honours_row_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[tuple[str, dict[str, str]] | int] = []

    class FakeLazyFrame:
        def head(self, row_limit: int) -> Self:
            captured.append(row_limit)
            return self

        def collect(self) -> pl.DataFrame:
            return pl.DataFrame({"source_system": ["GBB"]})

    def scan_parquet(uri: str, storage_options: dict[str, str]) -> FakeLazyFrame:
        captured.append((uri, storage_options))
        return FakeLazyFrame()

    monkeypatch.setattr(pl, "scan_parquet", scan_parquet)

    dataframe = read_parquet_table("s3://bucket/table", {"A": "B"}, row_limit=5)

    assert dataframe.to_dict(as_series=False) == {"source_system": ["GBB"]}
    assert captured == [("s3://bucket/table/*.parquet", {"A": "B"}), 5]


def test_discover_dashboard_config_derives_default_aemo_bucket() -> None:
    config = discover_dashboard_config({})

    assert config.development_environment == "dev"
    assert config.runtime_location == "local"
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
    assert config.full_table_scan_enabled is True


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


def test_discover_dashboard_config_uses_aws_runtime_defaults() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "DEVELOPMENT_ENVIRONMENT": "prod",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "AWS_DEFAULT_REGION": "ap-southeast-2",
        }
    )

    assert config.runtime_location == "aws"
    assert config.development_environment == "prod"
    assert config.aemo_bucket == "prod-energy-market-aemo"
    assert config.aws_endpoint_url is None
    assert config.aws_access_key_id is None
    assert config.aws_secret_access_key is None
    assert config.aws_allow_http == "false"
    assert config.storage_options() == {
        "AWS_REGION": "ap-southeast-2",
        "AWS_ALLOW_HTTP": "false",
        "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
    }
    assert config.full_table_scan_enabled is False
    assert config.max_preview_rows == 100


def test_discover_dashboard_config_accepts_runtime_overrides() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "MARIMO_MAX_PREVIEW_ROWS": "not-an-int",
            "MARIMO_FULL_TABLE_SCAN_ENABLED": "true",
        }
    )

    assert config.aws_runtime is True
    assert config.max_preview_rows == 100
    assert config.full_table_scan_enabled is True


def test_gas_model_specs_cover_required_dashboard_sections() -> None:
    sections = {spec.section for spec in GAS_MODEL_TABLES}
    table_names = {spec.table_name for spec in GAS_MODEL_TABLES}

    assert {"Prices", "Schedules", "Flow and capacity"} <= sections
    assert "silver_gas_fact_market_price" in table_names
    assert "silver_gas_fact_schedule_run" in table_names
    assert "silver_gas_fact_scheduled_quantity" in table_names
    assert "silver_gas_fact_connection_point_flow" in table_names
    assert "silver_gas_fact_capacity_outlook" in table_names


def test_load_gas_model_tables_passes_configured_uri_storage_and_limit() -> None:
    captured: list[tuple[str, Mapping[str, str], int | None]] = []
    config = _dashboard_config()
    specs = [
        GasTableSpec(
            section="Prices",
            label="Market prices",
            table_name="silver_gas_fact_market_price",
        )
    ]

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured.append((uri, storage_options, row_limit))
        return pl.DataFrame({"source_system": ["STTM"]})

    loads = load_gas_model_tables(config, specs=specs, reader=reader)

    assert len(loads) == 1
    assert loads[0].available
    assert loads[0].error is None
    assert captured == [
        (
            "s3://dev-energy-market-aemo/silver/gas_model/silver_gas_fact_market_price",
            config.storage_options(),
            None,
        )
    ]


def test_load_gas_model_tables_limits_aws_reads() -> None:
    captured: list[int | None] = []
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "17",
        }
    )
    specs = [
        GasTableSpec(
            section="Prices",
            label="Market prices",
            table_name="silver_gas_fact_market_price",
        )
    ]

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured.append(row_limit)
        return pl.DataFrame({"source_system": ["STTM"]})

    loads = load_gas_model_tables(config, specs=specs, reader=reader)

    assert loads[0].available
    assert captured == [17]
    assert loads[0].row_limit == 17
    assert loads[0].is_limited


def test_cached_load_gas_model_tables_reuses_cache_until_refresh() -> None:
    calls: list[str] = []
    clock_values = iter((10.0, 10.025, 20.0, 20.05))
    config = _dashboard_config()
    specs = [
        GasTableSpec(
            section="Prices",
            label="Market prices",
            table_name="silver_gas_fact_market_price",
            date_columns=("gas_date",),
        )
    ]
    cache: GasModelSessionCache = {}

    def clock() -> float:
        return next(clock_values)

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        calls.append(uri)
        return pl.DataFrame(
            {
                "gas_date": ["2024-01-01", "2024-01-03"],
                "price": [10.0, 30.0],
            }
        )

    first_load = cached_load_gas_model_tables(
        config,
        cache,
        specs=specs,
        reader=reader,
        clock=clock,
    )[0]
    cached_recent_load = cached_load_gas_model_tables(
        config,
        cache,
        specs=specs,
        reader=reader,
        view=GasModelTableView.RECENT,
        clock=clock,
    )[0]
    refreshed_load = cached_load_gas_model_tables(
        config,
        cache,
        specs=specs,
        reader=reader,
        refresh_token=1,
        clock=clock,
    )[0]

    assert len(calls) == 2
    assert not first_load.cache_hit
    assert first_load.load_duration_seconds == pytest.approx(0.025)
    assert cached_recent_load.cache_hit
    assert cached_recent_load.load_duration_seconds == pytest.approx(0.025)
    assert cached_recent_load.dataframe is not None
    assert cached_recent_load.dataframe.to_dict(as_series=False) == {
        "gas_date": ["2024-01-03", "2024-01-01"],
        "price": [30.0, 10.0],
    }
    assert not refreshed_load.cache_hit
    assert refreshed_load.load_duration_seconds == pytest.approx(0.05)


def test_cached_load_gas_model_tables_uses_stable_run_button_refresh_token() -> None:
    class RunButtonControl:
        value = False

    calls: list[int] = []
    clock_values = iter((1.0, 1.01, 2.0, 2.02, 3.0, 3.03))
    config = _dashboard_config()
    specs = [
        GasTableSpec(
            section="Prices",
            label="Market prices",
            table_name="silver_gas_fact_market_price",
        )
    ]
    cache: GasModelSessionCache = {}
    refresh_control = RunButtonControl()

    def clock() -> float:
        return next(clock_values)

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        calls.append(len(calls) + 1)
        return pl.DataFrame({"read_version": [calls[-1]]})

    first_load = cached_load_gas_model_tables(
        config,
        cache,
        specs=specs,
        reader=reader,
        refresh_token=refresh_token_from_control(refresh_control),
        clock=clock,
    )[0]

    refresh_control.value = True
    refreshed_load = cached_load_gas_model_tables(
        config,
        cache,
        specs=specs,
        reader=reader,
        refresh_token=refresh_token_from_control(refresh_control),
        clock=clock,
    )[0]

    refresh_control.value = False
    reset_load = cached_load_gas_model_tables(
        config,
        cache,
        specs=specs,
        reader=reader,
        refresh_token=refresh_token_from_control(refresh_control),
        clock=clock,
    )[0]

    refresh_control.value = True
    second_refreshed_load = cached_load_gas_model_tables(
        config,
        cache,
        specs=specs,
        reader=reader,
        refresh_token=refresh_token_from_control(refresh_control),
        clock=clock,
    )[0]

    assert calls == [1, 2, 3]
    assert not first_load.cache_hit
    assert not refreshed_load.cache_hit
    assert reset_load.cache_hit
    assert not second_refreshed_load.cache_hit
    assert reset_load.dataframe is not None
    assert reset_load.dataframe.item() == 2
    assert second_refreshed_load.dataframe is not None
    assert second_refreshed_load.dataframe.item() == 3


def test_gas_table_load_status_reports_bounded_limit_cache_and_timing() -> None:
    clock_values = iter((1.0, 1.125))
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "17",
        }
    )
    specs = [
        GasTableSpec(
            section="Prices",
            label="Market prices",
            table_name="silver_gas_fact_market_price",
        )
    ]

    def clock() -> float:
        return next(clock_values)

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        assert row_limit == 17
        return pl.DataFrame({"source_system": ["STTM", "DWGM"]})

    loads = load_gas_model_tables(
        config,
        specs=specs,
        reader=reader,
        clock=clock,
    )
    message = gas_table_load_status_message(loads)
    status = gas_table_load_status_frame(loads)

    assert (
        "Bounded preview reads are capped at `17` rows per table by "
        "`MARIMO_MAX_PREVIEW_ROWS`."
    ) in message
    assert "- Load timing: `125 ms` across `1` table reads" in message
    assert "- Session cache: `0` hits; use **Refresh data**" in message
    assert status.row(0, named=True)["row limit"] == "Bounded preview: 17 rows max"
    assert status.row(0, named=True)["load time"] == "125 ms"
    assert status.row(0, named=True)["cache"] == "Refreshed read"


def test_gas_table_load_status_handles_empty_unavailable_and_no_loads() -> None:
    empty_spec = GasTableSpec(
        section="Prices",
        label="Market prices",
        table_name="empty_prices",
    )
    missing_spec = GasTableSpec(
        section="Schedules",
        label="Schedule runs",
        table_name="missing_schedules",
    )
    loads = [
        GasTableLoad(
            spec=empty_spec,
            uri="s3://bucket/empty_prices",
            dataframe=pl.DataFrame(),
            error=None,
            row_limit=None,
            load_duration_seconds=0.0005,
            cache_hit=True,
        ),
        GasTableLoad(
            spec=missing_spec,
            uri="s3://bucket/missing_schedules",
            dataframe=None,
            error="FileNotFoundError: no parquet files found",
            row_limit=17,
            load_duration_seconds=2.5,
            cache_hit=False,
        ),
    ]

    message = gas_table_load_status_message(loads)
    status = gas_table_load_status_frame(loads)

    assert gas_table_load_status_message([]) == (
        "No `silver.gas_model` tables were requested."
    )
    assert (
        "Bounded preview reads are capped at `17` rows per table by "
        "`MARIMO_MAX_PREVIEW_ROWS`."
    ) in message
    assert status["status"].to_list() == ["Empty", "Unavailable"]
    assert status["load time"].to_list() == ["<1 ms", "2.50 s"]
    assert status["cache"].to_list() == ["Session cache hit", "Refreshed read"]


def test_shared_load_display_helpers_cover_full_scan_messages() -> None:
    table_read = GasModelTableRead(
        table_name="prices",
        uri="s3://bucket/prices",
        dataframe=pl.DataFrame({"price": [10.0]}),
        error=None,
        row_limit=5,
        load_duration_seconds=0.01,
    )
    empty_read = GasModelTableRead(
        table_name="empty",
        uri="s3://bucket/empty",
        dataframe=pl.DataFrame(),
        error=None,
        row_limit=None,
        load_duration_seconds=0.0,
    )

    assert table_read.available
    assert table_read.is_limited
    assert not empty_read.available
    assert not empty_read.is_limited
    assert format_load_duration(0.0005) == "<1 ms"
    assert format_load_duration(2.5) == "2.50 s"
    assert format_row_limit(None) == "Full table scan"
    assert row_limit_message(None) == (
        "Full table scans are enabled; row counts reflect loaded table data."
    )
    assert cache_status_label(True) == "Session cache hit"


def test_refresh_token_from_control_handles_missing_and_unhashable_values() -> None:
    class Control:
        value = ["not", "hashable"]

    class HashableControl:
        value = 2

    class RunButtonControl:
        value = False

    refresh_control = RunButtonControl()

    assert refresh_token_from_control(None) == 0
    assert refresh_token_from_control(HashableControl()) == 2
    assert refresh_token_from_control(Control()) == "['not', 'hashable']"
    assert refresh_token_from_control(refresh_control) == 0

    refresh_control.value = True
    assert refresh_token_from_control(refresh_control) == 1
    assert refresh_token_from_control(refresh_control) == 1

    refresh_control.value = False
    assert refresh_token_from_control(refresh_control) == 1

    refresh_control.value = True
    assert refresh_token_from_control(refresh_control) == 2


def test_load_gas_model_read_requests_cover_available_missing_and_empty() -> None:
    config = _dashboard_config()
    requests = (
        GasModelReadRequest("available"),
        GasModelReadRequest("missing"),
        GasModelReadRequest("empty"),
    )

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        assert storage_options == config.storage_options()
        assert row_limit is None
        if uri.endswith("/missing"):
            raise FileNotFoundError("no parquet files found")
        if uri.endswith("/empty"):
            return pl.DataFrame()
        return pl.DataFrame({"source_system": ["STTM"]})

    loads = load_gas_model_read_requests(config, requests, reader=reader)

    assert loads[0].available
    assert loads[0].table_name == "available"
    assert loads[0].uri == "s3://dev-energy-market-aemo/silver/gas_model/available"
    assert not loads[0].is_limited
    assert not loads[1].available
    assert loads[1].dataframe is None
    assert loads[1].error == "FileNotFoundError: no parquet files found"
    assert not loads[2].available
    assert loads[2].dataframe is not None
    assert loads[2].dataframe.is_empty()
    assert loads[2].error is None


def test_load_gas_model_read_request_keeps_recent_view_without_date_columns() -> None:
    config = _dashboard_config()
    request = GasModelReadRequest(
        table_name="silver_gas_fact_market_price",
        view=GasModelTableView.RECENT,
        date_columns=("missing_date",),
    )

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        return pl.DataFrame({"price": [10.0, 30.0]})

    load = load_gas_model_read_request(config, request, reader=reader)

    assert load.table_name == "silver_gas_fact_market_price"
    assert load.available
    assert load.dataframe is not None
    assert load.dataframe.to_dict(as_series=False) == {"price": [10.0, 30.0]}


def test_load_gas_model_read_requests_support_recent_bounded_aws_view() -> None:
    captured: list[int | None] = []
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "2",
        }
    )
    request = GasModelReadRequest(
        table_name="silver_gas_fact_market_price",
        view=GasModelTableView.RECENT,
        date_columns=("gas_date",),
    )

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured.append(row_limit)
        assert uri == (
            "s3://prod-energy-market-aemo/silver/gas_model/silver_gas_fact_market_price"
        )
        assert storage_options == config.storage_options()
        return pl.DataFrame(
            {
                "gas_date": ["2024-01-01", "2024-01-03"],
                "price": [10.0, 30.0],
            }
        )

    loads = load_gas_model_read_requests(config, (request,), reader=reader)

    assert captured == [2]
    assert loads[0].is_limited
    assert loads[0].row_limit == 2
    assert loads[0].dataframe is not None
    assert loads[0].dataframe.to_dict(as_series=False) == {
        "gas_date": ["2024-01-03", "2024-01-01"],
        "price": [30.0, 10.0],
    }


def test_load_gas_model_tables_returns_empty_state_detail_on_read_error() -> None:
    config = _dashboard_config()
    specs = [
        GasTableSpec(
            section="Prices",
            label="Market prices",
            table_name="silver_gas_fact_market_price",
        )
    ]

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
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

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        raise EmptyMessageError

    loads = load_gas_model_tables(config, specs=specs, reader=reader)

    assert loads[0].error == "EmptyMessageError"


def test_table_load_by_name_returns_matching_load() -> None:
    config = _dashboard_config()
    specs = [
        GasTableSpec(section="Prices", label="Market prices", table_name="prices"),
        GasTableSpec(section="Schedules", label="Schedules", table_name="schedules"),
    ]

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        return pl.DataFrame({"source_system": ["STTM"]})

    loads = load_gas_model_tables(config, specs=specs, reader=reader)

    assert table_load_by_name(loads, "schedules") == loads[1]
    assert table_load_by_name(loads, "missing") is None


def test_render_dashboard_context_panel_covers_complete_concept() -> None:
    html = render_dashboard_context_panel("gas-market-overview")
    no_related_html = render_dashboard_context_panel(
        "gas-market-overview",
        related_limit=0,
    )

    assert "Gas Market Overview" in html
    assert "generated-gold paths" in html
    assert "source chunk IDs" in html
    assert "backing assets" in html
    assert "tools/gas-market-knowledge-base/generated/gold/glossary/gas-day.md" in html
    assert "chunk-gbb-guide-gas-day" in html
    assert "silver.gas_model.silver_gas_fact_market_price" in html
    assert "Gas Day Context" in html
    assert "No related concepts share generated-gold paths" in no_related_html


def test_render_dashboard_context_panel_handles_missing_optional_fields() -> None:
    entry = DashboardRegistryEntry(
        concept_id="minimal-context",
        title="Minimal Context",
        description="Registry entry with only required context metadata.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.PLANNED,
        notebook_name=None,
        backing_assets=("silver.gas_model.minimal_table",),
        generated_gold_paths=(),
        source_chunks=(),
    )

    html = render_dashboard_context_panel("minimal-context", entries=(entry,))

    assert "Minimal Context" in html
    assert "No generated-gold paths recorded in the Marimo registry." in html
    assert "No source chunk IDs recorded in the Marimo registry." in html
    assert "No notebook route recorded" in html
    assert "silver.gas_model.minimal_table" in html


def test_render_dashboard_context_panel_includes_dashboard_usage_metadata() -> None:
    html = render_dashboard_context_panel("gbb-interactive-map")

    assert 'data-concept-id="gbb-interactive-map"' in html
    assert 'data-status="available"' in html
    assert 'data-notebook-name="gbb_interactive_map"' in html
    assert 'data-notebook-route="/marimo/gbb_interactive_map/"' in html
    assert "<dt>Audiences</dt>" in html
    assert "operator, analyst, stakeholder" in html
    assert "/marimo/gbb_interactive_map/" in html


def test_render_dashboard_context_panel_rejects_unknown_concept() -> None:
    with pytest.raises(DashboardRegistryError, match="concept not found"):
        render_dashboard_context_panel("missing-context")


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
