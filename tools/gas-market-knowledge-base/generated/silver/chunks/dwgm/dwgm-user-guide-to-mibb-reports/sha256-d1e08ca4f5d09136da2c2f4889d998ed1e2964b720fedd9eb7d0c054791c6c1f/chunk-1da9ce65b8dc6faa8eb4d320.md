---
{
  "chunk_id": "chunk-1da9ce65b8dc6faa8eb4d320",
  "chunk_ordinal": 929,
  "chunk_text_sha256": "203be7843c4065ac0751aba3a23b7404e70f217bea667590539736bb8511f0c8",
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
              "b": 485.1300048828125,
              "coord_origin": "BOTTOMLEFT",
              "l": 43.386810302734375,
              "r": 539.1124267578125,
              "t": 604.2436370849609
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 146
          }
        ],
        "self_ref": "#/tables/258"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-1da9ce65b8dc6faa8eb4d320.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-1da9ce65b8dc6faa8eb4d320.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

gas_date, Data Type = varchar 20. gas_date, No Nulls = True. gas_date, Primary Key = True. gas_date, CQ = N. gas_date, Comments = Gas day being reported e.g. as 30 Jun1998. flag, Data Type = varchar 5. flag, No Nulls = True. flag, Primary Key = True. flag, CQ = N. flag, Comments = WTHDL- int92 withdrawals INJ - integer 98 injections. id, Data Type = varchar 40. id, No Nulls = True. id, Primary Key = True. id, CQ = N. id, Comments = Meter registration number or withdrawal zone name. ti, Data Type = integer. ti, No Nulls = True. ti, Primary Key = True. ti, CQ = N. ti, Comments = Trading interval (1-24). energy_gj, Data Type = Numeric(18,3). energy_gj, No Nulls = True. energy_gj, Primary Key = False. energy_gj, CQ = N. energy_gj, Comments = Energy value
