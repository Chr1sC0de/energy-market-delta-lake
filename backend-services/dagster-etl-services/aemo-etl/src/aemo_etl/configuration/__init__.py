import os

from aemo_etl.configuration._configuration import (
    ADMINISTRATOR_IPS,
    BRONZE_BUCKET,
    DEVELOPMENT_ENVIRONMENT,
    DEVELOPMENT_LOCATION,
    ECGS_REPORTS,
    GOLD_BUCKET,
    IO_MANAGER_BUCKET,
    LANDING_BUCKET,
    NAME_PREFIX,
    QUEENSLAND_GAS_RETAIL_REPORT_DETAILS,
    SHARED_PREFIX,
    SILVER_BUCKET,
    SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS,
    STACK_PREFIX,
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
    VICTORIAN_GAS_RETAIL_REPORTS_DETAILS,
    VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS,
    Link,
    ProcessedLink,
)
from aemo_etl.configuration import gasbb, mibb

__all__ = [
    "NAME_PREFIX",
    "STACK_PREFIX",
    "DEVELOPMENT_ENVIRONMENT",
    "DEVELOPMENT_LOCATION",
    "ADMINISTRATOR_IPS",
    "SHARED_PREFIX",
    "IO_MANAGER_BUCKET",
    "LANDING_BUCKET",
    "BRONZE_BUCKET",
    "SILVER_BUCKET",
    "GOLD_BUCKET",
    "VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS",
    "VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS",
    "VICTORIAN_GAS_RETAIL_REPORTS_DETAILS",
    "QUEENSLAND_GAS_RETAIL_REPORT_DETAILS",
    "SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS",
    "ECGS_REPORTS",
    "Link",
    "ProcessedLink",
    "gasbb",
    "mibb",
]


if os.environ.get("DEVELOPMENT_LOCATION") == "local-s3":
    from boto3.session import Session

    session = Session()
    credentials = session.get_credentials()

    if credentials is not None:
        current_credentials = credentials.get_frozen_credentials()

        if current_credentials.access_key is not None:
            os.environ["AWS_ACCESS_KEY_ID"] = current_credentials.access_key

        if current_credentials.secret_key is not None:
            os.environ["AWS_SECRET_ACCESS_KEY"] = current_credentials.secret_key

        if current_credentials.token is not None:
            os.environ["AWS_SESSION_TOKEN"] = current_credentials.token
        os.environ["AWS_REGION"] = "ap-southeast-2"

    # ── to not use locking ──────────────────────────────────────────────────────────
    # os.environ["AWS_S3_ALLOW_UNSAFE_RENAME"] = "true"

    # ── use the bellow code when using dynamo db ────────────────────────────────────
    os.environ["AWS_S3_LOCKING_PROVIDER"] = "dynamodb"

    """ create a test locking table with the bellow code
    aws dynamodb create-table \
    --table-name delta_log \
    --attribute-definitions
        AttributeName=tablePath,AttributeType=S
        AttributeName=fileName,AttributeType=S \
    --key-schema
        AttributeName=tablePath,KeyType=HASH
        AttributeName=fileName,KeyType=RANGE \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
    """
