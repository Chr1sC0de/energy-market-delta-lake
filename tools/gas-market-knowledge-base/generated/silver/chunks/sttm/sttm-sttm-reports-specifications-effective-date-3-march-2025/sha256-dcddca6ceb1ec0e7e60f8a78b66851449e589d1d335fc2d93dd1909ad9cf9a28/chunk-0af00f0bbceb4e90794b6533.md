---
{
  "chunk_id": "chunk-0af00f0bbceb4e90794b6533",
  "chunk_ordinal": 425,
  "chunk_text_sha256": "c5c46674f7256b105cc24079d5d8a48b627a40e53983f9e26cccb3b0d9561716",
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-0af00f0bbceb4e90794b6533.md",
  "heading_path": [
    "5.5.21. INT715B - Trading Participant Contingency Gas Quantity Confirmation"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-0af00f0bbceb4e90794b6533.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

contingency gas bid/offer step.. contingency_gas_bid_offer_ confirmed_step_quantity, Not Null = True. contingency_gas_bid_offer_ confirmed_step_quantity, Primary Key = False. contingency_gas_bid_offer_ confirmed_step_quantity, Comment = Confirmed cumulative quantity of contingency gas offered or bid on a contingency gas bid/offer step.. contingency_gas_bid_offer_s tep_confirmation_type, Not Null = True. contingency_gas_bid_offer_s tep_confirmation_type, Primary Key = False. contingency_gas_bid_offer_s tep_confirmation_type, Comment = This field indicates the method of confirmation used. Valid values are: • T (Total Quantity) • R (Registered Steps). contingency_gas_bid_offer_s tep_registered_reference, Not Null = False. contingency_gas_bid_offer_s tep_registered_reference, Primary Key = False. contingency_gas_bid_offer_s tep_registered_reference, Comment = The registered step reference.
