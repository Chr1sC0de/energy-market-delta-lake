---
{
  "chunk_id": "chunk-419fb293205fcb0acc0b1aab",
  "chunk_ordinal": 177,
  "chunk_text_sha256": "135f6143ff68db417722a53f9de15f505ebcba9e02d411c36593521bb9976a24",
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
              "b": 81.9805908203125,
              "coord_origin": "BOTTOMLEFT",
              "l": 52.60906982421875,
              "r": 541.8364868164062,
              "t": 339.8188781738281
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 35
          }
        ],
        "self_ref": "#/tables/46"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-419fb293205fcb0acc0b1aab.md",
  "heading_path": [
    "4.12.2 Data report format"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-419fb293205fcb0acc0b1aab.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

GasDate, Description = Date of gas day. Timestamps are ignored. The gas day as defined in the pipeline contract or market rules.. GasDate, Data type = Datetime. GasDate, Examples = 2018-02-23. FacilityId, Description = A unique AEMO defined Facility Identifier.. FacilityId, Data type = Int. FacilityId, Examples = 520345. FacilityName, Description = The name of the BB facility.. FacilityName, Data type = varchar(100). FacilityName, Examples = Berwyndale to Wallumbilla Pipeline. CapacityType, Description = Capacity type values can be: STORAGE- Holding capacity in storage; or MDQ -Daily maximum firm capacity under the expected operating conditions.. CapacityType, Data type = varchar(20). CapacityType, Examples = STORAGE; MDQ. CapacityTypeDescription, Description = Description of the Capacity Type. CapacityTypeDescription, Data type = Varchar(800). CapacityTypeDescription, Examples = Daily maximum firm capacity under the expected operating conditions. OutlookQuantity, Description = Capacity outlook quantity to three decimal places. Three decimal places is not required if the value has trailing zeros
