---
{
  "chunk_id": "chunk-a93dc2bfe6ffc41b1486993a",
  "chunk_ordinal": 119,
  "chunk_text_sha256": "c4c0a0440c10d25557b312929718eb575cfd7e7571c78c65b270505254478de6",
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
              "b": 131.84405517578125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.17449951171875,
              "r": 527.497802734375,
              "t": 749.5273971557617
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 34
          }
        ],
        "self_ref": "#/tables/37"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-a93dc2bfe6ffc41b1486993a.md",
  "heading_path": [
    "4.7.1. Data elements and fields"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-a93dc2bfe6ffc41b1486993a.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

, Date field name = . , Description = of gas that can be received and processed into storage on a gas day. Delivery LNG Storage: The flow direction type only used for capacities. For LNG import facilities , it represents the amount of gas withdrawn from storage for processing to a gaseous state on a gas day.. , Mandatory = . , Data type = . , Example / Allowed values = . Capacity Description, Date field name = CapacityDes cription. Capacity Description, Description = Free text to describe the meaning of the capacity number provided, including a description of material factors that impact the capacity number and any other relevant information. If applicable, BB compression facilities must also provide a Capacity Description of other maximum quantities under other standard operating conditions including a description of those conditions including expected inlet and outlet pressures.. Capacity Description, Mandatory = Conditional This information is mandatory for BB pipelines and BB compression facilities . Otherwise leave this blank.. Capacity Description, Data type = varchar(1000). Capacity Description, Example / Allowed values = This transmission capacity is the amount of gas that the Culcairn delivery point is able to withdraw from this pipeline facility. Receipt Location, Date field name = ReceiptLocati on. Receipt Location, Description = The Connection
