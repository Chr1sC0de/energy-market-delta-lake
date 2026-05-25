---
{
  "chunk_id": "chunk-f84f699baf4c13f9417b2ed5",
  "chunk_ordinal": 457,
  "chunk_text_sha256": "f35210a438068bf69ac892135f0d2f68158dc2024ff612667009671c17efea79",
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
              "b": 405.8606262207031,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.47624969482422,
              "r": 527.3873291015625,
              "t": 749.754753112793
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 104
          }
        ],
        "self_ref": "#/tables/152"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-f84f699baf4c13f9417b2ed5.md",
  "heading_path": [
    "5.5.28. INT736 - SA ROLR Allocation Quantities"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-f84f699baf4c13f9417b2ed5.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

gas_date, Not Null = True. gas_date, Primary Key = True. gas_date, Comment = The gas date that the allocation is applicable for.. crn, Not Null = True. crn, Primary Key = True. crn, Comment = The CRN the allocation relates to.. trn, Not Null = True. trn, Primary Key = True. trn, Comment = The TRN the allocation relates to.. quantity_gj, Not Null = True. quantity_gj, Primary Key = False. quantity_gj, Comment = The last received allocation quantity (GJ) for the TRN and gas date. Note: Gas dates with no allocation quantity available are not displayed in the report.. scaled_quantity_gj, Not Null = True. scaled_quantity_gj, Primary Key = False. scaled_quantity_gj, Comment = The scaled value for the last received allocation quantity (GJ) for the TRN and gas date. If the allocation has not been scaled, it is the same as the quantity_gj. Note: Gas dates with no allocation quantity available are not displayed in the report.. quality_type, Not Null = True.
