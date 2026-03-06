# from aemo_etl.configs import AEMO_BUCKET
# from aemo_etl.factories.download_nemweb_public_files_to_s3.factory import (
#     download_link_and_upload_to_s3_asset_factory,
# )
# from aemo_etl.factories.download_nemweb_public_files_to_s3.ops.dynamic_nemweb_links_fetcher import (
#     FilteredDynamicNEMWebLinksFetcher,
#     InMemoryCachedLinkFilter,
# )
# from aemo_etl.factories.download_nemweb_public_files_to_s3.ops.nemweb_link_fetcher import (
#     HTTPNEMWebLinkFetcher,
# )
# from aemo_etl.factories.download_nemweb_public_files_to_s3.ops.nemweb_link_processor import (
#     S3NemwebLinkProcessor,
# )
# from aemo_etl.factories.download_nemweb_public_files_to_s3.ops.processed_link_combiner import (
#     S3ProcessedLinkCombiner,
# )
#
# download_link_and_upload_to_s3_asset_factory(
#     group_name="aemo__metadata",
#     key_prefix=["bronze", "vicgas"],
#     name=(table_name := "bronze_downloaded_public_files_vicgas"),
#     nemweb_relative_href="REPORTS/CURRENT/VicGas",
#     s3_landing_prefix=(s3_target_prefix := "aemo/vicgas"),
#     nemweb_link_fetcher=HTTPNEMWebLinkFetcher(),
#     dynamic_nemweb_links_fetcher=FilteredDynamicNEMWebLinksFetcher(
#         link_filter=InMemoryCachedLinkFilter(
#             table_path=f"s3://{AEMO_BUCKET}/{s3_target_prefix}/{table_name}",
#             ttl_seconds=900,
#         )
#     ),
#     nemweb_link_processor=S3NemwebLinkProcessor(
#         buffer_processor=...,
#         s3_target_bucket=f"s3://{AEMO_BUCKET}",
#         s3_target_prefix=s3_target_prefix,
#     ),
#     processed_link_combiner=S3ProcessedLinkCombiner(),
# )
