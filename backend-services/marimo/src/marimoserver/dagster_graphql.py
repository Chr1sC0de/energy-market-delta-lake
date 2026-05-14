"""Stdlib Dagster GraphQL helpers for Marimo notebooks."""

from collections.abc import Mapping
from dataclasses import dataclass
import json
from typing import Protocol
from urllib.request import Request, urlopen


DEFAULT_DAGSTER_GRAPHQL_URL = (
    "http://dagster-webserver-guest:3000/dagster-webserver/guest/graphql"
)
DEFAULT_DAGSTER_GRAPHQL_TIMEOUT_SECONDS = 3

DAGSTER_TABLE_ASSETS_QUERY = """
query LocalMarimoTableAssets {
  assetNodes(loadMaterializations: true) {
    assetKey {
      path
    }
    groupName
    kinds
    description
    isMaterializable
    isExecutable
    metadataEntries {
      ...LocalMarimoMetadataEntryFields
    }
    assetMaterializations(limit: 1) {
      timestamp
      metadataEntries {
        ...LocalMarimoMetadataEntryFields
      }
    }
  }
}

fragment LocalMarimoMetadataEntryFields on MetadataEntry {
  __typename
  label
  description
  ... on TextMetadataEntry {
    text
  }
  ... on UrlMetadataEntry {
    url
  }
  ... on PathMetadataEntry {
    path
  }
  ... on JsonMetadataEntry {
    jsonString
  }
  ... on MarkdownMetadataEntry {
    mdStr
  }
  ... on TableSchemaMetadataEntry {
    schema {
      columns {
        name
        type
        description
      }
    }
  }
  ... on TableMetadataEntry {
    table {
      schema {
        columns {
          name
          type
          description
        }
      }
    }
  }
}
"""


class DagsterGraphQLError(RuntimeError):
    """Dagster GraphQL request or response error."""


