"""Data transfer objects for NEMWeb public file processing."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Link:
    """Source link discovered from NEMWeb."""

    source_absolute_href: str
    source_upload_datetime: datetime | None = None


@dataclass
class ProcessedLink:
    """NEMWeb link after landing storage processing."""

    source_absolute_href: str
    target_s3_href: str
    target_s3_bucket: str
    target_s3_prefix: str
    target_s3_name: str
    target_ingested_datetime: datetime
    source_upload_datetime: datetime | None = None
