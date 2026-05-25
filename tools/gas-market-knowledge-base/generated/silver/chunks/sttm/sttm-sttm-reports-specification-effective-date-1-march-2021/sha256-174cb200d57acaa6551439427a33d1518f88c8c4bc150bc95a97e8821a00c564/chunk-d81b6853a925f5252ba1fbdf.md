---
{
  "chunk_id": "chunk-d81b6853a925f5252ba1fbdf",
  "chunk_ordinal": 376,
  "chunk_text_sha256": "08f0373bb4748a435508879b50d6a2beb22645d7e469eaa79920f97066bdea36",
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
              "b": 93.13458251953125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.56053161621094,
              "r": 527.3240356445312,
              "t": 600.5171661376953
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 124
          }
        ],
        "self_ref": "#/tables/122"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-d81b6853a925f5252ba1fbdf.md",
  "heading_path": [
    "5.5.11. INT708 - Trading Participant Contingency Gas Schedules"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-d81b6853a925f5252ba1fbdf.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

trading_participant_identifier, Not Null = True. trading_participant_identifier, Primary Key = False. trading_participant_identifier, Comment = The unique identifier of the trading participant.. trading_participant_name, Not Null = True. trading_participant_name, Primary Key = False. trading_participant_name, Comment = The name of the trading participant. gas_date, Not Null = True. gas_date, Primary Key = False. gas_date, Comment = The gas date. contingency_gas_provider_id entifier, Not Null = True. contingency_gas_provider_id entifier, Primary Key = False. contingency_gas_provider_id entifier, Comment = Contingency gas provider unique identifier. contingency_gas_provider_na me, Not Null = True. contingency_gas_provider_na me, Primary Key = False. contingency_gas_provider_na me, Comment = Contingency gas provider company name. hub_identifier, Not Null = True. hub_identifier, Primary Key = False.
