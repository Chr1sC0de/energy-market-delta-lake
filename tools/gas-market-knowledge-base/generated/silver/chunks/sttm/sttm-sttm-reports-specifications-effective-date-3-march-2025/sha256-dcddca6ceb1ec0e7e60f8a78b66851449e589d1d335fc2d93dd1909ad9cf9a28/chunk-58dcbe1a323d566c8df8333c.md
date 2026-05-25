---
{
  "chunk_id": "chunk-58dcbe1a323d566c8df8333c",
  "chunk_ordinal": 392,
  "chunk_text_sha256": "36a8db5038f7f5d8003cb17c9b2663bce64fc4fcbfe59b370b336ed0282db69b",
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
              "b": 209.8070068359375,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.19122314453125,
              "r": 527.3718872070312,
              "t": 750.0355377197266
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 89
          }
        ],
        "self_ref": "#/tables/123"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-58dcbe1a323d566c8df8333c.md",
  "heading_path": [
    "5.5.16. INT712 - Trading Participant Settlement MOS Allocations v2"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-58dcbe1a323d566c8df8333c.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

False. overrun_mos_gj, Comment = The overrun MOS quantity allocated to the CRN A positive quantity indicates an increase in flow to the hub; a negative quantity indicates an increase in flow from the hub.. stack_identifier, Not Null = False. stack_identifier, Primary Key = False. stack_identifier, Comment = The unique identifier for the MOS stack. Can be null when the record is identifying CRN MOS data i.e. is not identifying MOS stack step data.. stack_type, Not Null = False. stack_type, Primary Key = False. stack_type, Comment = Refers to (I) increase or (D) decrease. Valid values are: • I • D. stack_step_identifier, Not Null = False. stack_step_identifier, Primary Key = False. stack_step_identifier, Comment = The step identifier that the MOS stack step quantity is linked to. Can be null when the record is identifying CRN MOS data.. stack_step_allocation, Not Null = False. stack_step_allocation, Primary Key = False. stack_step_allocation,
