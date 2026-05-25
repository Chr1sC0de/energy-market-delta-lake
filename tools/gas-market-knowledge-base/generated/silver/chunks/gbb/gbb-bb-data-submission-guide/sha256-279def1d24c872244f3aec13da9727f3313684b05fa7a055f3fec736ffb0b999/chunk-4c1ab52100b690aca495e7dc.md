---
{
  "chunk_id": "chunk-4c1ab52100b690aca495e7dc",
  "chunk_ordinal": 160,
  "chunk_text_sha256": "ffff3535ea1ac5866382c07053863d2b6498c3e5676945a7543ddcdd763f682e",
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-4c1ab52100b690aca495e7dc.md",
  "heading_path": [
    "4.14.1. Data elements and fields"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-4c1ab52100b690aca495e7dc.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

Name, Mandatory = Yes. Buyer Name, Data type = Varchar (255). Buyer Name, Example / Allowed values = Star Energy. Seller Name, Data field name = SellerName. Seller Name, Description = The descriptive name of the seller. Seller Name, Mandatory = Yes. Seller Name, Data type = Varchar (255). Seller Name, Example / Allowed values = Purple Energy. State, Data field name = State. State, Description = The state where the gas seller must supply the gas. State, Mandatory = Yes. State, Data type = Varchar (5). State, Example / Allowed values = VIC,NSW,QLD,SA ,NT,TAS. Location, Data field name = Location. Location, Description = The location at which the gas seller must supply the gas. Location, Mandatory = Yes. Location, Data type = Varchar (255). Location, Example / Allowed values = Delivered at Horsley Park - 1202003. Transaction Type, Data field name = TransactionTy pe. Transaction Type, Description = The type of gas transaction. Can be one of; supply transaction; location based swap transaction; time based swap transaction; and location and time based swap transaction. Transaction Type,
