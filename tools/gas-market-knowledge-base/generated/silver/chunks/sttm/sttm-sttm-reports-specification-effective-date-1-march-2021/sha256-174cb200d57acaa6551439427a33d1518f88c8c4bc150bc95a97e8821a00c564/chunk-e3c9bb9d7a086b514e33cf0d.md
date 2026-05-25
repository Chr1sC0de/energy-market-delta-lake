---
{
  "chunk_id": "chunk-e3c9bb9d7a086b514e33cf0d",
  "chunk_ordinal": 442,
  "chunk_text_sha256": "561e98ae5d9f27123d30a1773dd1059337c462d42217fbbc6f6cb6e437e63bd3",
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
              "b": 518.3789978027344,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.27156829833984,
              "r": 527.3206176757812,
              "t": 749.5476837158203
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 144
          }
        ],
        "self_ref": "#/tables/144"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-e3c9bb9d7a086b514e33cf0d.md",
  "heading_path": [
    "5.5.21. INT715B - Trading Participant Contingency Gas Quantity Confirmation"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-e3c9bb9d7a086b514e33cf0d.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

contingency_gas_bid_offer_st ep_confirmation_type, Not Null = True. contingency_gas_bid_offer_st ep_confirmation_type, Primary Key = False. contingency_gas_bid_offer_st ep_confirmation_type, Comment = This field indicates the method of confirmation used. Valid values are: • T (Total Quantity) • R (Registered Steps). contingency_gas_bid_offer_st ep_registered_reference, Not Null = False. contingency_gas_bid_offer_st ep_registered_reference, Primary Key = False. contingency_gas_bid_offer_st ep_registered_reference, Comment = The registered step reference. This will only be populated if a trading participant has pre-registered their steps.. contingency_gas_bid_offer_co nfirmation_comments, Not Null = False. contingency_gas_bid_offer_co nfirmation_comments, Primary Key = False. contingency_gas_bid_offer_co nfirmation_comments, Comment = The comment entered by the participant when confirming the Contingency Gas bid/offer..
