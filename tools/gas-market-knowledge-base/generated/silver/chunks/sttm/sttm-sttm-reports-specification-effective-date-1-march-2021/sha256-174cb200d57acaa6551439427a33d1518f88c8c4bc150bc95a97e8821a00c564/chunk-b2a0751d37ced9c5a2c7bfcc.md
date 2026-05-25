---
{
  "chunk_id": "chunk-b2a0751d37ced9c5a2c7bfcc",
  "chunk_ordinal": 221,
  "chunk_text_sha256": "103cbe363ca803c9fe906f03d0f2f4d4b1214c85fd93905490e1c750889dac05",
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
              "b": 151.3726806640625,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.25961303710938,
              "r": 527.2711791992188,
              "t": 554.8341064453125
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 70
          }
        ],
        "self_ref": "#/tables/68"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-b2a0751d37ced9c5a2c7bfcc.md",
  "heading_path": [
    "5.4.9. INT659 - Bid & Offer Report"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-b2a0751d37ced9c5a2c7bfcc.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

gas_date, Not Null = True. gas_date, Primary Key = True. gas_date, Comment = The gas date. company_identifier, Not Null = True. company_identifier, Primary Key = False. company_identifier, Comment = The unique identifier of the company that submitted the bid/offer. company_name, Not Null = True. company_name, Primary Key = False. company_name, Comment = The name of the company that submitted the bid/offer. hub_identifier, Not Null = True. hub_identifier, Primary Key = False. hub_identifier, Comment = The unique identifier of the hub. hub_name, Not Null = True. hub_name, Primary Key = False. hub_name, Comment = The name of the hub. schedule_identifier, Not Null = True. schedule_identifier, Primary Key = True. schedule_identifier, Comment = The unique identifier of the schedule in which the bids/offers were used.. facility_identifier, Not Null = True. facility_identifier, Primary Key = False. facility_identifier, Comment =
