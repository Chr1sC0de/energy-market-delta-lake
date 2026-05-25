---
{
  "chunk_id": "chunk-9ccb6beb6d674d3c9623581c",
  "chunk_ordinal": 88,
  "chunk_text_sha256": "03350ea0bb52ccf7e88df2ef0ad3afe85c9c0018373ec1645d30f0e0fcc1a087",
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
            "$ref": "#/texts/254"
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
              "b": 254.88775634765625,
              "coord_origin": "BOTTOMLEFT",
              "l": 66.93186950683594,
              "r": 522.5293579101562,
              "t": 734.8622665405273
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 17
          }
        ],
        "self_ref": "#/tables/17"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3/chunk-9ccb6beb6d674d3c9623581c.md",
  "heading_path": [
    "2.3. Ex ante bids and offers"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3/chunk-9ccb6beb6d674d3c9623581c.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3.md"
}
---

Table 8 Ex Ante Bid/Offer Field Validations
commencementdate, Validation Name = Date range validation.. commencementdate, Event Code = 4004. commencementdate, Description = Commencement date must be less than or equal to the termination date of the record.. commencementdate, Validation Name = Schedule cut off validation.. commencementdate, Event Code = 4204, 4205 & 4304, 4305 for bid and offer respectively.. commencementdate, Description = The transaction must be submitted by no later than Gas Day Start + 5:30 Hours on the gas date before the Commencement date.. trn, Validation Name = Trading Right Validation. trn, Event Code = 4201 & 4301 for bid and offer respectively.. trn, Description = The Trading Right Number must be that of a Trading Right in the STTM Systems and must be cover ALL of the days covered by the commencement and termination dates (inclusive).. step(n)price, Validation Name = Step Price Validation. step(n)price, Event Code = 4213, 4215, 4212 & 4313,4314,4312 for bid and offer respectively.. step(n)price, Description = Prices ($/GJ) may be entered up to
