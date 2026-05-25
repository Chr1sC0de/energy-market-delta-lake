---
{
  "chunk_id": "chunk-4e60e978ef806c4b37d2fcd4",
  "chunk_ordinal": 424,
  "chunk_text_sha256": "5b7067dd8f2fc5f7d2f80012cdf5035985511d03e0f371fed8a9f6e920b26b2e",
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
              "b": 120.6346435546875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.46717071533203,
              "r": 527.2177734375,
              "t": 600.6377868652344
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 138
          }
        ],
        "self_ref": "#/tables/138"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-4e60e978ef806c4b37d2fcd4.md",
  "heading_path": [
    "5.5.18. INT714 - Trading Participant Bid & Offer Confirmation"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-4e60e978ef806c4b37d2fcd4.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

relevant bid or offer. bid_offer_step_number, Not Null = True. bid_offer_step_number, Primary Key = True. bid_offer_step_number, Comment = The number of the bid/offer step (1 - 10) on the bid/offer stack. step_price, Not Null = False. step_price, Primary Key = False. step_price, Comment = Dollar price per GJ for bid/offer. step_cumulative_qty, Not Null = True. step_cumulative_qty, Primary Key = False. step_cumulative_qty, Comment = The cumulative quantity of bid/offer step. last_update_datetime, Not Null = True. last_update_datetime, Primary Key = False. last_update_datetime, Comment = The date & time the bid/offer was updated ie. saved into database. last_update_by, Not Null = True. last_update_by, Primary Key = False. last_update_by, Comment = The user name used in the bid/offer submission. report_datetime, Not Null = True. report_datetime, Primary Key = False. report_datetime, Comment = The date
