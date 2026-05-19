"""Component tests for the local table explorer helper surface."""

from collections.abc import Iterable, Mapping
from io import BytesIO
from typing import Self

import polars as pl
import pytest

from marimoserver import table_explorer as explorer
from marimoserver.bounded_read_diagnostics import (
    bounded_read_runtime_frame,
    bounded_read_state_frame,
    endpoint_mode_label,
    render_bounded_read_summary_cards,
)
from marimoserver.gas_dashboard import discover_dashboard_config
from marimoserver.table_explorer import (
    AWS_BOUNDED_READ_DIAGNOSTICS_ROUTE,
    AssetCatalogueState,
    DEFAULT_LOCAL_BUCKETS,
    DATA_READINESS_ROUTE,
    BucketHealthState,
    BucketStatus,
    CataloguedTable,
    S3Client,
    StorageDiscovery,
    TableQuery,
    TableExplorerConfig,
    TableAvailability,
    TableFormat,
    TablePrefix,
    TableScan,
    asset_catalogue_action_markdown,
    asset_schema_metadata_frame,
    bucket_health_state,
    build_bucket_health_summary,
    build_asset_catalogue_summary,
    cached_table_scan,
    catalogued_table_by_id,
    catalogued_table_group,
    catalogued_table_layers_or_domains,
    classify_table_prefixes,
    concept_gallery_asset_id,
    concept_gallery_entries_for_table,
    concept_gallery_metadata_frame,
    create_s3_client,
    default_catalogued_table_entry_id,
    discover_table_catalogue,
    discover_storage,
    discover_table_explorer_config,
    explore_table_scan,
    filter_table_prefixes,
    filter_catalogued_tables,
    format_materialization_timestamp,
    include_deep_linked_catalogued_table,
    inspect_table,
    overlay_table_catalogue,
    read_delta_table,
    read_parquet_table,
    render_asset_catalogue_status_cards,
    render_storage_health_cards,
    render_table_workbench_navigation,
    s3_bucket_health_frame,
    storage_health_action_markdown,
    table_asset_catalogue_frame,
    table_workbench_navigation_links,
    table_explorer_deep_link_from_query,
    table_prefix_discovery_frame,
    table_by_id,
)
from marimoserver.dagster_graphql import (
    DagsterAssetCatalogue,
    DagsterColumnMetadata,
    DagsterTableAsset,
)


class FakeBody:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def read(self) -> bytes:
        return self._data


class FakePaginator:
    def __init__(
        self,
        pages_by_bucket: Mapping[str, list[Mapping[str, object]]],
        errors_by_bucket: Mapping[str, Exception] | None = None,
    ) -> None:
        self._pages_by_bucket = pages_by_bucket
        self._errors_by_bucket = {} if errors_by_bucket is None else errors_by_bucket

    def paginate(self, *, Bucket: str) -> Iterable[Mapping[str, object]]:
        if Bucket in self._errors_by_bucket:
            raise self._errors_by_bucket[Bucket]
        return self._pages_by_bucket.get(Bucket, [])


class FakeS3Client:
    def __init__(
        self,
        *,
        bucket_names: list[object] | None = None,
        pages_by_bucket: Mapping[str, list[Mapping[str, object]]] | None = None,
        objects_by_key: Mapping[tuple[str, str], bytes] | None = None,
        list_error: Exception | None = None,
        list_errors_by_bucket: Mapping[str, Exception] | None = None,
    ) -> None:
        self._bucket_names = [] if bucket_names is None else bucket_names
        self._pages_by_bucket = {} if pages_by_bucket is None else pages_by_bucket
        self._objects_by_key = {} if objects_by_key is None else objects_by_key
        self._list_error = list_error
        self._list_errors_by_bucket = (
            {} if list_errors_by_bucket is None else list_errors_by_bucket
        )
        self.list_buckets_calls = 0

    def list_buckets(self) -> Mapping[str, object]:
        self.list_buckets_calls += 1
        if self._list_error is not None:
            raise self._list_error
        return {
            "Buckets": [
                {"Name": name} if isinstance(name, str) else name
                for name in self._bucket_names
            ]
        }

    def get_paginator(self, operation_name: str) -> FakePaginator:
        assert operation_name == "list_objects_v2"
        return FakePaginator(self._pages_by_bucket, self._list_errors_by_bucket)

    def get_object(self, *, Bucket: str, Key: str) -> Mapping[str, object]:
        return {"Body": FakeBody(self._objects_by_key[(Bucket, Key)])}


class FakeGraphQLClient:
    def __init__(self, payload: Mapping[str, object]) -> None:
        self.payload = payload

    def execute(
        self,
        query: str,
        variables: Mapping[str, object] | None = None,
        *,
        timeout_seconds: int | None = None,
    ) -> Mapping[str, object]:
        assert query
        assert variables is None
        assert timeout_seconds is None
        return self.payload


def test_discover_table_explorer_config_uses_compose_env() -> None:
    config = discover_table_explorer_config(
        {
            "AWS_ENDPOINT_URL": "http://localhost:4566",
            "AWS_DEFAULT_REGION": "ap-southeast-2",
            "AWS_ACCESS_KEY_ID": "local",
            "AWS_SECRET_ACCESS_KEY": "secret",
            "AWS_ALLOW_HTTP": "false",
            "DAGSTER_GRAPHQL_URL": "http://dagster.local/graphql",
        }
    )

    assert config.runtime_location == "local"
    assert config.default_buckets == DEFAULT_LOCAL_BUCKETS
    assert config.bucket_prefix == "dev-energy-market-"
    assert config.s3_client_kwargs() == {
        "endpoint_url": "http://localhost:4566",
        "region_name": "ap-southeast-2",
        "aws_access_key_id": "local",
        "aws_secret_access_key": "secret",
    }
    assert config.delta_storage_options() == {
        "AWS_ENDPOINT_URL": "http://localhost:4566",
        "AWS_REGION": "ap-southeast-2",
        "AWS_ACCESS_KEY_ID": "local",
        "AWS_SECRET_ACCESS_KEY": "secret",
        "AWS_ALLOW_HTTP": "false",
        "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
    }
    assert config.dagster_graphql_url == "http://dagster.local/graphql"
    assert config.full_table_scan_enabled is True
    assert config.max_preview_rows == 10_000


def test_discover_table_explorer_config_treats_blanks_as_unset() -> None:
    config = discover_table_explorer_config(
        {
            "AWS_ENDPOINT_URL": "",
            "AWS_DEFAULT_REGION": "",
            "AWS_ACCESS_KEY_ID": "",
            "AWS_SECRET_ACCESS_KEY": "",
            "AWS_ALLOW_HTTP": "",
            "DAGSTER_GRAPHQL_URL": "",
        }
    )

    assert config.aws_endpoint_url == "http://localstack:4566"
    assert config.aws_region == "ap-southeast-4"
    assert config.aws_access_key_id == "test"
    assert config.aws_secret_access_key == "test"
    assert config.aws_allow_http == "true"
    assert (
        config.dagster_graphql_url
        == "http://dagster-webserver-guest:3000/dagster-webserver/guest/graphql"
    )


def test_discover_table_explorer_config_uses_aws_runtime_defaults() -> None:
    config = discover_table_explorer_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "MARIMO_TABLE_BUCKETS": "prod-aemo, prod-io-manager",
            "AWS_DEFAULT_REGION": "ap-southeast-2",
            "DAGSTER_GRAPHQL_URL": (
                "http://webserver-guest.dagster:3000/dagster-webserver/guest/graphql"
            ),
        }
    )

    assert config.runtime_location == "aws"
    assert config.default_buckets == ("prod-aemo", "prod-io-manager")
    assert config.aws_endpoint_url is None
    assert config.aws_access_key_id is None
    assert config.aws_secret_access_key is None
    assert config.aws_allow_http == "false"
    assert config.s3_client_kwargs() == {"region_name": "ap-southeast-2"}
    assert config.delta_storage_options() == {
        "AWS_REGION": "ap-southeast-2",
        "AWS_ALLOW_HTTP": "false",
        "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
    }
    assert (
        config.dagster_graphql_url
        == "http://webserver-guest.dagster:3000/dagster-webserver/guest/graphql"
    )
    assert config.full_table_scan_enabled is False
    assert config.max_preview_rows == 100


