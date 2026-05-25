---
{
  "chunk_id": "chunk-a60c1a5ceef1e122371ca501",
  "chunk_ordinal": 461,
  "chunk_text_sha256": "763adefd268d8f9da16d3042144c7e9a8aad0ca6d00fe50b305ba41dfcd93f5f",
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-a60c1a5ceef1e122371ca501.md",
  "heading_path": [
    "5.5.25. INT725 - Trading Participant MOS Offer Confirmation"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-a60c1a5ceef1e122371ca501.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

of the hub which the MOS offer relates to. facility_identifier, Not Null = True. facility_identifier, Primary Key = False. facility_identifier, Comment = The unique identifier of the pipeline which the MOS offer relates to. facility_name, Not Null = True. facility_name, Primary Key = False. facility_name, Comment = The name of the pipeline which the MOS offer relates to. stack_type, Not Null = True. stack_type, Primary Key = False. stack_type, Comment = This field is a flag to indicate whether this is an Increase MOS offer or a Decrease MOS offer. Valid values are: • I • D. mos_offer_identifier, Not Null = True. mos_offer_identifier, Primary Key = True. mos_offer_identifier, Comment = The unique identifier of the relevant MOS offer. mos_offer_step_number, Not Null = True. mos_offer_step_number, Primary Key = True. mos_offer_step_number, Comment = The number of the MOS offer step (1 - 10).
