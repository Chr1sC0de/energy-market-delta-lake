---
{
  "chunk_id": "chunk-f0a0f334ddb36502bae8bc6b",
  "chunk_ordinal": 23,
  "chunk_text_sha256": "80378ca9bd4396acd64f8ea9d2e04d4fb803a42246f7dd382be8bfaf097b973a",
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
              "b": 255.43008422851562,
              "coord_origin": "BOTTOMLEFT",
              "l": 48.451087951660156,
              "r": 766.2650756835938,
              "t": 525.6949462890625
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 11
          }
        ],
        "self_ref": "#/tables/9"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-reports-mapping-reference-guide-gas-bulletin-board-mapping-reference-guide/sha256-5be581c2496b2bb5631a3a8a59e25e186dc603e2642a080cf9c7bd02297ea737/chunk-f0a0f334ddb36502bae8bc6b.md",
  "heading_path": [
    "1.0 Final September 2018"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-reports-mapping-reference-guide-gas-bulletin-board-mapping-reference-guide/sha256-5be581c2496b2bb5631a3a8a59e25e186dc603e2642a080cf9c7bd02297ea737/chunk-f0a0f334ddb36502bae8bc6b.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-reports-mapping-reference-guide-gas-bulletin-board-mapping-reference-guide/sha256-5be581c2496b2bb5631a3a8a59e25e186dc603e2642a080cf9c7bd02297ea737.md"
}
---

BB Zones (INT 902), From 30/9/2018. = LOCATIONS. BB Zones (INT 902), What's new/changed.Deleted fields: ▪ TransmissionDirection ▪ ReportDateTime = Modified fields: ▪ ZoneName is now LocationName ▪ ZoneId is now LocationId ▪ ZoneType is now LocationType ▪ ZoneDescription is now Description Added fields: ▪ State Deleted fields: ▪ ReportDateTime. BB Zones (INT 902), Notes/Comments. = Definition of Zone and State In the old report, the ZoneType field has three types: • PZONE - Production Zone • DZONE - Demand Zone • JURI - Jurisdiction In the new report, a new field called State is inserted to: • replace JURI, and; • clarify that the locations are no longer grouped purely by production and demand clusters, but by jurisdictions, and; • provide more flexibility in specifying the content in the LocationName and the Description fields for better accuracy
