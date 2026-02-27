from collections.abc import Mapping

from dagster import TableColumn, TableSchema
from polars import DataType, Datetime, Schema


def get_metadata_schema(
    df_schema: Mapping[str, type[DataType] | Datetime] | Schema,
    descriptions: Mapping[str, str] | None = None,
) -> TableSchema:
    descriptions = descriptions or {}
    return TableSchema(
        columns=[
            TableColumn(name=col, type=str(pl_type), description=descriptions.get(col))
            for col, pl_type in df_schema.items()
        ]
    )
