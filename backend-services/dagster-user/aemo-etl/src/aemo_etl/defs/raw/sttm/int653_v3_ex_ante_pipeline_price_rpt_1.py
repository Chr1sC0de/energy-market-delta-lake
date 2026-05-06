from dagster import AssetSpec

from aemo_etl.defs.raw.sttm._manifest import (
    get_sttm_report_manifest,
    sttm_report_schema,
    sttm_report_schema_descriptions,
)
from aemo_etl.factories.df_from_s3_keys.definitions import (
    df_from_s3_keys_definitions_factory,
)

REPORT = get_sttm_report_manifest("INT653")

defs = df_from_s3_keys_definitions_factory(
    domain="sttm",
    name_suffix=REPORT["name_suffix"],
    glob_pattern=REPORT["glob_pattern"],
    schema=sttm_report_schema(REPORT),
    schema_descriptions=sttm_report_schema_descriptions(REPORT),
    description=REPORT["description"],
    surrogate_key_sources=list(REPORT["surrogate_key_sources"]),
    group_name="gas_raw",
    deps=[AssetSpec(["bronze", "sttm", "bronze_nemweb_public_files_sttm"])],
)
