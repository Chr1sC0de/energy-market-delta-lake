# ────────────────────────────────────────────────────────────────────────────────
from abc import ABC, abstractmethod
from typing import Any

from dagster import In, Nothing, OpDefinition, OpExecutionContext, Out, op
from polars import LazyFrame, Schema, col

from aemo_etl.factories.nemweb_public_files.data_models import (
    ProcessedLink,
)
from aemo_etl.utils import get_surrogate_key


class ProcessedLinkedCombiner(ABC):
    @abstractmethod
    def combine(
        self,
        context: OpExecutionContext,
        processed_links: list[ProcessedLink | None],
        schema: Schema,
    ) -> LazyFrame: ...


def build_process_link_combiner_op(
    name: str,
    schema: Schema,
    surrogate_key_sources: list[str],
    io_manager_key: str | None,
    out_metadata_kwargs: dict[str, Any] | None,
    processed_link_combiner: ProcessedLinkedCombiner,
) -> OpDefinition:

    @op(
        name=f"{name}_processed_link_to_dataframe_combiner_op",
        description="""
            for each processed link, combine the downloaded files into a single data
            frame
        """,
        ins={"start": In(Nothing)},
        out=Out(io_manager_key=io_manager_key, metadata=out_metadata_kwargs),
    )
    def _op(
        context: OpExecutionContext, processed_links: list[ProcessedLink | None]
    ) -> LazyFrame:
        df = processed_link_combiner.combine(
            context, processed_links, schema
        ).with_columns(surrogate_key=get_surrogate_key(surrogate_key_sources))
        return df

    return _op


class S3ProcessedLinkCombiner(ProcessedLinkedCombiner):
    def combine(
        self,
        context: OpExecutionContext,
        processed_links: list[ProcessedLink | None],
        schema: Schema,
    ) -> LazyFrame:
        context.log.info("combining links into dataframe")
        filtered_links: list[ProcessedLink] = [
            link for link in processed_links if link is not None
        ]

        output = LazyFrame(
            dict(
                {
                    "source_absolute_href": [
                        link.source_absolute_href for link in filtered_links
                    ],
                    "source_upload_datetime": [
                        link.source_upload_datetime for link in filtered_links
                    ],
                    "target_s3_href": [link.target_s3_href for link in filtered_links],
                    "target_s3_bucket": [
                        link.target_s3_bucket for link in filtered_links
                    ],
                    "target_s3_prefix": [
                        link.target_s3_prefix for link in filtered_links
                    ],
                    "target_s3_name": [link.target_s3_name for link in filtered_links],
                    "target_ingested_datetime": [
                        link.target_ingested_datetime for link in filtered_links
                    ],
                }
            ),
            schema=schema,
        ).with_columns(
            col("source_upload_datetime").dt.convert_time_zone("UTC"),
            col("target_ingested_datetime").dt.convert_time_zone("UTC"),
        )

        context.log.info("finished combining links into dataframe")

        return output
