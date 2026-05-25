---
{
  "chunk_id": "chunk-e3f8eee401abd71036bda56b-2",
  "chunk_ordinal": 444,
  "chunk_text_sha256": "190729d156ee8014dd2efacffd35bd6921cbdaa53833b8de202cc54e2950540c",
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
              "b": 113.0660400390625,
              "coord_origin": "BOTTOMLEFT",
              "l": 43.06901168823242,
              "r": 539.7332153320312,
              "t": 715.3946304321289
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 75
          }
        ],
        "self_ref": "#/tables/117"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-e3f8eee401abd71036bda56b-2.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-e3f8eee401abd71036bda56b-2.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

Gas_Date, Data Type = varchar 20. Gas_Date, No Nulls = True. Gas_Date, Primary Key = True. Gas_Date, CQ = N. Gas_Date, Comments = Starting hour of gas day being reported e.g. 30 Jun 2007 06:00:00. Type, Data Type = char 1. Type, No Nulls = True. Type, Primary Key = True. Type, CQ = N. Type, Comments = e = EODlinepack record f = Comment record NB: Used for grouping and ordering. Flag, Data Type = char 3.. Flag, No Nulls = True. Flag, Primary Key = True. Flag, CQ = N. Flag, Comments = OS=Last Operational Schedule MS=Last Market Schedule. Company_Id, Data Type = integer. Company_Id, No Nulls = True. Company_Id, Primary Key = True. Company_Id, CQ = N. Company_Id, Comments = Number identifying participant registered to be reported. Pipeline_Id, Data Type = integer. Pipeline_Id, No Nulls = True. Pipeline_Id, Primary Key = False. Pipeline_Id, CQ = N.