def test_discover_table_explorer_config_uses_aws_bucket_fallbacks() -> None:
    config = discover_table_explorer_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "IO_MANAGER_BUCKET": "prod-energy-market-io-manager",
            "MARIMO_MAX_PREVIEW_ROWS": "not-an-int",
            "MARIMO_FULL_TABLE_SCAN_ENABLED": "yes",
        }
    )

    assert config.aws_runtime is True
    assert config.default_buckets == (
        "prod-energy-market-aemo",
        "prod-energy-market-io-manager",
    )
    assert config.max_preview_rows == 100
    assert config.full_table_scan_enabled is True


def test_bounded_read_diagnostics_render_local_runtime_configuration() -> None:
    gas_config = discover_dashboard_config({})
    table_config = discover_table_explorer_config({})

    runtime_rows = {
        row["setting"]: row
        for row in bounded_read_runtime_frame(gas_config, table_config).to_dicts()
    }
    state_rows = {
        row["state"]: row
        for row in bounded_read_state_frame(gas_config, table_config).to_dicts()
    }
    summary_html = render_bounded_read_summary_cards(gas_config, table_config)

    assert endpoint_mode_label(table_config) == "S3-compatible endpoint override"
    assert runtime_rows["Runtime location"]["value"] == "local"
    assert runtime_rows["Configured buckets"]["value"] == ", ".join(
        DEFAULT_LOCAL_BUCKETS
    )
    assert runtime_rows["Table preview row cap"]["value"] == "10,000"
    assert runtime_rows["Gas dashboard preview row cap"]["value"] == "100"
    assert runtime_rows["Full-table-scan flag"]["value"] == "True"
    assert runtime_rows["Active table explorer policy"]["value"] == "Full table scan"
    assert runtime_rows["Active gas dashboard policy"]["value"] == "Full table scan"
    assert state_rows["Bounded preview"]["active"] == "False"
    assert state_rows["Full table scan"]["active"] == "True"
    assert "local" in summary_html
    assert "Full table scan" in summary_html
    assert "S3-compatible endpoint override" in summary_html


def test_bounded_read_diagnostics_render_aws_runtime_configuration() -> None:
    environment = {
        "DEVELOPMENT_LOCATION": "aws",
        "AEMO_BUCKET": "prod-energy-market-aemo",
        "MARIMO_TABLE_BUCKETS": "prod-energy-market-aemo, prod-energy-market-io",
        "MARIMO_MAX_PREVIEW_ROWS": "125",
        "MARIMO_FULL_TABLE_SCAN_ENABLED": "false",
        "AWS_DEFAULT_REGION": "ap-southeast-2",
    }
    gas_config = discover_dashboard_config(environment)
    table_config = discover_table_explorer_config(environment)

    runtime_rows = {
        row["setting"]: row
        for row in bounded_read_runtime_frame(gas_config, table_config).to_dicts()
    }
    state_rows = {
        row["state"]: row
        for row in bounded_read_state_frame(gas_config, table_config).to_dicts()
    }
    summary_html = render_bounded_read_summary_cards(gas_config, table_config)

    assert endpoint_mode_label(table_config) == "AWS service endpoints"
    assert runtime_rows["Runtime location"]["value"] == "aws"
    assert runtime_rows["Endpoint mode"]["value"] == "AWS service endpoints"
    assert runtime_rows["Configured buckets"]["value"] == (
        "prod-energy-market-aemo, prod-energy-market-io"
    )
    assert runtime_rows["Gas model AEMO bucket"]["value"] == "prod-energy-market-aemo"
    assert runtime_rows["Table preview row cap"]["value"] == "125"
    assert runtime_rows["Gas dashboard preview row cap"]["value"] == "125"
    assert runtime_rows["Full-table-scan flag"]["value"] == "False"
    assert runtime_rows["Active table explorer policy"]["value"] == (
        "Bounded preview: 125 rows max"
    )
    assert runtime_rows["Active gas dashboard policy"]["value"] == (
        "Bounded preview: 125 rows max"
    )
    assert state_rows["Bounded preview"]["active"] == "True"
    assert state_rows["Full table scan"]["active"] == "False"
    assert "AWS service endpoints" in summary_html
    assert "Bounded preview: 125 rows max" in summary_html


def test_create_s3_client_uses_configured_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = discover_table_explorer_config({"AWS_ENDPOINT_URL": "http://s3.local"})
    captured: list[tuple[str, dict[str, str]]] = []
    fake_client = FakeS3Client()

    def client(service_name: str, **kwargs: str) -> S3Client:
        captured.append((service_name, kwargs))
        return fake_client

    monkeypatch.setattr("marimoserver.table_explorer.boto3.client", client)

    assert create_s3_client(config) is fake_client
    assert captured == [("s3", config.s3_client_kwargs())]


def test_discover_table_catalogue_uses_configured_graphql_url() -> None:
    config = discover_table_explorer_config(
        {"DAGSTER_GRAPHQL_URL": "http://dagster/graphql"}
    )

    catalogue = discover_table_catalogue(
        config,
        FakeGraphQLClient(
            {
                "assetNodes": [
                    {
                        "assetKey": {"path": ["silver", "gas", "table"]},
                        "kinds": ["table"],
                        "metadataEntries": [],
                        "assetMaterializations": [],
                    }
                ]
            }
        ),
    )

    assert catalogue.url == "http://dagster/graphql"
    assert [asset.asset_id for asset in catalogue.assets] == ["silver/gas/table"]


def test_overlay_table_catalogue_distinguishes_storage_states() -> None:
    live_table = TablePrefix(
        bucket="dev-energy-market-aemo",
        prefix="silver/gas_model/live",
        table_format=TableFormat.PARQUET,
        parquet_files=("silver/gas_model/live/part-000.parquet",),
    )
    storage_only_table = TablePrefix(
        bucket="dev-energy-market-aemo",
        prefix="bronze/storage_only",
        table_format=TableFormat.DELTA,
        parquet_files=(),
    )
    discovery = StorageDiscovery(
        buckets=(),
        tables=(live_table, storage_only_table),
        bucket_listing_error=None,
    )
    catalogue = DagsterAssetCatalogue(
        url="http://dagster/graphql",
        error=None,
        assets=(
            _asset(
                ("silver", "gas_model", "live"),
                uri="s3://dev-energy-market-aemo/silver/gas_model/live/",
                latest_materialization_timestamp=1_714_000_000,
            ),
            _asset(
                ("silver", "gas_model", "missing"),
                uri="s3://dev-energy-market-aemo/silver/gas_model/missing",
                latest_materialization_timestamp=1_714_000_001,
            ),
            _asset(
                ("silver", "gas_model", "unmaterialized"),
                uri="s3://dev-energy-market-aemo/silver/gas_model/unmaterialized",
                latest_materialization_timestamp=None,
            ),
            _asset(
                ("silver", "gas_model", "schema_only"),
                uri=None,
                latest_materialization_timestamp=None,
            ),
        ),
    )

    entries = overlay_table_catalogue(discovery, catalogue)

    assert [(entry.display_name, entry.status) for entry in entries] == [
        ("dev-energy-market-aemo/bronze/storage_only", TableAvailability.LIVE),
        ("silver/gas_model/live", TableAvailability.LIVE),
        ("silver/gas_model/missing", TableAvailability.MISSING),
        ("silver/gas_model/schema_only", TableAvailability.UNMATERIALIZED),
        ("silver/gas_model/unmaterialized", TableAvailability.UNMATERIALIZED),
    ]
    assert entries[1].table == live_table
    assert entries[1].uri == "s3://dev-energy-market-aemo/silver/gas_model/live/"
    assert entries[0].uri == "s3://dev-energy-market-aemo/bronze/storage_only"
    assert catalogued_table_by_id(entries, entries[2].entry_id) == entries[2]
    assert catalogued_table_by_id(entries, None) is None
    assert catalogued_table_by_id(entries, "missing") is None


