---
{
  "chunk_id": "chunk-861c3f3ecbe651ca538d17cb",
  "chunk_ordinal": 376,
  "chunk_text_sha256": "51240f3c8ad4502d464571ffdda40ad637ce9c635a31ee98d3df88cfa23898d9",
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
              "b": 104.03070068359375,
              "coord_origin": "BOTTOMLEFT",
              "l": 43.11100387573242,
              "r": 540.0564575195312,
              "t": 769.3577728271484
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 64
          }
        ],
        "self_ref": "#/tables/99"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-861c3f3ecbe651ca538d17cb.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-861c3f3ecbe651ca538d17cb.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

industry_ code, Data Type = varchar 100. industry_ code, No Nulls = False. industry_ code, Primary Key = False. industry_ code, CQ = N. industry_ code, Comments = Industry code to which the site is registered.. gas_date, Data Type = varchar 20. gas_date, No Nulls = True. gas_date, Primary Key = True. gas_date, CQ = N. gas_date, Comments = Gas Day Date and starting hour. hour_1, Data Type = Numeric (18,3). hour_1, No Nulls = False. hour_1, Primary Key = False. hour_1, CQ = N. hour_1, Comments = Restricted energy usage value (GJ) that cannot be exceeded for 6:00 AM. May be NULL for hours a restriction is not required.. hour_2, Data Type = Numeric (18,3). hour_2, No Nulls = False. hour_2, Primary Key = False. hour_2, CQ = N. hour_2, Comments = Restricted energy usage value (GJ) that cannot be exceeded for 7:00 AM. May
