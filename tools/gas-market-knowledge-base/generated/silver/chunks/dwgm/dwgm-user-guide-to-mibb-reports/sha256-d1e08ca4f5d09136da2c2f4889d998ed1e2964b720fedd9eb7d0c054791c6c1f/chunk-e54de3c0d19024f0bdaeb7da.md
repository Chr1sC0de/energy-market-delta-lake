---
{
  "chunk_id": "chunk-e54de3c0d19024f0bdaeb7da",
  "chunk_ordinal": 743,
  "chunk_text_sha256": "f6e47b74fe119f5c2e27e4f6dd11db7534eabfd0ca8bbc7119321d51d16c1c88",
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
              "b": 93.68048095703125,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.97660827636719,
              "r": 539.617919921875,
              "t": 370.8206481933594
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 117
          }
        ],
        "self_ref": "#/tables/202"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-e54de3c0d19024f0bdaeb7da.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-e54de3c0d19024f0bdaeb7da.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

gas_date, Data Type = Varchar 20. gas_date, No Nulls = True. gas_date, Primary Key = False. gas_date, CQ = N. gas_date, Comments = The date of gas day being reported (for example, 30 Jun 2012). schedule_ interval, Data Type = Int. schedule_ interval, No Nulls = True. schedule_ interval, Primary Key = True. schedule_ interval, CQ = N. schedule_ interval, Comments = (1,2,3,4 or 5). transmission_ id, Data Type = Int. transmission_ id, No Nulls = True. transmission_ id, Primary Key = True. transmission_ id, CQ = N. transmission_ id, Comments = Schedule ID from which results were drawn. mirn, Data Type = Varchar 10. mirn, No Nulls = True. mirn, Primary Key = True. mirn, CQ = N. mirn, Comments = Meter Registration Identification Number of the system point. tie_breaking_ event, Data Type = Int. tie_breaking_ event, No Nulls = False. tie_breaking_ event, Primary Key = False. tie_breaking_
