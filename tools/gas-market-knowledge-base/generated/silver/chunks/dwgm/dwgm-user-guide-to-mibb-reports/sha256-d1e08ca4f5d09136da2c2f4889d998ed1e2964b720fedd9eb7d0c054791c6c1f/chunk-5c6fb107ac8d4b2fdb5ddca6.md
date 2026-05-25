---
{
  "chunk_id": "chunk-5c6fb107ac8d4b2fdb5ddca6",
  "chunk_ordinal": 422,
  "chunk_text_sha256": "248d29b222e02959e297053be838b589979cda395041fcd14ea1c55b9e6a7087",
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
              "b": 363.95654296875,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.63107681274414,
              "r": 539.03662109375,
              "t": 756.7443923950195
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 71
          }
        ],
        "self_ref": "#/tables/110"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-5c6fb107ac8d4b2fdb5ddca6.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-5c6fb107ac8d4b2fdb5ddca6.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

= N. commencement_ time, Comments = Format: dd mon yyy hh:mm:ss. ti, Data Type = integer. ti, No Nulls = True. ti, Primary Key = False. ti, CQ = N. ti, Comments = Applicable to LPSCHED only, null fo LPMIN. 0-24. 0 means linepack at start of schedule. Ie 5:59am 1-24 represents the. termination_ datetime, Data Type = varchar 20. termination_ datetime, No Nulls = False. termination_ datetime, Primary Key = False. termination_ datetime, CQ = N. termination_ datetime, Comments = Format: dd mon yyyy hh:mm:ss. unit_id, Data Type = varchar 5. unit_id, No Nulls = False. unit_id, Primary Key = False. unit_id, CQ = N. unit_id, Comments = GJ. linepack_zone_ name, Data Type = varchar 40. linepack_zone_ name, No Nulls = False. linepack_zone_ name, Primary Key = False. linepack_zone_ name,
