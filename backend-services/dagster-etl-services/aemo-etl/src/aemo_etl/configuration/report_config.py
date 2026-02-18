from collections.abc import Mapping

from polars import DataType, Schema
from pydantic import BaseModel, Field, model_validator

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations


class ReportConfig(BaseModel):
    """Configuration for an AEMO report ETL pipeline.

    This Pydantic model defines all configuration parameters needed to set up
    a data ingestion pipeline for AEMO reports (MIBB and GASBB).
    """

    table_name: str = Field(..., description="Name of the table")
    s3_prefix: str = Field(..., description="S3 prefix for the data files")
    s3_file_glob: str = Field(..., description="Glob pattern for matching files")
    s3_table_location: str = Field(..., description="Full S3 path to the table")
    primary_keys: list[str] = Field(..., description="List of primary key column names")
    upsert_predicate: str = Field(
        ..., description="SQL predicate for upsert operations"
    )
    table_schema: Mapping[str, type[DataType]] | Schema = Field(
        ..., description="Polars schema definition"
    )
    schema_descriptions: Mapping[str, str] = Field(
        ..., description="Description for each column"
    )
    report_purpose: str = Field(
        ..., description="Purpose and description of the report"
    )
    group_name: str = Field(..., description="Dagster asset group name")
    key_prefix: list[str] = Field(..., description="Asset key prefix for Dagster")

    model_config = {"arbitrary_types_allowed": True}

    @model_validator(mode="after")
    def register_table_location(self) -> "ReportConfig":
        """Auto-register table location in global registry."""
        table_locations[self.table_name] = {
            "table_name": self.table_name,
            "table_type": "delta",
            "glue_schema": "aemo",
            "s3_table_location": self.s3_table_location,
        }
        return self


def mibb_config_factory(
    table_name: str,
    s3_file_glob: str,
    primary_keys: list[str],
    table_schema: Mapping[str, type[DataType]] | Schema,
    schema_descriptions: Mapping[str, str],
    report_purpose: str,
    group_name: str,
) -> ReportConfig:
    """Factory to create MIBB config with standard defaults.

    Args:
        table_name: Name of the table (e.g., "bronze_int037b_v4_indicative_mkt_price_1")
        s3_file_glob: Glob pattern for matching files in S3
        primary_keys: List of primary key column names
        table_schema: Polars schema definition mapping column names to types
        schema_descriptions: Description for each column
        report_purpose: Purpose and description of the report
        group_name: Dagster asset group name (e.g., "aemo__mibb__vic_dwm_sched_rpts")

    Returns:
        Configured ReportConfig instance with auto-registered table location
    """
    s3_prefix = "aemo/vicgas"
    return ReportConfig(
        table_name=table_name,
        s3_prefix=s3_prefix,
        s3_table_location=f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}",
        s3_file_glob=s3_file_glob,
        primary_keys=primary_keys,
        upsert_predicate="s.surrogate_key = t.surrogate_key",
        table_schema=table_schema,
        schema_descriptions=schema_descriptions,
        report_purpose=report_purpose,
        group_name=group_name,
        key_prefix=["bronze", "aemo", "vicgas"],
    )


def gasbb_config_factory(
    table_name: str,
    s3_file_glob: str,
    primary_keys: list[str],
    table_schema: Mapping[str, type[DataType]] | Schema,
    schema_descriptions: Mapping[str, str],
    report_purpose: str,
) -> ReportConfig:
    """Factory to create GASBB config with standard defaults.

    Args:
        table_name: Name of the table (e.g., "bronze_gasbb_basins")
        s3_file_glob: Glob pattern for matching files in S3
        primary_keys: List of primary key column names
        table_schema: Polars schema definition mapping column names to types
        schema_descriptions: Description for each column
        report_purpose: Purpose and description of the report

    Returns:
        Configured ReportConfig instance with auto-registered table location
    """
    s3_prefix = "aemo/gasbb"
    return ReportConfig(
        key_prefix=["bronze", "aemo", "gasbb"],
        table_name=table_name,
        s3_prefix=s3_prefix,
        s3_table_location=f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}",
        s3_file_glob=s3_file_glob,
        primary_keys=primary_keys,
        upsert_predicate="s.surrogate_key = t.surrogate_key",
        table_schema=table_schema,
        schema_descriptions=schema_descriptions,
        report_purpose=report_purpose,
        group_name="aemo__gasbb",
    )
