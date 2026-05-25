---
{
  "chunk_id": "chunk-7c6fb9a443ca8f8e1b61461f",
  "chunk_ordinal": 405,
  "chunk_text_sha256": "6945c497be1f0278d26a0cb9eb51dbb962e3b3aea333c5fb1822e06baf9e3a2d",
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
              "b": 345.3514404296875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.22586822509766,
              "r": 527.5071411132812,
              "t": 749.8605880737305
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 132
          }
        ],
        "self_ref": "#/tables/130"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-7c6fb9a443ca8f8e1b61461f.md",
  "heading_path": [
    "5.5.15. INT712 - Trading Participant Settlement MOS Allocations"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-7c6fb9a443ca8f8e1b61461f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

stack_step_identifier, Not Null = False. stack_step_identifier, Primary Key = False. stack_step_identifier, Comment = The step identifier that the MOS stack step quantity is linked to. Can be null when the record is identifying CRN MOS data.. stack_step_allocation, Not Null = False. stack_step_allocation, Primary Key = False. stack_step_allocation, Comment = The MOS stack step allocation quantity. transaction_identifier, Not Null = False. transaction_identifier, Primary Key = False. transaction_identifier, Comment = A STTM unique identifier given by AEMO to the allocation data file when it is received from the facility owner's allocation agent. This transaction identifier can be used as a reference when allocation agents send registered service allocations to AEMO.. report_datetime, Not Null = True. report_datetime, Primary Key = False. report_datetime, Comment = The date and time the report is generated.
