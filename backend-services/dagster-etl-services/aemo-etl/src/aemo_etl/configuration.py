import os
import datetime as dt
from dataclasses import dataclass

from configurations.parameters import (
    DEVELOPMENT_ENVIRONMENT,
    NAME_PREFIX,
)

LANDING_BUCKET = f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-landing"
BRONZE_BUCKET = f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-bronze"


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


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │        the bottom code is only executed locally (which is when we should be in         │
#     │                                      development)                                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


if os.environ.get("DEVELOPMENT_LOCATION") == "local-s3":
    import os
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
    --attribute-definitions AttributeName=tablePath,AttributeType=S AttributeName=fileName,AttributeType=S \
    --key-schema AttributeName=tablePath,KeyType=HASH AttributeName=fileName,KeyType=RANGE \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
    """
