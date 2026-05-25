---
{
  "chunk_id": "chunk-5e53e8e1fc946954b7fab9ec",
  "chunk_ordinal": 371,
  "chunk_text_sha256": "0a553f409196f1b1390f84678e925ce3a8daee126d3c9f01c4104df7bd55de31",
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
              "b": 86.65618896484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.13838195800781,
              "r": 527.4187622070312,
              "t": 429.5075988769531
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 122
          }
        ],
        "self_ref": "#/tables/120"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-5e53e8e1fc946954b7fab9ec.md",
  "heading_path": [
    "5.5.10. INT707 - Trading Participant Estimated Market Exposure"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-5e53e8e1fc946954b7fab9ec.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

trading_participant_identifier, Not Null = True. trading_participant_identifier, Primary Key = False. trading_participant_identifier, Comment = The unique identifier of the guarantor trading participant.. trading_participant_name, Not Null = True. trading_participant_name, Primary Key = False. trading_participant_name, Comment = The name of the guarantor trading participant.. prudential_run_identifier, Not Null = True. prudential_run_identifier, Primary Key = True. prudential_run_identifier, Comment = The unique identifier for the prudential run. prudential_start_date, Not Null = True. prudential_start_date, Primary Key = False. prudential_start_date, Comment = The first gas date included in the prudential run.. prudential_end_date, Not Null = True. prudential_end_date, Primary Key = False. prudential_end_date, Comment = The last gas date included in the prudential run.. bank_guarantee_reference, Not Null = True.
