import importlib
from pathlib import Path
from typing import Any, Callable, Sequence

import pytest
from dagster import AssetsDefinition, Definitions, materialize
from dagster_aws.s3 import S3Resource

from aemo_etl.defs.resources import (
    PolarsDataFrameSinkDeltaIoManager,
)
from tests.utils import GBB_DATA_DIR

_GBB_DEFS_DIR = Path(__file__).parents[3] / "src" / "aemo_etl" / "defs" / "raw" / "gbb"

_RESOURCES = {
    "s3": S3Resource(),
    "aemo_deltalake_ingest_partitioned_append_io_manager": PolarsDataFrameSinkDeltaIoManager(
        sink_delta_kwargs={
            "mode": "append",
            "delta_write_options": {"partition_by": "ingested_date"},
        }
    ),
    "aemo_deltalake_append_io_manager": PolarsDataFrameSinkDeltaIoManager(
        sink_delta_kwargs={"mode": "append"}
    ),
}


def _load_gbb_params() -> Sequence[Any]:
    params = []
    for f in sorted(_GBB_DEFS_DIR.glob("gasbb_*.py")):
        mod = importlib.import_module(f"aemo_etl.defs.raw.gbb.{f.stem}")
        params.append(pytest.param(mod.defs, id=f.stem))
    return params


@pytest.mark.parametrize("gbb_defs", _load_gbb_params())
@pytest.mark.skipif(
    condition=not GBB_DATA_DIR.exists(), reason=f"no gbb data dir {GBB_DATA_DIR}"
)
def test_gbb_bronze_silver(
    gbb_defs: Definitions,
    upload_gbb_files: Callable[[str], list[str]],
) -> None:
    bronze = next(
        a
        for a in (gbb_defs.assets or [])
        if isinstance(a, AssetsDefinition) and "bronze" in str(a.key)
    )

    glob_pattern: str = bronze.metadata_by_key[bronze.key]["glob_pattern"]

    s3_keys = upload_gbb_files(glob_pattern)
    assert s3_keys, f"No local files found for glob_pattern={glob_pattern!r}"

    op_key = bronze.key.to_python_identifier()

    result = materialize(
        [a for a in (gbb_defs.assets or []) if isinstance(a, AssetsDefinition)],
        resources=_RESOURCES,
        run_config={"ops": {op_key: {"config": {"s3_keys": s3_keys}}}},
    )
    assert result.success
