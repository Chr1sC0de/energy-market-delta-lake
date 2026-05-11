import ipaddress
import os

import requests


def get_administrator_ip_address() -> str:
    return requests.get("https://api.ipify.org").text


def _administrator_cidrs_from_env() -> list[str]:
    if os.environ.get("DEVELOPMENT_LOCATION", "").lower() == "local":
        raw_values = [get_administrator_ip_address()]
    else:
        raw_values = os.environ.get("ADMINISTRATOR_IPS", "").split()

    administrator_cidrs: list[str] = []
    for raw_value in raw_values:
        value = raw_value.strip()
        if value == "":
            continue

        network_value = value if "/" in value else f"{value}/32"
        network = ipaddress.ip_network(network_value, strict=False)
        if network.version != 4:
            raise ValueError(f"ADMINISTRATOR_IPS only supports IPv4 CIDRs: {value!r}")
        if network.prefixlen != 32:
            raise ValueError(
                "ADMINISTRATOR_IPS must contain individual administrator IPv4 "
                f"addresses or /32 CIDRs, got {value!r}"
            )
        administrator_cidrs.append(str(network))

    if len(administrator_cidrs) == 0:
        raise ValueError("ADMINISTRATOR_IPS must contain at least one administrator IP")

    return administrator_cidrs


ADMINISTRATOR_CIDRS = _administrator_cidrs_from_env()
ADMINISTRATOR_IPS = ADMINISTRATOR_CIDRS
ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")
NAME = f"{ENVIRONMENT}-energy-market"
