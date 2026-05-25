---
{
  "chunk_id": "chunk-a1e67ee7e42998bcfe67a492",
  "chunk_ordinal": 91,
  "chunk_text_sha256": "1baa14442bf372351e577362c740e65921ab1fadfb4c32baf40ca019a99f3e5c",
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
              "b": 551.2274533864597,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.88,
              "r": 532.06956,
              "t": 575.0408580273438
            },
            "charspan": [
              0,
              168
            ],
            "page_no": 13
          }
        ],
        "self_ref": "#/texts/159"
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
              "b": 515.3474533864597,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.88,
              "r": 534.4742000000003,
              "t": 539.1608580273438
            },
            "charspan": [
              0,
              135
            ],
            "page_no": 13
          }
        ],
        "self_ref": "#/texts/160"
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
              "b": 494.3474533864598,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.88,
              "r": 141.74887999999999,
              "t": 503.28085802734375
            },
            "charspan": [
              0,
              16
            ],
            "page_no": 13
          }
        ],
        "self_ref": "#/texts/161"
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
              "b": 473.4674533864598,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.88,
              "r": 469.52727999999996,
              "t": 482.40085802734376
            },
            "charspan": [
              0,
              84
            ],
            "page_no": 13
          }
        ],
        "self_ref": "#/texts/162"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-a1e67ee7e42998bcfe67a492.md",
  "heading_path": [
    "3.5 Filtering requests"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-a1e67ee7e42998bcfe67a492.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

You can filter GET requests by defining filter parameters in the GET request URL. The filter parameters that be used for a BB report are described in BB Report formats.
The following example shows HTTPS POST request to retrieve a Nominations and Forecasts Report filtered by Effective Date and Pipelines.
GET request URL:
http://xxxxxx/NominationsAndForecasts?FromGasDate=2018-07-01&FacilityIds=10000,10001
