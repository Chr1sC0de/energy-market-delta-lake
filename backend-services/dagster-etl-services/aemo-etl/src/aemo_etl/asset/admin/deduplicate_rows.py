from dagster import AssetExecutionContext, Config
from dagster import asset as dagster_asset
from polars import col, int_range, read_delta
from polars import len as polars_len


class DeduplicateConfig(Config):
    s3_uri: str
    primary_keys: list[str]
    sort_keys: list[str] | None = None


@dagster_asset(
    name="deduplicate_lazyframe_rows", key_prefix=["admin"], group_name="admin"
)
def asset(context: AssetExecutionContext, config: DeduplicateConfig):
    context.log.info(
        f"deduplicating rows for {config.s3_uri} with primary keys {config.primary_keys}"
    )
    original_df = read_delta(config.s3_uri)

    context.log.info(f"shape of original dataframe {original_df.shape}")

    deduplicated_df = (
        original_df.with_columns(
            int_range(polars_len())
            .over(config.primary_keys, order_by=config.sort_keys, descending=True)
            .alias("row_num")
        ).filter(col.row_num == 0)
    ).drop("row_num")

    context.log.info(f"shape of deduplicated dataframe {deduplicated_df.shape}")

    deduplicated_df.write_delta(
        config.s3_uri,
        mode="overwrite",
    )
