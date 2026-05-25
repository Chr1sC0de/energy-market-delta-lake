---
{
  "chunk_id": "chunk-704efdd463e1e36d9212baab",
  "chunk_ordinal": 170,
  "chunk_text_sha256": "a834b128f16b4e3ccac303fb41edf02bb298dd5450f66ad5a5311cbd4a469add",
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
              "b": 69.20098876953125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.16983795166016,
              "r": 527.48095703125,
              "t": 728.187255859375
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 48
          }
        ],
        "self_ref": "#/tables/57"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "text",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 706.7893873908081,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 484.81348,
              "t": 730.1108629101564
            },
            "charspan": [
              0,
              144
            ],
            "page_no": 49
          }
        ],
        "self_ref": "#/texts/576"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-704efdd463e1e36d9212baab.md",
  "heading_path": [
    "4.15.1. Data elements and fields"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-704efdd463e1e36d9212baab.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

Variable. Price escalation mechanism, Data field name = PriceEscalationMe chanism. Price escalation mechanism, Description = The price escalation mechanism applied over the term of the trade.. Price escalation mechanism, Mandatory = No. Price escalation mechanism, Data type = Varchar(255). Price escalation mechanism, Example / Allowed values = 10% per annum. Cancelled, Data field name = Cancelled. Cancelled, Description = Cancelled Flag. Can be 1, transaction is cancelled or 0, transaction is not cancelled. Cancelled, Mandatory = No. Cancelled, Data type = Bit. Cancelled, Example / Allowed values = 1, 0, TRUE, FALSE
Data submission example is listed in Appendix B for CSV file submissions. Visit AEMO developer portal for HTTP POST request submission examples.
