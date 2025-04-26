from aemo_gas.vichub.assets.bronze.mibb import s3_table_locations


def test__s3_table_locations_asset():
    asset = s3_table_locations.asset()

    assert asset is not None
