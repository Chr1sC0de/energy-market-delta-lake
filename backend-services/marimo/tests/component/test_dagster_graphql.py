"""Component tests for the local Dagster GraphQL helper."""

from collections.abc import Mapping
from urllib.request import Request

import pytest

from marimoserver import dagster_graphql as graphql
from marimoserver.dagster_graphql import (
    DAGSTER_TABLE_ASSETS_QUERY,
    DagsterGraphQLError,
    DagsterGraphQLClient,
    fetch_dagster_asset_catalogue,
    table_assets_from_graphql_payload,
)


class FakeGraphQLClient:
    def __init__(
        self,
        payload: Mapping[str, object] | None = None,
        error: DagsterGraphQLError | None = None,
    ) -> None:
        self.payload = {} if payload is None else payload
        self.error = error
        self.queries: list[str] = []

    def execute(
        self,
        query: str,
        variables: Mapping[str, object] | None = None,
        *,
        timeout_seconds: int | None = None,
    ) -> Mapping[str, object]:
        assert variables is None
        assert timeout_seconds is None
        self.queries.append(query)
        if self.error is not None:
            raise self.error
        return self.payload


class FakeResponse:
    def __init__(self, data: bytes) -> None:
        self.data = data

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.data


def test_table_assets_from_graphql_payload_extracts_table_metadata() -> None:
    assets = table_assets_from_graphql_payload(
        {
            "assetNodes": [
                "bad-node",
                {
                    "assetKey": {"path": ["ops", "status"]},
                    "groupName": "ops",
                    "kinds": ["status"],
                    "description": "Non-table asset.",
                    "isMaterializable": True,
                    "isExecutable": True,
                    "metadataEntries": [],
                    "assetMaterializations": [],
                },
                {
                    "assetKey": {
                        "path": [
                            "silver",
                            "gas_model",
                            "silver_gas_fact_market_price",
                        ]
                    },
                    "groupName": "gas_model",
                    "kinds": ["parquet", "table"],
                    "description": "Market prices.",
                    "isMaterializable": True,
                    "isExecutable": True,
                    "metadataEntries": [
                        {
                            "__typename": "TextMetadataEntry",
                            "label": "dagster/uri",
                            "text": (
                                "s3://dev-energy-market-aemo/silver/gas_model/"
                                "silver_gas_fact_market_price"
                            ),
                        },
                        {
                            "__typename": "TableSchemaMetadataEntry",
                            "label": "dagster/column_schema",
                            "schema": {
                                "columns": [
                                    {
                                        "name": "gas_date",
                                        "type": "Date",
                                        "description": "Gas day.",
                                    },
                                    {"name": "price", "type": "Float64"},
                                ]
                            },
                        },
                    ],
                    "assetMaterializations": [{"timestamp": 1_714_000_000.5}],
                },
                {
                    "assetKey": {"path": ["bronze", "gbb", "raw_table"]},
                    "groupName": "gas_raw",
                    "kinds": None,
                    "description": None,
                    "isMaterializable": False,
                    "isExecutable": False,
                    "metadataEntries": None,
                    "assetMaterializations": [
                        {
                            "timestamp": "1714000000500",
                            "metadataEntries": [
                                {
                                    "__typename": "PathMetadataEntry",
                                    "label": "dagster/uri",
                                    "path": (
                                        "s3://dev-energy-market-aemo/bronze/gbb/"
                                        "raw_table"
                                    ),
                                },
                                {
                                    "__typename": "TableMetadataEntry",
                                    "label": "schema",
                                    "table": {
                                        "schema": {
                                            "columns": [
                                                {
                                                    "name": "id",
                                                    "type": "Int64",
                                                    "description": "Identifier.",
                                                }
                                            ]
                                        }
                                    },
                                },
                            ],
                        }
                    ],
                },
            ]
        }
    )

    assert [asset.asset_id for asset in assets] == [
        "bronze/gbb/raw_table",
        "silver/gas_model/silver_gas_fact_market_price",
    ]
    assert assets[0].group_name == "gas_raw"
    assert assets[0].uri == "s3://dev-energy-market-aemo/bronze/gbb/raw_table"
    assert assets[0].latest_materialization_timestamp == 1_714_000_000.5
    assert [
        (column.name, column.dtype, column.description) for column in assets[0].columns
    ] == [("id", "Int64", "Identifier.")]
    assert assets[1].description == "Market prices."
    assert assets[1].kinds == ("parquet", "table")
    assert assets[1].is_materializable
    assert assets[1].is_executable
    assert [
        (column.name, column.dtype, column.description) for column in assets[1].columns
    ] == [
        ("gas_date", "Date", "Gas day."),
        ("price", "Float64", None),
    ]


def test_table_assets_from_graphql_payload_requires_asset_nodes_list() -> None:
    with pytest.raises(DagsterGraphQLError, match="assetNodes was not a list"):
        table_assets_from_graphql_payload({"assetNodes": {}})


def test_table_assets_from_graphql_payload_requires_asset_key_path() -> None:
    with pytest.raises(DagsterGraphQLError, match="assetKey.path"):
        table_assets_from_graphql_payload(
            {
                "assetNodes": [
                    {
                        "assetKey": {"path": "silver/gas"},
                        "kinds": ["table"],
                    }
                ]
            }
        )


def test_table_assets_from_graphql_payload_requires_asset_key_object() -> None:
    with pytest.raises(DagsterGraphQLError, match="assetKey was not an object"):
        table_assets_from_graphql_payload(
            {"assetNodes": [{"assetKey": None, "kinds": ["table"]}]}
        )


