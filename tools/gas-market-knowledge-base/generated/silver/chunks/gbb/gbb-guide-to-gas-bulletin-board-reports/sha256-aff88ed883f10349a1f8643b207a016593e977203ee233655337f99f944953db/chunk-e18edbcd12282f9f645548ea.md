---
{
  "chunk_id": "chunk-e18edbcd12282f9f645548ea",
  "chunk_ordinal": 255,
  "chunk_text_sha256": "cc06092b75470a81d6f3cac0ecd7079b1aaabcb0224121b279d6ce7c7f3bf244",
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
              "b": 106.57867431640625,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.629940032958984,
              "r": 542.0232543945312,
              "t": 400.0752258300781
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 56
          }
        ],
        "self_ref": "#/tables/76"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-e18edbcd12282f9f645548ea.md",
  "heading_path": [
    "4.24.2 Data report format"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-e18edbcd12282f9f645548ea.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

TradeId, Description = A unique AEMO defined Transaction Identifier. TradeId, Data type = Int. TradeId, Examples = 123456. VersionDateTime, Description = Time a successful submission is accepted by AEMO systems. VersionDateTime, Data type = Datetime. VersionDateTime, Examples = 2022-08-11. TradeDate, Description = The date the transaction was entered into. TradeDate, Data type = Date. TradeDate, Examples = 2018-03-01. FromGasDate, Description = The start date of the transaction. FromGasDate, Data type = Date. FromGasDate, Examples = 2018-03-10. ToGasDate, Description = The end date of the transaction. ToGasDate, Data type = Date. ToGasDate, Examples = 2018-03-20. FacilityId, Description = The gas storage facility ID for the facility by means of which the service is provided. FacilityId, Data type = Int. FacilityId, Examples = 520001. Priority, Description = The priority given to the service to which the transaction relates. Priority, Data type = Varchar(255). Priority, Examples = Secondary firm. MaximumStorageQuantity, Description = The
