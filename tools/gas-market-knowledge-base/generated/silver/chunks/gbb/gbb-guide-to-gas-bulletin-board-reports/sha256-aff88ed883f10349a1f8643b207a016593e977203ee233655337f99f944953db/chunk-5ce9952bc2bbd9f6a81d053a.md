---
{
  "chunk_id": "chunk-5ce9952bc2bbd9f6a81d053a",
  "chunk_ordinal": 250,
  "chunk_text_sha256": "80e587bcf76d2d69d6e65f5cd431894a0a8508ec46d5c6e15f0050e01c4c9cbe",
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
              "b": 207.739013671875,
              "coord_origin": "BOTTOMLEFT",
              "l": 52.760894775390625,
              "r": 541.8471069335938,
              "t": 395.6351013183594
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 55
          }
        ],
        "self_ref": "#/tables/74"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-5ce9952bc2bbd9f6a81d053a.md",
  "heading_path": [
    "4.23.2 Data report format"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-5ce9952bc2bbd9f6a81d053a.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

PeriodStartDate, Description = The time period start date. PeriodStartDate, Data type = Date. PeriodStartDate, Examples = 2022-08-01. PeriodEndDate, Description = The time period end date. PeriodEndDate, Data type = Date. PeriodEndDate, Examples = 2022-08-31. State, Description = The state where the transaction occured. State, Data type = Varchar(5). State, Examples = VIC,NSW,QLD,SA,NT,TAS. Quantity(TJ), Description = Total volume of the transactions where trade date is in the reporting period for the given state. Quantity(TJ), Data type = Decimal(18,3). Quantity(TJ), Examples = 10000.555. VolumeWeightedPrice ($), Description = Volume weighted price of transactions where trade date is in the reporting period for the given State. VolumeWeightedPrice ($), Data type = Decimal(18,2). VolumeWeightedPrice ($), Examples = 10.45. TransactionType, Description = Whether the swap is a location swap, time swap or both location and time swap. TransactionType,
