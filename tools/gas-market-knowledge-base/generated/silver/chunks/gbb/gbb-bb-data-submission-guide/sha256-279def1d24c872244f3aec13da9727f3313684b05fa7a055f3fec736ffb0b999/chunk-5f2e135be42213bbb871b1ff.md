---
{
  "chunk_id": "chunk-5f2e135be42213bbb871b1ff",
  "chunk_ordinal": 71,
  "chunk_text_sha256": "859aea621d9c800ae35932a6b9a26e393669b79f42d533119b1bc11206422228",
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
              "b": 111.2305908203125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.26266479492188,
              "r": 527.6892700195312,
              "t": 749.4043579101562
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 19
          }
        ],
        "self_ref": "#/tables/18"
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
              "b": 722.3893873908081,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 483.25348,
              "t": 745.7108629101564
            },
            "charspan": [
              0,
              142
            ],
            "page_no": 20
          }
        ],
        "self_ref": "#/texts/235"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-5f2e135be42213bbb871b1ff.md",
  "heading_path": [
    "4.1.1. Data elements"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-5f2e135be42213bbb871b1ff.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

comments directly related to the quantity and the times, dates, or duration for which those changes in quantities are expected to apply. This would be the 'outage type' and include the equipment involved. Include information on describing the location of transport routes affected.. Description, Mandatory = No. Description, Data type = varchar( 1000). Description, Example / Allowed values = EGP from Longford to Horsley Park, compressor outage. 2 week outage.. Active Flag, Data field name = ActiveFlag. Active Flag, Description = Indicates whether the submission is active or not. Active Flag, Mandatory = No. Active Flag, Data type = Bit. Active Flag, Example / Allowed values = 0,1
Refer Appendix B for data submission examples for CSV file submissions. Visit AEMO developer portal for HTTP POST request submission examples.
