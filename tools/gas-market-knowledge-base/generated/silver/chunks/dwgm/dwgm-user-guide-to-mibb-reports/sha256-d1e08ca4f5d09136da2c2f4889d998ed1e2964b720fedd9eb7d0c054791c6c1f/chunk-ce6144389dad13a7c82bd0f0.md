---
{
  "chunk_id": "chunk-ce6144389dad13a7c82bd0f0",
  "chunk_ordinal": 1174,
  "chunk_text_sha256": "07540e598ac70843029ca3d03aaa5d7275d52125d250322277d9e0274545a563",
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
              "b": 308.91375732421875,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.88390350341797,
              "r": 539.6755981445312,
              "t": 726.1369094848633
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 181
          }
        ],
        "self_ref": "#/tables/345"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-ce6144389dad13a7c82bd0f0.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-ce6144389dad13a7c82bd0f0.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

statement_ version_id, Data Type = integer. statement_ version_id, No Nulls = True. statement_ version_id, Primary Key = True. statement_ version_id, CQ = N. statement_ version_id, Comments = number identifying settlement run.. company_id, Data Type = integer. company_id, No Nulls = True. company_id, Primary Key = True. company_id, CQ = N. company_id, Comments = number identifying participant. gas_date, Data Type = varchar 20. gas_date, No Nulls = True. gas_date, Primary Key = True. gas_date, CQ = N. gas_date, Comments = gas day to which information applies. e.g. 30 Jun 2007. payment_type, Data Type = varchar 20. payment_type, No Nulls = True. payment_type, Primary Key = True. payment_type, CQ = N. payment_type, Comments = IMB_W - Imbalance payment w/draw amount (H) DEV_I - Deviation payment inject amount (H) DEV_W- Deviation payment w/draw amount (H) REG- registration
