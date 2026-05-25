---
{
  "chunk_id": "chunk-4f3dfd5bfa90764027443fbc",
  "chunk_ordinal": 412,
  "chunk_text_sha256": "9b30700aa27480cb16e19d53ae392a1a0c436f65e413908de2a19f97d8a56b0c",
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
              "b": 499.22784423828125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.45130157470703,
              "r": 527.3568725585938,
              "t": 749.7994232177734
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 94
          }
        ],
        "self_ref": "#/tables/132"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-4f3dfd5bfa90764027443fbc.md",
  "heading_path": [
    "5.5.19. INT715 - Trading Participant Contingency Gas Bid & Offer Confirmation"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-4f3dfd5bfa90764027443fbc.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

contingency_gas_bid_offer_i dentifier, Not Null = True. contingency_gas_bid_offer_i dentifier, Primary Key = True. contingency_gas_bid_offer_i dentifier, Comment = The unique identifier for the contingency gas bid/offer.. contingency_gas_bid_offer_s tep_number, Not Null = True. contingency_gas_bid_offer_s tep_number, Primary Key = True. contingency_gas_bid_offer_s tep_number, Comment = The step within each contingency gas bid/offer.. contingency_gas_bid_offer_t ype, Not Null = True. contingency_gas_bid_offer_t ype, Primary Key = False. contingency_gas_bid_offer_t ype, Comment = This field is a flag to indicate whether this is an (O) offer to increase gas at the hub or a (B) bid to decrease gas at the hub. Valid values are: • B • O. contingency_gas_bid_offer_s tep_price,
