import hashlib

import polars as pl
from requests import Response
from types_boto3_s3 import S3Client

from aemo_etl.configs import AEMO_BUCKET, ARCHIVE_BUCKET, LANDING_BUCKET
from aemo_etl.factories.aemo_gas_documents.assets import (
    AEMO_GAS_DOCUMENTS_PREFIX,
    records_to_lazyframe,
    scrape_and_land_aemo_gas_document_sources,
    write_aemo_gas_document_sources_batch,
)
from aemo_etl.factories.aemo_gas_documents.models import AEMOGasDocumentSourcePage

_PAGE_URL = "https://www.aemo.com.au/energy-systems/gas/integration"
_PDF_URL = "https://www.aemo.com.au/-/media/files/gas/integration-guide.pdf"
_PDF_BYTES = b"%PDF integration\n%%EOF\n"


def _response(*, url: str, text: str = "", content: bytes | None = None) -> Response:
    response = Response()
    response.status_code = 200
    response.url = url
    response.headers["Content-Type"] = "application/pdf" if content else "text/html"
    response.headers["Content-Length"] = str(len(content or text.encode("utf-8")))
    response._content = content if content is not None else text.encode("utf-8")
    response.encoding = "utf-8"
    return response


def _object_exists(s3: S3Client, *, bucket: str, key: str) -> bool:
    response = s3.list_objects_v2(Bucket=bucket, Prefix=key)
    return any(item["Key"] == key for item in response.get("Contents", []))


def test_aemo_gas_document_metadata_writes_delta_and_archives_pdf(
    s3: S3Client,
) -> None:
    html = f"<html><body><h1>Integration</h1><a href='{_PDF_URL}'>Integration Guide v1.0</a></body></html>"
    responses = {
        _PAGE_URL: _response(url=_PAGE_URL, text=html),
        _PDF_URL: _response(url=_PDF_URL, content=_PDF_BYTES),
    }

    def _request_getter(url: str) -> Response:
        return responses[url]

    scrape_result = scrape_and_land_aemo_gas_document_sources(
        s3_client=s3,
        source_pages=(
            AEMOGasDocumentSourcePage(
                corpus_source="integration",
                source_page_url=_PAGE_URL,
                include_decision="include",
            ),
        ),
        request_getter=_request_getter,
    )
    batch = records_to_lazyframe(
        scrape_result.records,
        ingested_timestamp=scrape_result.records[0].source_page_observed_at,
    )
    table_uri = (
        f"s3://{AEMO_BUCKET}/{AEMO_GAS_DOCUMENTS_PREFIX}/"
        "bronze_aemo_gas_document_sources"
    )
    write_result = write_aemo_gas_document_sources_batch(
        batch,
        target_table_uri=table_uri,
    )
    for key in scrape_result.landed_keys:
        s3.copy_object(
            CopySource={"Bucket": LANDING_BUCKET, "Key": key},
            Bucket=ARCHIVE_BUCKET,
            Key=key,
        )
        s3.delete_object(Bucket=LANDING_BUCKET, Key=key)

    expected_key = (
        f"{AEMO_GAS_DOCUMENTS_PREFIX}/{hashlib.sha256(_PDF_BYTES).hexdigest()}.pdf"
    )

    assert write_result.wrote_table is True
    assert scrape_result.landed_keys == [expected_key]
    assert not _object_exists(s3, bucket=LANDING_BUCKET, key=expected_key)
    assert _object_exists(s3, bucket=ARCHIVE_BUCKET, key=expected_key)

    frame = pl.scan_delta(table_uri).collect()
    pdf_rows = frame.filter(pl.col("content_sha256").is_not_null())
    decisions = set(frame["include_decision"].to_list())

    assert frame.height == 2
    assert decisions == {"include"}
    assert pdf_rows["storage_uri"].to_list() == [
        f"s3://{ARCHIVE_BUCKET}/{expected_key}"
    ]
    assert pdf_rows["document_version_id"].to_list() == [
        hashlib.sha256(_PDF_BYTES).hexdigest()
    ]
