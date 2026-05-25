---
{
  "chunk_id": "chunk-df84165aeed984eea247f52d",
  "chunk_ordinal": 212,
  "chunk_text_sha256": "f4a58f4c00c8522fc57d9738cd3b46da4c9dd55a2f1e5486277abbdacbdab155",
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
              "b": 83.8270263671875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.41255950927734,
              "r": 527.2830200195312,
              "t": 540.843017578125
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 66
          }
        ],
        "self_ref": "#/tables/64"
      },
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
              "b": 642.0366668701172,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.26298522949219,
              "r": 527.1592407226562,
              "t": 749.1365814208984
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 67
          }
        ],
        "self_ref": "#/tables/65"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-df84165aeed984eea247f52d.md",
  "heading_path": [
    "5.4.6. INT656 - Provisional Pipeline Data"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-df84165aeed984eea247f52d.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

provisional flow constraint price of the pipeline determined in the relevant provisional schedule
provisional_schedule_type, Not Null = True. provisional_schedule_type, Primary Key = True. provisional_schedule_type, Comment = The type of the provisional schedule. Valid values are: • D-2 • D-3 • NA (for non-schedule data). report_datetime, Not Null = True. report_datetime, Primary Key = False. report_datetime, Comment = The date and time the report was produced.
