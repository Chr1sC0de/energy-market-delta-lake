---
{
  "chunk_id": "chunk-995ad5dc9dc8ccb7185147b0",
  "chunk_ordinal": 174,
  "chunk_text_sha256": "20212e9083f4be0b779d78afff7416035e36baf42f8e85d390da9f84d037887b",
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
              "b": 79.7918701171875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.24571228027344,
              "r": 527.364013671875,
              "t": 208.6759033203125
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 49
          }
        ],
        "self_ref": "#/tables/59"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-995ad5dc9dc8ccb7185147b0.md",
  "heading_path": [
    "4.16.1. Data elements and fields"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-995ad5dc9dc8ccb7185147b0.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

Transaction Id, Data field name = TransactionId. Transaction Id, Description = A unique AEMO defined transaction identifier.. Transaction Id, Mandatory = Conditional This field is mandatory when updating an existing trade.. Transaction Id, Data type = Int. Transaction Id, Example / Allowed values = 123456. Facility Id, Data field name = FacilityId. Facility Id, Description = The LNG export facility at which the LNG is loaded. Facility Id, Mandatory = Yes. Facility Id, Data type = Int. Facility Id, Example / Allowed values = 520001. Trade Date, Data field name = Trade Date. Trade Date, Description = Date the trade was made.. Trade Date, Mandatory = Yes. Trade Date, Data type = Datetime. Trade Date, Example / Allowed values = 2022-04-01
