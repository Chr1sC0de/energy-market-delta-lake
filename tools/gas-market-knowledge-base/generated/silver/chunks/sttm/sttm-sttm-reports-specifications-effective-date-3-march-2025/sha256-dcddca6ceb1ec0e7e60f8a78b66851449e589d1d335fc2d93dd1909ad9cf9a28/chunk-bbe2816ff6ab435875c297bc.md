---
{
  "chunk_id": "chunk-bbe2816ff6ab435875c297bc",
  "chunk_ordinal": 255,
  "chunk_text_sha256": "08f7df1c01e53cbb67f81ad3a5955469cd746aee5314a2dbbad827914a7fd5ce",
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
              "b": 354.344482421875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.31029510498047,
              "r": 527.4078369140625,
              "t": 749.8996047973633
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 58
          }
        ],
        "self_ref": "#/tables/76"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-bbe2816ff6ab435875c297bc.md",
  "heading_path": [
    "5.4.24. INT674 - Total Contingency Gas Schedules"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-bbe2816ff6ab435875c297bc.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

facility_identifier, Not Null = True. facility_identifier, Primary Key = True. facility_identifier, Comment = The unique identifier of the relevant facility. Note that where deemed STTM distribution systems exist for a hub, the scheduled Contingency Gas bids and offers for the distribution systems are aggregated and reported against the associated "NETW" facility for that hub.. facility_name, Not Null = True. facility_name, Primary Key = False. facility_name, Comment = The name of the relevant facility.. contingency_gas_called_ide ntifier, Not Null = True. contingency_gas_called_ide ntifier, Primary Key = False. contingency_gas_called_ide ntifier, Comment = The unique identifier of the contingency gas called schedule. flow_direction, Not Null = True. flow_direction, Primary Key = True. flow_direction, Comment = This field indicates whether the contingency gas bid or offer is made based on a contract to (T) supply gas to the hub or (F) withdraw gas from the hub. Valid values are: • T • F Note: CG bids and
