---
{
  "chunk_id": "chunk-7f9ebc767cfd1d75c9a2f0f5",
  "chunk_ordinal": 122,
  "chunk_text_sha256": "de338e992c7971b6f8f05238b2745a9bd55e6e1b0da2b666b39746973a2cd199",
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
              "b": 231.07098388671875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.41261291503906,
              "r": 522.422119140625,
              "t": 749.9311752319336
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 28
          }
        ],
        "self_ref": "#/tables/40"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3/chunk-7f9ebc767cfd1d75c9a2f0f5.md",
  "heading_path": [
    "Table 24 Facility Allocation Transaction Context"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3/chunk-7f9ebc767cfd1d75c9a2f0f5.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3.md"
}
---

Invalid HUB, Event Code = 4634. Invalid HUB, Description = The STTM Hub associated with the Facility Allocation must be valid.. System Error, Event Code = 4635. System Error, Description = System error - Facility Allocation Transaction must be valid.. Invalid MOS Allocation, Event Code = 4644. Invalid MOS Allocation, Description = MOS must only be allocated to a shipper who is a valid MOS provider for the facility and gas day.. Invalid Allocation Quantity, Event Code = 4645. Invalid Allocation Quantity, Description = Total Facility Allocation quantity must not exceed the registered maximum facility hub capacity for the facility.. Aggregate Facility Allocation Mismatch, Event Code = 4653. Aggregate Facility Allocation Mismatch, Description = Facility allocations must sum to STTM withdrawal zone CTM data plus Transmission Connected STTM User (TCSU) allocations for given day and facility where applicable.. Upper Warning Limit, Event Code = 4654. Upper Warning Limit, Description = Total Facility Allocation exceeds the upper warning limit of the Facility. Where: • The upper warning limit is: - 30 day rolling average of the allocation quantity + - 4 standard deviations of those allocation quantities • The allocation quantity used is the sum of the allocation quantities for contracts
