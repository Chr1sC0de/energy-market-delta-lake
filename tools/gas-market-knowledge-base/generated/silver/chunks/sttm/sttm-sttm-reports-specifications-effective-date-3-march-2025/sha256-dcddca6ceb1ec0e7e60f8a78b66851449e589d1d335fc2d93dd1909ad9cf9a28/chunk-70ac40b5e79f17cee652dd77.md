---
{
  "chunk_id": "chunk-70ac40b5e79f17cee652dd77",
  "chunk_ordinal": 300,
  "chunk_text_sha256": "3c3dbd623dde8a481f5fae9ba74aa2f2fa321d1441f21fd46ef6e5836dad21f0",
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
              "b": 92.43798828125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.42903137207031,
              "r": 527.2631225585938,
              "t": 349.9313049316406
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 67
          }
        ],
        "self_ref": "#/tables/94"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-70ac40b5e79f17cee652dd77.md",
  "heading_path": [
    "5.4.38. INT690 - Deviation Price Data"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-70ac40b5e79f17cee652dd77.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

gas_date, Not Null = True. gas_date, Primary Key = True. gas_date, Comment = The gas date. hub_identifier, Not Null = True. hub_identifier, Primary Key = True. hub_identifier, Comment = The unique identifier of the hub. hub_name, Not Null = True. hub_name, Primary Key = False. hub_name, Comment = The name of the hub. positive_deviation_price, Not Null = True. positive_deviation_price, Primary Key = False. positive_deviation_price, Comment = The positive deviation price at the hub for the gas date. negative_deviation_price, Not Null = True. negative_deviation_price, Primary Key = False. negative_deviation_price, Comment = The negative deviation price at the hub for the gas date. ex_ante_market_price, Not Null = True. ex_ante_market_price, Primary Key = False. ex_ante_market_price, Comment = The ex ante market price used to determine the positive and negative deviation price. ex_post_imbalance_price, Not Null = True.
