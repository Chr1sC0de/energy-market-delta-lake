---
{
  "chunk_id": "chunk-cc10846c5b9d12e22ca72cbf",
  "chunk_ordinal": 1481,
  "chunk_text_sha256": "5a7d42b000c397906290ed5ecaddbce0d8b243a2db88b9ddadcf1a8efd20e8ca",
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
              "b": 655.1902160644531,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.94736862182617,
              "r": 539.03662109375,
              "t": 769.4335021972656
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 225
          }
        ],
        "self_ref": "#/tables/440"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-cc10846c5b9d12e22ca72cbf.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-cc10846c5b9d12e22ca72cbf.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

distributor_name, Data Type = varchar 40 .. distributor_name, No Nulls = True. distributor_name, Primary Key = True. distributor_name, CQ = N. distributor_name, Comments = Distribution business name. withdrawal_zone, Data Type = varchar 30 .. withdrawal_zone, No Nulls = True. withdrawal_zone, Primary Key = True. withdrawal_zone, CQ = N. withdrawal_zone, Comments = Withdrawal zone. curr_cum_date, Data Type = varchar 20 .. curr_cum_date, No Nulls = False. curr_cum_date, Primary Key = False. curr_cum_date, CQ = N. curr_cum_date, Comments = Current cumulative imbalance issue date. curr_cum_imb_gj, Data Type = numeric 18 .3. curr_cum_imb_gj, No Nulls = False. curr_cum_imb_gj, Primary Key = False. curr_cum_imb_gj, CQ = N. curr_cum_imb_gj, Comments = Current cumulative
