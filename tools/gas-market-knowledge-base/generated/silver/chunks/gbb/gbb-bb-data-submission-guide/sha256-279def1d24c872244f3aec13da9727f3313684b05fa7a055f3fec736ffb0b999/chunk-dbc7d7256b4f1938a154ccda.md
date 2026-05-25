---
{
  "chunk_id": "chunk-dbc7d7256b4f1938a154ccda",
  "chunk_ordinal": 345,
  "chunk_text_sha256": "6fb57649c8cc3a0787026a95f5bcd2115be3353f5203d1f3e503185161912a77",
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-dbc7d7256b4f1938a154ccda.md",
  "heading_path": [
    "Appendix C. Validation Error Codes"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-dbc7d7256b4f1938a154ccda.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

TerminationDate {0:yyyy-MM-dd HH:mm:ss} must be later than the EffectiveDate. 28, Error type = Date. 28, Transaction log description = ToGasDate must be equal to or greater than FromGasDate. 29, Error type = Date. 29, Transaction log description = Effective Date {1:yyyy-MM-dd} for connection point {0} is in the past. 30, Error type = Date. 30, Transaction log description = Month {0} provided is not valid. Must be between 1 and 12. 31, Error type = Date. 31, Transaction log description = Year {0} provided is not valid. 32, Error type = Date. 32, Transaction log description = Gas Date {0:yyyy-MM-dd HH:mm:ss} is not a historical date. 33, Error type = Date. 33, Transaction log description = FromGasDate must be equal to or greater than current gas day.. 34, Error type = Date. 34, Transaction log description = FromGasDate must not overlap the date range of any other row for the same FacilityId and Outlook Type.. 35, Error type = Date. 35,
