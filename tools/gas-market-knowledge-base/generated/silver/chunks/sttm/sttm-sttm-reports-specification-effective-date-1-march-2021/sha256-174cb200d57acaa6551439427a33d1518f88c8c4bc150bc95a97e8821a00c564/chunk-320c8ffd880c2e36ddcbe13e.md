---
{
  "chunk_id": "chunk-320c8ffd880c2e36ddcbe13e",
  "chunk_ordinal": 155,
  "chunk_text_sha256": "09654706e9d21ff5c6e7f289f839448391f086dd8a1c0a145375e99ff0fcc858",
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
              "b": 83.85009765625,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.44937133789062,
              "r": 528.096923828125,
              "t": 508.8413391113281
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 44
          }
        ],
        "self_ref": "#/tables/42"
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
              "b": 626.2958068847656,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.54750061035156,
              "r": 528.1047973632812,
              "t": 749.1320114135742
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 45
          }
        ],
        "self_ref": "#/tables/43"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-320c8ffd880c2e36ddcbe13e.md",
  "heading_path": [
    "5.1.2. INT720A - Active Facility Operator Registered Services"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-320c8ffd880c2e36ddcbe13e.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

crn_end_date, Primary Key = True. crn_end_date, Comment = End date of the Registered Service.. crn_capacity, Not Null = True. crn_capacity, Primary Key = False. crn_capacity, Comment = The capacity limit that applies to the registered service record.
crn_status, Not Null = True. crn_status, Primary Key = True. crn_status, Comment = The status of all registered services in this report will be 'active'. This signifies that the registered_service has been confirmed by the issuer and the registered_service holder has accepted the capacity on its trading right.. last_update_datetime, Not Null = True. last_update_datetime, Primary Key = True. last_update_datetime, Comment = The date & time the records within the report were last updated. report_datetime, Not Null = True. report_datetime, Primary Key = False. report_datetime, Comment = The date and time the report was produced.
