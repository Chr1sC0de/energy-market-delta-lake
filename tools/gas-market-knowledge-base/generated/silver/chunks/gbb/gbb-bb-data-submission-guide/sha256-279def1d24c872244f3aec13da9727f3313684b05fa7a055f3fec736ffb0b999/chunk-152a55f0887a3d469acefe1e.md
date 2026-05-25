---
{
  "chunk_id": "chunk-152a55f0887a3d469acefe1e",
  "chunk_ordinal": 225,
  "chunk_text_sha256": "7c0f6c2120c624d3bfdcaf297cd8afc7b35b3bdc87fc7fd54358842dca1295df",
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
              "b": 113.47723388671875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.23367309570312,
              "r": 527.4367065429688,
              "t": 558.8265075683594
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 62
          }
        ],
        "self_ref": "#/tables/79"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-152a55f0887a3d469acefe1e.md",
  "heading_path": [
    "4.22.1. Data elements and fields"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-152a55f0887a3d469acefe1e.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

Facility Id, Data Field Name = FacilityId. Facility Id, Description = A unique AEMO defined Facility identifier.. Facility Id, Mandatory = Yes. Facility Id, Data Type = int. Facility Id, Example/ Allowed Values = 520345. Gas Date, Data Field Name = GasDate. Gas Date, Description = Date of gas day. Any time component supplied will be ignored. The gas day is that applicable under the pipeline contract or market rules.. Gas Date, Mandatory = Yes. Gas Date, Data Type = Datetime. Gas Date, Example/ Allowed Values = 2018-09-23. Linepack Zone Id, Data Field Name = LinepackZoneId. Linepack Zone Id, Description = A unique AEMO defined linepack zone identifier.. Linepack Zone Id, Mandatory = Conditional. This field is required where LinepackType is Operational, GreenBound, AmberBound or RedBound. If the LinepackType is 'Contracted' then LinepackZoneID = Null. Linepack Zone Id, Data Type = Varchar(20). Linepack Zone Id, Example/ Allowed Values = SESA-LP-01. Linepack Type, Data Field Name = LinepackType. Linepack Type, Description =
