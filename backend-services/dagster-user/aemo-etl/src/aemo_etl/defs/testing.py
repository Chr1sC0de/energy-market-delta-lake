"""Opt-in Dagster definitions for operational testing probes."""

from dagster import AssetExecutionContext, Definitions, asset, definitions

FAILED_RUN_ALERT_PROBE_ERROR = (
    "Intentional failure for Dagster failed-run alert testing."
)


@asset(
    key_prefix=["ops", "testing"],
    group_name="ops_testing",
    kinds={"test"},
)
def failed_run_alert_probe(context: AssetExecutionContext) -> None:
    """Manual probe asset that always fails to test failed-run alert delivery."""
    context.log.warning(FAILED_RUN_ALERT_PROBE_ERROR)
    raise RuntimeError(FAILED_RUN_ALERT_PROBE_ERROR)


@definitions
def defs() -> Definitions:
    """Register operational testing assets."""
    return Definitions(assets=[failed_run_alert_probe])
