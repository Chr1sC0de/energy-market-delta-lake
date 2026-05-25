---
{
  "chunk_id": "chunk-3a3c05cb2b2f47d0e797c5bc",
  "chunk_ordinal": 167,
  "chunk_text_sha256": "e81cd315db8e0f48390e91d43bc3cc2ad2546cda06d479db79dab06eb6cf40f5",
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
              "b": 69.20098876953125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.16983795166016,
              "r": 527.48095703125,
              "t": 728.187255859375
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 48
          }
        ],
        "self_ref": "#/tables/57"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-3a3c05cb2b2f47d0e797c5bc.md",
  "heading_path": [
    "4.15.1. Data elements and fields"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-3a3c05cb2b2f47d0e797c5bc.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

Trade Id, Data field name = TradeId. Trade Id, Description = A unique AEMO defined trade identifier.. Trade Id, Mandatory = Conditional This field is mandatory when updating an existing trade.. Trade Id, Data type = Int. Trade Id, Example / Allowed values = 123456. Trade Date, Data field name = TradeDate. Trade Date, Description = Date the trade was made.. Trade Date, Mandatory = Yes. Trade Date, Data type = Date. Trade Date, Example / Allowed values = 2021-03-01. From Gas Date, Data field name = FromGasDate. From Gas Date, Description = Effective start date of the trade. From Gas Date, Mandatory = Yes. From Gas Date, Data type = Date. From Gas Date, Example / Allowed values = 2021-04-01. To Gas Date, Data field name = ToGasDate. To Gas Date, Description = Effective end date of the trade. To Gas Date, Mandatory = Yes. To Gas Date, Data type = Date. To Gas Date, Example / Allowed values = 2021-05-01. Buyer Name, Data field name = BuyerName. Buyer Name, Description = The descriptive name of the buyer. Buyer Name,
