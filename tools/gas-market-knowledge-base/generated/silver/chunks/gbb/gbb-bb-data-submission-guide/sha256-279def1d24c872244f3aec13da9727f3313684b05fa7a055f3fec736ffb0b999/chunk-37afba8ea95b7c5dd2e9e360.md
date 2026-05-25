---
{
  "chunk_id": "chunk-37afba8ea95b7c5dd2e9e360",
  "chunk_ordinal": 136,
  "chunk_text_sha256": "0478cd218f326077a8cc088ab967bae5461d2018ec312e6b23fcf07123c5fe8a",
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
              "b": 74.38458251953125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.09466552734375,
              "r": 527.6021728515625,
              "t": 749.4729385375977
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 39
          }
        ],
        "self_ref": "#/tables/42"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-37afba8ea95b7c5dd2e9e360.md",
  "heading_path": [
    "4.9.1. Data elements and fields"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-37afba8ea95b7c5dd2e9e360.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

places is not required if the value has trailing zeros after the decimal place.. Outlook Quantity, Mandatory = Yes. Outlook Quantity, Data type = number(18,3). Outlook Quantity, Example / Allowed values = 200.531 190.2 (if the value is 190.200). Flow Direction, Data field name = FlowDirection. Flow Direction, Description = Indicates whether the capacity is for a BB storage facility to inject into or withdraw from a BB pipeline . Flow Direction can be: Receipt: The flow of gas into the BB storage facility , or Delivery: The flow of gas out of the BB storage facility .. Flow Direction, Mandatory = Conditional This field is mandatory for BB storage facilities with MDQ Capacity Type value. Otherwise leave this blank.. Flow Direction, Data type = varchar(20). Flow Direction, Example / Allowed values = RECEIPT; DELIVERY. Capacity Description, Data field name = CapacityDescr iption. Capacity Description, Description = Free text to describe the meaning of the capacity number provided, including a description of material factors that impact the capacity number and any other relevant information.. Capacity Description, Mandatory = Conditional This information is mandatory for BB pipelines and BB compression facilities with a MDQ Capacity
