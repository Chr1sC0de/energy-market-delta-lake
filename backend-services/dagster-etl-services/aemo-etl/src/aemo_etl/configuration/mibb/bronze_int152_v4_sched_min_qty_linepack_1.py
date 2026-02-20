"""bronze_int152_v4_sched_min_qty_linepack_1 - Bronze MIBB report configuration."""

from polars import Int64, String
from aemo_etl.configuration import (
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int152_v4_sched_min_qty_linepack_1",
        s3_file_glob="int152_v4_sched_min_qty_linepack_1*",
        primary_keys=["gas_date", "type", "linepack_id", "commencement_datetime"],
        table_schema={
            "gas_date": String,
            "type": String,
            "linepack_id": Int64,
            "linepack_zone_id": Int64,
            "commencement_datetime": String,
            "ti": Int64,
            "termination_datetime": String,
            "unit_id": String,
            "linepack_zone_name": String,
            "transmission_document_id": Int64,
            "quantity": Int64,
            "current_date": String,
            "approval_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "Gas day (e.g. 30 Jun 2007)",
            "type": "LPMIN for INT046, LPSCHED for INT115",
            "linepack_id": "Linepack identifier",
            "linepack_zone_id": "Linepack zone identifier (Null for LPSCHED)",
            "commencement_datetime": "Format: dd mon yyy hh:mm:ss",
            "ti": "Applicable to LPSCHED only, null for LPMIN. 0-24. 0 means linepack at start of schedule. Ie 5:59am 1-24 represents the time interval of the day.",  # noqa: E501
            "termination_datetime": "Format: dd mon yyyy hh:mm:ss",
            "unit_id": "GJ",
            "linepack_zone_name": "Name of linepack zone",
            "transmission_document_id": "Null for LPMIN",
            "quantity": "Quantity value",
            "current_date": "Date and time the report was produced: Format dd mon yyyy hh:mm:ss",  # noqa: E501
            "approval_date": "Date of approval (e.g. 30 Jun 2007)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report provides transparency into the system operation of the gas market, as required under clause 320 of the NGR.\n\nThis report combines two different types of content:\n- the end-of-day linepack minimum target (in GJ) set by AEMO as part of system operations.\n- the hourly linepack quantities scheduled for the gas day\n\nIn examining hourly linepack quantities associated with a schedule (row where type = 'LPSCHED'), users may find it useful to\nre-order rows using the commencement time column.\n\nUsers should refer to INT108 (Schedule Run Log) to determine the characteristics of each schedule (for example, the\nschedule start date and time, publish time, schedule type and so on) associated with a specific transmission_document_id\n(which is also known as schedule_id).\n\nAs a report is generated each time an operational schedule is approved there will be at least 9 issues of INT152 each day (with\nan additional report generated for each ad hoc schedule required).\n\nEach report shows the scheduled and minimum linepack quantities (in GJ) for the:\n- previous 7 gas day\n- current gas day\n- next 2 gas days\n\nSome reports provide information only for the next gas day (not 2 days into the future).\n\nThe number of gas days and/or schedules covered by a report will depend on the time at which the particular report version is\nproduced. In general, reports produced by the approval of standard schedules at 06:00 AM and 10:00 AM will contain\ninformation only for the past 7, current and next gas day as at that point in time no schedules for 2 days in the future will have\nbeen run.\n\nFor the section of the report providing information on linepack minima (rows where type = 'LPMIN'), there is one row for the\nsystem linepack minimum for each gas day within the reporting window.\n\nFor the section of the report providing information on hourly scheduled linepack quantities (rows where type = 'LPSCHED'),\nthere are:\n- 25 rows for each schedule (operational or pricing) where the schedule start time is 06:00 AM:\n  - One row is tagged '05:59' in the commencement time column and provides the initial linepack condition at the start of\n    the gas day.\n  - Other rows are tagged with hourly intervals commencing from '06:00' and provide the scheduled linepack quantities for\n    each hour of the gas day.\n- 26 rows for each schedule (operational or pricing) where the schedule start time is other than 06:00 AM:\n  - One row is tagged '05:59' in the commencement time column and provide the initial linepack condition at the\n    start of the gas day.\n  - One row is tagged as one minute prior to the schedule start time (for example, 09:59 PM) and provide the initial\n    linepack condition at the start of the scheduling interval.\n  - Other rows are tagged with hourly intervals commencing from '06:00' and provide the scheduled linepack\n    quantities for each hour of the gas day.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )
