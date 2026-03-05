import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from time import time
from typing import Self, TypeAlias

from dagster import DynamicOutput, OpDefinition, OpExecutionContext, op
from deltalake.exceptions import TableNotFoundError
from polars import LazyFrame, col, lit, scan_delta
from polars import len as len_

from aemo_etl.factories.download_nemweb_public_files_to_s3.data_models import Link


class DynamicNEMWebLinksFetcher(ABC):
    @abstractmethod
    def fetch(
        self, context: OpExecutionContext, links: list[Link]
    ) -> list[DynamicOutput[Link]]: ...


def build_dynamic_nemweb_links_fetcher_op(
    name: str,
    href: str,
    fetcher: DynamicNEMWebLinksFetcher,
) -> OpDefinition:

    @op(
        name=f"{name}_dynamic_nemweb_link_fetcher_op",
        description=f"extract the list of links from {href}",
    )
    def _op(
        context: OpExecutionContext, links: list[Link]
    ) -> list[DynamicOutput[Link]]:
        return fetcher.fetch(context, links)

    return _op


LinkFilter: TypeAlias = Callable[[OpExecutionContext, Link], bool]


def default_link_filter(context: OpExecutionContext, link: Link) -> bool:
    return True


@dataclass
class FilteredDynamicNEMWebLinksFetcher(DynamicNEMWebLinksFetcher):
    link_filter: LinkFilter = default_link_filter

    def fetch(
        self, context: OpExecutionContext, links: list[Link]
    ) -> list[DynamicOutput[Link]]:
        context.log.info("creating dynamic download group")

        output = []

        for link in links:
            if self.link_filter(context, link):
                output.append(
                    DynamicOutput[Link](
                        link,
                        mapping_key=re.sub(
                            "[^0-9a-zA-Z]+",
                            "_",
                            link.source_absolute_href.split("/")[-1],
                        ),
                    )
                )

        context.log.info("finished creating dynamic download group")
        return output


class InMemoryCachedLinkFilter:
    table_path: str
    _cache: LazyFrame | None

    def __init__(self, table_path: str, ttl_seconds: float) -> None:
        self.table_path = table_path
        self.ttl_seconds = ttl_seconds
        self._cache = None

    def set(self) -> Self:
        self._cache = scan_delta(self.table_path)
        self.cache_time = time()
        return self

    def get(self) -> LazyFrame:
        if self._cache is None:
            self.set()
        else:
            if time() - self.cache_time > self.ttl_seconds:
                self.set()

        assert self._cache is not None, f"cache for {self.table_path} has not been set"

        return self._cache

    def __call__(self, _: OpExecutionContext, link: Link) -> bool:
        try:
            df = self.get()
            search_df = df.filter(
                col("source_absolute_href") == lit(link.source_absolute_href),
                col("source_upload_datetime")
                == lit(link.source_upload_datetime).cast(
                    df.collect_schema()["source_upload_datetime"]
                ),
            )
            if search_df.select(len_()).collect().item() > 0:
                return False
            return True
        except TableNotFoundError:
            return True
