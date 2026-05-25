---
{
  "chunk_id": "chunk-586edaa87ab1d33c73d0d39c",
  "chunk_ordinal": 242,
  "chunk_text_sha256": "4bbc548ec166c5fb0d1f069000877d1b82a6a69aa7ad35686d79f6ab6d0cf9b4",
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
              "b": 289.0396728515625,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.39292907714844,
              "r": 527.2494506835938,
              "t": 570.9369812011719
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 78
          }
        ],
        "self_ref": "#/tables/76"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-586edaa87ab1d33c73d0d39c.md",
  "heading_path": [
    "5.4.14. INT664 - Daily Provisional MOS Allocation Data"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-586edaa87ab1d33c73d0d39c.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

gas_date, Not Null = True. gas_date, Primary Key = True. gas_date, Comment = The gas date.. hub_identifier, Not Null = True. hub_identifier, Primary Key = False. hub_identifier, Comment = The unique identifier of the hub.. hub_name, Not Null = True. hub_name, Primary Key = False. hub_name, Comment = The name of the hub.. facility_identifier, Not Null = True. facility_identifier, Primary Key = True. facility_identifier, Comment = The unique identifier of the relevant facility.. facility_name, Not Null = True. facility_name, Primary Key = False. facility_name, Comment = The name of the relevant facility.. mos_allocated_qty, Not Null = True. mos_allocated_qty, Primary Key = False. mos_allocated_qty, Comment = The total allocated quantity - for the facility - for contracted MOS. A positive quantity indicates an increase in flow to the hub; a negative quantity indicates an increase in flow from the hub.. mos_overrun_qty,
