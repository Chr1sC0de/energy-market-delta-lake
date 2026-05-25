---
{
  "chunk_id": "chunk-2fb5a593c60b90beaa1579b4",
  "chunk_ordinal": 226,
  "chunk_text_sha256": "1cddc36cbcd3598a61e9b708df869452b4d7514f8d70d1955b3129afeaa25b8c",
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
              "b": 514.6450500488281,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.25302124023438,
              "r": 527.3836059570312,
              "t": 749.965705871582
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 52
          }
        ],
        "self_ref": "#/tables/64"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-2fb5a593c60b90beaa1579b4.md",
  "heading_path": [
    "5.4.15. INT665 - MOS Stack Data"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-2fb5a593c60b90beaa1579b4.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

, Not Null = . , Primary Key = . , Comment = • I • D. estimated_maximum_quantit y, Not Null = True. estimated_maximum_quantit y, Primary Key = False. estimated_maximum_quantit y, Comment = The estimated maximum MOS quantity expected for the MOS period, populated for both increase stacks and decrease stacks.. stack_step_identifier, Not Null = True. stack_step_identifier, Primary Key = True. stack_step_identifier, Comment = The identifier that uniquely identifies a step within a MOS stack.. trading_participant_identifier, Not Null = True. trading_participant_identifier, Primary Key = False. trading_participant_identifier, Comment = The identifier for the trading participant.. trading_participant_name, Not Null = True. trading_participant_name, Primary Key = False. trading_participant_name, Comment = The trading participant's organisation name. step_quantity, Not Null = True. step_quantity, Primary Key = False. step_quantity, Comment = The quantity of gas associated with this MOS stack step as submitted by the
