import uuid
from collections.abc import Mapping
from typing import Callable, cast

import requests
from dagster import TableColumn, TableSchema
from polars import DataType, Datetime, LazyFrame, Schema
from polars import len as len_
from requests import Response


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


def request_get(
    path: str, getter: Callable[[str], Response] = requests.get
) -> Response:
    response: Response = getter(path)
    response.raise_for_status()
    return response


def add_random_suffix(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def get_lazyframe_num_rows(df: LazyFrame) -> int:
    return cast(int, df.select(len_()).collect().item())
