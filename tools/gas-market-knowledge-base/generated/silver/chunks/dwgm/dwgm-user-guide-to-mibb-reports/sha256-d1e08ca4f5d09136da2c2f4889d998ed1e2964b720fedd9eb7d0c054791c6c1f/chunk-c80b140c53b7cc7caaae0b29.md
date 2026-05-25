---
{
  "chunk_id": "chunk-c80b140c53b7cc7caaae0b29",
  "chunk_ordinal": 999,
  "chunk_text_sha256": "e8cda589b67d122b6bec6fe91b94c2a23ca22583f73d12f2bf2991840a539608",
  "chunking_settings": {
    "chunker": "HybridChunker",
    "merge_peers": true,
    "omit_header_on_overflow": false,
    "repeat_table_header": true,
    "schema_version": 1,
    "tool": "docling-hybrid"
  },
  "chunking_settings_sha256": "a57e8b8018c83b551505462598681565b8effa3456c2824e782e833a2ef673eb",
  "chunking_tool": "docling-hybrid",
  "citations": {
    "doc_items": [
      {
        "children": [],
        "content_layer": "body",
        "label": "table",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 110.66644287109375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.794124603271484,
              "r": 539.0734252929688,
              "t": 209.42059326171875
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 155
          }
        ],
        "self_ref": "#/tables/284"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md",
    "source_manifest_line_number": 4,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/declared-wholesale-gas-market-dwgm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/april-2024-amendment-to-user-guide-to-mibb-reports/user-guide-to-mibb-reports.pdf?rev=b5b659bce66a4808b505db05ecb0ca13&sc_lang=en"
  },
  "content_sha256": "d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f",
  "corpus": "dwgm",
  "document_family": "dwgm__user-guide-to-mibb-reports",
  "document_family_id": "dwgm__user-guide-to-mibb-reports",
  "document_identity": "dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f",
  "document_title": "##### User Guide to MIBB Reports",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-c80b140c53b7cc7caaae0b29.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-c80b140c53b7cc7caaae0b29.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

mirn, Data Type = varchar 10 . True. mirn, No Nulls = varchar 10 . True. mirn, Primary Key = True. mirn, CQ = N. mirn, Comments = . gas_date, Data Type = varchar 20 .. gas_date, No Nulls = True. gas_date, Primary Key = True. gas_date, CQ = N. gas_date, Comments = Gas day being reported e.g. 30 Jun 2007. ti, Data Type = integer. ti, No Nulls = True. ti, Primary Key = True. ti, CQ = N. ti, Comments = Time Interval (1-24) where 1 is 6:00AM. energy_gj, Data Type = numeric 18.9. energy_gj, No Nulls = True. energy_gj, Primary Key = False. energy_gj, CQ = N. energy_gj, Comments = hourly energy (Gj)
