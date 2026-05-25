---
{
  "chunk_id": "chunk-a6c0ec6a5b444fabdb080733",
  "chunk_ordinal": 147,
  "chunk_text_sha256": "a872a35c5f89516827fc9cf40d3be67338b69ab6d710e4ade7b3ffb19648fcc2",
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
              "b": 481.83709716796875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.14408874511719,
              "r": 527.5050048828125,
              "t": 749.3259582519531
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 43
          }
        ],
        "self_ref": "#/tables/47"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-a6c0ec6a5b444fabdb080733.md",
  "heading_path": [
    "4.10.1. Data elements and fields"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-a6c0ec6a5b444fabdb080733.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

, Data field name = . , Description = . , Mandatory = This information is mandatory for Part 24 facilities; and BB Transportation Service Type = PARK or LOAN.. , Data type = . , Example / Allowed values = . Quantity, Data field name = Quantity. Quantity, Description = The traded maximum daily quantity (MDQ) (GJ/day).. Quantity, Mandatory = Yes. Quantity, Data type = int. Quantity, Example / Allowed values = 240. MHQ, Data field name = MHQ. MHQ, Description = The traded maximum hourly quantity (GJ/hour).. MHQ, Mandatory = Yes. MHQ, Data type = int. MHQ, Example / Allowed values = 10. Price, Data field name = Price. Price, Description = The price of the capacity traded ($/GJ/day).. Price, Mandatory = Yes. Price, Data type = Decimal (18,2). Price, Example / Allowed values = 4.20. Price structure, Data field name = PriceStructure. Price structure, Description = The price structure applied over the term of the trade.. Price structure, Mandatory = No. Price structure, Data type = varchar
