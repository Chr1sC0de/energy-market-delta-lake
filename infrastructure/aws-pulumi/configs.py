import os

import requests


def get_administrator_ip_address() -> str:
    return requests.get("https://api.ipify.org").text


if os.environ.get("DEVELOPMENT_LOCATION", "").lower() == "local":
    _administrator_ips = [get_administrator_ip_address()]
else:
    _administrator_ips = os.environ.get("ADMINISTRATOR_IPS", "").split(" ")

ADMINISTRATOR_IPS = _administrator_ips
ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")
NAME = f"{ENVIRONMENT}-energy-market"
