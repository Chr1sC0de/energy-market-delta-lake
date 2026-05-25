---
{
  "chunk_id": "chunk-fec286d978e307ff29ec76da",
  "chunk_ordinal": 125,
  "chunk_text_sha256": "2db6d65880069c0c47d51f841dfe6fcf031d4d2beebce515410824eaf85fb6e2",
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
              "b": 344.0874533864598,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.88,
              "r": 259.01888,
              "t": 353.02085802734376
            },
            "charspan": [
              0,
              48
            ],
            "page_no": 22
          }
        ],
        "self_ref": "#/texts/236"
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
              "b": 229.31658935546875,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.405818939208984,
              "r": 542.017822265625,
              "t": 335.5792541503906
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 22
          }
        ],
        "self_ref": "#/tables/27"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-fec286d978e307ff29ec76da.md",
  "heading_path": [
    "4.4.2 Data report format"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-fec286d978e307ff29ec76da.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

The following fields are provided in the report.
Location Name, Description = Name of the Location.. Location Name, Data type = varchar(1040). Location Name, Example = Sydney (SYD). Location Id, Description = Unique Location identifier.. Location Id, Data type = int. Location Id, Example = 520345. State, Description = Location. State, Data type = char(3). State, Example = NSW. LocationType, Description = Type of location. LocationType, Data type = Varchar(40). LocationType, Example = Head office. Description, Description = Free text description of the Location including boundaries and the basis of measurement.. Description, Data type = varchar(800). Description, Example = Sydney Basin. Last Updated, Description = Date the list of locations was last updated.. Last Updated, Data type = Date. Last Updated, Example = 2018-9-20 16:15:18
