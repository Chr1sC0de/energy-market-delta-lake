---
{
  "chunk_id": "chunk-9223f9f512b2d87bf9cc31cd",
  "chunk_ordinal": 152,
  "chunk_text_sha256": "3ca27f4fa1a93a475c814301e7449f693e85f2c84d1a4f6e4328320bceb2a4d8",
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
              "b": 361.72745338645984,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.88,
              "r": 357.91888,
              "t": 370.6608580273438
            },
            "charspan": [
              0,
              66
            ],
            "page_no": 29
          }
        ],
        "self_ref": "#/texts/319"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/23"
        },
        "prov": [
          {
            "bbox": {
              "b": 340.1274533864598,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.88,
              "r": 113.06888,
              "t": 349.0608580273438
            },
            "charspan": [
              0,
              10
            ],
            "page_no": 29
          }
        ],
        "self_ref": "#/texts/320"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/23"
        },
        "prov": [
          {
            "bbox": {
              "b": 319.36745338645983,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.88,
              "r": 113.06888,
              "t": 328.3008580273438
            },
            "charspan": [
              0,
              13
            ],
            "page_no": 29
          }
        ],
        "self_ref": "#/texts/321"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/23"
        },
        "prov": [
          {
            "bbox": {
              "b": 298.84745338645985,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.88,
              "r": 117.02888,
              "t": 307.7808580273438
            },
            "charspan": [
              0,
              12
            ],
            "page_no": 29
          }
        ],
        "self_ref": "#/texts/322"
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
              "b": 248.08745338645986,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.88,
              "r": 524.5034800000001,
              "t": 286.9008580273437
            },
            "charspan": [
              0,
              245
            ],
            "page_no": 29
          }
        ],
        "self_ref": "#/texts/323"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-9223f9f512b2d87bf9cc31cd.md",
  "heading_path": [
    "4.7.3 Report filters"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-9223f9f512b2d87bf9cc31cd.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

Nomination and Forecasts report in JSON format can be filtered by:
- Gas Date
- FacilityId.
- LocationId
The report output contains the latest submission for that gas day. For requested past dates, this is the day ahead or on-the-day nominations and forecast submission. For future dates, the output is the latest nominations and forecast submission.
