---
{
  "chunk_id": "chunk-3f54daacb49463ab7180ce62",
  "chunk_ordinal": 346,
  "chunk_text_sha256": "a7e3ecafe59da41e015889486f8933916ea9460aa9bac35c4c3513b13665370f",
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
              "b": 75.2181396484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.36595916748047,
              "r": 527.2260131835938,
              "t": 632.8666839599609
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 89
          }
        ],
        "self_ref": "#/tables/98"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md",
    "source_manifest_line_number": 12,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-bulletin-board-gbb/procedures-policies-and-guides/procedures-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/amendments-to-gbb-procedures-for-renewable-gas/decision/bb-data-submission-guide-v21.pdf?rev=1890be0ffbbe470d9694e56288a8df59&sc_lang=en"
  },
  "content_sha256": "279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999",
  "corpus": "gbb",
  "document_family": "gbb__bb-data-submission-guide",
  "document_family_id": "gbb__bb-data-submission-guide",
  "document_identity": "gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999",
  "document_title": "##### BB Data Submission Guide",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-3f54daacb49463ab7180ce62.md",
  "heading_path": [
    "Appendix C. Validation Error Codes"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-3f54daacb49463ab7180ce62.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

Transaction log description = ToGasDate must not overlap the date range of any other row for the same FacilityId and Outlook Type.. 36, Error type = Date. 36, Transaction log description = FromGasDate and ToGasDate can only be a maximum of one calendar month apart.. 37, Error type = Date. 37, Transaction log description = Gas Date {0:yyyy-MM-dd} can be for either of D, D+1 or D+2.. 105, Error type = Date. 105, Transaction log description = Gas Date is older than a month.. 40, Error type = Identifier. 40, Transaction log description = Facility Id {0} does not exist in the database.. 41, Error type = Identifier. 41, Transaction log description = Participant is not the registered operator of Facility {0}.. 42, Error type = Identifier. 42, Transaction log description = Zone ID {0} does not exist in the database.. 43, Error type = Identifier. 43, Transaction log description = Zone ID {1} is not associated with Facility Id {0}.. 44, Error type = Identifier. 44, Transaction log description = The
