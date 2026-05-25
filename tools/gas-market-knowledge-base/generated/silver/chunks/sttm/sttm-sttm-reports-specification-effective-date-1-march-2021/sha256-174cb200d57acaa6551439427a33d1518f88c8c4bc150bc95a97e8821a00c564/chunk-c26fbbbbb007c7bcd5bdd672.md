---
{
  "chunk_id": "chunk-c26fbbbbb007c7bcd5bdd672",
  "chunk_ordinal": 252,
  "chunk_text_sha256": "e1559d636c7af514b78669c418cc3cdea61d6695ae4a0d81daa9da91fb899541",
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
              "b": 272.22601318359375,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.19920349121094,
              "r": 527.1673583984375,
              "t": 613.717529296875
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 81
          }
        ],
        "self_ref": "#/tables/79"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-c26fbbbbb007c7bcd5bdd672.md",
  "heading_path": [
    "5.4.17. INT667 - Market Parameters"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-c26fbbbbb007c7bcd5bdd672.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

effective_from_date, Not Null = True. effective_from_date, Primary Key = True. effective_from_date, Comment = The first gas date the record is effective on.. effective_to_date, Not Null = True. effective_to_date, Primary Key = True. effective_to_date, Comment = The last gas date the record is effective to.. parameter_code, Not Null = True. parameter_code, Primary Key = True. parameter_code, Comment = The code of the parameter; referring respectively to 'Administered Price Cap', 'Market Price Cap', 'Minimum Market Price', 'MOS Cost Cap', 'Cumulative Price Threshold'. Valid values are: • APC • MPC • MMP • MOSCC. parameter_description, Not Null = True. parameter_description, Primary Key = False. parameter_description, Comment = The description of the parameter. Valid values are: • Administered Price Cap • Market Price Cap • Minimum Market Price • Market Operator Service Cost Cap • Cumulative Price Threshold. parameter_value, Not Null = True. parameter_value, Primary Key = False. parameter_value, Comment = The value of the parameter..
