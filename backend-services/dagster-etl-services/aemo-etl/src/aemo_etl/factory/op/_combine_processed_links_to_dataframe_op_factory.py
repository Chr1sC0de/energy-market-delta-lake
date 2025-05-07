from typing import Callable, Unpack

from dagster import OpDefinition, OpExecutionContext, op
from polars import Datetime, LazyFrame, String

from aemo_etl.configuration import ProcessedLink
from aemo_etl.factory.op.schema import OpKwargs


ProcessDataFrameHooks = Callable[[OpExecutionContext, LazyFrame], LazyFrame] | None


schema = {
    "source_absolute_href": String,
    "source_upload_datetime": Datetime("ms", time_zone="Australia/Melbourne"),
    "target_s3_href": String,
    "target_s3_bucket": String,
    "target_s3_prefix": String,
    "target_s3_name": String,
    "target_ingested_datetime": Datetime("ms", time_zone="Australia/Melbourne"),
}


def combine_processed_links_to_dataframe_op_factory(
    post_process_dataframe_hook: ProcessDataFrameHooks = None,
    **op_kwargs: Unpack[OpKwargs],
) -> OpDefinition:
    op_kwargs.setdefault("name", "combine_processed_links_to_dataframe_op")
    op_kwargs.setdefault(
        "description",
        "combine provided links into a dataframe",
    )

    @op(**op_kwargs)
    def combine_processed_links_to_dataframe_op(
        context: OpExecutionContext, processed_links: list[ProcessedLink | None]
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
        )

        if post_process_dataframe_hook is not None:
            output = post_process_dataframe_hook(context, output)

        context.log.info("finished combining links into dataframe")

        return output

    return combine_processed_links_to_dataframe_op
