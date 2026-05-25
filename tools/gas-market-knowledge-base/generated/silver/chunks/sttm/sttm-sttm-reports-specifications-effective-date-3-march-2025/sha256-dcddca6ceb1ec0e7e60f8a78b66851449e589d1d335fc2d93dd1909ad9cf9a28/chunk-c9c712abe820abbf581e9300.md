---
{
  "chunk_id": "chunk-c9c712abe820abbf581e9300",
  "chunk_ordinal": 229,
  "chunk_text_sha256": "ddced4ad8d89062125dbed32aada4d8cfac7b33f726932bfc8a7c8b871acc8b8",
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
              "b": 185.68499755859375,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.25544738769531,
              "r": 527.1961669921875,
              "t": 355.3305969238281
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 52
          }
        ],
        "self_ref": "#/tables/65"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-c9c712abe820abbf581e9300.md",
  "heading_path": [
    "5.4.16. INT666 - Market Notices"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-c9c712abe820abbf581e9300.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

market_notice_identifier, Not Null = True. market_notice_identifier, Primary Key = True. market_notice_identifier, Comment = The unique identifier of the of the market notice. critical_notice_flag, Not Null = True. critical_notice_flag, Primary Key = False. critical_notice_flag, Comment = Indicator whether or not the notice is critical: (Y) Yes, (N) No. • Y • N. market_message, Not Null = True. market_message, Primary Key = False. market_message, Comment = Short message. notice_start_date, Not Null = True. notice_start_date, Primary Key = False. notice_start_date, Comment = First date the notice applies to.. notice_end_date, Not Null = True. notice_end_date, Primary Key = False. notice_end_date, Comment = Last date the notice applied to.. url_path, Not Null = False. url_path, Primary Key = False. url_path, Comment = Path to any attachment included in the notice. report_datetime, Not Null = True. report_datetime,
