---
{
  "chunk_id": "chunk-ac9387366dec0a15927ddda0",
  "chunk_ordinal": 439,
  "chunk_text_sha256": "a0b1a273e5547c4522cb734a85290fef93b7f8ea03b10626de1c4eda8ac49bac",
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
              "b": 93.09222412109375,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.43631744384766,
              "r": 527.276123046875,
              "t": 600.4814605712891
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 143
          }
        ],
        "self_ref": "#/tables/143"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-ac9387366dec0a15927ddda0.md",
  "heading_path": [
    "5.5.21. INT715B - Trading Participant Contingency Gas Quantity Confirmation"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-ac9387366dec0a15927ddda0.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

flow_direction, Not Null = True. flow_direction, Primary Key = False. flow_direction, Comment = This field indicates whether the contingency gas bid or offer is made based on a contract to supply gas to the hub or withdraw gas from the hub. Valid values are: • T (supply gas to the hub) • F (withdraw gas from the hub and at the hub) Note: CG bids and offers based on a Distribution contract to withdraw gas at the hub are displayed as. contingency_gas_bid_offer_id entifier, Not Null = True. contingency_gas_bid_offer_id entifier, Primary Key = True. contingency_gas_bid_offer_id entifier, Comment = The unique identifier for the contingency gas bid/offer.. contingency_gas_bid_offer_st ep_number, Not Null = True. contingency_gas_bid_offer_st ep_number, Primary Key = True. contingency_gas_bid_offer_st ep_number, Comment = The step within each contingency gas bid/offer..
