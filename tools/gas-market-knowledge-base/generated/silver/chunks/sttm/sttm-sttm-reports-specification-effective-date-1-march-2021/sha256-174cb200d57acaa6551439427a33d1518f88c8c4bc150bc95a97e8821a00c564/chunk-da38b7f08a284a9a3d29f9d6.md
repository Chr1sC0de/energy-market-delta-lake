---
{
  "chunk_id": "chunk-da38b7f08a284a9a3d29f9d6",
  "chunk_ordinal": 395,
  "chunk_text_sha256": "fa13fef0966cd59839a0e75beef9f63cc06321c8f9bbda580bde359dafc5f434",
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
              "b": 489.46905517578125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.32568359375,
              "r": 527.2147827148438,
              "t": 749.6366119384766
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 129
          }
        ],
        "self_ref": "#/tables/127"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-da38b7f08a284a9a3d29f9d6.md",
  "heading_path": [
    "5.5.13. INT710 - Trading Participant Settlement Amounts"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-da38b7f08a284a9a3d29f9d6.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

charge_payment_amt_gst_ex, Comment = The monetary value of the charge / payment excluding GST. This value is positive if it is a charge payable TO AEMO, and negative if it is a payment payable BY AEMO.. charge_payment_amt_gst_ex,  = The monetary value of the charge / payment excluding GST. This value is positive if it is a charge payable TO AEMO, and negative if it is a payment payable BY AEMO.. gst_component, Not Null = True. gst_component, Primary Key = False. gst_component, Comment = GST component. gst_component,  = GST component. report_datetime, Not Null = True. report_datetime, Primary Key = False. report_datetime, Comment = The date and time the report was generated. report_datetime,  = The date and time the report was generated
