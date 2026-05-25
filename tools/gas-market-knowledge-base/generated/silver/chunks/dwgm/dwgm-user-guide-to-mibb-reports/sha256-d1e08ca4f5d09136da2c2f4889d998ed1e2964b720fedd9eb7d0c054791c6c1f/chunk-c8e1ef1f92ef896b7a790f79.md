---
{
  "chunk_id": "chunk-c8e1ef1f92ef896b7a790f79",
  "chunk_ordinal": 1093,
  "chunk_text_sha256": "addf60b227d6418c4d6817cd9bf54a7c95f4c4d2312cc521cd7904f17fbeaf3a",
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
              "b": 369.1531677246094,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.78644561767578,
              "r": 538.92724609375,
              "t": 585.6251831054688
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 169
          }
        ],
        "self_ref": "#/tables/317"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-c8e1ef1f92ef896b7a790f79.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-c8e1ef1f92ef896b7a790f79.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

statement_version_ id, Data Type = integer. statement_version_ id, No Nulls = True. statement_version_ id, Primary Key = False. statement_version_ id, CQ = N. statement_version_ id, Comments = Settlement statement version identifier. gas_date, Data Type = varchar(20). gas_date, No Nulls = True. gas_date, Primary Key = True. gas_date, CQ = N. gas_date, Comments = Dd mmmyyyy. sched_no, Data Type = Int. sched_no, No Nulls = True. sched_no, Primary Key = True. sched_no, CQ = N. sched_no, Comments = . company_id, Data Type = integer. company_id, No Nulls = True. company_id, Primary Key = True. company_id, CQ = N. company_id, Comments = . surprise_amt, Data Type = numeric (15,4). surprise_amt, No Nulls = True. surprise_amt, Primary Key = False. surprise_amt, CQ = Y.
