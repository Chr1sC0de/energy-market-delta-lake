---
{
  "chunk_id": "chunk-0ce374814ec3ecaf131a23d7",
  "chunk_ordinal": 176,
  "chunk_text_sha256": "4e7da42ef570cf35f4dbf17dfc8027210bf45e6cd21d9d240ea9aa24e6442226",
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
              "b": 468.14739990234375,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.20154571533203,
              "r": 527.2684936523438,
              "t": 749.3192520141602
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 50
          }
        ],
        "self_ref": "#/tables/60"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-0ce374814ec3ecaf131a23d7.md",
  "heading_path": [
    "4.16.1. Data elements and fields"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-0ce374814ec3ecaf131a23d7.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

transaction. Supply Period End, Mandatory = Yes. Supply Period End, Data type = Datetime. Supply Period End, Example / Allowed values = 2022-05-31. FOB Price, Data field name = FOBPrice. FOB Price, Description = The free on board price for the LNG (in $/GJ). FOB Price, Mandatory = Yes. FOB Price, Data type = Numeric(18,3). FOB Price, Example / Allowed values = 12.321. Price Structure, Data field name = PriceStructure. Price Structure, Description = The price structure applied over the term of the trade.. Price Structure, Mandatory = Yes. Price Structure, Data type = Varchar(255). Price Structure, Example / Allowed values = Variable. Cancelled, Data field name = Cancelled. Cancelled, Description = Cancelled Flag. Can be 1, transaction is cancelled or 0, transaction is not cancelled. Cancelled, Mandatory = No. Cancelled, Data type = Bit. Cancelled, Example / Allowed values = 0,1. Description, Data field name = Description. Description, Description = Free text field. Participants will be inputting their own ID in this field to help match multiple transactions to a trade.
