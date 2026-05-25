---
{
  "chunk_id": "chunk-ead74570fa7a81fbbad1a991",
  "chunk_ordinal": 370,
  "chunk_text_sha256": "7f1611f1e526bd0ca51b96e2b72667db05fcd10d25a197bb5b45d38acc356b0e",
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
              "b": 384.3485412597656,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.30670928955078,
              "r": 527.4077758789062,
              "t": 749.8643493652344
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 84
          }
        ],
        "self_ref": "#/tables/116"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-ead74570fa7a81fbbad1a991.md",
  "heading_path": [
    "5.5.12. INT709 - Trading Participant Market Schedule Variation"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-ead74570fa7a81fbbad1a991.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

, Not Null = . , Primary Key = . , Comment = • D - Decrease. quantity_gj, Not Null = True. quantity_gj, Primary Key = False. quantity_gj, Comment = The quantity of the market schedule variation.. counter_party_confirmation, Not Null = True. counter_party_confirmation, Primary Key = False. counter_party_confirmation, Comment = This field will have the status of the market schedule variation. Valid statuses include: "Confirmed' if the counter party has confirmed "Rejected" if the counter party has rejected "Submitted" if the counter party has neither confirmed nor rejected "Expired" if the counter party has not confirmed within the time frame required. msv_chargeable, Not Null = True. msv_chargeable, Primary Key = False. msv_chargeable, Comment = This field indicates whether the counter party will be charged (C) a variation charge for this market schedule variation if the counter party confirms or if it will be free (F). • C - Charged • F - Free. confirmation_datetime, Not Null = False. confirmation_datetime, Primary Key = False. confirmation_datetime, Comment = The date & time the market
