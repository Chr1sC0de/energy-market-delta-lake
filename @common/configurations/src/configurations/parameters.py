import os
from configurations.utils import get_administrator_ip_address


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
