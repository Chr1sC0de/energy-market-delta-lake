---
{
  "chunk_id": "chunk-ef3ebd0135c0735b9d8fda5f",
  "chunk_ordinal": 178,
  "chunk_text_sha256": "029ac985b86b1d08bbbc6e21a876380fdb7b606a577431b13bbbdeb739efa65b",
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
              "b": 79.949462890625,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.24608612060547,
              "r": 509.5865783691406,
              "t": 623.0806732177734
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 41
          }
        ],
        "self_ref": "#/tables/45"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-ef3ebd0135c0735b9d8fda5f.md",
  "heading_path": [
    "5.4.3. INT653 - Ex Ante Pipeline Data"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-ef3ebd0135c0735b9d8fda5f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

ex_ante_capacity_price, Comment = The capacity price of pipeline for the gas date. This price is either the capacity price determined by the scheduling and pricing engine or the administered price during an administered price period.. ex_ante_flow_direction_con straint_price, Not Null = False. ex_ante_flow_direction_con straint_price, Primary Key = False. ex_ante_flow_direction_con straint_price, Comment = The pipeline flow direction constraint price of the pipeline determined in the relevant market schedule. Note: pipeline flow direction constraint price is NOT capped during an administered cap price state.. schedule_capacity_price, Not Null = False. schedule_capacity_price, Primary Key = False. schedule_capacity_price, Comment = If the capacity price was capped at APC, this field will contain the capacity price which was derived from the bids and offers prior to the cap being
