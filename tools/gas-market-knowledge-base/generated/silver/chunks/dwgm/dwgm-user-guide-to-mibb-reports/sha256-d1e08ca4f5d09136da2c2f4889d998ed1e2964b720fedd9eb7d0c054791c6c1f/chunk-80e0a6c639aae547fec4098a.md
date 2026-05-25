---
{
  "chunk_id": "chunk-80e0a6c639aae547fec4098a",
  "chunk_ordinal": 1506,
  "chunk_text_sha256": "4ce60d7bf1696fcb86d528f7c8a89543dd5d08d66d732dd9b2e17d79b3a14eb8",
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
              "b": 104.09332275390625,
              "coord_origin": "BOTTOMLEFT",
              "l": 43.22220230102539,
              "r": 539.5689086914062,
              "t": 410.34991455078125
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 228
          }
        ],
        "self_ref": "#/tables/448"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-80e0a6c639aae547fec4098a.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-80e0a6c639aae547fec4098a.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

distributor_name, CQ = N. distributor_name, Comments = Name of the Distributor (Distribution region). withdrawal_zone, Data Type = varchar 30 .. withdrawal_zone, No Nulls = True. withdrawal_zone, Primary Key = True. withdrawal_zone, CQ = N. withdrawal_zone, Comments = Withdrawal zone. agg_consumption_ gj, Data Type = numeric 18 .3. agg_consumption_ gj, No Nulls = False. agg_consumption_ gj, Primary Key = False. agg_consumption_ gj, CQ = N. agg_consumption_ gj, Comments = Aggregated consumption in gj. injection_gj, Data Type = numeric 18 .3. injection_gj, No Nulls = False. injection_gj, Primary Key = False. injection_gj, CQ = . injection_gj, Comments = Injection in gj. imbalance_gj, Data Type = numeric 18 .3. imbalance_gj, No Nulls = False. imbalance_gj, Primary Key = False. imbalance_gj, CQ = N.
