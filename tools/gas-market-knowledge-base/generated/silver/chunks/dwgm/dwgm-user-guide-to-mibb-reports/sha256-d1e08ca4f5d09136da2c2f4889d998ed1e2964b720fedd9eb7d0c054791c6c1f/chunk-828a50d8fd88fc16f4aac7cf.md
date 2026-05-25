---
{
  "chunk_id": "chunk-828a50d8fd88fc16f4aac7cf",
  "chunk_ordinal": 170,
  "chunk_text_sha256": "48cf4745a879e58738a131004fbc3592d417d6e3dfee642e302ec7e59deec202",
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
              "b": 351.548828125,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.79967498779297,
              "r": 538.960205078125,
              "t": 497.8518371582031
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 33
          }
        ],
        "self_ref": "#/tables/42"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-828a50d8fd88fc16f4aac7cf.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-828a50d8fd88fc16f4aac7cf.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

gas_date, Data Type = varchar 20. gas_date, No Nulls = True. gas_date, Primary Key = False. gas_date, CQ = N. gas_date, Comments = Starting hour of gas day being reportedeg 30 Jun 2007 06:00:00. node_name, Data Type = varchar 40. node_name, No Nulls = True. node_name, Primary Key = True. node_name, CQ = N. node_name, Comments = Name of node at which price applies. ti, Data Type = integer. ti, No Nulls = True. ti, Primary Key = True. ti, CQ = N. ti, Comments = Hour index(1-24). nodal_price_value_gst_ ex, Data Type = float. nodal_price_value_gst_ ex, No Nulls = False. nodal_price_value_gst_ ex, Primary Key = False. nodal_price_value_gst_ ex, CQ = N. nodal_price_value_gst_ ex, Comments = Nodal price ($). transmission_id, Data Type =
