---
{
  "chunk_id": "chunk-bc22ccc5ed1957b0af2d89b4",
  "chunk_ordinal": 239,
  "chunk_text_sha256": "200398fca85a0e3da72457e31a6096b3259cf2107ead6226c078e2ab226f2992",
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
              "b": 125.5743408203125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.62554168701172,
              "r": 527.1859130859375,
              "t": 342.0634765625
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 54
          }
        ],
        "self_ref": "#/tables/69"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md",
    "source_manifest_line_number": 47,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/short-term-trading-market-sttm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/amendments-to-sttm-and-retail-market-procedures/decision/sttm-reports-specifications-v191.pdf?rev=30dbf1c556a7486b8c80e244b8690226&sc_lang=en"
  },
  "content_sha256": "dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28",
  "corpus": "sttm",
  "document_family": "sttm__sttm-reports-specifications-effective-date-3-march-2025",
  "document_family_id": "sttm__sttm-reports-specifications-effective-date-3-march-2025",
  "document_identity": "sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28",
  "document_title": "##### STTM Reports Specifications Effective date 3 March 2025",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-bc22ccc5ed1957b0af2d89b4.md",
  "heading_path": [
    "5.4.19. INT669 - Settlement Version"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-bc22ccc5ed1957b0af2d89b4.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

settlement_run_identifier, Not Null = True. settlement_run_identifier, Primary Key = True. settlement_run_identifier, Comment = . settlement_cat_type, Not Null = True. settlement_cat_type, Primary Key = False. settlement_cat_type, Comment = The category of the settlement run. Valid categories include: • Preliminary • Final • Revision. version_from_date, Not Null = True. version_from_date, Primary Key = False. version_from_date, Comment = Effective start date.. version_to_date, Not Null = True. version_to_date, Primary Key = False. version_to_date, Comment = Effective End date.. interest_rate, Not Null = False. interest_rate, Primary Key = False. interest_rate, Comment = The interest rate if the settlement category is of type revision.. issued_datetime, Not Null = True. issued_datetime, Primary Key = False. issued_datetime, Comment = The date & time the settlement statements are issued.. settlement_run_desc, Not Null = False. settlement_run_desc, Primary Key = False.
