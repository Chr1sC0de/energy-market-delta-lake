---
{
  "chunk_id": "chunk-304b94ed87abc87f5e2d595f",
  "chunk_ordinal": 185,
  "chunk_text_sha256": "ddf2b71246358ef1f29891f90b177aced94d7e7c1989b01928e9b66492368ede",
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
              "b": 288.02734375,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.18680572509766,
              "r": 527.4002685546875,
              "t": 749.703727722168
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 43
          }
        ],
        "self_ref": "#/tables/49"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-304b94ed87abc87f5e2d595f.md",
  "heading_path": [
    "5.4.5. INT655 - Provisional Schedule Quantity"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-304b94ed87abc87f5e2d595f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

null if the facility is of type ' network'.. provisional_as_available_sch eduled, Not Null = False. provisional_as_available_sch eduled, Primary Key = False. provisional_as_available_sch eduled, Comment = This field contains the total provisional as available gas quantity on the pipeline for the gas day i.e. total provisional scheduled quantities of all Trading Rights which are associated with Registered Services of priority other than 1. This field is null if the facility is of type 'network'.. flow_direction, Not Null = True. flow_direction, Primary Key = True. flow_direction, Comment = This field indicates whether the forecast quantity is for (T) supply to the hub or (F) withdrawal from the hub. Valid values are: • T • F. price_taker_bid_provisional_ not_sched_qty, Not Null = False. price_taker_bid_provisional_ not_sched_qty, Primary Key = False. price_taker_bid_provisional_ not_sched_qty, Comment = The price taker bid quantity not scheduled in the provisional schedule. This field will be null if the facility is
