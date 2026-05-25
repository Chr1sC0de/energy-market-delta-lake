---
{
  "chunk_id": "chunk-891b0cedb1db9f5c04540ad6",
  "chunk_ordinal": 164,
  "chunk_text_sha256": "6669a6be80f5ad91e54895084796ce759802aaaaad27fa5c5296c133e954b40c",
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
              "b": 75.62811279296875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.42521667480469,
              "r": 527.3045043945312,
              "t": 546.4179382324219
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 48
          }
        ],
        "self_ref": "#/tables/46"
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
              "b": 682.956298828125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.51763916015625,
              "r": 527.2728881835938,
              "t": 748.9364242553711
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 49
          }
        ],
        "self_ref": "#/tables/47"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-891b0cedb1db9f5c04540ad6.md",
  "heading_path": [
    "5.1.4. INT737 - Facility Hub Capacity and Allocation Data Confirmation"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-891b0cedb1db9f5c04540ad6.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

confirmed quantity of the hub capacity or the pipeline allocation, in GJ. validation_flag, Not Null = True. validation_flag, Primary Key = False. validation_flag, Comment = The confirmation validation flag. Either CH for confirmed warning high quantity or CL for confirmed warning low quantity. last_update_datetime, Not Null = True. last_update_datetime, Primary Key = False. last_update_datetime, Comment = The date and time of confirmation of the quantity
last_update_by, Not Null = True. last_update_by, Primary Key = False. last_update_by, Comment = The logged-in user who performed the confirmation. report_datetime, Not Null = True. report_datetime, Primary Key = False. report_datetime, Comment = The date and time of generation of the report
