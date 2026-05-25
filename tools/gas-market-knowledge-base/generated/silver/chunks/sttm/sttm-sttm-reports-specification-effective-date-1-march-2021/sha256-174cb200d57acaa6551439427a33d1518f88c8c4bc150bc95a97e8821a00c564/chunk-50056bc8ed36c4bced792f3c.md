---
{
  "chunk_id": "chunk-50056bc8ed36c4bced792f3c",
  "chunk_ordinal": 292,
  "chunk_text_sha256": "b360496273a41e138a801b4527ab84917bc76506ea0ed78cb1f608700bb7fdd5",
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
              "b": 260.22393798828125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.10952758789062,
              "r": 527.1588134765625,
              "t": 599.984375
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 94
          }
        ],
        "self_ref": "#/tables/92"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-50056bc8ed36c4bced792f3c.md",
  "heading_path": [
    "5.4.29. INT679 - Net Market Balance Settlement Amounts"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-50056bc8ed36c4bced792f3c.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

total_deviation_qty, Not Null = True. total_deviation_qty, Primary Key = False. total_deviation_qty, Comment = The total deviation quantity used to allocate surplus/short fall for the settlement period and hubs covered by the settlement run identified by the settlement_run_identifier.. total_withdrawals, Not Null = True. total_withdrawals, Primary Key = False. total_withdrawals, Comment = The total registered service allocations for registered services of the type "From the hub" or "At the hub" summed for the billing period and hubs covered by the settlement run identified by the settlement_run_identifier.. total_variation_charges, Not Null = True. total_variation_charges, Primary Key = False. total_variation_charges, Comment = Total variation charges for the settlement run for the hub.. report_datetime, Not Null = True. report_datetime, Primary Key = False. report_datetime, Comment = The date and time the report was generated.
