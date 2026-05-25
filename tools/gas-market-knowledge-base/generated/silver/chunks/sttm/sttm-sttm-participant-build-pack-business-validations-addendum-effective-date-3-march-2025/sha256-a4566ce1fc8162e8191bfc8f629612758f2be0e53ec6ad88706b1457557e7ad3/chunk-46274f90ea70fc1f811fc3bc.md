---
{
  "chunk_id": "chunk-46274f90ea70fc1f811fc3bc",
  "chunk_ordinal": 177,
  "chunk_text_sha256": "c74fce016a7e7c3d15c18ad10881f11d82ce31773cfe61bc7a1c11dd8072e1dd",
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
        "children": [
          {
            "$ref": "#/texts/633"
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
              "b": 410.2259216308594,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.16316986083984,
              "r": 522.4347534179688,
              "t": 734.2060241699219
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 44
          }
        ],
        "self_ref": "#/tables/71"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3/chunk-46274f90ea70fc1f811fc3bc.md",
  "heading_path": [
    "2.12. Deemed STTM Distribution System Allocation"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3/chunk-46274f90ea70fc1f811fc3bc.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3.md"
}
---

Hub associated with the Distribution System Allocation is invalid.. System Error, Event Code = 4630. System Error, Description = System error - Distribution System Allocation Transaction is not valid.. Multiple Registered Services, Event Code = 4628. Multiple Registered Services, Description = Multiple Registered Distribution Services exist for an STTM User at an STTM Hub for a gas day.. Missing Registered Service, Event Code = 4641. Missing Registered Service, Description = There is no matching Distribution System Service associated with the non zero allocation for the gas day and hub of the allocation. Note : this error refers to the validation of network allocations whereby zero allocation records can be submitted for participants who are not registered or have no capacity in the STTM for that gas day. However the system will not allow non zero allocations for such participants.. Missing Allocation, Event Code = 4642. Missing Allocation, Description = Allocation file for an STTM Hub must contain data for all Distribution System Services on that Distribution System that are active for each gas day for which allocation data is submitted.
