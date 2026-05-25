---
{
  "chunk_id": "chunk-b9d48e4ebf3e4b51a12a83df",
  "chunk_ordinal": 160,
  "chunk_text_sha256": "e6a9c748fddfafc0141316f1851ac896b89d9619f9ad737e109bc7e8f05507bf",
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
              "b": 533.4082641601562,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.04684448242188,
              "r": 528.3792724609375,
              "t": 749.4918975830078
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 47
          }
        ],
        "self_ref": "#/tables/45"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-b9d48e4ebf3e4b51a12a83df.md",
  "heading_path": [
    "5.1.3. INT720B - Facility Operator Registered Services B"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-b9d48e4ebf3e4b51a12a83df.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

crn_status, Not Null = True. crn_status, Primary Key = True. crn_status, Comment = The status of the registered service. Possible statuses include: • "submitted" for services which have not been confirmed by the issuer • "confirmed" for services which have been confirmed by the issuer • "rejected" for services which have been rejected by the issuer • "active" where the registered_service has been confirmed by the issuer and the registered_service holder has accepted the capacity on its trading right. last_update_datetime, Not Null = True. last_update_datetime, Primary Key = True. last_update_datetime, Comment = The date & time the records within the report were last updated. report_datetime, Not Null = True. report_datetime, Primary Key = False. report_datetime, Comment = The date and time the report was produced.
