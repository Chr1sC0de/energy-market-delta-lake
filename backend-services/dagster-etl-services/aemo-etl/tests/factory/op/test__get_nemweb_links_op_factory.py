from dagster import build_op_context

from aemo_etl.factory.op import get_nemweb_links_op_factory


class Test__get_nemweb_links_op_factory:
    def test__vicgas_no_filters(self) -> None:
        root_relative_href = "REPORTS/CURRENT/VicGas"
        link_list = get_nemweb_links_op_factory(
            root_relative_href,
        )(build_op_context())

        assert len(link_list) > 100

    def test__vicgas(self) -> None:
        root_relative_href = "REPORTS/CURRENT/VicGas"
        link_list = get_nemweb_links_op_factory(
            root_relative_href,
            hyperlink_tag_folder_filter=lambda _, x: x.text != "[To Parent Directory]",
            hyperlink_tag_file_filter=lambda _, x: x.text != "CURRENTDAY.ZIP",
        )(build_op_context())

        assert len(link_list) > 100

    def test__gbb(self) -> None:
        root_relative_href = "REPORTS/CURRENT/GBB/"
        link_list = get_nemweb_links_op_factory(
            root_relative_href,
            hyperlink_tag_folder_filter=lambda _, x: (
                x.text not in ("[To Parent Directory]", "DUPLICATE")
            ),
            hyperlink_tag_file_filter=lambda _, x: x.text != "CURRENTDAY.ZIP",
        )(build_op_context())

        assert len(link_list) > 1000
