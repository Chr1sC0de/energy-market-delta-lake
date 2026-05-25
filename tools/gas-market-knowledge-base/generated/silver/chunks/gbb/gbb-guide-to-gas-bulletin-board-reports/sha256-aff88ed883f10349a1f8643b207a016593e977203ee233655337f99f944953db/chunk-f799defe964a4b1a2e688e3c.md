---
{
  "chunk_id": "chunk-f799defe964a4b1a2e688e3c",
  "chunk_ordinal": 236,
  "chunk_text_sha256": "b583717c7459144b869a610ea5f9e411d449b09f5385ea81cbef6febb8650d84",
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
              "b": 473.5874533864598,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.88,
              "r": 259.01888,
              "t": 482.52085802734376
            },
            "charspan": [
              0,
              48
            ],
            "page_no": 51
          }
        ],
        "self_ref": "#/texts/471"
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
              "b": 377.62908935546875,
              "coord_origin": "BOTTOMLEFT",
              "l": 52.83267593383789,
              "r": 541.9466552734375,
              "t": 464.3590087890625
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 51
          }
        ],
        "self_ref": "#/tables/67"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-f799defe964a4b1a2e688e3c.md",
  "heading_path": [
    "4.19.2 Data report format"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-f799defe964a4b1a2e688e3c.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

The following fields are provided in the report.
PeriodID, Description = Reporting period. PeriodID, Data type = Varchar. PeriodID, Examples = 01-Oct-2022 to 31-Dec-2022. State, Description = State the trade was made. State, Data type = Varchar. State, Examples = NT,QLD,NSW,VIC,SA,TAS. Increase, Description = The sensitivity of 2P Reserves to a 10% increase in underlying gas price assumptions. Increase, Data type = Numeric(18,3). Increase, Examples = 1.234. Decrease, Description = The sensitivity of 2P Reserves to a 10% decrease in underlying gas price assumptions. Decrease, Data type = Numeric(18,3). Decrease, Examples = -1.234
