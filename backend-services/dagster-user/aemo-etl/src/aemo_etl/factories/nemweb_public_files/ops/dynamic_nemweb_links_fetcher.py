"""Dagster ops and strategies for batching NEMWeb links dynamically."""

import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from time import time
from typing import Self, TypeAlias

from dagster import (
    Backoff,
    DynamicOutput,
    Jitter,
    OpDefinition,
    OpExecutionContext,
    RetryPolicy,
    op,
)
from deltalake.exceptions import TableNotFoundError
from polars import LazyFrame, col, lit, scan_delta
from polars import len as len_

from aemo_etl.factories.nemweb_public_files.models import Link


class DynamicNEMWebLinksFetcher(ABC):
    """Strategy for splitting NEMWeb links into dynamic output batches."""

    @abstractmethod
    def fetch(
        self, context: OpExecutionContext, links: list[Link]
    ) -> list[DynamicOutput[list[Link]]]:
        """Return dynamic output batches for the provided links."""
        ...


def build_dynamic_nemweb_links_fetcher_op(
    name: str,
    href: str,
    fetcher: DynamicNEMWebLinksFetcher,
    retry_policy: RetryPolicy = RetryPolicy(
        max_retries=3,
        delay=5,
        backoff=Backoff.EXPONENTIAL,
        jitter=Jitter.PLUS_MINUS,
    ),
) -> OpDefinition:
    """Build the Dagster op that batches discovered NEMWeb links."""

    @op(
        name=f"{name}_dynamic_nemweb_link_fetcher_op",
        description=f"extract the list of links from {href}",
        retry_policy=retry_policy,
    )
    def _op(
        context: OpExecutionContext, links: list[Link]
    ) -> list[DynamicOutput[list[Link]]]:
        return fetcher.fetch(context, links)

    return _op


LinkFilter: TypeAlias = Callable[[OpExecutionContext, Link], bool]


def default_link_filter(context: OpExecutionContext, link: Link) -> bool:
    """Accept every discovered link."""
    return True


@dataclass
class FilteredDynamicNEMWebLinksFetcher(DynamicNEMWebLinksFetcher):
    """Batch links after applying a configurable link filter."""

    batch_size: int = 1
    n_executors: int | None = None
    link_filter: LinkFilter = default_link_filter

    def fetch(
        self, context: OpExecutionContext, links: list[Link]
    ) -> list[DynamicOutput[list[Link]]]:
        """Return filtered NEMWeb link batches for dynamic mapping."""
        context.log.info("creating dynamic download group")

        batch: list[Link] = []
        batches = []

        batch_size = self.batch_size

        if self.n_executors is not None:
            batch_size = len(links) // self.n_executors

        for link in links:
            if self.link_filter(context, link):
                if len(batch) == batch_size:
                    batches.append(batch)
                    batch = [link]
                else:
                    batch.append(link)

        if batch:
            batches.append(batch)

        output = []

        for i, batch in enumerate(batches):
            output.append(
                DynamicOutput[list[Link]](
                    batch,
                    mapping_key=re.sub(
                        "[^0-9a-zA-Z]+",
                        "_",
                        f"{i}_{batch[0].source_absolute_href}",
                    ),
                )
            )

        context.log.info("finished creating dynamic download group")
        return output


class InMemoryCachedLinkFilter:
    """Filter out links already present in a cached Delta table scan."""

    _cache: LazyFrame | None

    def __init__(self, table_path: str, ttl_seconds: float) -> None:
        """Initialise the filter for a Delta table path and cache TTL."""
        self.table_path = table_path
        self.ttl_seconds = ttl_seconds
        self._cache = None

    def set(self) -> Self:
        """Refresh the cached Delta scan."""
        self._cache = scan_delta(self.table_path)
        self.cache_time = time()
        return self

    def get(self) -> LazyFrame:
        """Return the cached Delta scan, refreshing it when stale."""
        if self._cache is None:
            self.set()
        else:
            if time() - self.cache_time > self.ttl_seconds:
                self.set()

        assert self._cache is not None, f"cache for {self.table_path} has not been set"

        return self._cache

    def __call__(self, context: OpExecutionContext, link: Link) -> bool:
        """Return whether a link is absent from the cached table."""
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
