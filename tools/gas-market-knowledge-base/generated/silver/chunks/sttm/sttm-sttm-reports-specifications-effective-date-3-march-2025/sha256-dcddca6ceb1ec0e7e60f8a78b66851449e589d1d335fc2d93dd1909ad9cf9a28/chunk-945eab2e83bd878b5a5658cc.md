---
{
  "chunk_id": "chunk-945eab2e83bd878b5a5658cc",
  "chunk_ordinal": 429,
  "chunk_text_sha256": "7bdaf565a7eafe4876bb7793c7c21cfc5ff1c115dd22407752d0bcca07d29642",
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
              "b": 306.10736083984375,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.03701782226562,
              "r": 527.5983276367188,
              "t": 736.3510208129883
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 97
          }
        ],
        "self_ref": "#/tables/137"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-945eab2e83bd878b5a5658cc.md",
  "heading_path": [
    "5.5.22. INT716 - Trading Participant Settlement Details"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-945eab2e83bd878b5a5658cc.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

True. charge_payment_type, Comment = The code for the charge / payment. charge_payment_desc, Not Null = True. charge_payment_desc, Primary Key = False. charge_payment_desc, Comment = The description associated with the charge / payment. facility_identifier, Not Null = True. facility_identifier, Primary Key = True. facility_identifier, Comment = The unique identifier of the facility. facility_name, Not Null = True. facility_name, Primary Key = False. facility_name, Comment = The name of the facility.. service_type, Not Null = True. service_type, Primary Key = True. service_type, Comment = Indicates the type of Registered Service that the allocation quantity is associated with. Valid values are: • F - From the hub (facility flows from the hub) • T - To the hub (facility flows to the hub) • A - At the hub (distribution system -network- flows at the hub) Note: For amounts relating to MOS step quantities, the direction is determined as follows: Increase MOS is to the hub Decrease MOS is from the hub. quantity_gj, Not Null =
