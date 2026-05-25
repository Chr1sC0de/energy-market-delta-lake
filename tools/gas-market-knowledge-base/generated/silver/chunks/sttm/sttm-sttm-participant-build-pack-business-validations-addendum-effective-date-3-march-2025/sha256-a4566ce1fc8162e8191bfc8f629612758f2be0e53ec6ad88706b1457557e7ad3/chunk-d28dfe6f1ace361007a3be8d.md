---
{
  "chunk_id": "chunk-d28dfe6f1ace361007a3be8d",
  "chunk_ordinal": 94,
  "chunk_text_sha256": "ec15a056c3a33647eef61f4e9ad9f63348fe820ecd7afa0644e5ae4149b79106",
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
          "$ref": "#/tables/22"
        },
        "prov": [
          {
            "bbox": {
              "b": 737.9043566676115,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 250.49,
              "t": 746.0499829101562
            },
            "charspan": [
              0,
              42
            ],
            "page_no": 19
          }
        ],
        "self_ref": "#/texts/289"
      },
      {
        "children": [
          {
            "$ref": "#/texts/289"
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
              "b": 504.585693359375,
              "coord_origin": "BOTTOMLEFT",
              "l": 66.9933853149414,
              "r": 522.3262939453125,
              "t": 734.1380157470703
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 19
          }
        ],
        "self_ref": "#/tables/22"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3/chunk-d28dfe6f1ace361007a3be8d.md",
  "heading_path": [
    "2.4. Price Taker Bids"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3/chunk-d28dfe6f1ace361007a3be8d.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3.md"
}
---

Table 12 Price Taker Bid Field Validations

gasdate, Validation Name = Gas Date Validation. gasdate, Event Code = 4404, 4405. gasdate, Description = The transaction must be submitted by no later than Gas Day Start + 5:30 Hours on the gas date before the Price Taker Bid gas date.. trn, Validation Name = Trading Right Validation. trn, Event Code = 4402, 4406. trn, Description = The Trading Right Number (TRN) must be that of a valid Trading Right in the STTM Systems and must be valid for the gas date. quantity, Validation Name = Step Quantity Validation. quantity, Event Code = 4407. quantity, Description = Quantity must be greater than or equal to 0. Quantity must not have any decimal places.. quantity, Validation Name = Step Quantity Trading Right Capacity Validation. quantity, Event Code = 4408. quantity, Description = Quantity must not exceed the Trading Right Capacity of the nominated Trading Right (referred to by the TRN in the submission) LESS the maximum step quantity for the most recently submitted ex ante bid for the same gas day and Trading Right.
