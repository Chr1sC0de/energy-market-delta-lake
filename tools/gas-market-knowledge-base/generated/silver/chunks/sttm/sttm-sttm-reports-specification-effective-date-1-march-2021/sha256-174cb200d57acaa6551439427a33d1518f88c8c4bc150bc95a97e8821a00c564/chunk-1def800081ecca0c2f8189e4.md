---
{
  "chunk_id": "chunk-1def800081ecca0c2f8189e4",
  "chunk_ordinal": 460,
  "chunk_text_sha256": "550ad01b53928c2a06e6adb8a228dbe82df32c9edaad549af4547b328efc60d5",
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
              "b": 118.28802490234375,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.33476257324219,
              "r": 527.1797485351562,
              "t": 600.6230163574219
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 150
          }
        ],
        "self_ref": "#/tables/151"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-1def800081ecca0c2f8189e4.md",
  "heading_path": [
    "5.5.25. INT725 - Trading Participant MOS Offer Confirmation"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-1def800081ecca0c2f8189e4.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

trading_participant_identifier, Not Null = True. trading_participant_identifier, Primary Key = False. trading_participant_identifier, Comment = The unique identifier for the trading participant.. trading_participant_name, Not Null = True. trading_participant_name, Primary Key = False. trading_participant_name, Comment = Trading participant name.. effective_from_date, Not Null = True. effective_from_date, Primary Key = False. effective_from_date, Comment = The first gas date covered by the MOS offer i.e. start date of MOS Period. effective_to_date, Not Null = True. effective_to_date, Primary Key = False. effective_to_date, Comment = The end gas date covered by the MOS offer i.e. end date of MOS Period. hub_identifier, Not Null = True. hub_identifier, Primary Key = False. hub_identifier, Comment = The unique identifier of the hub which the MOS offer relates to. hub_name, Not Null = True. hub_name, Primary Key = False. hub_name, Comment = The name
