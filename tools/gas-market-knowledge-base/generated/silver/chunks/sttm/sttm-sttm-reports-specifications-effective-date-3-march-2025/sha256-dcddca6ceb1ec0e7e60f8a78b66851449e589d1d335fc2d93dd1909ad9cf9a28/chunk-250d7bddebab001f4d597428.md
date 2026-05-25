---
{
  "chunk_id": "chunk-250d7bddebab001f4d597428",
  "chunk_ordinal": 161,
  "chunk_text_sha256": "917f5ecfab6b027d7ae604d81c6cd4042b8b98fd571fd4476959d237bf542dc1",
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
              "b": 141.335693359375,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.2916259765625,
              "r": 527.592529296875,
              "t": 750.1739273071289
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 37
          }
        ],
        "self_ref": "#/tables/41"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-250d7bddebab001f4d597428.md",
  "heading_path": [
    "5.3.2. INT721A - Active Pipeline Operator MOS Stack"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-250d7bddebab001f4d597428.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

stack refers to either an (I) Increase or (D) Decrease. Valid values are: • I • D. estimated_maximum_quantit y, Not Null = True. estimated_maximum_quantit y, Primary Key = False. estimated_maximum_quantit y, Comment = The estimated maximum MOS quantity expected for the MOS period, populated for both increase stacks and decrease stacks.. stack_step_identifier, Not Null = True. stack_step_identifier, Primary Key = True. stack_step_identifier, Comment = The identifier that uniquely identifies a step within a MOS stack.. trading_participant_identifier, Not Null = True. trading_participant_identifier, Primary Key = False. trading_participant_identifier, Comment = The unique identifier of the contract holder of the trading right of the MOS stack step. This may or may not be the trading participant of the MOS Offer. (The field name has been left as is to minimise change.). trading_participant_name, Not Null = True. trading_participant_name, Primary Key = False. trading_participant_name, Comment = The
