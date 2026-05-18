"""Component tests for the data readiness dashboard helper surface."""

from marimoserver.dagster_graphql import (
    DagsterAssetCatalogue,
    DagsterColumnMetadata,
    DagsterTableAsset,
)
from marimoserver.data_readiness import (
    DataReadinessOverview,
    ReadinessCard,
    ReadinessState,
    bucket_readiness_frame,
    build_data_readiness_overview,
    dagster_materialization_frame,
    readiness_action_markdown,
    render_readiness_cards,
    table_readiness_frame,
)
from marimoserver.table_explorer import (
    BucketStatus,
    CataloguedTable,
    StorageDiscovery,
    TableAvailability,
    TableExplorerConfig,
    TableFormat,
    TablePrefix,
    discover_table_explorer_config,
)


def test_data_readiness_overview_reports_missing_localstack_and_graphql() -> None:
    overview = build_data_readiness_overview(
        _config(),
        StorageDiscovery(
            buckets=(
                _bucket(
                    name="dev-energy-market-aemo",
                    reachable=True,
                    object_count=0,
                    table_count=0,
                ),
            ),
            tables=(),
            bucket_listing_error=None,
        ),
        DagsterAssetCatalogue(
            url="http://dagster/graphql",
            assets=(),
            error="connection refused",
        ),
        (),
    )

    assert _card(overview.cards, "S3 buckets").state is ReadinessState.EMPTY
    assert _card(overview.cards, "Table catalogue").state is ReadinessState.EMPTY
    assert (
        _card(overview.cards, "Dagster catalogue").state is ReadinessState.UNAVAILABLE
    )
    assert _card(overview.cards, "Bounded reads").value == "Full scans enabled"

    action_markdown = readiness_action_markdown(overview)
    assert "Seed LocalStack or materialize" in action_markdown
    assert "DAGSTER_GRAPHQL_URL" in action_markdown


def test_data_readiness_overview_reports_aws_bounded_read_policy() -> None:
    config = _config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "MARIMO_TABLE_BUCKETS": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "7",
        }
    )
    table = _table("prod-energy-market-aemo", "silver/gas_model/live")
    discovery = StorageDiscovery(
        buckets=(
            _bucket(
                name="prod-energy-market-aemo",
                reachable=True,
                object_count=4,
                table_count=1,
            ),
        ),
        tables=(table,),
        bucket_listing_error=None,
    )
    catalogue = DagsterAssetCatalogue(
        url="http://dagster/graphql",
        assets=(
            _asset(
                ("silver", "gas_model", "live"),
                uri=table.uri,
                latest_materialization_timestamp=1_714_000_000,
            ),
            _asset(
                ("silver", "gas_model", "missing"),
                uri="s3://prod-energy-market-aemo/silver/gas_model/missing",
                latest_materialization_timestamp=1_714_000_001,
            ),
        ),
        error=None,
    )
    table_catalogue = (
        CataloguedTable(
            entry_id="asset:silver/gas_model/live",
            status=TableAvailability.LIVE,
            asset=catalogue.assets[0],
            table=table,
        ),
        CataloguedTable(
            entry_id="asset:silver/gas_model/missing",
            status=TableAvailability.MISSING,
            asset=catalogue.assets[1],
            table=None,
        ),
    )

    overview = build_data_readiness_overview(
        config,
        discovery,
        catalogue,
        table_catalogue,
    )

    assert _card(overview.cards, "S3 buckets").state is ReadinessState.READY
    assert _card(overview.cards, "Table catalogue").state is ReadinessState.ATTENTION
    assert _card(overview.cards, "Dagster catalogue").value == "2/2 materialized"
    assert _card(overview.cards, "Bounded reads").value == "7 row cap"
    assert (
        "AWS preview reads are capped"
        in _card(
            overview.cards,
            "Bounded reads",
        ).detail
    )


def test_data_readiness_overview_covers_s3_status_branches() -> None:
    no_bucket = build_data_readiness_overview(
        _config(),
        StorageDiscovery(buckets=(), tables=(), bucket_listing_error=None),
        _ready_catalogue(),
        _ready_table_catalogue(),
    )
    all_unreachable = build_data_readiness_overview(
        _config(),
        StorageDiscovery(
            buckets=(
                _bucket(
                    name="dev-energy-market-aemo",
                    reachable=False,
                    object_count=0,
                    table_count=0,
                    error="EndpointConnectionError",
                ),
            ),
            tables=(),
            bucket_listing_error="ListBuckets denied",
        ),
        _ready_catalogue(),
        _ready_table_catalogue(),
    )
    partial = build_data_readiness_overview(
        _config(),
        StorageDiscovery(
            buckets=(
                _bucket(
                    name="dev-energy-market-aemo",
                    reachable=True,
                    object_count=3,
                    table_count=1,
                    truncated=True,
                ),
                _bucket(
                    name="dev-energy-market-landing",
                    reachable=False,
                    object_count=0,
                    table_count=0,
                    error="AccessDenied",
                ),
            ),
            tables=(_table("dev-energy-market-aemo", "silver/gas_model/live"),),
            bucket_listing_error=None,
        ),
        _ready_catalogue(),
        _ready_table_catalogue(),
    )

    assert _card(no_bucket.cards, "S3 buckets").value == "No buckets"
    assert (
        _card(all_unreachable.cards, "S3 buckets").state is ReadinessState.UNAVAILABLE
    )
    assert _card(partial.cards, "S3 buckets").state is ReadinessState.ATTENTION


