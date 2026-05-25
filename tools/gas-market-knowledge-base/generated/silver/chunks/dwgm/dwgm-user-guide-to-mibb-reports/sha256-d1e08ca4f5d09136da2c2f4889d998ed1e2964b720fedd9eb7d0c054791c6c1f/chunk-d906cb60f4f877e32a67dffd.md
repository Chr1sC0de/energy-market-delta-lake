---
{
  "chunk_id": "chunk-d906cb60f4f877e32a67dffd",
  "chunk_ordinal": 176,
  "chunk_text_sha256": "c90914c14f67e9bde348e53df56e254ee303e0639d7a31385c3c9418bb8cebdc",
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
              "b": 402.6647644042969,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.868865966796875,
              "r": 539.1809692382812,
              "t": 546.662353515625
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 34
          }
        ],
        "self_ref": "#/tables/44"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-d906cb60f4f877e32a67dffd.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-d906cb60f4f877e32a67dffd.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

gas_date, Data Type = varchar 20. gas_date, No Nulls = True. gas_date, Primary Key = True. gas_date, CQ = N. gas_date, Comments = Starting hour of gas day being reported e.g. 30 Jun 1998 09:00:00. withdrawal_ zone_name, Data Type = varchar 40. withdrawal_ zone_name, No Nulls = True. withdrawal_ zone_name, Primary Key = True. withdrawal_ zone_name, CQ = N. withdrawal_ zone_name, Comments = Withdrawal zone name. scheduled_qty, Data Type = Numeric (18,3). scheduled_qty, No Nulls = False. scheduled_qty, Primary Key = False. scheduled_qty, CQ = Y. scheduled_qty, Comments = SUMScheduled withdrawal (GJ) for wthdrawal zone.. transmission_id, Data Type = integer. transmission_id, No Nulls = True. transmission_id, Primary Key = True. transmission_id, CQ = N. transmission_id, Comments = Schedule ID from which results were drawn. current_date, Data Type =
