import pathlib as pt
from typing import cast

import dagster as dg
import polars as pl

from aemo_etl.configuration.registry import GASBB_CONFIGS
from aemo_etl.definitions.bronze_gasbb_reports.utils import default_post_process_hook

cwd = pt.Path(__file__).parent

primary_keys = GASBB_CONFIGS["bronze_gasbb_medium_term_capacity_outlook"].primary_keys


def main() -> None:
    source_file = cwd / "gasbbmediumtermcapacityoutlook~250719162416.parquet"
    default_post_process_hook(
        dg.build_asset_context(),
        pl.scan_parquet(source_file).with_columns(
            source_file=pl.lit("gasbbmediumtermcapacityoutlook~250719162416.parquet")
        ),
        primary_keys=primary_keys,
        datetime_pattern="%Y/%m/%d %H:%M:%S",
    ).pipe(lambda lf: cast(pl.DataFrame, lf.collect())).write_delta(
        cwd / "bronze_gasbb_medium_term_capacity_outlook"
    )


if __name__ == "__main__":
    main()