def test_data_readiness_overview_covers_table_catalogue_status_branches() -> None:
    graphql_unavailable = _overview_for_table_catalogue(
        (_catalogued_entry(TableAvailability.GRAPHQL_UNAVAILABLE),)
    )
    none_live = _overview_for_table_catalogue(
        (
            _catalogued_entry(TableAvailability.UNMATERIALIZED),
            _catalogued_entry(TableAvailability.MISSING),
        )
    )
    all_live = _overview_for_table_catalogue(
        (_catalogued_entry(TableAvailability.LIVE),)
    )

    assert (
        _card(graphql_unavailable.cards, "Table catalogue").action
        == "Restore Dagster GraphQL to classify storage prefixes against the asset catalogue."
    )
    assert _card(none_live.cards, "Table catalogue").value == "0/2 live"
    assert _card(all_live.cards, "Table catalogue").state is ReadinessState.READY


def test_data_readiness_overview_covers_dagster_catalogue_status_branches() -> None:
    no_assets = _overview_for_catalogue(
        DagsterAssetCatalogue(url="http://dagster/graphql", assets=(), error=None)
    )
    no_materializations = _overview_for_catalogue(
        DagsterAssetCatalogue(
            url="http://dagster/graphql",
            assets=(
                _asset(
                    ("silver", "gas_model", "unmaterialized"),
                    uri="s3://bucket/silver/gas_model/unmaterialized",
                    latest_materialization_timestamp=None,
                ),
            ),
            error=None,
        )
    )

    assert _card(no_assets.cards, "Dagster catalogue").state is ReadinessState.EMPTY
    assert (
        _card(no_materializations.cards, "Dagster catalogue").detail
        == "No materializations recorded."
    )
    assert (
        _card(no_materializations.cards, "Dagster catalogue").state
        is ReadinessState.ATTENTION
    )


def test_data_readiness_frames_render_actions_and_empty_rows() -> None:
    bucket_frame = bucket_readiness_frame(
        StorageDiscovery(
            buckets=(
                _bucket(
                    name="dev-energy-market-aemo",
                    reachable=False,
                    object_count=0,
                    table_count=0,
                    error="NoSuchBucket",
                ),
                _bucket(
                    name="dev-energy-market-landing",
                    reachable=True,
                    object_count=0,
                    table_count=0,
                ),
                _bucket(
                    name="dev-energy-market-archive",
                    reachable=True,
                    object_count=3,
                    table_count=1,
                ),
            ),
            tables=(),
            bucket_listing_error=None,
        )
    )
    empty_bucket_frame = bucket_readiness_frame(
        StorageDiscovery(
            buckets=(),
            tables=(),
            bucket_listing_error="ListBuckets denied",
        )
    )
    table_frame = table_readiness_frame(
        (
            _catalogued_entry(TableAvailability.LIVE),
            _catalogued_entry(TableAvailability.UNMATERIALIZED),
            _catalogued_entry(TableAvailability.MISSING),
            _catalogued_entry(TableAvailability.GRAPHQL_UNAVAILABLE),
        )
    )
    empty_table_frame = table_readiness_frame(())

    assert bucket_frame["status"].to_list() == [
        ReadinessState.UNAVAILABLE.value,
        ReadinessState.EMPTY.value,
        ReadinessState.READY.value,
    ]
    assert empty_bucket_frame.row(0, named=True)["bucket"] == "No configured buckets"
    assert table_frame["tables"].to_list() == [1, 1, 1, 1]
    assert "Materialize the Dagster asset" in table_frame.row(1, named=True)["action"]
    assert empty_table_frame.row(0, named=True)["status"] == ReadinessState.EMPTY.value


def test_dagster_materialization_frame_renders_unavailable_empty_and_asset_rows() -> (
    None
):
    unavailable = dagster_materialization_frame(
        DagsterAssetCatalogue(
            url="http://dagster/graphql",
            assets=(),
            error="offline",
        )
    )
    empty = dagster_materialization_frame(
        DagsterAssetCatalogue(
            url="http://dagster/graphql",
            assets=(),
            error=None,
        )
    )
    populated = dagster_materialization_frame(
        DagsterAssetCatalogue(
            url="http://dagster/graphql",
            assets=(
                _asset(
                    ("silver", "gas_model", "live"),
                    uri="s3://bucket/silver/gas_model/live",
                    latest_materialization_timestamp=0,
                ),
                _asset(
                    ("silver", "gas_model", "unmaterialized"),
                    uri=None,
                    latest_materialization_timestamp=None,
                ),
            ),
            error=None,
        )
    )

    assert unavailable.row(0, named=True)["status"] == ReadinessState.UNAVAILABLE.value
    assert empty.row(0, named=True)["asset"] == "No table assets returned"
    assert populated["status"].to_list() == [
        "Materialized",
        "No materialization",
    ]
    assert populated.row(0, named=True)["latest materialization"].startswith(
        "1970-01-01T00:00:00"
    )


