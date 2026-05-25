---
{
  "chunk_id": "chunk-a1f55ab92aac30e6ac779676",
  "chunk_ordinal": 91,
  "chunk_text_sha256": "75d923e80b08c779f8c6bf31833915f3a294da8605c9852500c21d9965451296",
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
              "b": 506.0487060546875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.15776062011719,
              "r": 527.4537963867188,
              "t": 727.6211318969727
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 26
          }
        ],
        "self_ref": "#/tables/26"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-a1f55ab92aac30e6ac779676.md",
  "heading_path": [
    "4.4.1. Data elements and fields"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-a1f55ab92aac30e6ac779676.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

Connection Point Id, Data field name = ConnectionPointId. Connection Point Id, Description = A unique AEMO defined connection point identifier.. Connection Point Id, Mandatory = Yes. Connection Point Id, Data type = int. Connection Point Id, Example/ Allowed values = 1201001. Capacity Quantity, Data field name = CapacityQuantity. Capacity Quantity, Description = Standing capacity quantity.. Capacity Quantity, Mandatory = Yes. Capacity Quantity, Data type = number(18,3). Capacity Quantity, Example/ Allowed values = 32.232 25.2 (if the value is 25.200). Effective Date, Data field name = EffectiveDate. Effective Date, Description = Gas day date that corresponding record takes effect. Any time component supplied will be ignored.. Effective Date, Mandatory = Yes. Effective Date, Data type = datetime. Effective Date, Example/ Allowed values = 2018-03-23. Description, Data field name = Description. Description, Description = Free text facility use is restricted to a description for reasons or comments directly related to the capacity quantity or the change in quantity provided in relation to a BB facility and the times, dates, or duration for which those quantities or changes in quantities are expected to apply.. Description,
