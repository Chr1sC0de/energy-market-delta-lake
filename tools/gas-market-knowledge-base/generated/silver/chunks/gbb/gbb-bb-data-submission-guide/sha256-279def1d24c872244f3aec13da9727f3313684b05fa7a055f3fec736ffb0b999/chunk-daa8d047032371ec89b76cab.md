---
{
  "chunk_id": "chunk-daa8d047032371ec89b76cab",
  "chunk_ordinal": 171,
  "chunk_text_sha256": "55230dbb9b89f7ec44172b5e65bee941f90fe6563f32a6955e2bb906c6638bcb",
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
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/46"
        },
        "prov": [
          {
            "bbox": {
              "b": 652.6693873908081,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 498.919,
              "t": 661.4708629101564
            },
            "charspan": [
              0,
              85
            ],
            "page_no": 49
          }
        ],
        "self_ref": "#/texts/578"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/46"
        },
        "prov": [
          {
            "bbox": {
              "b": 631.9093873908081,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 337.6667600000002,
              "t": 640.7108629101564
            },
            "charspan": [
              0,
              59
            ],
            "page_no": 49
          }
        ],
        "self_ref": "#/texts/579"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-daa8d047032371ec89b76cab.md",
  "heading_path": [
    "4.15.2. Requirements"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-daa8d047032371ec89b76cab.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

- All fields are mandatory except for TradeId, Cancelled and PriceEscalationMechanism
- If the field Cancelled is omitted, it will default to '0'
