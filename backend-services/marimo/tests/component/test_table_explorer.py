"""Component tests for the local table explorer helper surface."""

from collections.abc import Iterable, Mapping
from io import BytesIO

import polars as pl
import pytest

from marimoserver import table_explorer as explorer
from marimoserver.table_explorer import (
    DEFAULT_LOCAL_BUCKETS,
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
    cached_table_scan,
    catalogued_table_by_id,
    catalogued_table_group,
    catalogued_table_layers_or_domains,
    classify_table_prefixes,
    create_s3_client,
    discover_table_catalogue,
    discover_storage,
    discover_table_explorer_config,
    explore_table_scan,
    filter_catalogued_tables,
    format_materialization_timestamp,
    inspect_table,
    overlay_table_catalogue,
    read_delta_table,
    read_parquet_table,
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

    def list_buckets(self) -> Mapping[str, object]:
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
    assert config.dagster_graphql_url == "http://dagster-webserver-guest:3000/graphql"


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
    ) -> pl.DataFrame:
        assert table_arg == table
        assert config_arg == config
        return pl.DataFrame({"id": [1, 2], "name": ["a", "b"]})

    monkeypatch.setattr(explorer, "read_delta_table", fake_read_delta_table)

    inspection = inspect_table(table, config, preview_rows=1)

    assert inspection.available
    assert inspection.error is None
    assert inspection.row_count == 2
    assert [(column.name, column.dtype) for column in inspection.schema] == [
        ("id", "Int64"),
        ("name", "String"),
    ]
    assert inspection.preview.to_dict(as_series=False) == {"id": [1], "name": ["a"]}


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


def test_explore_table_scan_handles_empty_tables_without_error() -> None:
    table = TablePrefix(
        bucket="dev-energy-market-aemo",
        prefix="silver/empty",
        table_format=TableFormat.PARQUET,
        parquet_files=(),
    )

    exploration = explore_table_scan(
        TableScan(table=table, dataframe=pl.DataFrame(), error=None),
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
        TableScan(table=table, dataframe=pl.DataFrame({"id": [1]}), error="boom"),
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


def _parquet_bytes(dataframe: pl.DataFrame) -> bytes:
    buffer = BytesIO()
    dataframe.write_parquet(buffer)
    return buffer.getvalue()
