---
{
  "chunk_id": "chunk-ec157b123f8b61752effd5af",
  "chunk_ordinal": 172,
  "chunk_text_sha256": "6f0d428205a86e651351281b8c1df14b9aad8a81333b282d528821e901d24f29",
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
              "b": 219.9501953125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.42018127441406,
              "r": 527.3683471679688,
              "t": 693.1859588623047
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 40
          }
        ],
        "self_ref": "#/tables/44"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-ec157b123f8b61752effd5af.md",
  "heading_path": [
    "5.4.2. INT652 - Ex Ante Schedule Quantity"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-ec157b123f8b61752effd5af.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

gas_date, Not Null = True. gas_date, Primary Key = True. gas_date, Comment = The gas date. hub_identifier, Not Null = True. hub_identifier, Primary Key = False. hub_identifier, Comment = The unique identifier of the hub. hub_name, Not Null = True. hub_name, Primary Key = False. hub_name, Comment = The name of the hub. schedule_identifier, Not Null = True. schedule_identifier, Primary Key = False. schedule_identifier, Comment = The unique identifier of the schedule from which the schedule quantity is produced. facility_identifier, Not Null = True. facility_identifier, Primary Key = True. facility_identifier, Comment = The unique identifier of the facility. facility_name, Not Null = True. facility_name, Primary Key = False. facility_name, Comment = The name of the facility. scheduled_qty, Not Null = True. scheduled_qty, Primary Key = False. scheduled_qty, Comment = The total scheduled quantity for the facility (if the facility is of type
