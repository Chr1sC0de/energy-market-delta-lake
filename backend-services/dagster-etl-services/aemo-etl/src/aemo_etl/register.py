from typing import Literal, TypedDict

from dagster import Definitions


class TableLocation(TypedDict):
    table_name: str
    table_type: Literal["parquet", "delta"]
    glue_schema: str
    s3_table_location: str


table_locations: dict[str, TableLocation] = {}
definitions_list: list[Definitions] = []
