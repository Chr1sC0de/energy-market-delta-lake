from aemo_gas import utils

config = dict(
    group_name="BRONZE__AEMO__GAS__VICHUB",
    key_prefix=["bronze", "aemo", "gas", "vichub"],
    name="int029a_system_wide_notices",
    schema=dict(
        system_wide_notice_id=int,
        critical_notice_flag=str,
        system_message=str,
        system_email_message=str,
        notice_start_date=str,
        notice_end_date=str,
        url_path=str,
        current_date=str,
    ),
    search_prefix="int029a",
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
    cron_schedule="00 23 * * *",
    execution_timezone="Australia/Melbourne",
    job_tags={
        "ecs/cpu": "1024",
        "ecs/memory": "8192",
    },
)
