---
{
  "chunk_id": "chunk-217523df13fc59ba1c8ec8ed",
  "chunk_ordinal": 1018,
  "chunk_text_sha256": "16993791a7fdf87f8472a3dec8ca072b9ce940a44d192275d818ddbbc42b29b1",
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
              "b": 106.23822021484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 43.09011459350586,
              "r": 539.2232666015625,
              "t": 253.06683349609375
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 158
          }
        ],
        "self_ref": "#/tables/292"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-217523df13fc59ba1c8ec8ed.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-217523df13fc59ba1c8ec8ed.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

gas_date, Data Type = varchar 20 True. gas_date, No Nulls = varchar 20 True. gas_date, Primary Key = True. gas_date, CQ = N. gas_date, Comments = Gas Date data generated e.g. 02 Feb 2001. node_id, Data Type = integer. node_id, No Nulls = True. node_id, Primary Key = True. node_id, CQ = N. node_id, Comments = AMDQnode ID. node_name, Data Type = varchar 40. node_name, No Nulls = True. node_name, Primary Key = False. node_name, CQ = N. node_name, Comments = AMDQnode name. current_system_ capacity, Data Type = Numeric (18,9). current_system_ capacity, No Nulls = False. current_system_ capacity, Primary Key = False. current_system_ capacity, CQ = N. current_system_ capacity, Comments = Current system spare capacity available for Gas Date (refer to Content notes). current_lateral_ capacity, Data Type = Numeric
