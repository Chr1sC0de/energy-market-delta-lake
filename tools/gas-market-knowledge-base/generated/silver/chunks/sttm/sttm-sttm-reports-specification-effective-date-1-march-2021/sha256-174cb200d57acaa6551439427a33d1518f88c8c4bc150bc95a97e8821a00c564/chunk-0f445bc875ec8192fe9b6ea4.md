---
{
  "chunk_id": "chunk-0f445bc875ec8192fe9b6ea4",
  "chunk_ordinal": 445,
  "chunk_text_sha256": "1d486aeb88893ed2b0a0048a8014106c2b4edfb8ba6c816a5471134d4b68b4da",
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
              "b": 96.26470947265625,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.40728759765625,
              "r": 527.2117919921875,
              "t": 573.9371032714844
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 145
          }
        ],
        "self_ref": "#/tables/145"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-0f445bc875ec8192fe9b6ea4.md",
  "heading_path": [
    "5.5.22. INT716 - Trading Participant Settlement Details"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-0f445bc875ec8192fe9b6ea4.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

trading_participant_identifier, Not Null = True. trading_participant_identifier, Primary Key = False. trading_participant_identifier, Comment = The unique identifier of the trading participant.. trading_participant_name, Not Null = True. trading_participant_name, Primary Key = False. trading_participant_name, Comment = The name of the trading participant. settlement_run_identifier, Not Null = True. settlement_run_identifier, Primary Key = True. settlement_run_identifier, Comment = STTM identifier for the settlement run. hub_identifier, Not Null = True. hub_identifier, Primary Key = True. hub_identifier, Comment = The unique identifier of the hub.. hub_name, Not Null = True. hub_name, Primary Key = False. hub_name, Comment = The name of the hub.. gas_date, Not Null = True. gas_date, Primary Key = True. gas_date, Comment = Gas day the charge / payment is applicable for.. charge_payment_type, Not Null = True. charge_payment_type, Primary Key =
