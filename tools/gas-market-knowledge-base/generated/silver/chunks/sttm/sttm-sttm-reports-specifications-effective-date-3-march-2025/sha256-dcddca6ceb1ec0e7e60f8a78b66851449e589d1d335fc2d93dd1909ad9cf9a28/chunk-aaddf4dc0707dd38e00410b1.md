---
{
  "chunk_id": "chunk-aaddf4dc0707dd38e00410b1",
  "chunk_ordinal": 287,
  "chunk_text_sha256": "e160b6a6e26562c722cfbb526b20adacd6ba01b0e629ae9b2b8af6ae92469abf",
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
              "b": 73.7554931640625,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.21234130859375,
              "r": 527.15380859375,
              "t": 245.88458251953125
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 64
          }
        ],
        "self_ref": "#/tables/88"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-aaddf4dc0707dd38e00410b1.md",
  "heading_path": [
    "5.4.34. INT684 - Settlement Used MOS Steps"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-aaddf4dc0707dd38e00410b1.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

settlement_run_identifier, Not Null = True. settlement_run_identifier, Primary Key = True. settlement_run_identifier, Comment = The unique identifier for the settlement run.. gas_date, Not Null = True. gas_date, Primary Key = True. gas_date, Comment = Gas date on which the MOS step was used.. hub_identifier, Not Null = True. hub_identifier, Primary Key = False. hub_identifier, Comment = The unique identifier of the hub.. hub_name, Not Null = True. hub_name, Primary Key = False. hub_name, Comment = The name of the hub.. facility_identifier, Not Null = True. facility_identifier, Primary Key = False. facility_identifier, Comment = The unique identifier of the relevant facility.. facility_name, Not Null = True. facility_name, Primary Key = False. facility_name, Comment = The name of the relevant facility.. stack_identifier, Not Null = True. stack_identifier, Primary Key = True. stack_identifier,
