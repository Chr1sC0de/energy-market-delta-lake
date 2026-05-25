---
{
  "chunk_id": "chunk-60c350cbbdeb39f9098c2afc",
  "chunk_ordinal": 1499,
  "chunk_text_sha256": "0f5d245155b2b66773f6513a3830e0ffb24e716e0ac7becec7f9cd9a0e23facf",
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
              "b": 308.08795166015625,
              "coord_origin": "BOTTOMLEFT",
              "l": 43.18081283569336,
              "r": 538.8294677734375,
              "t": 452.2479248046875
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 227
          }
        ],
        "self_ref": "#/tables/446"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-60c350cbbdeb39f9098c2afc.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-60c350cbbdeb39f9098c2afc.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

network_name, Data Type = varchar 40 .. network_name, No Nulls = True. network_name, Primary Key = False. network_name, CQ = N. network_name, Comments = . fro_name, Data Type = varchar 40 .. fro_name, No Nulls = True. fro_name, Primary Key = True. fro_name, CQ = N. fro_name, Comments = Name of Financially Responsible Organisation. gas_date, Data Type = varchar 20 .. gas_date, No Nulls = True. gas_date, Primary Key = True. gas_date, CQ = N. gas_date, Comments = Format dd mmmyyyy e.g. 01 Jul 2007. distributor_name, Data Type = varchar 40 .. distributor_name, No Nulls = True. distributor_name, Primary Key = True. distributor_name, CQ = N. distributor_name, Comments = Distributor name. withdrawal_zone, Data Type = varchar 30 .. withdrawal_zone, No Nulls = True. withdrawal_zone, Primary Key = True. withdrawal_zone, CQ