def test_overlay_table_catalogue_keeps_storage_when_graphql_unavailable() -> None:
    table = TablePrefix(
        bucket="dev-energy-market-aemo",
        prefix="silver/gas_model/live",
        table_format=TableFormat.PARQUET,
        parquet_files=("silver/gas_model/live/part-000.parquet",),
    )
    discovery = StorageDiscovery(
        buckets=(),
        tables=(table,),
        bucket_listing_error=None,
    )
    catalogue = DagsterAssetCatalogue(
        url="http://dagster/graphql",
        error="Connection refused",
        assets=(),
    )

    entries = overlay_table_catalogue(discovery, catalogue)

    assert entries == (
        CataloguedTable(
            entry_id="storage:dev-energy-market-aemo/silver/gas_model/live",
            status=TableAvailability.GRAPHQL_UNAVAILABLE,
            asset=None,
            table=table,
        ),
    )


def test_asset_catalogue_dashboard_helpers_report_graphql_success() -> None:
    live_table = TablePrefix(
        bucket="dev-energy-market-aemo",
        prefix="silver/gas_model/live",
        table_format=TableFormat.PARQUET,
        parquet_files=("silver/gas_model/live/part-000.parquet",),
    )
    missing_asset = DagsterTableAsset(
        asset_key=("silver", "gas_model", "missing"),
        group_name="gas_model",
        kinds=("table",),
        description="Missing table.",
        uri="s3://dev-energy-market-aemo/silver/gas_model/missing",
        columns=(),
        is_materializable=False,
        is_executable=True,
        latest_materialization_timestamp=1_714_000_100,
    )
    discovery = StorageDiscovery(
        buckets=(),
        tables=(live_table,),
        bucket_listing_error=None,
    )
    catalogue = DagsterAssetCatalogue(
        url="http://dagster/graphql",
        error=None,
        assets=(
            _asset(
                ("silver", "gas_model", "live"),
                uri=live_table.uri,
                latest_materialization_timestamp=1_714_000_000,
            ),
            missing_asset,
        ),
    )
    entries = overlay_table_catalogue(discovery, catalogue)

    summary = build_asset_catalogue_summary(catalogue, entries)
    action_markdown = asset_catalogue_action_markdown(summary)
    card_html = render_asset_catalogue_status_cards(summary)
    catalogue_frame = table_asset_catalogue_frame(entries)
    schema_frame = asset_schema_metadata_frame(entries)

    assert summary.graphql_available is True
    assert summary.table_asset_count == 2
    assert summary.live_count == 1
    assert summary.missing_count == 1
    assert summary.schema_asset_count == 1
    assert summary.uri_asset_count == 2
    assert summary.materializable_asset_count == 1
    assert summary.executable_asset_count == 2
    assert summary.latest_materialization_label == "2024-04-24T23:08:20+00:00"
    assert "Missing tables" in action_markdown
    assert 'class="asset-catalogue-card asset-catalogue-card--ready"' in card_html
    assert "Dagster GraphQL" in card_html
    assert catalogue_frame["group"].to_list() == ["gas_model", "gas_model"]
    assert catalogue_frame["kinds"].to_list() == ["parquet, table", "table"]
    assert catalogue_frame["materializable"].to_list() == ["Yes", "No"]
    assert catalogue_frame["executable"].to_list() == ["Yes", "Yes"]
    assert catalogue_frame["schema available"].to_list() == ["Yes", "No"]
    assert schema_frame.row(0, named=True) == {
        "asset key": "silver/gas_model/live",
        "group": "gas_model",
        "column": "id",
        "type": "Int64",
        "description": "",
    }


def test_asset_catalogue_dashboard_helpers_keep_storage_rows_when_graphql_errors() -> (
    None
):
    table = TablePrefix(
        bucket="dev-energy-market-aemo",
        prefix="silver/gas_model/live",
        table_format=TableFormat.DELTA,
        parquet_files=(),
    )
    entries = overlay_table_catalogue(
        StorageDiscovery(buckets=(), tables=(table,), bucket_listing_error=None),
        DagsterAssetCatalogue(
            url="http://dagster/graphql",
            error="Connection refused",
            assets=(),
        ),
    )
    summary = build_asset_catalogue_summary(
        DagsterAssetCatalogue(
            url="http://dagster/graphql",
            error="Connection refused",
            assets=(),
        ),
        entries,
    )

    cards = explorer.asset_catalogue_status_cards(summary)
    action_markdown = asset_catalogue_action_markdown(summary)
    catalogue_frame = table_asset_catalogue_frame(entries)
    schema_frame = asset_schema_metadata_frame(entries)

    assert cards[0].state is AssetCatalogueState.UNAVAILABLE
    assert summary.graphql_unavailable_count == 1
    assert summary.local_table_prefix_count == 1
    assert summary.degraded_table_count == 1
    assert "Storage-only table rows remain usable" in action_markdown
    assert catalogue_frame.row(0, named=True)["status"] == (
        TableAvailability.GRAPHQL_UNAVAILABLE.value
    )
    assert catalogue_frame.row(0, named=True)["uri"] == (
        "s3://dev-energy-market-aemo/silver/gas_model/live"
    )
    assert schema_frame.row(0, named=True)["asset key"] == (
        "No schema metadata available"
    )


def test_asset_catalogue_dashboard_helpers_cover_empty_ready_and_unmaterialized() -> (
    None
):
    empty_catalogue = DagsterAssetCatalogue(
        url="http://dagster/graphql",
        error=None,
        assets=(),
    )
    empty_summary = build_asset_catalogue_summary(empty_catalogue, ())
    empty_cards = explorer.asset_catalogue_status_cards(empty_summary)
    empty_frame = table_asset_catalogue_frame(())

    assert [card.state for card in empty_cards] == [
        AssetCatalogueState.EMPTY,
        AssetCatalogueState.EMPTY,
        AssetCatalogueState.EMPTY,
        AssetCatalogueState.EMPTY,
    ]
    assert "no table assets were returned" in asset_catalogue_action_markdown(
        empty_summary
    )
    assert empty_frame.row(0, named=True)["status"] == AssetCatalogueState.EMPTY.value

    live_table = TablePrefix(
        bucket="dev-energy-market-aemo",
        prefix="silver/gas_model/live",
        table_format=TableFormat.PARQUET,
        parquet_files=("silver/gas_model/live/part-000.parquet",),
    )
    ready_catalogue = DagsterAssetCatalogue(
        url="http://dagster/graphql",
        error=None,
        assets=(
            _asset(
                ("silver", "gas_model", "live"),
                uri=live_table.uri,
                latest_materialization_timestamp=1_714_000_000,
            ),
        ),
    )
    ready_entries = overlay_table_catalogue(
        StorageDiscovery(buckets=(), tables=(live_table,), bucket_listing_error=None),
        ready_catalogue,
    )
    ready_summary = build_asset_catalogue_summary(ready_catalogue, ready_entries)
    ready_cards = explorer.asset_catalogue_status_cards(ready_summary)

    assert [card.state for card in ready_cards] == [
        AssetCatalogueState.READY,
        AssetCatalogueState.READY,
        AssetCatalogueState.READY,
        AssetCatalogueState.READY,
    ]
    assert asset_catalogue_action_markdown(ready_summary) == (
        "Dagster GraphQL and table asset coverage are usable under the current configuration."
    )

    unmaterialized_catalogue = DagsterAssetCatalogue(
        url="http://dagster/graphql",
        error=None,
        assets=(
            _asset(
                ("silver", "gas_model", "unmaterialized"),
                uri=None,
                latest_materialization_timestamp=None,
            ),
        ),
    )
    unmaterialized_entries = overlay_table_catalogue(
        StorageDiscovery(buckets=(), tables=(), bucket_listing_error=None),
        unmaterialized_catalogue,
    )
    unmaterialized_summary = build_asset_catalogue_summary(
        unmaterialized_catalogue,
        unmaterialized_entries,
    )
    unmaterialized_cards = explorer.asset_catalogue_status_cards(unmaterialized_summary)

    assert unmaterialized_summary.unmaterialized_count == 1
    assert unmaterialized_cards[-1].state is AssetCatalogueState.ATTENTION
    assert "Unmaterialized assets" in asset_catalogue_action_markdown(
        unmaterialized_summary
    )


