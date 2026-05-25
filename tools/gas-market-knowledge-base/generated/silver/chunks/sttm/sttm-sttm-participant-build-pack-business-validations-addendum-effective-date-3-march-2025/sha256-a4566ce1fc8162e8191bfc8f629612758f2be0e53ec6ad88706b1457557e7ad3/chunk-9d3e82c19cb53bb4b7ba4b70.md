---
{
  "chunk_id": "chunk-9d3e82c19cb53bb4b7ba4b70",
  "chunk_ordinal": 104,
  "chunk_text_sha256": "b226d606c2eae1d63a48223fe51f7e687cf46fd1a74729bec383ba1a8322f677",
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
            "$ref": "#/texts/330"
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
              "b": 297.126220703125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.13885498046875,
              "r": 522.1008911132812,
              "t": 696.8643493652344
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 22
          }
        ],
        "self_ref": "#/tables/28"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3/chunk-9d3e82c19cb53bb4b7ba4b70.md",
  "heading_path": [
    "2.5. Contingency Gas Bids and Offers"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3/chunk-9d3e82c19cb53bb4b7ba4b70.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3.md"
}
---

Table 17 Contingency Gas Bid/Offer Field Validations
commencementdate, Validation Name = Date range validation.. commencementdate, Event Code = 4004. commencementdate, Description = Commencement date must be less than or equal to the termination date of the record.. commencementdate, Validation Name = Schedule cut off validation.. commencementdate, Event Code = 4702, 4703. commencementdate, Description = The transaction must be submitted by no later than 6pm EST on the gas date before the Commencement date.. facilityid, Validation Name = Facility validation. facilityid, Event Code = 4700. facilityid, Description = Contingency Gas Bids and Offers must be submitted against valid facilities. Contingency Gas Bids and Offers intended to be applied at the hub must be submitted against a specific STTM distribution system/deemed STTM distribution system when the hub is comprised of multiple STTM distribution systems/deemed STTM distribution systems. 'NETBRI1' must not be used for the submission of Contingency Gas Bids and Offers.. step(n)price, Validation Name = Step Price Validation. step(n)price, Event Code = 4713,4714,4715,4716. step(n)price, Description = CG
