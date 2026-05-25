---
{
  "chunk_id": "chunk-94371559acff2ebe2acfc20b",
  "chunk_ordinal": 312,
  "chunk_text_sha256": "f4aa5d72f2bba5053798ab6c4dcda12027b8184183927bb1ea2a8cb1b093931b",
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
              "b": 392.98443603515625,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.16173553466797,
              "r": 527.4378051757812,
              "t": 749.7822952270508
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 70
          }
        ],
        "self_ref": "#/tables/99"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-94371559acff2ebe2acfc20b.md",
  "heading_path": [
    "5.5.2. INT702 - Trading Participant Provisional Schedule"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-94371559acff2ebe2acfc20b.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

True. trn, Primary Key = True. trn, Comment = The trading right number which the schedule quantity relates to. provisional_qty, Not Null = True. provisional_qty, Primary Key = False. provisional_qty, Comment = The schedule quantity for the trading right number. bid_offer_type, Not Null = True. bid_offer_type, Primary Key = True. bid_offer_type, Comment = This field is a flag to indicate whether the schedule is for an offer (O) to supply gas to the hub or a bid (B) to flow gas from the hub (for consumption at the hub or flow away from the hub) or a (P) Price Taker Bid to flow gas from the hub for consumption at the hub. Valid values are: • B • O • P. provisional_schedule_type, Not Null = True. provisional_schedule_type, Primary Key = False. provisional_schedule_type, Comment = The type of the provisional schedule. Valid values are: • D-2 • D-3. report_datetime, Not Null = True. report_datetime, Primary Key = False. report_datetime, Comment = The date and time the report was