def test_filter_catalogued_tables_combines_group_layer_status_and_search() -> None:
    live_table = TablePrefix(
        bucket="dev-energy-market-aemo",
        prefix="silver/gas_model/live",
        table_format=TableFormat.PARQUET,
        parquet_files=("silver/gas_model/live/part-000.parquet",),
    )
    live_entry = CataloguedTable(
        entry_id="asset:silver/gas_model/live",
        status=TableAvailability.LIVE,
        asset=_asset(
            ("silver", "gas_model", "live"),
            uri=live_table.uri,
            latest_materialization_timestamp=1_714_000_000,
        ),
        table=live_table,
    )
    missing_entry = CataloguedTable(
        entry_id="asset:bronze/raw/missing",
        status=TableAvailability.MISSING,
        asset=_asset(
            ("bronze", "raw", "missing"),
            uri="s3://dev-energy-market-aemo/bronze/raw/missing",
            latest_materialization_timestamp=1_714_000_001,
            group_name="raw",
        ),
        table=None,
    )
    uri_only_entry = CataloguedTable(
        entry_id="asset:silver_gas_dim_zone",
        status=TableAvailability.UNMATERIALIZED,
        asset=_asset(
            ("silver_gas_dim_zone",),
            uri="s3://dev-energy-market-aemo/silver/gas_model/silver_gas_dim_zone",
            latest_materialization_timestamp=None,
        ),
        table=None,
    )
    storage_entry = CataloguedTable(
        entry_id="storage:dev-energy-market-landing/bronze/storage_only",
        status=TableAvailability.LIVE,
        asset=None,
        table=TablePrefix(
            bucket="dev-energy-market-landing",
            prefix="bronze/storage_only",
            table_format=TableFormat.PARQUET,
            parquet_files=("bronze/storage_only/part-000.parquet",),
        ),
    )

    entries = (live_entry, missing_entry, storage_entry)

    assert catalogued_table_group(storage_entry) == "Storage only"
    assert catalogued_table_layers_or_domains(live_entry) == ("silver", "gas_model")
    assert catalogued_table_layers_or_domains(uri_only_entry) == (
        "silver",
        "gas_model",
    )
    assert catalogued_table_layers_or_domains(
        CataloguedTable(
            entry_id="asset:schema_only",
            status=TableAvailability.UNMATERIALIZED,
            asset=_asset(
                ("schema_only",),
                uri=None,
                latest_materialization_timestamp=None,
            ),
            table=None,
        )
    ) == ("schema_only",)
    assert filter_catalogued_tables(
        entries,
        groups=("gas_model",),
        layers_or_domains=("silver",),
        statuses=(TableAvailability.LIVE,),
        search="live",
    ) == (live_entry,)
    assert filter_catalogued_tables(entries, layers_or_domains=("silver",)) == (
        live_entry,
    )
    assert filter_catalogued_tables(entries, statuses=("Missing",)) == (missing_entry,)
    assert filter_catalogued_tables(entries, search="storage only") == (storage_entry,)


def test_table_workbench_navigation_links_readiness_bounded_and_concepts() -> None:
    table_name = "silver_gas_fact_market_price"
    table = TablePrefix(
        bucket="dev-energy-market-aemo",
        prefix=f"silver/gas_model/{table_name}",
        table_format=TableFormat.PARQUET,
        parquet_files=(f"silver/gas_model/{table_name}/part-000.parquet",),
    )
    entry = CataloguedTable(
        entry_id=f"asset:silver/gas_model/{table_name}",
        status=TableAvailability.LIVE,
        asset=_asset(
            ("silver", "gas_model", table_name),
            uri=table.uri,
            latest_materialization_timestamp=1_714_000_000,
        ),
        table=table,
    )

    links = table_workbench_navigation_links(entry)
    routes_by_label = {link.label: link.route for link in links}
    concept_ids = [
        concept.concept_id for concept in concept_gallery_entries_for_table(entry)
    ]
    metadata_rows = concept_gallery_metadata_frame(entry).to_dicts()
    html = render_table_workbench_navigation(entry)

    assert concept_gallery_asset_id(entry) == (
        "silver.gas_model.silver_gas_fact_market_price"
    )
    assert routes_by_label["Data readiness overview"] == DATA_READINESS_ROUTE
    assert (
        routes_by_label["AWS bounded read diagnostics"]
        == AWS_BOUNDED_READ_DIAGNOSTICS_ROUTE
    )
    assert routes_by_label["Concept gallery"] == (
        "/marimo#concept-gas-model-table-explorer"
    )
    assert "gas-model-table-explorer" in concept_ids
    assert "data-readiness-overview" in concept_ids
    assert {row["concept id"]: row["notebook route"] for row in metadata_rows}[
        "data-readiness-overview"
    ] == "/marimo/data_readiness_overview/"
    assert 'href="/marimo/data_readiness_overview/"' in html
    assert 'href="/marimo/aws_bounded_read_diagnostics/"' in html
    assert 'href="/marimo#concept-gas-model-table-explorer"' in html
    assert 'data-link-scope="mapped silver.gas_model asset"' in html


def test_concept_gallery_metadata_maps_storage_prefixes_and_empty_states() -> None:
    storage_entry = CataloguedTable(
        entry_id="storage:dev-energy-market-aemo/silver/gas_model/silver_gas_dim_date",
        status=TableAvailability.LIVE,
        asset=None,
        table=TablePrefix(
            bucket="dev-energy-market-aemo",
            prefix="silver/gas_model/silver_gas_dim_date",
            table_format=TableFormat.PARQUET,
            parquet_files=("silver/gas_model/silver_gas_dim_date/part-000.parquet",),
        ),
    )
    unmapped_entry = CataloguedTable(
        entry_id="storage:dev-energy-market-aemo/bronze/raw",
        status=TableAvailability.LIVE,
        asset=None,
        table=TablePrefix(
            bucket="dev-energy-market-aemo",
            prefix="bronze/raw",
            table_format=TableFormat.PARQUET,
            parquet_files=("bronze/raw/part-000.parquet",),
        ),
    )

    storage_rows = concept_gallery_metadata_frame(storage_entry).to_dicts()
    unmapped_row = concept_gallery_metadata_frame(unmapped_entry).row(0, named=True)

    assert concept_gallery_asset_id(storage_entry) == (
        "silver.gas_model.silver_gas_dim_date"
    )
    assert "gas-model-table-explorer" in {row["concept id"] for row in storage_rows}
    assert concept_gallery_asset_id(unmapped_entry) is None
    assert unmapped_row["concept id"] == "No mapped concept-gallery metadata"
    assert unmapped_row["concept gallery"] == (
        "/marimo#concept-gas-model-table-explorer"
    )


def test_table_workbench_navigation_describes_degraded_statuses() -> None:
    unmaterialized_entry = CataloguedTable(
        entry_id="asset:silver/gas_model/unmaterialized",
        status=TableAvailability.UNMATERIALIZED,
        asset=_asset(
            ("silver", "gas_model", "unmaterialized"),
            uri=None,
            latest_materialization_timestamp=None,
        ),
        table=None,
    )
    missing_entry = CataloguedTable(
        entry_id="asset:silver/gas_model/missing",
        status=TableAvailability.MISSING,
        asset=_asset(
            ("silver", "gas_model", "missing"),
            uri="s3://dev-energy-market-aemo/silver/gas_model/missing",
            latest_materialization_timestamp=1_714_000_000,
        ),
        table=None,
    )
    graphql_unavailable_entry = CataloguedTable(
        entry_id="storage:dev-energy-market-aemo/silver/gas_model/live",
        status=TableAvailability.GRAPHQL_UNAVAILABLE,
        asset=None,
        table=TablePrefix(
            bucket="dev-energy-market-aemo",
            prefix="silver/gas_model/live",
            table_format=TableFormat.PARQUET,
            parquet_files=("silver/gas_model/live/part-000.parquet",),
        ),
    )

    unmaterialized_links = table_workbench_navigation_links(
        unmaterialized_entry,
        entries=(),
    )
    missing_links = table_workbench_navigation_links(missing_entry, entries=())
    graphql_links = table_workbench_navigation_links(
        graphql_unavailable_entry,
        entries=(),
    )

    assert _link_detail(unmaterialized_links, "Data readiness overview") == (
        "Review why Dagster knows the asset before storage is materialized."
    )
    assert _link_detail(missing_links, "Data readiness overview") == (
        "Review the missing-storage readiness state and expected S3 prefix."
    )
    assert _link_detail(graphql_links, "Data readiness overview") == (
        "Review storage-only readiness while Dagster GraphQL is unavailable."
    )
    assert (
        _link_detail(
            unmaterialized_links,
            "AWS bounded read diagnostics",
        )
        == "Review row-limit policy before previewing this asset after it materializes."
    )


