---
{
  "chunk_id": "chunk-53502a374debb609fa9cddb4",
  "chunk_ordinal": 227,
  "chunk_text_sha256": "5d15c554a361e3e03af84c8316a6fff3f4ef4bf81547d6f54a5bd4f2e423b427",
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
              "b": 85.2474365234375,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.34701538085938,
              "r": 527.314697265625,
              "t": 587.1436767578125
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 72
          }
        ],
        "self_ref": "#/tables/70"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-53502a374debb609fa9cddb4.md",
  "heading_path": [
    "5.4.10. INT660 - Contingency Gas Bid & Offer"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-53502a374debb609fa9cddb4.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

bid/offer. contingency_gas_bid_offer_st ep_number, Not Null = True. contingency_gas_bid_offer_st ep_number, Primary Key = True. contingency_gas_bid_offer_st ep_number, Comment = The number of the contingency gas bid/offer step (1 - 10) on the bid/offer stack. contingency_gas_bid_offer_st ep_price, Not Null = True. contingency_gas_bid_offer_st ep_price, Primary Key = False. contingency_gas_bid_offer_st ep_price, Comment = The price at which the contingency bid or offer is made.. contingency_gas_bid_offer_st ep_quantity, Not Null = True. contingency_gas_bid_offer_st ep_quantity, Primary Key = False. contingency_gas_bid_offer_st ep_quantity, Comment = Cumulative quantity of contingency gas offered or bid on a contingency gas bid/offer step.
