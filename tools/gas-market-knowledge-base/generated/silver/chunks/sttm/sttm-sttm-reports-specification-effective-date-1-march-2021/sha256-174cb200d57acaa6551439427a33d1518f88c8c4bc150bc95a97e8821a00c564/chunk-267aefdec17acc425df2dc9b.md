---
{
  "chunk_id": "chunk-267aefdec17acc425df2dc9b",
  "chunk_ordinal": 435,
  "chunk_text_sha256": "065236cc90e335f816045c3e7eb41d83528b219d06f62017c2ae40dffbd50a40",
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
              "b": 564.029296875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.19737243652344,
              "r": 527.262939453125,
              "t": 749.4802093505859
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 142
          }
        ],
        "self_ref": "#/tables/142"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-267aefdec17acc425df2dc9b.md",
  "heading_path": [
    "5.5.20. INT715A - Trading Participant Active Contingency Gas Bids & Offers"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-267aefdec17acc425df2dc9b.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

contingency_gas_bid_offer_st ep_registered_reference, Not Null = False. contingency_gas_bid_offer_st ep_registered_reference, Primary Key = False. contingency_gas_bid_offer_st ep_registered_reference, Comment = The registered step reference. This will only be populated if a trading participant has pre-registered their steps.. contingency_gas_bid_offer_co mments, Not Null = False. contingency_gas_bid_offer_co mments, Primary Key = False. contingency_gas_bid_offer_co mments, Comment = The comment entered by the participant when submitting the Contingency Gas bid/offer.. last_update_datetime, Not Null = True. last_update_datetime, Primary Key = False. last_update_datetime, Comment = The date & time the CG bid/offer was last updated ie. when the record is submitted.. last_update_by, Not Null = True. last_update_by, Primary Key = False. last_update_by, Comment = The user name of the person who performed the CG
