import polars as pl
import pathlib as pt
import dagster as dg
from aemo_etl.definitions.bronze_gasbb_reports.bronze_gasbb_medium_term_capacity_outlook import (
    default_post_process_hook,
    primary_keys,
)

cwd = pt.Path(__file__).parent


def main():
    source_file = cwd / "gasbbmediumtermcapacityoutlook~250719162416.parquet"
    default_post_process_hook(
        dg.build_asset_context(),
        pl.scan_parquet(source_file).with_columns(
            source_file=pl.lit("gasbbmediumtermcapacityoutlook~250719162416.parquet")
        ),
        primary_keys=primary_keys,
        datetime_pattern="%Y/%m/%d %H:%M:%S",
    ).collect().write_delta(cwd / "bronze_gasbb_medium_term_capacity_outlook")


if __name__ == "__main__":
    main()
