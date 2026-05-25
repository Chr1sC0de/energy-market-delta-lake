---
{
  "chunk_id": "chunk-1947c5ba3bac7b6c527af3d6",
  "chunk_ordinal": 170,
  "chunk_text_sha256": "f8ea629bff86d5a8162a83ebb127eb2a426499a6aafd7f461e3dc05b4ad55f93",
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
        "label": "text",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 184.259387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 528.6822800000001,
              "t": 309.10086291015637
            },
            "charspan": [
              0,
              756
            ],
            "page_no": 41
          }
        ],
        "self_ref": "#/texts/587"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "caption",
        "parent": {
          "$ref": "#/pictures/52"
        },
        "prov": [
          {
            "bbox": {
              "b": 737.9043566676115,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 421.87,
              "t": 746.0499829101562
            },
            "charspan": [
              0,
              70
            ],
            "page_no": 42
          }
        ],
        "self_ref": "#/texts/591"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "caption",
        "parent": {
          "$ref": "#/tables/67"
        },
        "prov": [
          {
            "bbox": {
              "b": 460.55435666761156,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 335.10999999999996,
              "t": 468.6999829101563
            },
            "charspan": [
              0,
              58
            ],
            "page_no": 42
          }
        ],
        "self_ref": "#/texts/624"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3.md",
    "source_manifest_line_number": 41,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/short-term-trading-market-sttm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/amendments-to-sttm-and-retail-market-procedures/decision/sttm-participant-build-pack-business-validations-addendum-v81.pdf?rev=eec7a7dd84b947f7af5164f757b8f62e&sc_lang=en"
  },
  "content_sha256": "a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3",
  "corpus": "sttm",
  "document_family": "sttm__sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025",
  "document_family_id": "sttm__sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025",
  "document_identity": "sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3",
  "document_title": "##### STTM Participant Build Pack Business Validations Addendum Effective date 3 March 2025",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3/chunk-1947c5ba3bac7b6c527af3d6.md",
  "heading_path": [
    "2.12. Deemed STTM Distribution System Allocation"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3/chunk-1947c5ba3bac7b6c527af3d6.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3.md"
}
---

The activity diagram below shows the activity flow that follows a submission of Deemed STTM Distribution System Allocation Data by the Pipeline Operator to the AEMO STTM systems. Upon receipt of the transaction file, the STTM systems will perform primary validation (file name) and provide a Message Acknowledgment back to the submitter indicating that the file is valid or that it is in error. If the file is found to be invalid during primary validation, no further action is taken by the STTM system. If the file is found to be valid during the primary validation, the STTM system will proceed to validate the data within the file and provide a Transaction Acknowledgement back to the submitter indicating whether the file passed data validation or not.
Figure 10 Deemed STTM Distribution System Allocation -Activity Diagram