def test_concept_gallery_asset_id_uses_uri_fallback_and_rejects_invalid_keys() -> None:
    uri_fallback_entry = CataloguedTable(
        entry_id="asset:legacy/table",
        status=TableAvailability.UNMATERIALIZED,
        asset=_asset(
            ("legacy", "table"),
            uri=(
                "s3://dev-energy-market-aemo/silver/gas_model/"
                "silver_gas_fact_schedule_run"
            ),
            latest_materialization_timestamp=None,
        ),
        table=None,
    )
    invalid_key_entry = CataloguedTable(
        entry_id="asset:bronze/raw/table",
        status=TableAvailability.UNMATERIALIZED,
        asset=_asset(
            ("bronze", "raw", "table"),
            uri=None,
            latest_materialization_timestamp=None,
        ),
        table=None,
    )
    blank_table_name_entry = CataloguedTable(
        entry_id="asset:silver/gas_model/",
        status=TableAvailability.UNMATERIALIZED,
        asset=_asset(
            ("silver", "gas_model", ""),
            uri=None,
            latest_materialization_timestamp=None,
        ),
        table=None,
    )

    assert concept_gallery_asset_id(uri_fallback_entry) == (
        "silver.gas_model.silver_gas_fact_schedule_run"
    )
    assert concept_gallery_asset_id(invalid_key_entry) is None
    assert concept_gallery_asset_id(blank_table_name_entry) is None


def test_table_explorer_deep_link_from_query_normalizes_url_defaults() -> None:
    deep_link = table_explorer_deep_link_from_query(
        {
            "search": ["", " silver_gas_fact_market_price "],
            "table": " asset:silver/gas_model/silver_gas_fact_market_price ",
            "asset": ["asset:silver/gas_model/silver_gas_dim_facility"],
        }
    )

    assert deep_link.search == "silver_gas_fact_market_price"
    assert (
        deep_link.table_entry_id
        == "asset:silver/gas_model/silver_gas_fact_market_price"
    )
    assert deep_link.asset_entry_id == "asset:silver/gas_model/silver_gas_dim_facility"
    assert (
        deep_link.requested_entry_id
        == "asset:silver/gas_model/silver_gas_fact_market_price"
    )
    asset_deep_link = table_explorer_deep_link_from_query(
        {"asset": "asset:silver/gas_model/silver_gas_dim_facility"}
    )

    assert (
        asset_deep_link.requested_entry_id
        == "asset:silver/gas_model/silver_gas_dim_facility"
    )


def test_table_explorer_deep_link_keeps_requested_entry_selectable() -> None:
    live_entry = CataloguedTable(
        entry_id="asset:silver/gas_model/live",
        status=TableAvailability.LIVE,
        asset=_asset(
            ("silver", "gas_model", "live"),
            uri="s3://dev-energy-market-aemo/silver/gas_model/live",
            latest_materialization_timestamp=None,
        ),
        table=None,
    )
    missing_entry = CataloguedTable(
        entry_id="asset:silver/gas_model/missing",
        status=TableAvailability.MISSING,
        asset=_asset(
            ("silver", "gas_model", "missing"),
            uri="s3://dev-energy-market-aemo/silver/gas_model/missing",
            latest_materialization_timestamp=None,
        ),
        table=None,
    )
    entries = (live_entry, missing_entry)
    filtered_entries = filter_catalogued_tables(entries, search="live")

    linked_entries = include_deep_linked_catalogued_table(
        entries,
        filtered_entries,
        missing_entry.entry_id,
    )

    assert linked_entries == (missing_entry, live_entry)
    assert (
        include_deep_linked_catalogued_table(entries, filtered_entries, None)
        == filtered_entries
    )
    assert (
        include_deep_linked_catalogued_table(entries, filtered_entries, "unknown")
        == filtered_entries
    )
    assert (
        include_deep_linked_catalogued_table(
            entries,
            linked_entries,
            missing_entry.entry_id,
        )
        == linked_entries
    )
    assert (
        default_catalogued_table_entry_id(linked_entries, missing_entry.entry_id)
        == missing_entry.entry_id
    )
    assert (
        default_catalogued_table_entry_id(linked_entries, "unknown")
        == missing_entry.entry_id
    )
    assert default_catalogued_table_entry_id((), missing_entry.entry_id) is None


def test_catalogued_table_properties_fall_back_to_entry_id() -> None:
    entry = CataloguedTable(
        entry_id="entry",
        status=TableAvailability.UNMATERIALIZED,
        asset=None,
        table=None,
    )

    assert entry.display_name == "entry"
    assert entry.uri is None
    assert catalogued_table_layers_or_domains(entry) == ()
    assert catalogued_table_layers_or_domains(
        CataloguedTable(
            entry_id="storage:bucket/",
            status=TableAvailability.LIVE,
            asset=None,
            table=TablePrefix(
                bucket="bucket",
                prefix="",
                table_format=TableFormat.PARQUET,
                parquet_files=("part-000.parquet",),
            ),
        )
    ) == ("bucket",)


def test_format_materialization_timestamp_returns_utc_iso_string() -> None:
    assert format_materialization_timestamp(None) == ""
    assert format_materialization_timestamp(0) == "1970-01-01T00:00:00+00:00"
    assert explorer._s3_table_location("http://not-s3/table") is None


def test_discover_storage_reports_bucket_health_and_tables() -> None:
    config = discover_table_explorer_config({})
    fake_client = FakeS3Client(
        bucket_names=[
            "dev-energy-market-aemo",
            "dev-energy-market-extra",
            "not-energy-market",
            {"Name": 123},
            123,
        ],
        pages_by_bucket={
            "dev-energy-market-aemo": [
                {
                    "Contents": [
                        {"Key": "silver/gas/_delta_log/000000.json"},
                        {"Key": "silver/gas/part-000.parquet"},
                        {"Key": "silver/gas/gas_date=2026-01-01/part-001.parquet"},
                    ]
                }
            ],
            "dev-energy-market-landing": [{"Contents": []}],
            "dev-energy-market-archive": [
                {"Contents": 5},
                {"Contents": ["bad-item"]},
                {"Contents": [{"Key": 5}]},
                {
                    "Contents": [
                        {"Key": "archive/raw-1.csv"},
                        {"Key": "archive/raw-2.csv"},
                        {"Key": "archive/raw-3.csv"},
                    ]
                },
            ],
            "dev-energy-market-extra": [
                {
                    "Contents": [
                        {"Key": ("bronze/prices/gas_date=2026-01-01/part-000.parquet")}
                    ]
                }
            ],
        },
        list_errors_by_bucket={
            "dev-energy-market-io-manager": RuntimeError("bucket denied")
        },
    )

    discovery = discover_storage(
        config,
        s3_client=fake_client,
        object_limit_per_bucket=2,
    )

    assert discovery.bucket_listing_error is None
    assert [bucket.name for bucket in discovery.buckets] == [
        "dev-energy-market-aemo",
        "dev-energy-market-landing",
        "dev-energy-market-archive",
        "dev-energy-market-io-manager",
        "dev-energy-market-extra",
    ]
    assert discovery.buckets[0] == BucketStatus(
        name="dev-energy-market-aemo",
        is_default=True,
        discovered=True,
        reachable=True,
        object_count=2,
        table_count=1,
        truncated=True,
        error=None,
    )
    assert discovery.buckets[1].table_count == 0
    assert discovery.buckets[2].truncated
    assert discovery.buckets[3].error == "RuntimeError: bucket denied"
    assert not discovery.buckets[3].reachable
    assert not discovery.buckets[4].is_default
    assert [table.table_id for table in discovery.tables] == [
        "dev-energy-market-aemo/silver/gas",
        "dev-energy-market-extra/bronze/prices",
    ]
    assert discovery.tables[0].table_format is TableFormat.DELTA
    assert discovery.tables[1].table_format is TableFormat.PARQUET


def test_discover_storage_uses_defaults_when_bucket_listing_fails() -> None:
    config = discover_table_explorer_config({})
    fake_client = FakeS3Client(list_error=RuntimeError("list failed"))

    discovery = discover_storage(config, s3_client=fake_client)

    assert discovery.bucket_listing_error == "RuntimeError: list failed"
    assert [bucket.name for bucket in discovery.buckets] == list(DEFAULT_LOCAL_BUCKETS)
    assert all(bucket.reachable for bucket in discovery.buckets)
    assert discovery.tables == ()


