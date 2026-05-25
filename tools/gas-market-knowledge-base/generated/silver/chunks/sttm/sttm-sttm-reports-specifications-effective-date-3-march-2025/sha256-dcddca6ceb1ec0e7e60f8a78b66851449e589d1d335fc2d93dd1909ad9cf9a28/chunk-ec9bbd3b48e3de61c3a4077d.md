---
{
  "chunk_id": "chunk-ec9bbd3b48e3de61c3a4077d",
  "chunk_ordinal": 166,
  "chunk_text_sha256": "0ca07964cb7149d5a215d0e698eb85e4879536c0b29ccfaf5241ef406afc28ff",
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
              "b": 234.06854248046875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.45790100097656,
              "r": 527.2196655273438,
              "t": 512.2098388671875
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 38
          }
        ],
        "self_ref": "#/tables/42"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-ec9bbd3b48e3de61c3a4077d.md",
  "heading_path": [
    "5.3.3. INT733 - Transmission Connected STTM Users"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-ec9bbd3b48e3de61c3a4077d.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

company_identifier, Comment = The unique identifier of the Transmission Connected STTM User.. company_name, Not Null = True. company_name, Primary Key = False. company_name, Comment = The company name of the Transmission Connected STTM User. period_start_date, Not Null = True. period_start_date, Primary Key = True. period_start_date, Comment = Start date of the service held by the Transmission Connected STTM User on the Facility. period_end_date, Not Null = True. period_end_date, Primary Key = False. period_end_date, Comment = End date of the service held by the Transmission Connected STTM User on the Facility. last_update_datetime, Not Null = True. last_update_datetime, Primary Key = False. last_update_datetime, Comment = The date and time the records within the report were last updated. report_datetime, Not Null = True. report_datetime, Primary Key = False. report_datetime, Comment = The date and time the report was produced
