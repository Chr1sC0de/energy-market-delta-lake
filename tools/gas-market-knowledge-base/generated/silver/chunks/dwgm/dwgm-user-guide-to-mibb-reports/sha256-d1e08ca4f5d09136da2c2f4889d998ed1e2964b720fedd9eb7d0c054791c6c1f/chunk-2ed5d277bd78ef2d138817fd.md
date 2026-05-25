---
{
  "chunk_id": "chunk-2ed5d277bd78ef2d138817fd",
  "chunk_ordinal": 1186,
  "chunk_text_sha256": "9c1bf1fd326b79807115c63664ab8441c5f2c8f45333aadd8c41cbf7ceee1b07",
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
              "b": 584.0501098632812,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.876953125,
              "r": 539.0047607421875,
              "t": 725.8094635009766
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 183
          }
        ],
        "self_ref": "#/tables/349"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-2ed5d277bd78ef2d138817fd.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-2ed5d277bd78ef2d138817fd.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

gas_date, Data Type = varchar 20 True. gas_date, No Nulls = varchar 20 True. gas_date, Primary Key = True. gas_date, CQ = N. gas_date, Comments = Starting hour of gas day being reported, example: 30 Jun 2007. hv_zone, Data Type = integer. hv_zone, No Nulls = True. hv_zone, Primary Key = True. hv_zone, CQ = N. hv_zone, Comments = Heating value zone number as assigned by the AEMO. Values for Victoria can be in the range of 400-699. hv_zone_ desc, Data Type = varchar 254. hv_zone_ desc, No Nulls = False. hv_zone_ desc, Primary Key = False. hv_zone_ desc, CQ = Y. hv_zone_ desc, Comments = Heating value zone name. heating_ value, Data Type = numeric (5,2). heating_ value, No Nulls = True. heating_ value, Primary Key = False. heating_ value, CQ = N. heating_ value,
