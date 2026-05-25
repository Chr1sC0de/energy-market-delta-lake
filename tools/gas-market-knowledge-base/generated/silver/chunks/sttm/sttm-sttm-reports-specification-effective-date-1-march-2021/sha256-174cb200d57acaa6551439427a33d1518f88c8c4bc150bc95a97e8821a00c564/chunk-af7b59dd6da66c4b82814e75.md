---
{
  "chunk_id": "chunk-af7b59dd6da66c4b82814e75",
  "chunk_ordinal": 276,
  "chunk_text_sha256": "b07703fa65b9fb7ae6bc8181d57823124ed626097abbff0902b2f9328e6e5894",
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
              "b": 95.1741943359375,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.33265686035156,
              "r": 527.2540893554688,
              "t": 613.7532348632812
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 89
          }
        ],
        "self_ref": "#/tables/87"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-af7b59dd6da66c4b82814e75.md",
  "heading_path": [
    "5.4.24. INT674 - Total Contingency Gas Schedules"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-af7b59dd6da66c4b82814e75.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

contingency_gas_called_identi fier, Comment = The unique identifier of the contingency gas called schedule. flow_direction, Not Null = True. flow_direction, Primary Key = True. flow_direction, Comment = This field indicates whether the contingency gas bid or offer is made based on a contract to (T) supply gas to the hub or (F) withdraw gas from the hub. Valid values are: • T • F Note: CG bids and offers based on a Distribution contract to withdraw gas (A) at the hub are displayed as F.. contingency_gas_bid_offer_ty pe, Not Null = True. contingency_gas_bid_offer_ty pe, Primary Key = True. contingency_gas_bid_offer_ty pe, Comment = This field is a flag to indicate whether this is an (O) offer to increase gas at the hub or (B) a bid to decrease gas at the hub. Valid values are: • O • B. contingency_gas_bid_offer_ca lled_quantity, Not Null = True. contingency_gas_bid_offer_ca
