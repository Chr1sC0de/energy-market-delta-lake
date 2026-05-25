---
{
  "chunk_id": "chunk-d0e9283a4a0b9c4cc7b46d29",
  "chunk_ordinal": 341,
  "chunk_text_sha256": "5a42351a3696a4d18b8dd674e3dd842cfc795008a1fb95f0332a39d6aac89ef8",
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
              "b": 185.2027587890625,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.29637145996094,
              "r": 527.1309204101562,
              "t": 570.8398132324219
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 111
          }
        ],
        "self_ref": "#/tables/109"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-d0e9283a4a0b9c4cc7b46d29.md",
  "heading_path": [
    "5.5.5. INT704 - Trading Participant Deviation and Variation Data v2"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-d0e9283a4a0b9c4cc7b46d29.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

crn_type, Not Null = False. crn_type, Primary Key = True. crn_type, Comment = Where the charge_payment _type is DVP or DVC (signifying a Deviation Payment or Deviation Charge) this field indicates the type of Registered Services associated with the deviation. When the payment_type is VAC (signifying Variation Charge) this field will hold NULL value. Valid Non-Null values are: • F • T • A Where (F) denotes "Flow From The Hub" on a facility contract to supply gas from the hub, or on a distribution contract to withdraw gas at the hub as distinguished by the facility, (T) denotes "Flow To The Hub" for facility contract to supply gas to the hub, (A) denotes "Withdraw At The Hub" for distribution contract to withdraw gas at the hub.
