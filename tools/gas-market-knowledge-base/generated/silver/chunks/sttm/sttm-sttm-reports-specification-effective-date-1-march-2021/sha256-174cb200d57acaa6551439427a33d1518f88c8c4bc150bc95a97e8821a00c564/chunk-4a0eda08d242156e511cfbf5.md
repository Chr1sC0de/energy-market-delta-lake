---
{
  "chunk_id": "chunk-4a0eda08d242156e511cfbf5",
  "chunk_ordinal": 304,
  "chunk_text_sha256": "23afff2d90b5855a86931269a2c262b1460c1abe382e830c9a48b3934603a106",
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
              "b": 328.2325439453125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.24964904785156,
              "r": 527.2449951171875,
              "t": 574.3992309570312
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 98
          }
        ],
        "self_ref": "#/tables/96"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-4a0eda08d242156e511cfbf5.md",
  "heading_path": [
    "5.4.33. INT683 - Provisional Used MOS Steps"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-4a0eda08d242156e511cfbf5.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

gas_date, Not Null = True. gas_date, Primary Key = True. gas_date, Comment = Gas date on which the MOS step was used.. hub_identifier, Not Null = True. hub_identifier, Primary Key = False. hub_identifier, Comment = The unique identifier of the hub.. hub_name, Not Null = True. hub_name, Primary Key = False. hub_name, Comment = The name of the hub.. facility_identifier, Not Null = True. facility_identifier, Primary Key = False. facility_identifier, Comment = The unique identifier of the relevant facility.. facility_name, Not Null = True. facility_name, Primary Key = False. facility_name, Comment = The name of the relevant facility.. stack_identifier, Not Null = True. stack_identifier, Primary Key = True. stack_identifier, Comment = The identifier that uniquely identifies the MOS stack.. stack_type, Not Null = True. stack_type, Primary Key = False. stack_type, Comment = Each MOS stack refers to either an
