---
{
  "chunk_id": "chunk-ea1ecf18cfc17b67ff32fd8d",
  "chunk_ordinal": 1250,
  "chunk_text_sha256": "29fcff25def27012575e3406bf861041956338cc3b6aedc3ca4aa029884978b5",
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
              "b": 601.5485534667969,
              "coord_origin": "BOTTOMLEFT",
              "l": 43.14054489135742,
              "r": 539.1275634765625,
              "t": 715.7870178222656
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 192
          }
        ],
        "self_ref": "#/tables/371"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-ea1ecf18cfc17b67ff32fd8d.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-ea1ecf18cfc17b67ff32fd8d.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

network_name, Data Type = varchar 40. network_name, No Nulls = True. network_name, Primary Key = True. network_name, CQ = N. network_name, Comments = Network name. version_id, Data Type = integer. version_id, No Nulls = True. version_id, Primary Key = True. version_id, CQ = N. version_id, Comments = Set to BMPrun id. extract_type, Data Type = char 1. extract_type, No Nulls = True. extract_type, Primary Key = False. extract_type, CQ = N. extract_type, Comments = Type (e.g. F for Final, P for Preliminary, R=Revision). version_from_date, Data Type = varchar 20. version_from_date, No Nulls = True. version_from_date, Primary Key = True. version_from_date, CQ = N. version_from_date, Comments = Effective start date. version_to_date, Data Type = varchar 20. version_to_date, No Nulls = True. version_to_date, Primary Key
