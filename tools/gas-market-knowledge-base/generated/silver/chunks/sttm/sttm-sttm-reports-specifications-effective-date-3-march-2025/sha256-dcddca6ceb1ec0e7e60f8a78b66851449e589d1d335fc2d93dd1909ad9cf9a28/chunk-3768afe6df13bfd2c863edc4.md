---
{
  "chunk_id": "chunk-3768afe6df13bfd2c863edc4",
  "chunk_ordinal": 436,
  "chunk_text_sha256": "31506bc87fc147ec8225a1e84daee81e9cbcc871268f04b90323bc5065cd5424",
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
              "b": 430.09564208984375,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.18312072753906,
              "r": 527.4052124023438,
              "t": 749.8253707885742
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 99
          }
        ],
        "self_ref": "#/tables/142"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-3768afe6df13bfd2c863edc4.md",
  "heading_path": [
    "5.5.23. INT718 - Trading Participant Estimated Market Exposure Details"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-3768afe6df13bfd2c863edc4.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

prudential_end_date, Not Null = True. prudential_end_date, Primary Key = False. prudential_end_date, Comment = The last gas date included in the prudential run.. hub_identifier, Not Null = True. hub_identifier, Primary Key = False. hub_identifier, Comment = The name of the hub the charges relate to ie ADL,SYD. hub_name, Not Null = True. hub_name, Primary Key = False. hub_name, Comment = The description of the hub the charges relate to ie. Sydney, Adelaide. charge_payment_type, Not Null = True. charge_payment_type, Primary Key = True. charge_payment_type, Comment = The code for the charge / payment.. charge_payment_amt_gst_e x, Not Null = True. charge_payment_amt_gst_e x, Primary Key = False. charge_payment_amt_gst_e x, Comment = The monetary value of the charge / payment excluding GST. This value is positive if it is a charge payable TO AEMO, and negative if it is
