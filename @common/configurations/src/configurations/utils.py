import requests


def get_administrator_ip_address() -> str:
    return requests.get("https://api.ipify.org").text
