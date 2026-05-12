"""Private Dagster shell builder for ordinary silver gas-model assets."""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

import polars as pl
from dagster import (
    AssetCheckResult,
    AssetIn,
    AutomationCondition,
    AutomationConditionSensorDefinition,
    Backoff,
    Definitions,
    Jitter,
    MaterializeResult,
    RetryPolicy,
    asset,
    asset_check,
)
from polars import LazyFrame
from polars._typing import PolarsDataType

from aemo_etl.configs import AEMO_BUCKET, DEFAULT_SENSOR_STATUS
from aemo_etl.factories.checks import (
    duplicate_row_check_factory,
    schema_drift_check_factory,
    schema_matches_check_factor,
)
from aemo_etl.utils import get_metadata_schema

DOMAIN = "gas_model"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
IO_MANAGER_KEY = "aemo_parquet_overwrite_io_manager"
KINDS = {"table", "parquet"}

type GasModelMaterializeFn = Callable[..., MaterializeResult[LazyFrame]]
type GasModelSchema = Mapping[str, PolarsDataType]


@dataclass(frozen=True, kw_only=True)
class GasModelAssetSpec:
    """Specification for an ordinary dependency-updated gas-model asset."""

    name: str
    description: str
    ins: Mapping[str, AssetIn]
    materialize: GasModelMaterializeFn
    schema: GasModelSchema
    column_descriptions: Mapping[str, str]
    grain: str
    surrogate_key_sources: Sequence[str]
    source_tables: Sequence[str]
    required_columns: Sequence[str]
    required_fields_description: str


def build_gas_model_asset_definitions(spec: GasModelAssetSpec) -> Definitions:
    """Build Dagster definitions for an ordinary silver gas-model asset."""
    assets_definition = asset(
        name=spec.name,
        key_prefix=KEY_PREFIX,
        group_name=GROUP_NAME,
        description=spec.description,
        ins=dict(spec.ins),
        io_manager_key=IO_MANAGER_KEY,
        metadata={
            "dagster/table_name": f"silver.{DOMAIN}.{spec.name}",
            "dagster/uri": f"s3://{AEMO_BUCKET}/{'/'.join(KEY_PREFIX)}/{spec.name}",
            "dagster/column_schema": get_metadata_schema(
                spec.schema,
                spec.column_descriptions,
            ),
            "grain": spec.grain,
            "surrogate_key_sources": list(spec.surrogate_key_sources),
            "source_tables": list(spec.source_tables),
        },
        kinds=KINDS,
        retry_policy=RetryPolicy(
            max_retries=3,
            delay=60,
            backoff=Backoff.EXPONENTIAL,
            jitter=Jitter.PLUS_MINUS,
        ),
        automation_condition=AutomationCondition.any_deps_updated()
        & ~AutomationCondition.in_progress()
        & ~AutomationCondition.any_deps_missing(),
    )(spec.materialize)

    @asset_check(
        asset=assets_definition,
        name="check_required_fields",
        description=spec.required_fields_description,
    )
    def required_fields_check(input_df: LazyFrame) -> AssetCheckResult:
        null_counts = (
            input_df.select(
                pl.col(column).is_null().sum() for column in spec.required_columns
            )
            .collect()
            .to_dicts()[0]
        )
        passed = all(count == 0 for count in null_counts.values())
        return AssetCheckResult(
            passed=passed,
            check_name="check_required_fields",
            metadata={"null_counts": null_counts},
        )

    return Definitions(
        assets=[assets_definition],
        asset_checks=[
            duplicate_row_check_factory(
                assets_definition=assets_definition,
                check_name="check_for_duplicate_rows",
                primary_key="surrogate_key",
                description="Check that surrogate_key is unique.",
            ),
            schema_matches_check_factor(
                schema=spec.schema,
                assets_definition=assets_definition,
                check_name="check_schema_matches",
                description="Check observed schema matches target schema.",
            ),
            schema_drift_check_factory(
                schema=spec.schema,
                assets_definition=assets_definition,
                check_name="check_schema_drift",
                description="Check for schema drift against the declared asset schema.",
            ),
            required_fields_check,
        ],
        sensors=[
            AutomationConditionSensorDefinition(
                name=f"{spec.name}_sensor",
                target=[assets_definition.key],
                default_status=DEFAULT_SENSOR_STATUS,
            )
        ],
    )
