from deltalake.exceptions import TableNotFoundError
import polars as pl
import dagster as dg


def factory(name: str, table_path: str) -> dg.OpDefinition:
    @dg.op(name=name)
    def get_table_op() -> pl.LazyFrame | None:
        try:
            df = pl.read_delta(table_path, use_pyarrow=True).lazy()
        except TableNotFoundError:
            df = None
        return df

    return get_table_op
