from abc import ABC, abstractmethod

from polars import LazyFrame, col, row_index


class Hook[T](ABC):
    @abstractmethod
    def process(self, s3_bucket: str, s3_key: str, object_: T) -> T: ...


class Deduplicate(Hook[LazyFrame]):
    def process(self, s3_bucket: str, s3_key: str, object_: LazyFrame) -> LazyFrame:
        return (
            object_.with_columns(row_num=row_index().over("surrogate_key"))
            .filter(col.row_num == 0)
            .drop("row_num")
        )
