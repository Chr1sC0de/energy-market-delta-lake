---
{
  "chunk_id": "chunk-e981548ea3eba9001a0ddf28",
  "chunk_ordinal": 424,
  "chunk_text_sha256": "7e2f1f226e305c51057c820d9aff990f6a59b33112724f1a41f9388294d2956e",
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
              "b": 253.22235107421875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.17784881591797,
              "r": 527.41650390625,
              "t": 750.0382232666016
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 96
          }
        ],
        "self_ref": "#/tables/136"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-e981548ea3eba9001a0ddf28.md",
  "heading_path": [
    "5.5.21. INT715B - Trading Participant Contingency Gas Quantity Confirmation"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-e981548ea3eba9001a0ddf28.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

contingency_gas_bid_offer_t ype, Not Null = True. contingency_gas_bid_offer_t ype, Primary Key = False. contingency_gas_bid_offer_t ype, Comment = This field is a flag to indicate whether this is an offer to increase gas at the hub or a bid to decrease gas at the hub. Valid values are: • B (bid to decrease gas at the hub) • O (offer to increase gas at the hub). contingency_gas_bid_offer_s tep_price, Not Null = True. contingency_gas_bid_offer_s tep_price, Primary Key = False. contingency_gas_bid_offer_s tep_price, Comment = The price at which the contingency bid or offer is made.. contingency_gas_bid_offer_s tep_quantity, Not Null = True. contingency_gas_bid_offer_s tep_quantity, Primary Key = False. contingency_gas_bid_offer_s tep_quantity, Comment = Cumulative quantity of contingency gas offer or bid on a
