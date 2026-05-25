---
{
  "chunk_id": "chunk-0a183f16cadf73bed485a176",
  "chunk_ordinal": 190,
  "chunk_text_sha256": "24c5c9750cf48aeeff01a037c5fe6e95fc860f27558eeede89fbc557353f83fe",
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
              "b": 102.56268310546875,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.93600082397461,
              "r": 539.2733764648438,
              "t": 191.046630859375
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 36
          }
        ],
        "self_ref": "#/tables/49"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-0a183f16cadf73bed485a176.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-0a183f16cadf73bed485a176.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

gas_date, Data Type = varchar 20. gas_date, No Nulls = True. gas_date, Primary Key = True. gas_date, CQ = N. gas_date, Comments = e.g. 30 Jun 2007. unit_id, Data Type = varchar 5. unit_id, No Nulls = True. unit_id, Primary Key = False. unit_id, CQ = N. unit_id, Comments = GJ. qty, Data Type = float .. qty, No Nulls = True. qty, Primary Key = False. qty, CQ = Y. qty, Comments = Total Gas withdrawn Daily.. qty_reinj, Data Type = float .. qty_reinj, No Nulls = False. qty_reinj, Primary Key = False. qty_reinj, CQ = Y. qty_reinj, Comments = Total Net Gas withdrawn Daily (Withdrawals less re-injections). current_date, Data Type = varchar 20. current_date, No Nulls = True. current_date, Primary Key = False. current_date, CQ =
