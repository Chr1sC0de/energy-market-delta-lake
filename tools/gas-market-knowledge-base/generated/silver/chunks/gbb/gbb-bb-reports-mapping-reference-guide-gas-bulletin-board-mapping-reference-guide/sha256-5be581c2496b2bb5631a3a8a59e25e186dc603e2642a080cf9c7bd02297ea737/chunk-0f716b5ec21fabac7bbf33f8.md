---
{
  "chunk_id": "chunk-0f716b5ec21fabac7bbf33f8",
  "chunk_ordinal": 22,
  "chunk_text_sha256": "1e386e9f7d093fe870c989e96622326ac67248f5e1864a359d4e828c8bfdf940",
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
              "b": 84.64923095703125,
              "coord_origin": "BOTTOMLEFT",
              "l": 48.71575164794922,
              "r": 766.2073974609375,
              "t": 525.5600051879883
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 10
          }
        ],
        "self_ref": "#/tables/8"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-reports-mapping-reference-guide-gas-bulletin-board-mapping-reference-guide/sha256-5be581c2496b2bb5631a3a8a59e25e186dc603e2642a080cf9c7bd02297ea737.md",
    "source_manifest_line_number": 13,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-bulletin-board-gbb/procedures-policies-and-guides/procedures-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/natural_gas_services_bulletin_board/site-content/gbb-documents/guides-and-procedures/gasbb-reports-mapping-reference-guide-v1.pdf?rev=a49a6213530b40a5a54526c35c75cebe"
  },
  "content_sha256": "5be581c2496b2bb5631a3a8a59e25e186dc603e2642a080cf9c7bd02297ea737",
  "corpus": "gbb",
  "document_family": "gbb__bb-reports-mapping-reference-guide-gas-bulletin-board-mapping-reference-guide",
  "document_family_id": "gbb__bb-reports-mapping-reference-guide-gas-bulletin-board-mapping-reference-guide",
  "document_identity": "gbb/gbb-bb-reports-mapping-reference-guide-gas-bulletin-board-mapping-reference-guide/sha256-5be581c2496b2bb5631a3a8a59e25e186dc603e2642a080cf9c7bd02297ea737",
  "document_title": "##### BB Reports Mapping Reference Guide Gas Bulletin Board - Mapping Reference Guide",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-reports-mapping-reference-guide-gas-bulletin-board-mapping-reference-guide/sha256-5be581c2496b2bb5631a3a8a59e25e186dc603e2642a080cf9c7bd02297ea737/chunk-0f716b5ec21fabac7bbf33f8.md",
  "heading_path": [
    "1.0 Final September 2018"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-reports-mapping-reference-guide-gas-bulletin-board-mapping-reference-guide/sha256-5be581c2496b2bb5631a3a8a59e25e186dc603e2642a080cf9c7bd02297ea737/chunk-0f716b5ec21fabac7bbf33f8.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-reports-mapping-reference-guide-gas-bulletin-board-mapping-reference-guide/sha256-5be581c2496b2bb5631a3a8a59e25e186dc603e2642a080cf9c7bd02297ea737.md"
}
---

, From 30/9/2018 = . , What's new/changed = ▪ FromDate is now FromGasDate ▪ ToDate is now ToGasDate ▪ ReceiptPoint is now ReceiptLocation ▪ DeliveryPoint is now DeliveryLocation ▪ DataProviderID is CompanyId ▪ DataProviderName is now CompanyName Deleted fields: ▪ ReportDateTime. , Notes/Comments = . Secondary Pipeline Capacity Trade Summary (INT 914), From 30/9/2018 = SECONDARY_PIPELINE_CAPACITY_TRAD E_SUMMARY. Secondary Pipeline Capacity Trade Summary (INT 914), What's new/changed = Modified fields: ▪ PipelineName is now FacilityName ▪ PipelineId is now FacilityId ▪ FromDate is now FromGasDate ▪ ToDate is now ToGasDate ▪ DataProviderID is CompanyId ▪ DataProviderName is now CompanyName Added fields: ▪ ReceiptLocation ▪ DeliveryLocation. Secondary Pipeline Capacity Trade Summary (INT 914), Notes/Comments = Flow direction The TransmissionDirection field in the old report (FORWARD or REVERSE) has been directly replaced by ReceiptLocation and DeliveryLocation fields in the new report to minimise confusion on the flow directions.
