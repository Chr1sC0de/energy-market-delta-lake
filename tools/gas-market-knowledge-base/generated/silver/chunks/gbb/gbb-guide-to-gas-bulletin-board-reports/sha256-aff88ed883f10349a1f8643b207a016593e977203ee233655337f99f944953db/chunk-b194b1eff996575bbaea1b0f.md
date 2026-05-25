---
{
  "chunk_id": "chunk-b194b1eff996575bbaea1b0f",
  "chunk_ordinal": 276,
  "chunk_text_sha256": "5cacad96d095c54600bbdf2a3598ab5a544fc96c2a6eb818da31665aaa308522",
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
        "label": "text",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 561.5474533864598,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.88,
              "r": 259.01888,
              "t": 570.4808580273439
            },
            "charspan": [
              0,
              48
            ],
            "page_no": 61
          }
        ],
        "self_ref": "#/texts/588"
      },
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
              "b": 446.9880065917969,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.06909942626953,
              "r": 542.059326171875,
              "t": 552.5157165527344
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 61
          }
        ],
        "self_ref": "#/tables/87"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-b194b1eff996575bbaea1b0f.md",
  "heading_path": [
    "4.29.2 Data report format"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-b194b1eff996575bbaea1b0f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

The following fields are provided in the report.
GasDate, Description = Date of gas day. Timestamps are ignored. The gas day as defined in the pipeline contract or market rules.. GasDate, Data type = Datetime. GasDate, Examples = 2022-05-13 00:00:00. FacilityName, Description = Name of the facility.. FacilityName, Data type = Varchar(100). FacilityName, Examples = Berwyndale to Wallumbilla Pipeline. FacilityId, Description = A unique AEMO defined Facility identifier.. FacilityId, Data type = Int. FacilityId, Examples = 520345. ConnectionPointId, Description = A unique AEMO defined connection point identifier. ConnectionPointId, Data type = Int. ConnectionPointId, Examples = 1201001
