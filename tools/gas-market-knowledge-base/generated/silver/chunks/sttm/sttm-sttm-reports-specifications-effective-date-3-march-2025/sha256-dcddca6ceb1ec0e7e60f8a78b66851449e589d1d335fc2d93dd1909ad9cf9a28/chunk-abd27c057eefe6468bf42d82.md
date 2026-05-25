---
{
  "chunk_id": "chunk-abd27c057eefe6468bf42d82",
  "chunk_ordinal": 274,
  "chunk_text_sha256": "c3db6134b093d998f8a3d2c6f7771b249e1a8de56a1c30cd5e2aab86df944e7a",
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
              "b": 595.1103057861328,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.3045883178711,
              "r": 527.3017578125,
              "t": 749.6692886352539
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 62
          }
        ],
        "self_ref": "#/tables/84"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-abd27c057eefe6468bf42d82.md",
  "heading_path": [
    "5.4.30. INT680 - DP Flag Data"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-abd27c057eefe6468bf42d82.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

hub_identifier, Not Null = True. hub_identifier, Primary Key = True. hub_identifier, Comment = The unique identifier of the hub.. hub_name, Not Null = True. hub_name, Primary Key = False. hub_name, Comment = The name of the hub.. effective_from_date, Not Null = True. effective_from_date, Primary Key = True. effective_from_date, Comment = The gas date from which the DP flag setting applies.. effective_to_date, Not Null = False. effective_to_date, Primary Key = False. effective_to_date, Comment = The gas date to which the DP flag setting applies. If this is NULL it implies ongoing effectiveness.. dp_flag, Not Null = True. dp_flag, Primary Key = False. dp_flag, Comment = The dp_flag setting: When the DP flag has been set for a given hub and gas date in SBS, this value is 1 else 0.. report_datetime, Not Null = True. report_datetime, Primary Key = False. report_datetime, Comment = The date and
