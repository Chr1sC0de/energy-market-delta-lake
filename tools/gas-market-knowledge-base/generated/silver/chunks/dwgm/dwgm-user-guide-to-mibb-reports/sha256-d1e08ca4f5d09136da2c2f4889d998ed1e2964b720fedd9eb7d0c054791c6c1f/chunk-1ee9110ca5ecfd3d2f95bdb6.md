---
{
  "chunk_id": "chunk-1ee9110ca5ecfd3d2f95bdb6",
  "chunk_ordinal": 525,
  "chunk_text_sha256": "ad506c8e4b922ead38467241253271d78756ba20103e58c17fc4fa9e9b30d606",
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
              "b": 541.1373291015625,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.91505813598633,
              "r": 538.34912109375,
              "t": 769.7196807861328
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 88
          }
        ],
        "self_ref": "#/tables/138"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-1ee9110ca5ecfd3d2f95bdb6.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-1ee9110ca5ecfd3d2f95bdb6.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

detail, Data Type = varchar(20). detail, No Nulls = True. detail, Primary Key = True. detail, CQ = N. detail, Comments = DAILY EOD MCEBOD 10% EXCEEDANCE NORMAL 90% EXCEEDANCE. transmission_doc_id, Data Type = Int. transmission_doc_id, No Nulls = . transmission_doc_id, Primary Key = False. transmission_doc_id, CQ = N. transmission_doc_id, Comments = Run Id, (0 for Administered price). id, Data Type = varchar(40). id, No Nulls = True. id, Primary Key = True. id, CQ = N. id, Comments = Withdrawal Zone (e.g. Ballarat), ALLCOMPRESSORS SYSTEM. value, Data Type = float. value, No Nulls = False. value, Primary Key = False. value, CQ = Y. value, Comments = Quantity or Price. current_date, Data Type = varchar(20). current_date, No Nulls = True. current_date, Primary Key = False. current_date, CQ = N. current_date, Comments =
