---
{
  "chunk_id": "chunk-ef3d9a140f6a59e8d7a68f2f",
  "chunk_ordinal": 85,
  "chunk_text_sha256": "e1300729d4933c0d134c7e3fd84024b8f19488f8452faa66652fb402b8367965",
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
              "b": 601.5374533864598,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.88,
              "r": 399.67888000000005,
              "t": 610.4708580273439
            },
            "charspan": [
              0,
              74
            ],
            "page_no": 12
          }
        ],
        "self_ref": "#/texts/146"
      },
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
              "b": 580.5374533864598,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.88,
              "r": 382.39888,
              "t": 589.4708580273439
            },
            "charspan": [
              0,
              71
            ],
            "page_no": 12
          }
        ],
        "self_ref": "#/texts/147"
      },
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
              "b": 523.7474533864597,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.88,
              "r": 520.3167599999998,
              "t": 547.5608580273438
            },
            "charspan": [
              0,
              199
            ],
            "page_no": 12
          }
        ],
        "self_ref": "#/texts/148"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-ef3d9a140f6a59e8d7a68f2f.md",
  "heading_path": [
    "Market Facing MarketNet web service host"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-ef3d9a140f6a59e8d7a68f2f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

https://apis.preprod.marketnet.net.au:9319/ws/gbb/report/v1/{resourceName}
https://apis.prod.marketnet.net.au:9319/ws/gbb/report/v1/{resourceName}
The report name is the name of one of the available reports. All possible ReportName values are listed in Table 2. URLs for listing and retrieving reports are appended to the base URL for the report.
