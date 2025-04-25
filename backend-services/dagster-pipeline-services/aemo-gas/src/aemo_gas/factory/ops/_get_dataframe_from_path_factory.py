import polars as pl
from typing import Callable
import dagster as dg
from aemo_gas import utils


def get_dataframe_from_path_factory(
    name: str, table_path: str
) -> Callable[[], pl.LazyFrame | None]:
    @dg.op(name=name)
    def get_dataframe_from_path() -> pl.LazyFrame | None:
        return utils.get_table(table_path)

    return get_dataframe_from_path
