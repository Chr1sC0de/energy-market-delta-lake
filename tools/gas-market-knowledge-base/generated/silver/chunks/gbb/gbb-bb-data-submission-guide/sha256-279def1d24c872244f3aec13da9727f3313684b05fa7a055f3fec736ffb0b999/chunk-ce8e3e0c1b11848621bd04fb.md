---
{
  "chunk_id": "chunk-ce8e3e0c1b11848621bd04fb",
  "chunk_ordinal": 76,
  "chunk_text_sha256": "170075317cb703507d260e213d672eb0ebe3c5309938f8622ed56ef4dc6c92e3",
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
              "b": 68.63726806640625,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.25897979736328,
              "r": 527.6124267578125,
              "t": 322.33502197265625
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 21
          }
        ],
        "self_ref": "#/tables/20"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-ce8e3e0c1b11848621bd04fb.md",
  "heading_path": [
    "4.2.1. Data elements and fields"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-ce8e3e0c1b11848621bd04fb.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

Facility Id, Data Field Name = FacilityId. Facility Id, Description = A unique AEMO defined Facility identifier.. Facility Id, Mandatory = Yes. Facility Id, Data Type = int. Facility Id, Example/ Allowed Values = 520345. Gas Date, Data Field Name = GasDate. Gas Date, Description = Date of gas day. Any time component supplied will be ignored. The gas day is that applicable under the pipeline contract or market rules.. Gas Date, Mandatory = Yes. Gas Date, Data Type = Datetime. Gas Date, Example/ Allowed Values = 2018-09-23. Actual Quantity, Data Field Name = ActualQuantity. Actual Quantity, Description = The actual quantity of gas that flowed into a BB facility or out of a BB facility, or The actual quantity of gas compressed by the BB compression facility. The actual quantity of gas processed into an LNG Import facility. The actual quantity of gas that can be withdrawn from an LNG Import facility for processing. Actual Quantity, Mandatory = Conditional This field is mandatory where Quality value is 'OK'. Actual Quantity, Data Type = number(18,3). Actual Quantity, Example/ Allowed Values = 32.232 25.2 (if Actual Quantity is
