---
{
  "chunk_id": "chunk-1b1e6515ed8bb76df2ec2734",
  "chunk_ordinal": 217,
  "chunk_text_sha256": "2a0f00da40a8923f0c1fa790a8f626b8c3c7dd2128893400364a1d2abb1f2d6a",
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
              "b": 84.32769775390625,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.51875305175781,
              "r": 527.438232421875,
              "t": 289.83404541015625
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 59
          }
        ],
        "self_ref": "#/tables/75"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-1b1e6515ed8bb76df2ec2734.md",
  "heading_path": [
    "4.21.1. Data elements and fields"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-1b1e6515ed8bb76df2ec2734.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

Facility Id, Data Field Name = FacilityId. Facility Id, Description = A unique AEMO defined Facility identifier.. Facility Id, Mandatory = Conditional This field is mandatory where the submission is for a BB large user facility or a LNG export project. Facility Id, Data Type = int. Facility Id, Example/ Allowed Values = 520345. Gas Date, Data Field Name = GasDate. Gas Date, Description = Date of gas day. Any time component supplied will be ignored. The gas day is that applicable under the pipeline contract or market rules.. Gas Date, Mandatory = Yes. Gas Date, Data Type = Datetime. Gas Date, Example/ Allowed Values = 2018-09-23. Forecast Quantity, Data Field Name = ForecastQuantity. Forecast Quantity, Description = The forecast quantity of gas to be consumed in the. Forecast Quantity, Mandatory = Yes. Forecast Quantity, Data Type = number(18,3). Forecast Quantity, Example/ Allowed Values = 32.232
