---
{
  "chunk_id": "chunk-ffef2fdb3e1a81d42d342860",
  "chunk_ordinal": 552,
  "chunk_text_sha256": "b39847472def007f129c7b4543120feeabca7e54bc77dfe992757de79d359001",
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
              "b": 106.6162109375,
              "coord_origin": "BOTTOMLEFT",
              "l": 43.06748580932617,
              "r": 539.9102172851562,
              "t": 769.5131988525391
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 91
          }
        ],
        "self_ref": "#/tables/146"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "text",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 103.73626464843755,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.59,
              "r": 121.09911155999998,
              "t": 112.02751464843755
            },
            "charspan": [
              0,
              4
            ],
            "page_no": 91
          }
        ],
        "self_ref": "#/texts/1261"
      },
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
              "b": 680.8592224121094,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.190921783447266,
              "r": 538.9845581054688,
              "t": 769.7683563232422
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 92
          }
        ],
        "self_ref": "#/tables/147"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-ffef2fdb3e1a81d42d342860.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-ffef2fdb3e1a81d42d342860.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

varchar. comment, No Nulls = False. comment, Primary Key = False. comment, CQ = N. comment, Comments = Comments on schedule
255.
transmission_ id, Data Type = integer. transmission_ id, No Nulls = True. transmission_ id, Primary Key = True. transmission_ id, CQ = N. transmission_ id, Comments = Unique identifier associated with each schedule. Note the value in this column is actually the transmission_doc_id. current_date, Data Type = varchar 20. current_date, No Nulls = True. current_date, Primary Key = False. current_date, CQ = N. current_date, Comments = Time Report Produced For example, 30 Jun 2007 06:00:00
