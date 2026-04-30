"""Post-processing hooks for S3-key driven asset ingestion."""

from abc import ABC, abstractmethod

from polars import LazyFrame, col, row_index


class Hook[T](ABC):
    """Base hook for object or LazyFrame post-processing."""

    @abstractmethod
    def process(self, s3_bucket: str, s3_key: str, object_: T) -> T:
        """Process an object loaded from S3."""
        ...


class Deduplicate(Hook[LazyFrame]):
    """Remove duplicate rows by keeping the first surrogate key occurrence."""

    def process(self, s3_bucket: str, s3_key: str, object_: LazyFrame) -> LazyFrame:
        """Deduplicate the LazyFrame by surrogate key."""
        return (
            object_.with_columns(row_num=row_index().over("surrogate_key"))
            .filter(col.row_num == 0)
            .drop("row_num")
        )
