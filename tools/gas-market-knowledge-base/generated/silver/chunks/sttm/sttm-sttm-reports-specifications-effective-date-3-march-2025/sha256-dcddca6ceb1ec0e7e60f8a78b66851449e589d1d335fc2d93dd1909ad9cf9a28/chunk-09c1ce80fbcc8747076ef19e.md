---
{
  "chunk_id": "chunk-09c1ce80fbcc8747076ef19e",
  "chunk_ordinal": 213,
  "chunk_text_sha256": "63dbfc89053f4c2baef8600ff29adcaec84915d01c9e1569c53f7a69294e0f08",
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
              "b": 388.0464172363281,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.15409088134766,
              "r": 527.3165893554688,
              "t": 749.9520797729492
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 49
          }
        ],
        "self_ref": "#/tables/58"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-09c1ce80fbcc8747076ef19e.md",
  "heading_path": [
    "5.4.11. INT661 - Contingency Gas Called Scheduled Bid Offer"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-09c1ce80fbcc8747076ef19e.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

confirmed_step_quantity, Not Null = True. contingency_gas_bid_offer_ confirmed_step_quantity, Primary Key = False. contingency_gas_bid_offer_ confirmed_step_quantity, Comment = This is the quantity of gas in each contingency gas bid or offer step that the provider has confirmed as being available.. contingency_gas_bid_offer_ called_step_quantity, Not Null = False. contingency_gas_bid_offer_ called_step_quantity, Primary Key = False. contingency_gas_bid_offer_ called_step_quantity, Comment = The quantity of gas in each contingency gas bid or offer step that the provider has been called to provide.. approval_datetime, Not Null = True. approval_datetime, Primary Key = False. approval_datetime, Comment = the date and time that the contingency gas called was approved. report_datetime, Not Null = True. report_datetime, Primary Key = False. report_datetime, Comment = The date and time the report was produced.
