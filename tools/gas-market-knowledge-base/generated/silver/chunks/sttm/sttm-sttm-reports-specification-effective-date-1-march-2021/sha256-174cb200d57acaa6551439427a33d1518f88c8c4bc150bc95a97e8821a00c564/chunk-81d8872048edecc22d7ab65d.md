---
{
  "chunk_id": "chunk-81d8872048edecc22d7ab65d",
  "chunk_ordinal": 423,
  "chunk_text_sha256": "134c9c1b550154e6758da9c6ce259159e6cd4beaf0bd0653073764d3b75e5a0e",
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-81d8872048edecc22d7ab65d.md",
  "heading_path": [
    "5.5.18. INT714 - Trading Participant Bid & Offer Confirmation"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-81d8872048edecc22d7ab65d.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

Not Null = True. facility_identifier, Primary Key = False. facility_identifier, Comment = The unique identifier of the facility which the bid/offer relates to. facility_name, Not Null = True. facility_name, Primary Key = False. facility_name, Comment = The name of the facility which the bid/offer relates to. bid_offer_type, Not Null = True. bid_offer_type, Primary Key = False. bid_offer_type, Comment = This field is a flag to indicate whether this is an (O) offer to supply gas to the hub or a (B) bid to flow gas from the hub for consumption at the hub or flow away from the hub or (P) a price taker bid for consumption at the hub. Valid values are: • B • O • P. trn, Not Null = True. trn, Primary Key = False. trn, Comment = The Trading Right Identifier used for the bid / offer.. bid_offer_identifier, Not Null = True. bid_offer_identifier, Primary Key = True. bid_offer_identifier, Comment = The unique identifier of the
