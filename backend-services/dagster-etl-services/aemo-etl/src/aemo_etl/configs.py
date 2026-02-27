"""
Abbreviation Key:
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

# ────────────────────────────────────────────────────────────────────────────────

NAME_PREFIX = os.environ.get("NAME_PREFIX", "energy-market")
DEVELOPMENT_ENVIRONMENT = os.environ.get("DEVELOPMENT_ENVIRONMENT", "dev").lower()
DEVELOPMENT_LOCATION = os.environ.get("DEVELOPMENT_LOCATION", "local").lower()

SHARED_PREFIX = f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}"

IO_MANAGER_BUCKET = f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-io-manager"
LANDING_BUCKET = f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-landing"
BRONZE_BUCKET = f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-bronze"
SILVER_BUCKET = f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-silver"
GOLD_BUCKET = f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-gold"

# ────────────────────────────────────────────────────────────────────────────────

VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS = "vic_dwm_sched_rpts"
VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS = "vic_ws_settle_meter_rpts"

VICTORIAN_GAS_RETAIL_REPORTS_DETAILS = "vic_gas_ret_rpt_dets"
QUEENSLAND_GAS_RETAIL_REPORT_DETAILS = "qld_gas_ret_rpt_dets"
SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS = "sa_gas_ret_rpts"

ECGS_REPORTS = "ecgs_rpts"
