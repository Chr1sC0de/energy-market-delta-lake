---
{
  "chunk_id": "chunk-70af17f90ce9d23d0ad8457a",
  "chunk_ordinal": 210,
  "chunk_text_sha256": "99125ee41f8a6513a5b6c32a39e1b1adb981cb862eae72421840c939fe78f3cc",
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
              "b": 123.8634033203125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.2086181640625,
              "r": 527.535888671875,
              "t": 749.5653381347656
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 58
          }
        ],
        "self_ref": "#/tables/73"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-70af17f90ce9d23d0ad8457a.md",
  "heading_path": [
    "4.20.1. Data elements and fields"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-70af17f90ce9d23d0ad8457a.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

Capacity From, Data field name = CapacityFrom. Capacity From, Description = The lower estimate of Nameplate Capacity. For LNG import terminals, how much gas can be delivered to a pipeline on a day (TJ/day). For LNG Export terminals, how much gas can be received from a pipeline on a day (TJ/day). For Storage facilities, how much gas it can hold in storage (TJ). For Production facilities, how much gas can be delivered to a pipeline on a day (TJ/day). For a Large User, how much gas can be received from a pipeline on a day (TJ/day). For a pipeline, the maximum amount that can flow through the pipeline in the primary forward haul direction of the pipeline on a day (TJ/day).. Capacity From, Mandatory = Yes. Capacity From, Data type = Numeric(18,3). Capacity From, Example / Allowed values = 500.365. Capacity To, Data field name = CapacityTo. Capacity To, Description = The lower estimate of Nameplate Capacity. For LNG import terminals, how much gas can be delivered to a pipeline on a day (TJ/day). For LNG Export
