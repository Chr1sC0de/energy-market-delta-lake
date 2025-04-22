import dagster as dg
from dagster_aws.s3 import S3Resource
from aemo_gas.vichub import assets


def test__report_list():
    _ = assets.bronze.mibb.report_list.asset()
