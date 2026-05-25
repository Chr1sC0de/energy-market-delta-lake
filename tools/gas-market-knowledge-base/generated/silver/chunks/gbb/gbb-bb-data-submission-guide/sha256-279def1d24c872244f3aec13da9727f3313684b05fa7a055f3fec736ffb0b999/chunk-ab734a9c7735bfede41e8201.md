---
{
  "chunk_id": "chunk-ab734a9c7735bfede41e8201",
  "chunk_ordinal": 67,
  "chunk_text_sha256": "8cc1be2da5f55d0821bceeb774d06c55c1a873548c5b982c95e63f5592684be5",
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
              "b": 72.3096923828125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.12350463867188,
              "r": 527.519775390625,
              "t": 381.5113525390625
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 18
          }
        ],
        "self_ref": "#/tables/17"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-ab734a9c7735bfede41e8201.md",
  "heading_path": [
    "4.1.1. Data elements"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-ab734a9c7735bfede41e8201.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

Facility Id, Data field name = FacilityId. Facility Id, Description = A unique AEMO defined Facility identifier.. Facility Id, Mandatory = Yes. Facility Id, Data type = int. Facility Id, Example / Allowed values = 520345. Gas Date, Data field name = GasDate. Gas Date, Description = Date of gas day. Any time component supplied will be ignored. The gas day is that applicable under the pipeline contract or market rules.. Gas Date, Mandatory = Yes. Gas Date, Data type = datetime. Gas Date, Example / Allowed values = 2018-09-23. Capacity Type, Data field name = CapacityType. Capacity Type, Description = Capacity type may be: Storage: Holding capacity in storage for a BB Storage or LNG Import facility, or MDQ: Daily maximum firm capacity under the expected operating conditions.. Capacity Type, Mandatory = Yes. Capacity Type, Data type = varchar( 20). Capacity Type, Example / Allowed values = STORAGE;MD Q. Outlook Quantity, Data field name = OutlookQuantity. Outlook Quantity, Description = Capacity Outlook quantity in TJ to three decimal places. Three decimal places is not required if the value has trailing zeros after the decimal
