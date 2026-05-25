---
{
  "chunk_id": "chunk-a45caeea277cd8afb0a99223",
  "chunk_ordinal": 218,
  "chunk_text_sha256": "048bcef0b88e5658ce1915cc2faab49b5d07efa32a0a1847bdb0fe3f945c325c",
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
              "b": 71.88726806640625,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.25337219238281,
              "r": 527.3303833007812,
              "t": 749.1649932861328
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 60
          }
        ],
        "self_ref": "#/tables/76"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-a45caeea277cd8afb0a99223.md",
  "heading_path": [
    "4.21.1. Data elements and fields"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-a45caeea277cd8afb0a99223.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

, Data Field Name = . , Description = corresponding Demand Zone for a Part 27 retailer. The forecast quantity of gas to be consumed by the Large User Facility. The forecast quantity of gas to be consumed by the LNG Export Project. Value in TJ to three decimal places. Three decimal places are not required if the value has trailing zeros after the decimal place.. , Mandatory = . , Data Type = . , Example/ Allowed Values = 25.2 (if Forecast Quantity is 25.200). Demand Zone Id, Data Field Name = DemandZoneId. Demand Zone Id, Description = A unique AEMO defined demand zone identifier.. Demand Zone Id, Mandatory = Conditional This information is mandatory for Part 27 retailers . Otherwise this must be left blank.. Demand Zone Id, Data Type = Varchar(20). Demand Zone Id, Example/ Allowed Values = SESA-DE-01. Purchases Gas Supply Agreement, Data Field Name = PurchasesGSA. Purchases Gas Supply Agreement, Description = The expected daily gas demand that is to be provided by a gas supply agreement. Value in TJ to three decimal places. Three decimal places are not required if the value has trailing zeros after the decimal place.. Purchases Gas Supply Agreement,