def test_discover_storage_skips_account_bucket_listing_in_aws_runtime() -> None:
    config = discover_table_explorer_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "MARIMO_TABLE_BUCKETS": "prod-energy-market-aemo,prod-energy-market-io-manager",
        }
    )
    fake_client = FakeS3Client(
        list_error=RuntimeError("list all buckets denied"),
        pages_by_bucket={
            "prod-energy-market-aemo": [
                {"Contents": [{"Key": "silver/gas/part-000.parquet"}]}
            ],
            "prod-energy-market-io-manager": [{"Contents": []}],
        },
    )

    discovery = discover_storage(config, s3_client=fake_client)

    assert fake_client.list_buckets_calls == 0
    assert discovery.bucket_listing_error is None
    assert [bucket.name for bucket in discovery.buckets] == [
        "prod-energy-market-aemo",
        "prod-energy-market-io-manager",
    ]
    assert all(bucket.is_default for bucket in discovery.buckets)
    assert [table.table_id for table in discovery.tables] == [
        "prod-energy-market-aemo/silver/gas"
    ]
    summary = build_bucket_health_summary(config, discovery)
    html = render_storage_health_cards(summary)

    assert summary.aws_runtime
    assert "AWS mode checks configured buckets only" in html


def test_s3_bucket_health_dashboard_helpers_cover_bucket_states() -> None:
    delta_table = TablePrefix(
        bucket="dev-energy-market-aemo",
        prefix="silver/gas_model/delta",
        table_format=TableFormat.DELTA,
        parquet_files=("silver/gas_model/delta/part-000.parquet",),
    )
    parquet_table = TablePrefix(
        bucket="dev-energy-market-archive",
        prefix="archive/raw",
        table_format=TableFormat.PARQUET,
        parquet_files=("archive/raw/part-000.parquet",),
    )
    buckets = (
        BucketStatus(
            name="dev-energy-market-aemo",
            is_default=True,
            discovered=True,
            reachable=True,
            object_count=3,
            table_count=1,
            truncated=False,
            error=None,
        ),
        BucketStatus(
            name="dev-energy-market-landing",
            is_default=True,
            discovered=True,
            reachable=True,
            object_count=0,
            table_count=0,
            truncated=False,
            error=None,
        ),
        BucketStatus(
            name="dev-energy-market-archive",
            is_default=True,
            discovered=True,
            reachable=True,
            object_count=10_000,
            table_count=1,
            truncated=True,
            error=None,
        ),
        BucketStatus(
            name="dev-energy-market-io-manager",
            is_default=True,
            discovered=False,
            reachable=False,
            object_count=0,
            table_count=0,
            truncated=False,
            error="ClientError: NoSuchBucket",
        ),
        BucketStatus(
            name="dev-energy-market-denied",
            is_default=False,
            discovered=True,
            reachable=False,
            object_count=0,
            table_count=0,
            truncated=False,
            error="ClientError: AccessDenied",
        ),
    )
    discovery = StorageDiscovery(
        buckets=buckets,
        tables=(delta_table, parquet_table),
        bucket_listing_error="ListBuckets denied",
    )
    config = discover_table_explorer_config({})

    summary = build_bucket_health_summary(config, discovery)
    bucket_frame = s3_bucket_health_frame(discovery)
    prefix_frame = table_prefix_discovery_frame(discovery.tables)
    filtered_prefixes = filter_table_prefixes(
        discovery.tables,
        buckets=("dev-energy-market-aemo",),
        formats=(TableFormat.DELTA,),
        search="silver",
    )
    action_markdown = storage_health_action_markdown(summary)
    html = render_storage_health_cards(summary)

    assert [bucket_health_state(bucket) for bucket in buckets] == [
        BucketHealthState.REACHABLE,
        BucketHealthState.EMPTY,
        BucketHealthState.TRUNCATED,
        BucketHealthState.MISSING,
        BucketHealthState.UNAVAILABLE,
    ]
    assert summary.reachable_bucket_count == 3
    assert summary.populated_bucket_count == 2
    assert summary.empty_bucket_count == 1
    assert summary.truncated_bucket_count == 1
    assert summary.missing_bucket_count == 1
    assert summary.unavailable_bucket_count == 1
    assert summary.table_prefix_count == 2
    assert summary.delta_table_prefix_count == 1
    assert summary.parquet_table_prefix_count == 1
    assert bucket_frame["status"].to_list() == [
        BucketHealthState.REACHABLE.value,
        BucketHealthState.EMPTY.value,
        BucketHealthState.TRUNCATED.value,
        BucketHealthState.MISSING.value,
        BucketHealthState.UNAVAILABLE.value,
    ]
    assert bucket_frame["Delta prefixes"].to_list() == [1, 0, 0, 0, 0]
    assert bucket_frame["Parquet prefixes"].to_list() == [0, 0, 1, 0, 0]
    assert prefix_frame["format"].to_list() == [
        TableFormat.DELTA.value,
        TableFormat.PARQUET.value,
    ]
    assert filtered_prefixes == (delta_table,)
    assert "Missing buckets" in action_markdown
    assert "Truncated buckets" in action_markdown
    assert 'class="storage-health-card storage-health-card--truncated"' in html
    assert summary.degraded_bucket_count == 4


def test_s3_bucket_health_dashboard_helpers_cover_empty_summary_branches() -> None:
    config = discover_table_explorer_config({})
    delta_table = TablePrefix(
        bucket="dev-energy-market-aemo",
        prefix="silver/gas_model/live",
        table_format=TableFormat.DELTA,
        parquet_files=("silver/gas_model/live/part-000.parquet",),
    )
    empty_discovery = StorageDiscovery(
        buckets=(),
        tables=(),
        bucket_listing_error="ListBuckets denied",
    )
    ready_discovery = StorageDiscovery(
        buckets=(
            _bucket_status(
                name="dev-energy-market-aemo",
                reachable=True,
                object_count=1,
                table_count=1,
            ),
        ),
        tables=(delta_table,),
        bucket_listing_error=None,
    )
    no_table_discovery = StorageDiscovery(
        buckets=(
            _bucket_status(
                name="dev-energy-market-aemo",
                reachable=True,
                object_count=1,
                table_count=0,
            ),
        ),
        tables=(),
        bucket_listing_error=None,
    )
    all_empty_discovery = StorageDiscovery(
        buckets=(
            _bucket_status(
                name="dev-energy-market-aemo",
                reachable=True,
                object_count=0,
                table_count=0,
            ),
        ),
        tables=(),
        bucket_listing_error=None,
    )
    unavailable_discovery = StorageDiscovery(
        buckets=(
            _bucket_status(
                name="dev-energy-market-aemo",
                reachable=False,
                object_count=0,
                table_count=0,
                error="ClientError: AccessDenied",
            ),
        ),
        tables=(),
        bucket_listing_error=None,
    )
    partial_unavailable_discovery = StorageDiscovery(
        buckets=(
            _bucket_status(
                name="dev-energy-market-aemo",
                reachable=True,
                object_count=1,
                table_count=1,
            ),
            _bucket_status(
                name="dev-energy-market-landing",
                reachable=False,
                object_count=0,
                table_count=0,
                error="ClientError: AccessDenied",
            ),
        ),
        tables=(delta_table,),
        bucket_listing_error=None,
    )
    inconsistent_discovery = StorageDiscovery(
        buckets=(
            _bucket_status(
                name="dev-energy-market-aemo",
                reachable=False,
                object_count=0,
                table_count=0,
            ),
        ),
        tables=(),
        bucket_listing_error=None,
    )

    empty_summary = build_bucket_health_summary(config, empty_discovery)
    ready_summary = build_bucket_health_summary(config, ready_discovery)
    no_table_summary = build_bucket_health_summary(config, no_table_discovery)
    all_empty_summary = build_bucket_health_summary(config, all_empty_discovery)
    unavailable_summary = build_bucket_health_summary(config, unavailable_discovery)
    partial_unavailable_summary = build_bucket_health_summary(
        config,
        partial_unavailable_discovery,
    )

    assert s3_bucket_health_frame(empty_discovery).row(0, named=True)["bucket"] == (
        "No configured buckets"
    )
    assert table_prefix_discovery_frame(()).row(0, named=True)["bucket"] == (
        "No table prefixes discovered"
    )
    assert filter_table_prefixes((delta_table,), formats=("Parquet",)) == ()
    assert filter_table_prefixes((delta_table,), search="missing") == ()
    assert storage_health_action_markdown(ready_summary) == (
        "All checked buckets are reachable under the current configuration."
    )
    assert "No table prefixes were discovered" in storage_health_action_markdown(
        no_table_summary
    )
    assert (
        s3_bucket_health_frame(inconsistent_discovery).row(0, named=True)["detail"]
        == ""
    )
    assert "storage-health-card--empty" in render_storage_health_cards(empty_summary)
    assert "storage-health-card--empty" in render_storage_health_cards(
        all_empty_summary
    )
    assert "storage-health-card--reachable" in render_storage_health_cards(
        ready_summary
    )
    assert "storage-health-card--unavailable" in render_storage_health_cards(
        unavailable_summary
    )
    assert "storage-health-card--unavailable" in render_storage_health_cards(
        partial_unavailable_summary
    )


