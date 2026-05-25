---
{
  "chunk_id": "chunk-efba6aa8df314157e5a6b3c9",
  "chunk_ordinal": 162,
  "chunk_text_sha256": "04fda8b99f73acac3ed5ecf0a550931ff8766671bf78eaa77125d8aa6afc8606",
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
              "b": 118.08905029296875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.31845092773438,
              "r": 527.3973388671875,
              "t": 727.8372802734375
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 46
          }
        ],
        "self_ref": "#/tables/55"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-efba6aa8df314157e5a6b3c9.md",
  "heading_path": [
    "4.14.1. Data elements and fields"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-efba6aa8df314157e5a6b3c9.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

type = Decimal (18,3). Take Or Pay Quantity, Example / Allowed values = 5000.111. Price, Data field name = Price. Price, Description = The transaction price (in $/GJ). Price, Mandatory = Yes. Price, Data type = Decimal (18,2). Price, Example / Allowed values = 10.45. Price Structure, Data field name = PriceStructure. Price Structure, Description = The price structure applied over the term of the trade.. Price Structure, Mandatory = No. Price Structure, Data type = Varchar (255). Price Structure, Example / Allowed values = Varies inline with ABC index. Price Escalation Mechanism, Data field name = PriceEscalatio n Mechanism. Price Escalation Mechanism, Description = The price escalation mechanism applied over the term of the trade.. Price Escalation Mechanism, Mandatory = No. Price Escalation Mechanism, Data type = Varchar (255). Price Escalation Mechanism, Example / Allowed values = 10% per annum. Cancelled, Data field name = Cancelled. Cancelled, Description = Cancelled Flag. Can be 1, transaction is cancelled or 0, transaction is not cancelled. Cancelled, Mandatory = No.
