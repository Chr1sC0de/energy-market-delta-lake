import pathlib as pt

cwd = pt.Path(__file__).parent

template = """
from aemo_etl.configuration.mibb.{file_stem} import (
    group_name,
    primary_keys,
    report_purpose,
    s3_file_glob,
    s3_prefix,
    s3_table_location,
    schema_descriptions,
    table_name,
    table_schema,
    upsert_predicate,
)
from aemo_etl.definitions.bronze_vicgas_mibb_reports.utils import (
    definition_builder_factory,
)
from aemo_etl.register import definitions_list

definition_builder = definition_builder_factory(
    report_purpose,
    table_schema,
    schema_descriptions,
    primary_keys,
    upsert_predicate,
    s3_table_location,
    s3_prefix,
    s3_file_glob,
    table_name,
    group_name=group_name,
)

definitions_list.append(definition_builder.build())
""".strip("\n")


def main():
    configuration_folder = cwd / "../../configuration/mibb"

    for file in configuration_folder.glob("bronze*.py"):
        file_stem = file.stem
        new_file = cwd / f"{file_stem}.py"
        new_file.write_text(template.format(file_stem=file_stem))

    return


if __name__ == "__main__":
    main()
