---
{
  "chunk_id": "chunk-1d5cfd047c17f36869dded8d",
  "chunk_ordinal": 18,
  "chunk_text_sha256": "8d18a048c07e2430547974dd1f0faa97278db37ef0779b6bf7565e0414b97f55",
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
              "b": 83.46395874023438,
              "coord_origin": "BOTTOMLEFT",
              "l": 48.88724136352539,
              "r": 766.0391235351562,
              "t": 525.7158660888672
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 8
          }
        ],
        "self_ref": "#/tables/6"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-reports-mapping-reference-guide-gas-bulletin-board-mapping-reference-guide/sha256-5be581c2496b2bb5631a3a8a59e25e186dc603e2642a080cf9c7bd02297ea737/chunk-1d5cfd047c17f36869dded8d.md",
  "heading_path": [
    "1.0 Final September 2018"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-reports-mapping-reference-guide-gas-bulletin-board-mapping-reference-guide/sha256-5be581c2496b2bb5631a3a8a59e25e186dc603e2642a080cf9c7bd02297ea737/chunk-1d5cfd047c17f36869dded8d.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-reports-mapping-reference-guide-gas-bulletin-board-mapping-reference-guide/sha256-5be581c2496b2bb5631a3a8a59e25e186dc603e2642a080cf9c7bd02297ea737.md"
}
---

, From 30/9/2018 = . , What's new/changed = ▪ Supply ▪ TransferIn ▪ TransferOut ▪ Completeness ▪ LastUpdated Deleted fields: ▪ DeliveryQuantity ▪ ReceiptQuantity ▪ Units ▪ ReportDateTime. , Notes/Comments = connection point mapping reference sheet to reconstruct comparable actual flows.. None, From 30/9/2018 = PIPELINE_CONNECTION_FLOW. None, What's new/changed = New report with the following fields: ▪ GasDate ▪ FacilityID ▪ FacilityName ▪ ConnectionPointId ▪ ConnectionPointName ▪ FlowDirection ▪ ActualQuantity ▪ Quality ▪ LastUpdated. None, Notes/Comments = This is the raw data submitted by individual BB Participants and provides flow for each connection point. This report, if aggregated in accordance with the Aggregation Methodology, provides the same data as the Actual Flow and Storage. Reconstruct Actual Flow for historical data comparison If you want to compare actual flow with historical actual data, use the 'PIPELINE_CONNECTION_FLOW' data and the connection point mapping reference sheet provided to reconstruct comparable actual flows.. Forecast Pipeline Flows (INT 923) Forecast Storage Flows (INT 927), From
