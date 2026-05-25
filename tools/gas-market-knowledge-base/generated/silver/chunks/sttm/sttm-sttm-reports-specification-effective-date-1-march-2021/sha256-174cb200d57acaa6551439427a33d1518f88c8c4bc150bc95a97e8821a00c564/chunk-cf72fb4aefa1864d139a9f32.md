---
{
  "chunk_id": "chunk-cf72fb4aefa1864d139a9f32",
  "chunk_ordinal": 180,
  "chunk_text_sha256": "c96bd39e7ff850aec3d477cd6be064c2f41bc4c70290fc27aaf3d34aab236fb6",
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
              "b": 111.537841796875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.31350708007812,
              "r": 527.3286743164062,
              "t": 501.68450927734375
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 54
          }
        ],
        "self_ref": "#/tables/52"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-cf72fb4aefa1864d139a9f32.md",
  "heading_path": [
    "5.3.2. INT721A - Active Pipeline Operator MOS Stack"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-cf72fb4aefa1864d139a9f32.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

Primary Key = False. facility_name, Comment = The name of the facility.. stack_type, Not Null = True. stack_type, Primary Key = False. stack_type, Comment = Each MOS stack refers to either an (I) Increase or (D) Decrease. Valid values are: • I • D. estimated_maximum_quantity, Not Null = True. estimated_maximum_quantity, Primary Key = False. estimated_maximum_quantity, Comment = The estimated maximum MOS quantity expected for the MOS period, populated for both increase stacks and decrease stacks.. stack_step_identifier, Not Null = True. stack_step_identifier, Primary Key = True. stack_step_identifier, Comment = The identifier that uniquely identifies a step within a MOS stack.. trading_participant_identifier, Not Null = True. trading_participant_identifier, Primary Key = False. trading_participant_identifier, Comment = The unique identifier of the contract holder of the trading right of the MOS stack step. This may or may not be the trading participant of the MOS Offer. (The field name has been left as is to
