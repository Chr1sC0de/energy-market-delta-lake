---
{
  "chunk_id": "chunk-793e1e6ae1c4cd53b2cbc997",
  "chunk_ordinal": 1032,
  "chunk_text_sha256": "fa5a72d53aaa0af29b56ee6299dadf7b8613b8f1e51449d4b2b07cc9f1e134b1",
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
              "b": 137.93988037109375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.892112731933594,
              "r": 539.3777465820312,
              "t": 343.9978332519531
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 160
          }
        ],
        "self_ref": "#/tables/297"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-793e1e6ae1c4cd53b2cbc997.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-793e1e6ae1c4cd53b2cbc997.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

statement_version_id, Data Type = integer .. statement_version_id, No Nulls = True. statement_version_id, Primary Key = True. statement_version_id, CQ = N. statement_version_id, Comments = Settlement statement version identifier.. company_id, Data Type = integer .. company_id, No Nulls = True. company_id, Primary Key = True. company_id, CQ = N. company_id, Comments = Market participant identifier. gas_date, Data Type = varchar 20 .. gas_date, No Nulls = True. gas_date, Primary Key = True. gas_date, CQ = N. gas_date, Comments = gas_date (e.g. 30 Jun 2007). transmission_tariffed_ zone, Data Type = integer .. transmission_tariffed_ zone, No Nulls = True. transmission_tariffed_ zone, Primary Key = True. transmission_tariffed_ zone, CQ = N. transmission_tariffed_ zone, Comments = injection zone or withdrawal zone identifier. extract_type, Data Type = char 1 .. extract_type, No
