---
{
  "chunk_id": "chunk-a3f8c04367ba6bd26cb1a936",
  "chunk_ordinal": 255,
  "chunk_text_sha256": "6fc6d4aaa1e4d787d6190d7744eafd349d164d66fc804c214270762e90174219",
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
              "b": 163.94671630859375,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.3407211303711,
              "r": 527.22705078125,
              "t": 568.9741516113281
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 82
          }
        ],
        "self_ref": "#/tables/80"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-a3f8c04367ba6bd26cb1a936.md",
  "heading_path": [
    "5.4.18. INT668 - Schedule Log"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-a3f8c04367ba6bd26cb1a936.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

schedule_identifier, Not Null = True. schedule_identifier, Primary Key = True. schedule_identifier, Comment = Unique identity for each schedule.. gas_date, Not Null = True. gas_date, Primary Key = False. gas_date, Comment = The gas date the schedule relates to.. hub_identifier, Not Null = True. hub_identifier, Primary Key = False. hub_identifier, Comment = The identifier of the hub the schedule header relates to.. hub_name, Not Null = True. hub_name, Primary Key = False. hub_name, Comment = The name of the hub.. schedule_type, Not Null = True. schedule_type, Primary Key = False. schedule_type, Comment = The type of the schedule. Valid types include: • ex ante • provisional • ex post • PPOST. schedule_day, Not Null = True. schedule_day, Primary Key = False. schedule_day, Comment = The day the schedule is produced relative to the gas date. Valid days include: • D-1 • D-2 • D-3 • D+1. creation_datetime, Not Null
