"""Runtime constants and environment-derived settings for aemo-etl.

Abbreviation key:
- vic, qld, sa = state abbreviations
- dwm = Declared Wholesale Market
- sched = scheduling
- ws = wholesale
- settle = settlements
- meter = metering
- ret = retail
- rpt / rpts = report(s)
- dets = details
"""

import os

from dagster import DefaultScheduleStatus, DefaultSensorStatus

DAGSTER_URI = "dagster/uri"
DAGSTER_FAILURE_ALERT_TOPIC_ARN_ENV_VAR = "DAGSTER_FAILURE_ALERT_TOPIC_ARN"
DAGSTER_FAILURE_ALERT_BASE_URL_ENV_VAR = "DAGSTER_FAILURE_ALERT_BASE_URL"

# ────────────────────────────────────────────────────────────────────────────────

NAME_PREFIX = os.environ.get("NAME_PREFIX", "energy-market")
DEVELOPMENT_ENVIRONMENT = os.environ.get("DEVELOPMENT_ENVIRONMENT", "dev").lower()
DEVELOPMENT_LOCATION = os.environ.get("DEVELOPMENT_LOCATION", "local").lower()

SHARED_PREFIX = f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}"

IO_MANAGER_BUCKET = f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-io-manager"
LANDING_BUCKET = f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-landing"
ARCHIVE_BUCKET = f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-archive"
AEMO_BUCKET = f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-aemo"

# ────────────────────────────────────────────────────────────────────────────────

VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS = "vic_dwm_sched_rpts"
VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS = "vic_ws_settle_meter_rpts"

VICTORIAN_GAS_RETAIL_REPORTS_DETAILS = "vic_gas_ret_rpt_dets"
QUEENSLAND_GAS_RETAIL_REPORT_DETAILS = "qld_gas_ret_rpt_dets"
SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS = "sa_gas_ret_rpts"

ECGS_REPORTS = "ecgs_rpts"

DEFAULT_SENSOR_STATUS = (
    DefaultSensorStatus.RUNNING
    if DEVELOPMENT_LOCATION == "aws"
    else DefaultSensorStatus.STOPPED
)

DEFAULT_SCHEDULE_STATUS = (
    DefaultScheduleStatus.RUNNING
    if DEVELOPMENT_LOCATION == "aws"
    else DefaultScheduleStatus.STOPPED
)
