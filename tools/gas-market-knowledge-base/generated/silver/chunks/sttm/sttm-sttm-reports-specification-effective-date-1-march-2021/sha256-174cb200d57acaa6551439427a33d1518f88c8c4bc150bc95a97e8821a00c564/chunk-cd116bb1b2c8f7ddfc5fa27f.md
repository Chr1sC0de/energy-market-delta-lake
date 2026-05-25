---
{
  "chunk_id": "chunk-cd116bb1b2c8f7ddfc5fa27f",
  "chunk_ordinal": 387,
  "chunk_text_sha256": "f3aa5bc684769bf72d7cfbc07ebea60fba7709a6a952b9b76532d8001017cf06",
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
              "b": 117.47137451171875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.0060043334961,
              "r": 527.2931518554688,
              "t": 749.745735168457
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 127
          }
        ],
        "self_ref": "#/tables/125"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-cd116bb1b2c8f7ddfc5fa27f.md",
  "heading_path": [
    "5.5.12. INT709 - Trading Participant Market Schedule Variation"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-cd116bb1b2c8f7ddfc5fa27f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

increase or (D) decrease of the counter-party's modified market schedule (MMS). • I - Increase • D - Decrease. quantity_gj, Not Null = True. quantity_gj, Primary Key = False. quantity_gj, Comment = The quantity of the market schedule variation.. counter_party_confirmation, Not Null = True. counter_party_confirmation, Primary Key = False. counter_party_confirmation, Comment = This field will have the status of the market schedule variation. Valid statuses include: "Confirmed' if the counter party has confirmed "Rejected" if the counter party has rejected "Submitted" if the counter party has neither confirmed nor rejected "Expired" if the counter party has not confirmed within the time frame required. msv_chargeable, Not Null = True. msv_chargeable, Primary Key = False. msv_chargeable, Comment = This field indicates whether the counter party will be charged (C) a variation charge for this market schedule variation if the counter party confirms or if it will be free (F). • C - Charged. confirmation_datetime, Not Null = False. confirmation_datetime, Primary Key = False. confirmation_datetime,
