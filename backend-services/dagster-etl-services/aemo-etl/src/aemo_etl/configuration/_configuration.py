import datetime as dt
import os
from dataclasses import dataclass

import requests


def get_administrator_ip_address() -> str:
    return requests.get("https://api.ipify.org").text


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                            name which prefixes every object                            │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯
NAME_PREFIX = os.environ.get("NAME_PREFIX", "energy-market")

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                            name which prefixes every stack                             │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯
STACK_PREFIX = "".join(
    [part.capitalize() for part in NAME_PREFIX.replace("_", "-").split("-")]
)

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                             grab the required environments                             │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯
DEVELOPMENT_ENVIRONMENT = os.environ.get("DEVELOPMENT_ENVIRONMENT", "dev").lower()
DEVELOPMENT_LOCATION = os.environ.get("DEVELOPMENT_LOCATION", "local").lower()

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      collect the required ips for administration                       │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

if os.environ.get("DEVELOPMENT_LOCATION", "").lower() == "local":
    _administrator_ips = [get_administrator_ip_address()]
else:
    _administrator_ips = os.environ.get("ADMINISTRATOR_IPS", "").split(" ")

ADMINISTRATOR_IPS = _administrator_ips

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │         This prefix combines the development environment wit hthe name prefix          │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯
SHARED_PREFIX = f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}"

IO_MANAGER_BUCKET = f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-io-manager"
LANDING_BUCKET = f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-landing"
BRONZE_BUCKET = f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-bronze"
SILVER_BUCKET = f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-silver"
GOLD_BUCKET = f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-gold"

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

VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS = "vic_dwm_sched_rpts"
VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS = "vic_ws_settle_meter_rpts"

VICTORIAN_GAS_RETAIL_REPORTS_DETAILS = "vic_gas_ret_rpt_dets"
QUEENSLAND_GAS_RETAIL_REPORT_DETAILS = "qld_gas_ret_rpt_dets"
SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS = "sa_gas_ret_rpts"

ECGS_REPORTS = "ecgs_rpts"


@dataclass
class Link:
    source_absolute_href: str
    source_upload_datetime: dt.datetime | None = None


@dataclass
class ProcessedLink:
    source_absolute_href: str
    target_s3_href: str
    target_s3_bucket: str
    target_s3_prefix: str
    target_s3_name: str
    target_ingested_datetime: dt.datetime
    source_upload_datetime: dt.datetime | None = None
