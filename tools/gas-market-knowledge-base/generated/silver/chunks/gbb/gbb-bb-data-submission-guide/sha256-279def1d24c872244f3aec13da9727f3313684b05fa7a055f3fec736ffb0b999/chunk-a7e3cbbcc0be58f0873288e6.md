---
{
  "chunk_id": "chunk-a7e3cbbcc0be58f0873288e6",
  "chunk_ordinal": 110,
  "chunk_text_sha256": "427e822bd79b1fefbda739bd57110879a236cf61484189b96d25f7390aa89fcc",
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
              "b": 470.6513977050781,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.00891876220703,
              "r": 527.628662109375,
              "t": 749.638298034668
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 31
          }
        ],
        "self_ref": "#/tables/34"
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
              "b": 426.439387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 484.81348,
              "t": 449.7608629101563
            },
            "charspan": [
              0,
              144
            ],
            "page_no": 31
          }
        ],
        "self_ref": "#/texts/367"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-a7e3cbbcc0be58f0873288e6.md",
  "heading_path": [
    "4.6.2. Data elements and fields"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-a7e3cbbcc0be58f0873288e6.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

, Data field name = . , Description = . , Mandatory = submissions for BB reporting entities for BB facilities (excluding BB large user facilities and LNG processing facilities). , Data type = . , Example / Allowed values = . Recall Description, Data field name = RecallDescrip tion. Recall Description, Description = Describe reasons or provide comments directly related to the recall times including the limitations of recall, and expected capacity that would be available if the facility was recalled.. Recall Description, Mandatory = Conditional. Only mandatory for specific facility types when there is a maintenance activity. Relates to Part 27 submissions for BB reporting entities for BB facilities (excluding BB large user facilities and LNG processing facilities). Recall Description, Data type = Varchar(10 00). Recall Description, Example / Allowed values = Once the facility is offline, partial capacity of 20 TJ day can be restored with 24 hours notice, full capacity with five days notice.
Data submission example is listed in Appendix B for CSV file submissions. Visit AEMO developer portal for HTTP POST request submission examples.
