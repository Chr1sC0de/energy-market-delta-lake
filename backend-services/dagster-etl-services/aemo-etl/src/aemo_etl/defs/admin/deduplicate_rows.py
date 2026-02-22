from dagster import AssetExecutionContext, Config
from dagster import asset as dagster_asset
from polars import col, int_range, scan_delta
from polars import len as polars_len

from aemo_etl.util import get_lazyframe_shape


class DeduplicateConfig(Config):
    s3_uri: str
    primary_keys: list[str]
    sort_keys: list[str] | None = None


@dagster_asset(
    name="deduplicate_lazyframe_rows", key_prefix=["admin"], group_name="admin"
)
def asset(context: AssetExecutionContext, config: DeduplicateConfig) -> None:
    context.log.info(
        f"deduplicating rows for {config.s3_uri} with primary keys {config.primary_keys}"  # noqa: E501
    )
    original_df = scan_delta(config.s3_uri)

    context.log.info(f"shape of original dataframe {get_lazyframe_shape(original_df)}")

    deduplicated_df = (
        original_df.with_columns(
            int_range(polars_len())
            .over(config.primary_keys, order_by=config.sort_keys, descending=True)
            .alias("row_num")
        ).filter(col.row_num == 0)
    ).drop("row_num")

    context.log.info(
        f"shape of deduplicated dataframe {get_lazyframe_shape(deduplicated_df)}"
    )

    deduplicated_df.sink_delta(
        config.s3_uri,
        mode="overwrite",
    )
