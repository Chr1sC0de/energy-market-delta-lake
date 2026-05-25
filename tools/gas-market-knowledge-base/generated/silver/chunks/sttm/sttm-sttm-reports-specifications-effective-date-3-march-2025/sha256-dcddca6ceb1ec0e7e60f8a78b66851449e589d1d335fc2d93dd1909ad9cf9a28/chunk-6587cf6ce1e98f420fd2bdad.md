---
{
  "chunk_id": "chunk-6587cf6ce1e98f420fd2bdad",
  "chunk_ordinal": 265,
  "chunk_text_sha256": "5eed89e3960478bf5d915661a1572469b858cc7dfd8e063ec43cba1f2a6d1eb8",
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
              "b": 491.3700256347656,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.43587493896484,
              "r": 528.0665893554688,
              "t": 749.8520431518555
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 60
          }
        ],
        "self_ref": "#/tables/81"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-6587cf6ce1e98f420fd2bdad.md",
  "heading_path": [
    "5.4.27. INT677 - Contingency Gas Price"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-6587cf6ce1e98f420fd2bdad.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

, Not Null = . , Primary Key = . , Comment = called for the gas day. If high contingency gas price was administered, this field contains the administered high contingency gas price.. low_contingency_gas_price, Not Null = False. low_contingency_gas_price, Primary Key = False. low_contingency_gas_price, Comment = If contingency gas has been called upon to decrease supply to the hub, then this field is populated with the low contingency gas price. Stored in $ / GJ. This field will be null if no contingency gas was called for the gas day. If low contingency gas price was administered, this field contains the administered low contingency gas price.. schedule_high_contingency _gas_price, Not Null = False. schedule_high_contingency _gas_price, Primary Key = False. schedule_high_contingency _gas_price, Comment = If the high contingency gas price was administered, this field contains the high contingency gas price determined from the contingency gas offers.. schedule_low_contingency_ gas_price, Not Null =
