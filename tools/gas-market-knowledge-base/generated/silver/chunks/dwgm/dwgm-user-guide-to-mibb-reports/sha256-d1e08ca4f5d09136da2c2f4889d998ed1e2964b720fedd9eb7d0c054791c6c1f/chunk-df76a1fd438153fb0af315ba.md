---
{
  "chunk_id": "chunk-df76a1fd438153fb0af315ba",
  "chunk_ordinal": 523,
  "chunk_text_sha256": "5476f5b7160ab3cff682c4a4079032aacf3303479d3529c0560de2c7e72eabde",
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
              "b": 184.94952392578125,
              "coord_origin": "BOTTOMLEFT",
              "l": 43.30164337158203,
              "r": 538.4042358398438,
              "t": 424.9216003417969
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 87
          }
        ],
        "self_ref": "#/tables/137"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-df76a1fd438153fb0af315ba.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-df76a1fd438153fb0af315ba.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

transmission_id, Data Type = numeric(9,0). transmission_id, No Nulls = True. transmission_id, Primary Key = True. transmission_id, CQ = N. transmission_id, Comments = Schedule Id, (0 for Administered price) Unique identifier associated with each schedule. gas_date, Data Type = varchar(20). gas_date, No Nulls = True. gas_date, Primary Key = True. gas_date, CQ = N. gas_date, Comments = (e.g. 30 Jun 2007 ). flag, Data Type = varchar(25). flag, No Nulls = True. flag, Primary Key = False. flag, CQ = N. flag, Comments = Schedule_Type - OS, MS, (Administered Pricing). day_in_advance, Data Type = varchar(5). day_in_advance, No Nulls = True. day_in_advance, Primary Key = True. day_in_advance, CQ = Y. day_in_advance, Comments = D-2, D-1, D-0. data_type, Data Type =
