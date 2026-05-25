---
{
  "chunk_id": "chunk-b3e48c6ee7905db549e77ee5",
  "chunk_ordinal": 16,
  "chunk_text_sha256": "135a5ce8f56c3351d7679ae8e1a9be163b580d19225917c96608da9177be2732",
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
              "b": 73.9495849609375,
              "coord_origin": "BOTTOMLEFT",
              "l": 48.76154708862305,
              "r": 766.2001342773438,
              "t": 525.5518417358398
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 7
          }
        ],
        "self_ref": "#/tables/5"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-reports-mapping-reference-guide-gas-bulletin-board-mapping-reference-guide/sha256-5be581c2496b2bb5631a3a8a59e25e186dc603e2642a080cf9c7bd02297ea737/chunk-b3e48c6ee7905db549e77ee5.md",
  "heading_path": [
    "1.0 Final September 2018"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-reports-mapping-reference-guide-gas-bulletin-board-mapping-reference-guide/sha256-5be581c2496b2bb5631a3a8a59e25e186dc603e2642a080cf9c7bd02297ea737/chunk-b3e48c6ee7905db549e77ee5.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-reports-mapping-reference-guide-gas-bulletin-board-mapping-reference-guide/sha256-5be581c2496b2bb5631a3a8a59e25e186dc603e2642a080cf9c7bd02297ea737.md"
}
---

, From 30/9/2018 = . , What's new/changed = ▪ GasDayStartHour is now GasDayStart ▪ ZoneId is now LocationId ▪ Zone is now LocationName Added fields: ▪ FlowDirection ▪ NodeId ▪ StateId ▪ StateName ▪ LastUpdated Deleted fields: ▪ ConnectsToPlantID ▪ ConnectsToPlantName ▪ ReportDateTime. , Notes/Comments = . Actual Flow (INT 924, INT 925) Actual Gas Held in Storage (930), From 30/9/2018 = ACTUAL_FLOW_AND_STORAGE. Actual Flow (INT 924, INT 925) Actual Gas Held in Storage (930), What's new/changed = Modified fields: ▪ PlantName is now FacilityName ▪ PlantId is now FacilityId ▪ ZoneName is now LocationName ▪ ZoneId is now LocationId ▪ ActualHeldQuantity is now HeldinStorage Added fields: ▪ State ▪ Demand. Actual Flow (INT 924, INT 925) Actual Gas Held in Storage (930), Notes/Comments = Receipts and Deliveries In the old reports, the actual flow data is only reported by delivery (gas going out of the facility) and receipt (gas
