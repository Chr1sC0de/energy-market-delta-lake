---
{
  "chunk_id": "chunk-2be604a71b8ccf65ece27af1",
  "chunk_ordinal": 402,
  "chunk_text_sha256": "0da95ec2f6427ce7e3d90ba10f476db8e29969538ff544e2e69db275c00abbf4",
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
              "b": 113.54534912109375,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.37496185302734,
              "r": 527.1309204101562,
              "t": 554.3094482421875
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 131
          }
        ],
        "self_ref": "#/tables/129"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-2be604a71b8ccf65ece27af1.md",
  "heading_path": [
    "5.5.15. INT712 - Trading Participant Settlement MOS Allocations"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-2be604a71b8ccf65ece27af1.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

facility_identifier, Comment = The unique identifier of the facility. facility_name, Not Null = True. facility_name, Primary Key = False. facility_name, Comment = The name of the facility. crn, Not Null = False. crn, Primary Key = False. crn, Comment = The contract right number that the pipeline operator has allocated MOS to. Can be null when the record is identifying MOS Stack Step data i.e. is not identifying CRN level MOS data.. quality_type, Not Null = False. quality_type, Primary Key = False. quality_type, Comment = The allocation quality type, reflecting (D) daily, (U) update, (P) preliminary, (F) final and (R) revision and (S) AEMO substituted with ex ante market schedule quantity. Valid values are: • D • U • P • F • R • S. total_mos_gj, Not Null = False. total_mos_gj, Primary Key = False. total_mos_gj, Comment = The total (contracted and overrun) MOS quantity allocated to the CRN. A positive quantity indicates an increase in flow
