---
{
  "chunk_id": "chunk-bc0cfca0bd82b148f0e70b80",
  "chunk_ordinal": 164,
  "chunk_text_sha256": "d2beb2cfbab343f6f8ce9c53e2cd0edeaa4155f371c5115c9a77a2637912d4a3",
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
        "label": "caption",
        "parent": {
          "$ref": "#/tables/60"
        },
        "prov": [
          {
            "bbox": {
              "b": 737.9043566676115,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 376.75,
              "t": 746.0499829101562
            },
            "charspan": [
              0,
              67
            ],
            "page_no": 39
          }
        ],
        "self_ref": "#/texts/547"
      },
      {
        "children": [
          {
            "$ref": "#/texts/547"
          }
        ],
        "content_layer": "body",
        "label": "table",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 581.8018188476562,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.4269027709961,
              "r": 517.8207397460938,
              "t": 733.6927108764648
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 39
          }
        ],
        "self_ref": "#/tables/60"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3/chunk-bc0cfca0bd82b148f0e70b80.md",
  "heading_path": [
    "Table 35 MSV Scenarios"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3/chunk-bc0cfca0bd82b148f0e70b80.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3.md"
}
---

Table 41 Market Schedule Variation Confirmation Transaction Context

Trigger, 1 = A Trading Participant who is a counterparty to a Market Schedule Variation determines they want to confirm (or reject) that Market Schedule Variation as per the Rules.. Rules and Procedures References, 1 = Rule 423. Pre-condition, 1 = The counterparty will have all of the information relating to the submitted Market Schedule Variation including the unique AEMO identifier of the Market Schedule Variation. This is available in the STTM MIS Report INT709.. Post-condition, 1 = Following successful validation, the Market Schedule Variation Confirmation will result in AEMO noting the associated Market Schedule Variation as confirmed (or rejected) and if confirmed that variation will be used in the calculation of settlement and prudential payments and charges for the participants. Specifically, this effects the deviation charges and payments and the variation charges that the submitter and counterparty to the Market Schedule Variation are subject to.
