---
{
  "chunk_id": "chunk-a9d85fb6c6fdec5ed38072a6",
  "chunk_ordinal": 108,
  "chunk_text_sha256": "cfebf72b3bdef13e940079d5c46c7782e7f519c9180ada5951fe2d1bc3b879df",
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
              "b": 71.421630859375,
              "coord_origin": "BOTTOMLEFT",
              "l": 52.58028793334961,
              "r": 542.331787109375,
              "t": 354.36468505859375
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 18
          }
        ],
        "self_ref": "#/tables/20"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md",
    "source_manifest_line_number": 14,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-bulletin-board-gbb/procedures-policies-and-guides/procedures-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/natural_gas_services_bulletin_board/site-content/gbb-documents/guides-and-procedures/guide-to-gas-bulletin-board-reports.pdf?rev=8d79cc57e0fd4faf9f5c92e94b42f86b&sc_lang=en"
  },
  "content_sha256": "aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db",
  "corpus": "gbb",
  "document_family": "gbb__guide-to-gas-bulletin-board-reports",
  "document_family_id": "gbb__guide-to-gas-bulletin-board-reports",
  "document_identity": "gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db",
  "document_title": "##### Guide to Gas Bulletin Board Reports",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-a9d85fb6c6fdec5ed38072a6.md",
  "heading_path": [
    "4.2.2 Data report format"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-a9d85fb6c6fdec5ed38072a6.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

ConnectionPointName, Description = Connection Point name where the connection point is associated to a BB Pipeline or BB compression facility. ConnectionPointName, Data type = varchar(200). ConnectionPointName, Example = Albion Park. ConnectionPointId, Description = A unique AEMO defined connection point identifier.. ConnectionPointId, Data type = int. ConnectionPointId, Example = 1201001. FacilityName, Description = The facility reported.. FacilityName, Data type = varchar(50). FacilityName, Example = Eastern Gas Pipeline. FacilityId, Description = Unique facility identifier.. FacilityId, Data type = int. FacilityId, Example = 520047. FacilityType, Description = The type of facility. FacilityType, Data type = varchar(40). FacilityType, Example = COMPRESSOR, PIPE. OwnerName, Description = The reporting facility owner.. OwnerName, Data type = varchar(50). OwnerName, Example = Jemena Eastern Gas Pipeline (1) Pty Ltd. OwnerId, Description = The reporting facility owner ID. OwnerId, Data type = bigint. OwnerId, Example = 138. OperatorName, Description = Name of the operator for the