def test_classify_table_prefixes_handles_root_tables_and_case() -> None:
    root_tables = classify_table_prefixes(
        "bucket",
        ["_delta_log/000000.json", "part-000.parquet"],
    )
    parquet_tables = classify_table_prefixes(
        "bucket",
        ["reports/month=2026-01/file.PARQUET"],
    )
    root_parquet_tables = classify_table_prefixes("bucket", ["file.parquet"])

    assert [(table.table_id, table.table_format) for table in root_tables] == [
        ("bucket/", TableFormat.DELTA)
    ]
    assert [(table.table_id, table.table_format) for table in parquet_tables] == [
        ("bucket/reports", TableFormat.PARQUET)
    ]
    assert [(table.table_id, table.table_format) for table in root_parquet_tables] == [
        ("bucket/", TableFormat.PARQUET)
    ]
    assert root_tables[0].uri == "s3://bucket"
    assert root_tables[0].display_name == "bucket/"
    assert parquet_tables[0].uri == "s3://bucket/reports"
    assert parquet_tables[0].display_name == "bucket/reports"
    assert table_by_id(parquet_tables, "bucket/reports") == parquet_tables[0]
    assert table_by_id(parquet_tables, None) is None
    assert table_by_id(parquet_tables, "missing") is None


def test_read_delta_table_delegates_to_polars(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = discover_table_explorer_config({})
    table = TablePrefix(
        bucket="dev-energy-market-aemo",
        prefix="silver/gas",
        table_format=TableFormat.DELTA,
        parquet_files=(),
    )
    captured: list[tuple[str, dict[str, str]]] = []

    def read_delta(uri: str, storage_options: dict[str, str]) -> pl.DataFrame:
        captured.append((uri, storage_options))
        return pl.DataFrame({"id": [1]})

    monkeypatch.setattr("marimoserver.table_explorer.pl.read_delta", read_delta)

    dataframe = read_delta_table(table, config)

    assert dataframe.to_dict(as_series=False) == {"id": [1]}
    assert captured == [(table.uri, config.delta_storage_options())]


def test_read_delta_table_honours_row_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = discover_table_explorer_config({})
    table = TablePrefix(
        bucket="dev-energy-market-aemo",
        prefix="silver/gas",
        table_format=TableFormat.DELTA,
        parquet_files=(),
    )
    captured: list[tuple[str, dict[str, str]] | int] = []

    class FakeLazyFrame:
        def head(self, row_limit: int) -> Self:
            captured.append(row_limit)
            return self

        def collect(self) -> pl.DataFrame:
            return pl.DataFrame({"id": [1]})

    def scan_delta(uri: str, storage_options: dict[str, str]) -> FakeLazyFrame:
        captured.append((uri, storage_options))
        return FakeLazyFrame()

    monkeypatch.setattr("marimoserver.table_explorer.pl.scan_delta", scan_delta)

    dataframe = read_delta_table(table, config, row_limit=5)

    assert dataframe.to_dict(as_series=False) == {"id": [1]}
    assert captured == [(table.uri, config.delta_storage_options()), 5]


def test_read_parquet_table_reads_discovered_files() -> None:
    table = TablePrefix(
        bucket="dev-energy-market-landing",
        prefix="bronze/prices",
        table_format=TableFormat.PARQUET,
        parquet_files=(
            "bronze/prices/part-000.parquet",
            "bronze/prices/part-001.parquet",
        ),
    )
    fake_client = FakeS3Client(
        objects_by_key={
            (
                "dev-energy-market-landing",
                "bronze/prices/part-000.parquet",
            ): _parquet_bytes(pl.DataFrame({"id": [1], "price": [10.5]})),
            (
                "dev-energy-market-landing",
                "bronze/prices/part-001.parquet",
            ): _parquet_bytes(pl.DataFrame({"id": [2], "region": ["VIC"]})),
        }
    )

    dataframe = read_parquet_table(table, fake_client)

    assert dataframe.sort("id").to_dict(as_series=False) == {
        "id": [1, 2],
        "price": [10.5, None],
        "region": [None, "VIC"],
    }


def test_read_parquet_table_honours_row_limit() -> None:
    table = TablePrefix(
        bucket="dev-energy-market-landing",
        prefix="bronze/prices",
        table_format=TableFormat.PARQUET,
        parquet_files=(
            "bronze/prices/part-000.parquet",
            "bronze/prices/part-001.parquet",
        ),
    )
    fake_client = FakeS3Client(
        objects_by_key={
            (
                "dev-energy-market-landing",
                "bronze/prices/part-000.parquet",
            ): _parquet_bytes(pl.DataFrame({"id": [1, 2]})),
            (
                "dev-energy-market-landing",
                "bronze/prices/part-001.parquet",
            ): _parquet_bytes(pl.DataFrame({"id": [3, 4]})),
        }
    )

    dataframe = read_parquet_table(table, fake_client, row_limit=3)

    assert dataframe.to_dict(as_series=False) == {"id": [1, 2, 3]}


def test_read_parquet_table_returns_empty_frame_without_files() -> None:
    table = TablePrefix(
        bucket="dev-energy-market-landing",
        prefix="empty",
        table_format=TableFormat.PARQUET,
        parquet_files=(),
    )

    assert read_parquet_table(table, FakeS3Client()).is_empty()


def test_inspect_table_loads_delta_schema_count_and_preview(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = discover_table_explorer_config({})
    table = TablePrefix(
        bucket="dev-energy-market-aemo",
        prefix="silver/gas",
        table_format=TableFormat.DELTA,
        parquet_files=(),
    )

    def fake_read_delta_table(
        table_arg: TablePrefix,
        config_arg: TableExplorerConfig,
        row_limit: int | None = None,
    ) -> pl.DataFrame:
        assert table_arg == table
        assert config_arg == config
        assert row_limit is None
        return pl.DataFrame({"id": [1, 2], "name": ["a", "b"]})

    monkeypatch.setattr(explorer, "read_delta_table", fake_read_delta_table)

    inspection = inspect_table(table, config, preview_rows=1)

    assert inspection.available
    assert inspection.error is None
    assert inspection.row_count == 2
    assert inspection.is_limited is False
    assert [(column.name, column.dtype) for column in inspection.schema] == [
        ("id", "Int64"),
        ("name", "String"),
    ]
    assert inspection.preview.to_dict(as_series=False) == {"id": [1], "name": ["a"]}


def test_load_table_dataframe_limits_aws_preview(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = discover_table_explorer_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "MARIMO_TABLE_BUCKETS": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "7",
        }
    )
    table = TablePrefix(
        bucket="prod-energy-market-aemo",
        prefix="silver/gas",
        table_format=TableFormat.DELTA,
        parquet_files=(),
    )
    captured: list[int | None] = []

    def fake_read_delta_table(
        table_arg: TablePrefix,
        config_arg: TableExplorerConfig,
        row_limit: int | None = None,
    ) -> pl.DataFrame:
        assert table_arg == table
        assert config_arg == config
        captured.append(row_limit)
        return pl.DataFrame({"id": list(range(10))})

    monkeypatch.setattr(explorer, "read_delta_table", fake_read_delta_table)

    scan = explorer.load_table_dataframe(table, config)

    assert scan.available
    assert scan.is_limited is True
    assert scan.row_limit == 7
    assert captured == [7]


def test_inspect_table_loads_parquet_with_injected_s3_client() -> None:
    config = discover_table_explorer_config({})
    table = TablePrefix(
        bucket="dev-energy-market-landing",
        prefix="bronze/prices",
        table_format=TableFormat.PARQUET,
        parquet_files=("bronze/prices/part-000.parquet",),
    )
    fake_client = FakeS3Client(
        objects_by_key={
            (
                "dev-energy-market-landing",
                "bronze/prices/part-000.parquet",
            ): _parquet_bytes(pl.DataFrame({"id": [1]}))
        }
    )

    inspection = inspect_table(table, config, s3_client=fake_client)

    assert inspection.available
    assert inspection.row_count == 1
    assert inspection.preview.to_dict(as_series=False) == {"id": [1]}


def test_inspect_table_returns_error_detail() -> None:
    config = discover_table_explorer_config({})
    table = TablePrefix(
        bucket="dev-energy-market-landing",
        prefix="bronze/prices",
        table_format=TableFormat.PARQUET,
        parquet_files=("bronze/prices/part-000.parquet",),
    )

    inspection = inspect_table(table, config, s3_client=BadBodyS3Client())

    assert not inspection.available
    assert inspection.error == "TypeError: S3 response Body must provide read()"
    assert inspection.schema == ()
    assert inspection.row_count == 0
    assert inspection.preview.is_empty()


def test_cached_table_scan_reuses_scan_until_refresh_token_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = discover_table_explorer_config({})
    table = TablePrefix(
        bucket="dev-energy-market-aemo",
        prefix="silver/gas",
        table_format=TableFormat.PARQUET,
        parquet_files=("silver/gas/part-000.parquet",),
    )
    calls: list[int] = []

    def fake_load_table_dataframe(
        table_arg: TablePrefix,
        config_arg: TableExplorerConfig,
        s3_client: S3Client | None = None,
    ) -> TableScan:
        assert table_arg == table
        assert config_arg == config
        assert s3_client is None
        calls.append(len(calls) + 1)
        return TableScan(
            table=table_arg,
            dataframe=pl.DataFrame({"scan": [calls[-1]]}),
            is_limited=False,
            row_limit=None,
            error=None,
        )

    monkeypatch.setattr(explorer, "load_table_dataframe", fake_load_table_dataframe)
    cache: dict[explorer.TableScanCacheKey, TableScan] = {}

    first_scan = cached_table_scan(table, config, cache)
    cached_scan = cached_table_scan(table, config, cache)
    refreshed_scan = cached_table_scan(table, config, cache, refresh_token=1)

    assert first_scan.available
    assert first_scan is cached_scan
    assert refreshed_scan is not first_scan
    assert [scan.dataframe.item() for scan in (first_scan, refreshed_scan)] == [1, 2]
    assert calls == [1, 2]


def test_explore_table_scan_applies_column_sort_text_and_stats() -> None:
    table = TablePrefix(
        bucket="dev-energy-market-aemo",
        prefix="silver/gas",
        table_format=TableFormat.PARQUET,
        parquet_files=("silver/gas/part-000.parquet",),
    )
    scan = TableScan(
        table=table,
        dataframe=pl.DataFrame(
            {
                "id": [2, 1, 3],
                "name": ["Beta", None, "alpha"],
                "region": ["VIC", "NSW", "VIC"],
            }
        ),
        is_limited=False,
        row_limit=None,
        error=None,
    )

    exploration = explore_table_scan(
        scan,
        TableQuery(
            row_limit=1,
            columns=("id", "name"),
            sort_column="id",
            text_search="a",
        ),
    )

    assert exploration.available
    assert exploration.row_count == 3
    assert exploration.filtered_row_count == 2
    assert [(column.name, column.dtype) for column in exploration.schema] == [
        ("id", "Int64"),
        ("name", "String"),
        ("region", "String"),
    ]
    assert exploration.preview.to_dict(as_series=False) == {
        "id": [2],
        "name": ["Beta"],
    }
    assert [
        (statistic.column, statistic.null_count, statistic.distinct_count)
        for statistic in exploration.column_statistics
    ] == [("id", 0, 3), ("name", 1, 2)]


def test_explore_table_scan_disables_global_operations_for_limited_scan() -> None:
    table = TablePrefix(
        bucket="prod-energy-market-aemo",
        prefix="silver/gas",
        table_format=TableFormat.PARQUET,
        parquet_files=("silver/gas/part-000.parquet",),
    )
    scan = TableScan(
        table=table,
        dataframe=pl.DataFrame(
            {
                "id": [2, 1, 3],
                "name": ["Beta", None, "alpha"],
                "region": ["VIC", "NSW", "VIC"],
            }
        ),
        is_limited=True,
        row_limit=100,
        error=None,
    )

    exploration = explore_table_scan(
        scan,
        TableQuery(
            row_limit=2,
            columns=("id", "name"),
            sort_column="id",
            text_search="alpha",
        ),
    )

    assert exploration.available
    assert exploration.is_limited is True
    assert exploration.row_count == 3
    assert exploration.filtered_row_count == 3
    assert exploration.preview.to_dict(as_series=False) == {
        "id": [2, 1],
        "name": ["Beta", None],
    }
    assert exploration.column_statistics == ()


def test_explore_table_scan_handles_empty_tables_without_error() -> None:
    table = TablePrefix(
        bucket="dev-energy-market-aemo",
        prefix="silver/empty",
        table_format=TableFormat.PARQUET,
        parquet_files=(),
    )

    exploration = explore_table_scan(
        TableScan(
            table=table,
            dataframe=pl.DataFrame(),
            is_limited=False,
            row_limit=None,
            error=None,
        ),
        TableQuery(),
    )

    assert exploration.available
    assert exploration.row_count == 0
    assert exploration.filtered_row_count == 0
    assert exploration.preview.is_empty()
    assert exploration.column_statistics == ()


def test_explore_table_scan_returns_scan_errors() -> None:
    table = TablePrefix(
        bucket="dev-energy-market-aemo",
        prefix="silver/error",
        table_format=TableFormat.PARQUET,
        parquet_files=(),
    )

    exploration = explore_table_scan(
        TableScan(
            table=table,
            dataframe=pl.DataFrame({"id": [1]}),
            is_limited=False,
            row_limit=None,
            error="boom",
        ),
        TableQuery(),
    )

    assert not exploration.available
    assert exploration.error == "boom"
    assert exploration.schema == ()
    assert exploration.row_count == 0
    assert exploration.preview.is_empty()


def test_compact_error_handles_empty_messages() -> None:
    class EmptyMessageError(Exception):
        def __str__(self) -> str:
            return ""

    assert explorer._compact_error(EmptyMessageError()) == "EmptyMessageError"


def _link_detail(links: tuple[explorer.TableWorkbenchLink, ...], label: str) -> str:
    for link in links:
        if link.label == label:
            return link.detail
    raise AssertionError(f"missing workbench link: {label}")


class BadBodyS3Client(FakeS3Client):
    def get_object(self, *, Bucket: str, Key: str) -> Mapping[str, object]:
        return {"Body": object()}


def _asset(
    asset_key: tuple[str, ...],
    *,
    uri: str | None,
    latest_materialization_timestamp: float | None,
    group_name: str = "gas_model",
) -> DagsterTableAsset:
    return DagsterTableAsset(
        asset_key=asset_key,
        group_name=group_name,
        kinds=("parquet", "table"),
        description="Asset description.",
        uri=uri,
        columns=(DagsterColumnMetadata(name="id", dtype="Int64", description=None),),
        is_materializable=True,
        is_executable=True,
        latest_materialization_timestamp=latest_materialization_timestamp,
    )


def _bucket_status(
    *,
    name: str,
    reachable: bool,
    object_count: int,
    table_count: int,
    error: str | None = None,
    truncated: bool = False,
) -> BucketStatus:
    return BucketStatus(
        name=name,
        is_default=True,
        discovered=True,
        reachable=reachable,
        object_count=object_count,
        table_count=table_count,
        truncated=truncated,
        error=error,
    )


def _parquet_bytes(dataframe: pl.DataFrame) -> bytes:
    buffer = BytesIO()
    dataframe.write_parquet(buffer)
    return buffer.getvalue()
