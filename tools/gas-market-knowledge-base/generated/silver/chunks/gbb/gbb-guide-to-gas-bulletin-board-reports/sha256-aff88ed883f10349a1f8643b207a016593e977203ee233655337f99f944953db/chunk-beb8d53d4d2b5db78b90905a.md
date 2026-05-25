---
{
  "chunk_id": "chunk-beb8d53d4d2b5db78b90905a",
  "chunk_ordinal": 131,
  "chunk_text_sha256": "932ffd5dd2cfbb461b4ce9207c2c9f9a3f50d5e9f2f8bd292220203040a4ba7e",
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
              "b": 73.96734619140625,
              "coord_origin": "BOTTOMLEFT",
              "l": 52.4467658996582,
              "r": 542.3056640625,
              "t": 701.7734832763672
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 24
          }
        ],
        "self_ref": "#/tables/29"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-beb8d53d4d2b5db78b90905a.md",
  "heading_path": [
    "4.5.2 Data report format"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-beb8d53d4d2b5db78b90905a.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

FacilityId, Description = Unique plant identifier.. FacilityId, Data type = Int. FacilityId, Example = 520345. FacilityName, Description = Name of the plant.. FacilityName, Data type = varchar(255). FacilityName, Example = Berwyndale to Wallumbilla Pipeline. FromGasDate, Description = Date of gas day. Any time component supplied is ignored. The gas day is applicable under the pipeline contract or market rules.. FromGasDate, Data type = datetime. FromGasDate, Example = 2018-09-23. ToGasDate, Description = Date of gas day. Any time component supplied is ignored. The gas day is that applicable under the pipeline contract or market rules.. ToGasDate, Data type = datetime. ToGasDate, Example = 2018-09-23. CapacityType, Description = Capacity type values can be: STORAGE- Holding capacity in storage; or MDQ -Daily maximum firm capacity under the expected operating conditions.. CapacityType, Data type = varchar(20). CapacityType, Example = STORAGE; MDQ. OutlookQuantity, Description = Capacity outlook quantity in TJ to three decimal places. Three decimal places is not