class DagsterGraphQLClient:
    """Small stdlib GraphQL client for the local Dagster webserver."""

    def __init__(
        self,
        url: str,
        *,
        timeout_seconds: int = DEFAULT_DAGSTER_GRAPHQL_TIMEOUT_SECONDS,
    ) -> None:
        """Initialize the client for one Dagster GraphQL endpoint."""
        self.url = url
        self.timeout_seconds = timeout_seconds

    def execute(
        self,
        query: str,
        variables: Mapping[str, object] | None = None,
        *,
        timeout_seconds: int | None = None,
    ) -> Mapping[str, object]:
        """Execute a GraphQL request and return its data payload."""
        body = json.dumps({"query": query, "variables": dict(variables or {})}).encode(
            "utf-8"
        )
        request = Request(
            self.url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        request_timeout_seconds = (
            self.timeout_seconds if timeout_seconds is None else timeout_seconds
        )
        try:
            with urlopen(request, timeout=request_timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except OSError as error:
            raise DagsterGraphQLError(
                f"Dagster GraphQL request failed at {self.url}: {error}"
            ) from error
        except json.JSONDecodeError as error:
            raise DagsterGraphQLError(
                f"Dagster GraphQL returned invalid JSON at {self.url}: {error}"
            ) from error

        if not isinstance(payload, dict):
            raise DagsterGraphQLError("Dagster GraphQL returned a non-object payload")
        errors = payload.get("errors")
        if errors:
            raise DagsterGraphQLError(f"Dagster GraphQL returned errors: {errors}")
        data = payload.get("data")
        if not isinstance(data, Mapping):
            raise DagsterGraphQLError("Dagster GraphQL response did not include data")
        return data


@dataclass(frozen=True)
class DagsterColumnMetadata:
    """One Dagster table column from GraphQL metadata."""

    name: str
    dtype: str
    description: str | None


@dataclass(frozen=True)
class DagsterTableAsset:
    """A table-like Dagster asset returned by GraphQL."""

    asset_key: tuple[str, ...]
    group_name: str
    kinds: tuple[str, ...]
    description: str | None
    uri: str | None
    columns: tuple[DagsterColumnMetadata, ...]
    is_materializable: bool
    is_executable: bool
    latest_materialization_timestamp: float | None

    @property
    def asset_id(self) -> str:
        """Return a slash-separated asset key."""
        return "/".join(self.asset_key)


@dataclass(frozen=True)
class DagsterAssetCatalogue:
    """Dagster table asset catalogue or a recoverable GraphQL error."""

    url: str
    assets: tuple[DagsterTableAsset, ...]
    error: str | None

    @property
    def available(self) -> bool:
        """Return whether GraphQL catalogue discovery succeeded."""
        return self.error is None


class GraphQLExecutorProtocol(Protocol):
    """Small execution surface shared by the real and fake GraphQL clients."""

    def execute(
        self,
        query: str,
        variables: Mapping[str, object] | None = None,
        *,
        timeout_seconds: int | None = None,
    ) -> Mapping[str, object]:
        """Execute GraphQL and return a data payload."""
        raise NotImplementedError  # pragma: no cover


def fetch_dagster_asset_catalogue(
    url: str,
    client: GraphQLExecutorProtocol | None = None,
) -> DagsterAssetCatalogue:
    """Fetch and parse table-like assets from a Dagster GraphQL endpoint."""
    graphql_client = DagsterGraphQLClient(url) if client is None else client
    try:
        payload = graphql_client.execute(DAGSTER_TABLE_ASSETS_QUERY)
        assets = table_assets_from_graphql_payload(payload)
    except DagsterGraphQLError as error:
        return DagsterAssetCatalogue(url=url, assets=(), error=str(error))
    return DagsterAssetCatalogue(url=url, assets=assets, error=None)


def table_assets_from_graphql_payload(
    payload: Mapping[str, object],
) -> tuple[DagsterTableAsset, ...]:
    """Parse table-like Dagster assets from a GraphQL data payload."""
    asset_nodes = payload.get("assetNodes")
    if not isinstance(asset_nodes, list):
        raise DagsterGraphQLError("Dagster GraphQL assetNodes was not a list")

    assets: list[DagsterTableAsset] = []
    for asset_node in asset_nodes:
        if not isinstance(asset_node, Mapping):
            continue
        asset = _read_table_asset(asset_node)
        if asset is not None:
            assets.append(asset)

    return tuple(sorted(assets, key=lambda asset: asset.asset_id))


def _read_table_asset(asset_node: Mapping[str, object]) -> DagsterTableAsset | None:
    asset_key = _read_asset_key(asset_node.get("assetKey"))
    kinds = _read_string_tuple(asset_node.get("kinds"))
    definition_metadata = _read_metadata_entries(asset_node.get("metadataEntries"))
    latest_timestamp, materialization_metadata = _read_latest_materialization(
        asset_node.get("assetMaterializations")
    )
    uri = _metadata_entry_text(definition_metadata, "dagster/uri")
    if uri is None:
        uri = _metadata_entry_text(materialization_metadata, "dagster/uri")
    columns = _columns_from_metadata_entries(definition_metadata)
    if not columns:
        columns = _columns_from_metadata_entries(materialization_metadata)

    if not _is_table_asset(kinds=kinds, uri=uri, columns=columns):
        return None

    group_name = asset_node.get("groupName")
    description = asset_node.get("description")
    return DagsterTableAsset(
        asset_key=asset_key,
        group_name=group_name if isinstance(group_name, str) else "",
        kinds=kinds,
        description=description if isinstance(description, str) else None,
        uri=uri,
        columns=columns,
        is_materializable=asset_node.get("isMaterializable") is True,
        is_executable=asset_node.get("isExecutable") is True,
        latest_materialization_timestamp=latest_timestamp,
    )


def _read_asset_key(value: object) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        raise DagsterGraphQLError("Dagster GraphQL assetKey was not an object")
    path = value.get("path")
    if not isinstance(path, list) or not all(isinstance(part, str) for part in path):
        raise DagsterGraphQLError("Dagster GraphQL assetKey.path was not a string list")
    return tuple(path)


def _read_string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(sorted(item for item in value if isinstance(item, str)))


def _read_metadata_entries(value: object) -> tuple[Mapping[str, object], ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _read_latest_materialization(
    value: object,
) -> tuple[float | None, tuple[Mapping[str, object], ...]]:
    if not isinstance(value, list) or not value:
        return None, ()
    latest = value[0]
    if not isinstance(latest, Mapping):
        return None, ()
    return (
        _read_timestamp_seconds(latest.get("timestamp")),
        _read_metadata_entries(latest.get("metadataEntries")),
    )


def _read_timestamp_seconds(value: object) -> float | None:
    if isinstance(value, int | float):
        timestamp = float(value)
    elif isinstance(value, str):
        try:
            timestamp = float(value)
        except ValueError:
            return None
    else:
        return None

    if timestamp > 10_000_000_000:
        return timestamp / 1000
    return timestamp


def _metadata_entry_text(
    entries: tuple[Mapping[str, object], ...],
    label: str,
) -> str | None:
    for entry in entries:
        if entry.get("label") != label:
            continue
        for field_name in ("text", "url", "path", "mdStr", "jsonString"):
            value = entry.get(field_name)
            if isinstance(value, str) and value != "":
                return value
    return None


def _columns_from_metadata_entries(
    entries: tuple[Mapping[str, object], ...],
) -> tuple[DagsterColumnMetadata, ...]:
    for entry in entries:
        typename = entry.get("__typename")
        label = entry.get("label")
        is_column_schema = label in {"dagster/column_schema", "column_schema", "schema"}
        if typename == "TableSchemaMetadataEntry" and is_column_schema:
            columns = _columns_from_schema(entry.get("schema"))
            if columns:
                return columns
        if typename == "TableMetadataEntry" and is_column_schema:
            table = entry.get("table")
            if isinstance(table, Mapping):
                columns = _columns_from_schema(table.get("schema"))
                if columns:
                    return columns
    return ()


def _columns_from_schema(value: object) -> tuple[DagsterColumnMetadata, ...]:
    if not isinstance(value, Mapping):
        return ()
    raw_columns = value.get("columns")
    if not isinstance(raw_columns, list):
        return ()

    columns: list[DagsterColumnMetadata] = []
    for raw_column in raw_columns:
        if not isinstance(raw_column, Mapping):
            continue
        name = raw_column.get("name")
        if not isinstance(name, str) or name == "":
            continue
        dtype = raw_column.get("type")
        description = raw_column.get("description")
        columns.append(
            DagsterColumnMetadata(
                name=name,
                dtype=dtype if isinstance(dtype, str) else "",
                description=description if isinstance(description, str) else None,
            )
        )
    return tuple(columns)


def _is_table_asset(
    *,
    kinds: tuple[str, ...],
    uri: str | None,
    columns: tuple[DagsterColumnMetadata, ...],
) -> bool:
    return (
        any(kind.lower() == "table" for kind in kinds)
        or (uri is not None and uri.startswith("s3://"))
        or bool(columns)
    )