def test_table_asset_parser_ignores_malformed_optional_metadata() -> None:
    assets = table_assets_from_graphql_payload(
        {
            "assetNodes": [
                {
                    "assetKey": {"path": ["silver", "gas", "table"]},
                    "kinds": ["table"],
                    "groupName": 5,
                    "description": 5,
                    "isMaterializable": False,
                    "isExecutable": False,
                    "metadataEntries": [
                        {"__typename": "UrlMetadataEntry", "label": "dagster/uri"},
                        {
                            "__typename": "TableSchemaMetadataEntry",
                            "label": "dagster/column_schema",
                            "schema": "bad",
                        },
                        {
                            "__typename": "TableSchemaMetadataEntry",
                            "label": "dagster/column_schema",
                            "schema": {"columns": "bad"},
                        },
                        {
                            "__typename": "TableMetadataEntry",
                            "label": "schema",
                            "table": "bad",
                        },
                    ],
                    "assetMaterializations": ["bad"],
                }
            ]
        }
    )

    assert len(assets) == 1
    assert assets[0].group_name == ""
    assert assets[0].description is None
    assert assets[0].uri is None
    assert assets[0].columns == ()
    assert assets[0].latest_materialization_timestamp is None


def test_table_asset_parser_accepts_schema_only_assets() -> None:
    assets = table_assets_from_graphql_payload(
        {
            "assetNodes": [
                {
                    "assetKey": {"path": ["silver", "gas", "schema_only"]},
                    "kinds": [],
                    "metadataEntries": [
                        {
                            "__typename": "TableSchemaMetadataEntry",
                            "label": "dagster/column_schema",
                            "schema": {
                                "columns": [
                                    {"name": "", "type": "String"},
                                    {"name": "name", "type": 5, "description": 5},
                                    "bad",
                                ]
                            },
                        }
                    ],
                    "assetMaterializations": [],
                }
            ]
        }
    )

    assert [
        (column.name, column.dtype, column.description) for column in assets[0].columns
    ] == [("name", "", None)]


def test_fetch_dagster_asset_catalogue_returns_assets() -> None:
    fake_client = FakeGraphQLClient(
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
    )

    catalogue = fetch_dagster_asset_catalogue("http://dagster/graphql", fake_client)

    assert catalogue.available
    assert catalogue.error is None
    assert [asset.asset_id for asset in catalogue.assets] == ["silver/gas/table"]
    assert fake_client.queries == [DAGSTER_TABLE_ASSETS_QUERY]


def test_fetch_dagster_asset_catalogue_returns_recoverable_error() -> None:
    catalogue = fetch_dagster_asset_catalogue(
        "http://dagster/graphql",
        FakeGraphQLClient(error=DagsterGraphQLError("offline")),
    )

    assert not catalogue.available
    assert catalogue.assets == ()
    assert catalogue.error == "offline"


def test_dagster_graphql_client_posts_json_and_returns_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[tuple[Request, int]] = []

    def fake_urlopen(request: Request, timeout: int) -> FakeResponse:
        captured.append((request, timeout))
        return FakeResponse(b'{"data": {"ok": true}}')

    monkeypatch.setattr(graphql, "urlopen", fake_urlopen)

    data = DagsterGraphQLClient("http://dagster/graphql", timeout_seconds=7).execute(
        "query Test { ok }",
        {"name": "value"},
        timeout_seconds=2,
    )

    assert data == {"ok": True}
    assert len(captured) == 1
    request, timeout = captured[0]
    assert request.full_url == "http://dagster/graphql"
    assert request.headers["Content-type"] == "application/json"
    assert request.get_method() == "POST"
    assert timeout == 2
    assert request.data == (
        b'{"query": "query Test { ok }", "variables": {"name": "value"}}'
    )


@pytest.mark.parametrize(
    ("response_body", "message"),
    [
        (b"not-json", "invalid JSON"),
        (b"[]", "non-object payload"),
        (b'{"errors": [{"message": "bad query"}]}', "returned errors"),
        (b'{"data": []}', "did not include data"),
    ],
)
def test_dagster_graphql_client_rejects_bad_payloads(
    monkeypatch: pytest.MonkeyPatch,
    response_body: bytes,
    message: str,
) -> None:
    def fake_urlopen(request: Request, timeout: int) -> FakeResponse:
        return FakeResponse(response_body)

    monkeypatch.setattr(graphql, "urlopen", fake_urlopen)

    with pytest.raises(DagsterGraphQLError, match=message):
        DagsterGraphQLClient("http://dagster/graphql").execute("query Test { ok }")


def test_dagster_graphql_client_wraps_transport_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_urlopen(request: Request, timeout: int) -> FakeResponse:
        raise OSError("connection refused")

    monkeypatch.setattr(graphql, "urlopen", fake_urlopen)

    with pytest.raises(DagsterGraphQLError, match="connection refused"):
        DagsterGraphQLClient("http://dagster/graphql").execute("query Test { ok }")


def test_timestamp_parser_rejects_unreadable_values() -> None:
    assets = table_assets_from_graphql_payload(
        {
            "assetNodes": [
                {
                    "assetKey": {"path": ["silver", "gas", "bad_timestamp"]},
                    "kinds": ["table"],
                    "metadataEntries": [],
                    "assetMaterializations": [{"timestamp": "not-a-timestamp"}],
                },
                {
                    "assetKey": {"path": ["silver", "gas", "missing_timestamp"]},
                    "kinds": ["table"],
                    "metadataEntries": [],
                    "assetMaterializations": [{"timestamp": None}],
                },
            ]
        }
    )

    assert [asset.latest_materialization_timestamp for asset in assets] == [None, None]
