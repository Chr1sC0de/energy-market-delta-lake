import re
from io import BytesIO
from textwrap import dedent

import bs4
import requests
from dagster import OpExecutionContext, job, op
from dagster_aws.s3 import S3Resource
from types_boto3_s3 import S3Client

from aemo_etl.configs import LANDING_BUCKET
from aemo_etl.utils import get_response_factory

ROOT_URL = "https://nemweb.com.au"
REPORT_URL = f"{ROOT_URL}/REPORTS/CURRENT/VicGas"
PUBLIC_REPORT_PATTERN = re.compile(r"^PublicRpts\d{2}\.zip$", re.IGNORECASE)
S3_PREFIX = "bronze/vicgas"
DESCRIPTION = dedent(f"""
    Download the public report zip files from {REPORT_URL} and upload to {LANDING_BUCKET}/{S3_PREFIX}.
""").strip("\n")


@op(description=f"Operation: {DESCRIPTION}".replace("\n\n", "\n"))
def download_vicgas_public_report_zip_files_op(
    context: OpExecutionContext, s3: S3Resource
) -> None:
    response = requests.get(REPORT_URL, timeout=30)
    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.text)

    public_report_links = []

    for link in soup.findAll("a"):
        if not isinstance(link, bs4.Tag):
            continue

        if link.text.lower() == "[to parent directory]":
            continue

        ref = link.get("href")

        if (
            not isinstance(ref, str)
            or not ref.lower().endswith(".zip")
            or "publicrpts" not in ref.lower()
        ):
            continue

        public_report_links.append(f"{ROOT_URL}{ref}")

    response_getter = get_response_factory()

    s3_client: S3Client = s3.get_client()

    for link in public_report_links:
        context.log.info(f"uploading {link} to s3://{LANDING_BUCKET}/{S3_PREFIX}")
        contents = response_getter(link)
        s3_client.upload_fileobj(BytesIO(contents), LANDING_BUCKET, S3_PREFIX)


@job(
    description=f"Job: {DESCRIPTION}. To be run ad-hoc e.g. during initialization or sync missing data".replace(
        "\n\n", "\n"
    )
)
def download_vicgas_public_report_zip_files_job() -> None:
    download_vicgas_public_report_zip_files_op()
