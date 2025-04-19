import polars as pl
from aemo_gas import utils


def post_process_hook(df: pl.LazyFrame) -> pl.LazyFrame:
    return (
        df.filter(
            (
                pl.col("current_date").str.strptime(pl.Datetime, "%d %b %Y %H:%M:%S")
                == pl.col("current_date")
                .str.strptime(pl.Datetime, "%d %b %Y %H:%M:%S")
                .max()
            ).over("system_wide_notice_id")
        )
        .collect()
        .lazy()
    )


config = dict(
    group_name="BRONZE__AEMO__GAS__VICHUB",
    key_prefix=["bronze", "aemo", "gas", "vichub"],
    name="int029a_system_wide_notices",
    schema=dict(
        system_wide_notice_id=pl.Int64,
        critical_notice_flag=pl.String,
        system_message=pl.String,
        system_email_message=pl.String,
        notice_start_date=pl.String,
        notice_end_date=pl.String,
        url_path=pl.String,
        current_date=pl.String,
    ),
    search_prefix="int029a_",
    io_manager_key="bronze_aemo_gas_upsert_io_manager",
    description=utils.join_by_newlines(
        "This report is a comma separated values (csv) file that contains details of public system-wide notices published by AEMO to",
        "the MIBB. This report allows AEMO to provide consistent information (in content and timing) to the public about the market",
        "operation. The same content is published in INT029a as a downloadable csv file, while report INT105 is an HTML file that can",
        "be viewed in a web browser",
        "Similar reports titled INT029b and INT106 are published directly to specific Registered Participants on the MIBB.",
    ),
    metadata={
        "merge_predicate": utils.join_by_newlines(
            "s.system_wide_notice_id = t.system_wide_notice_id",
        ),
    },
    # schedules are in utc
    compact_and_vacuum_cron_schedule="00 23 * * *",
    execution_timezone="Australia/Melbourne",
    post_process_hook=post_process_hook,
)
