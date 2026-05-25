---
{
  "chunk_id": "chunk-548bf1a412ccbd2eed2fb626",
  "chunk_ordinal": 103,
  "chunk_text_sha256": "d79d845d73ffa86431ded3feefc177d2a3b36f10bb2284040d12f7b3b53954cf",
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
              "b": 68.2490234375,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.284423828125,
              "r": 527.4963989257812,
              "t": 200.798583984375
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 28
          }
        ],
        "self_ref": "#/tables/31"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-548bf1a412ccbd2eed2fb626.md",
  "heading_path": [
    "4.6.2. Data elements and fields"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-548bf1a412ccbd2eed2fb626.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

Facility Id, Data field name = FacilityId. Facility Id, Description = A unique AEMO defined Facility identifier.. Facility Id, Mandatory = Yes. Facility Id, Data type = int. Facility Id, Example / Allowed values = 520345. From Gas Date, Data field name = FromGasDate. From Gas Date, Description = Date of gas day. Any time component will result in submission being rejected. The gas day is applicable under the pipeline contract or market rules.. From Gas Date, Mandatory = Conditional This field can be left blank if all other fields (excluding Facility Id) are also left blank. This clears all. From Gas Date, Data type = datetime. From Gas Date, Example / Allowed values = 2018-09-23