def test_readiness_card_rendering_escapes_content_and_handles_no_actions() -> None:
    overview = build_data_readiness_overview(
        _config(),
        _ready_discovery(),
        _ready_catalogue(),
        _ready_table_catalogue(),
    )
    html = render_readiness_cards(
        (
            *_cards_for_all_states(),
            ReadinessCard(
                area="<unsafe>",
                state=ReadinessState.READY,
                value="1 < 2",
                detail="ready",
                action="No action.",
            ),
        )
    )

    assert (
        readiness_action_markdown(overview)
        == "All readiness surfaces are reachable under the current configuration."
    )
    assert 'class="readiness-card readiness-card--ready"' in html
    assert 'class="readiness-card readiness-card--needs-attention"' in html
    assert 'class="readiness-card readiness-card--empty"' in html
    assert 'class="readiness-card readiness-card--unavailable"' in html
    assert "&lt;unsafe&gt;" in html
    assert "1 &lt; 2" in html


def _overview_for_table_catalogue(
    table_catalogue: tuple[CataloguedTable, ...],
) -> DataReadinessOverview:
    return build_data_readiness_overview(
        _config(),
        _ready_discovery(),
        _ready_catalogue(),
        table_catalogue,
    )


def _overview_for_catalogue(catalogue: DagsterAssetCatalogue) -> DataReadinessOverview:
    return build_data_readiness_overview(
        _config(),
        _ready_discovery(),
        catalogue,
        _ready_table_catalogue(),
    )


def _config(environ: dict[str, str] | None = None) -> TableExplorerConfig:
    return discover_table_explorer_config({} if environ is None else environ)


def _ready_discovery() -> StorageDiscovery:
    table = _table("dev-energy-market-aemo", "silver/gas_model/live")
    return StorageDiscovery(
        buckets=(
            _bucket(
                name="dev-energy-market-aemo",
                reachable=True,
                object_count=3,
                table_count=1,
            ),
        ),
        tables=(table,),
        bucket_listing_error=None,
    )


def _ready_catalogue() -> DagsterAssetCatalogue:
    return DagsterAssetCatalogue(
        url="http://dagster/graphql",
        assets=(
            _asset(
                ("silver", "gas_model", "live"),
                uri="s3://dev-energy-market-aemo/silver/gas_model/live",
                latest_materialization_timestamp=1_714_000_000,
            ),
        ),
        error=None,
    )


def _ready_table_catalogue() -> tuple[CataloguedTable, ...]:
    return (_catalogued_entry(TableAvailability.LIVE),)


def _bucket(
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
        discovered=False,
        reachable=reachable,
        object_count=object_count,
        table_count=table_count,
        truncated=truncated,
        error=error,
    )


def _table(bucket: str, prefix: str) -> TablePrefix:
    return TablePrefix(
        bucket=bucket,
        prefix=prefix,
        table_format=TableFormat.PARQUET,
        parquet_files=(f"{prefix}/part-000.parquet",),
    )


def _catalogued_entry(status: TableAvailability) -> CataloguedTable:
    table = _table("dev-energy-market-aemo", f"silver/gas_model/{status.value}")
    asset = _asset(
        ("silver", "gas_model", status.value),
        uri=table.uri,
        latest_materialization_timestamp=1_714_000_000,
    )
    return CataloguedTable(
        entry_id=f"asset:{status.value}",
        status=status,
        asset=None if status is TableAvailability.GRAPHQL_UNAVAILABLE else asset,
        table=table if status is not TableAvailability.MISSING else None,
    )


def _asset(
    asset_key: tuple[str, ...],
    *,
    uri: str | None,
    latest_materialization_timestamp: float | None,
) -> DagsterTableAsset:
    return DagsterTableAsset(
        asset_key=asset_key,
        group_name="gas_model",
        kinds=("parquet", "table"),
        description="Asset description.",
        uri=uri,
        columns=(DagsterColumnMetadata(name="id", dtype="Int64", description=None),),
        is_materializable=True,
        is_executable=True,
        latest_materialization_timestamp=latest_materialization_timestamp,
    )


def _card(
    cards: tuple[ReadinessCard, ...],
    area: str,
) -> ReadinessCard:
    for card in cards:
        if card.area == area:
            return card
    raise AssertionError(f"missing readiness card: {area}")


def _cards_for_all_states() -> tuple[ReadinessCard, ...]:
    return tuple(
        ReadinessCard(
            area=state.value,
            state=state,
            value=state.value,
            detail=state.value,
            action="No action.",
        )
        for state in ReadinessState
    )
