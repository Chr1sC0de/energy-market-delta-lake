---
{
  "chunk_id": "chunk-973e70d130a55e6db9ad1cc6",
  "chunk_ordinal": 381,
  "chunk_text_sha256": "3a17feaa7e42b14b4c80c11458ba76e519ffdc72bec08d7d3e0555e0df0a04d3",
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
              "b": 489.46307373046875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.19194793701172,
              "r": 527.2689208984375,
              "t": 749.6032028198242
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 125
          }
        ],
        "self_ref": "#/tables/123"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md",
    "source_manifest_line_number": 46,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/short-term-trading-market-sttm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/sttm/policies/sttm-reports-specifications-v190.pdf?rev=ee0167ede9c94105b170ff3edcc2fc99&sc_lang=en"
  },
  "content_sha256": "174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564",
  "corpus": "sttm",
  "document_family": "sttm__sttm-reports-specification-effective-date-1-march-2021",
  "document_family_id": "sttm__sttm-reports-specification-effective-date-1-march-2021",
  "document_identity": "sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564",
  "document_title": "##### STTM Reports Specification Effective date 1 March 2021",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-973e70d130a55e6db9ad1cc6.md",
  "heading_path": [
    "5.5.11. INT708 - Trading Participant Contingency Gas Schedules"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-973e70d130a55e6db9ad1cc6.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

lled_step_quantity, Not Null = False. contingency_gas_bid_offer_ca lled_step_quantity, Primary Key = False. contingency_gas_bid_offer_ca lled_step_quantity, Comment = This is the quantity of gas in each contingency gas bid or offer step that the provider has been called to provide.. contingency_gas_comments, Not Null = False. contingency_gas_comments, Primary Key = False. contingency_gas_comments, Comment = Any comment provided as part of the process for calling contingency gas. approval_datetime, Not Null = True. approval_datetime, Primary Key = False. approval_datetime, Comment = The date and time that the contingency gas called was approved. report_datetime, Not Null = True. report_datetime, Primary Key = False. report_datetime, Comment = The date and time the report was produced.
