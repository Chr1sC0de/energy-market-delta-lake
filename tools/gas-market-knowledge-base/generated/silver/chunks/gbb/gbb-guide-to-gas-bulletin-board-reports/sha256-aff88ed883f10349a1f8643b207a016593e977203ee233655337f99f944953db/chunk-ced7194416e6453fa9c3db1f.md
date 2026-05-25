---
{
  "chunk_id": "chunk-ced7194416e6453fa9c3db1f",
  "chunk_ordinal": 86,
  "chunk_text_sha256": "6b353e6f1e40443668081640b0835e4870a354e46074422cb976d767f838464b",
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
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/15"
        },
        "prov": [
          {
            "bbox": {
              "b": 466.1474533864598,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.88,
              "r": 517.5718,
              "t": 490.08085802734377
            },
            "charspan": [
              0,
              160
            ],
            "page_no": 12
          }
        ],
        "self_ref": "#/texts/150"
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
              "b": 451.2674533864598,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 398.72752,
              "t": 460.20085802734377
            },
            "charspan": [
              0,
              72
            ],
            "page_no": 12
          }
        ],
        "self_ref": "#/texts/151"
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
              "b": 436.2674533864598,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 391.63888000000003,
              "t": 445.20085802734377
            },
            "charspan": [
              0,
              70
            ],
            "page_no": 12
          }
        ],
        "self_ref": "#/texts/152"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/16"
        },
        "prov": [
          {
            "bbox": {
              "b": 415.6274533864598,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.88,
              "r": 416.59888,
              "t": 424.5608580273438
            },
            "charspan": [
              0,
              73
            ],
            "page_no": 12
          }
        ],
        "self_ref": "#/texts/153"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "caption",
        "parent": {
          "$ref": "#/tables/12"
        },
        "prov": [
          {
            "bbox": {
              "b": 386.37435178479905,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.88,
              "r": 207.17000000000002,
              "t": 394.51997802734377
            },
            "charspan": [
              0,
              35
            ],
            "page_no": 12
          }
        ],
        "self_ref": "#/texts/154"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-ced7194416e6453fa9c3db1f.md",
  "heading_path": [
    "Notes :"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-ced7194416e6453fa9c3db1f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

- Participants can use either service (Internet or MarketNet) to retrieve reports. For example, if you use MarketNet instead of the Internet service, substitute
https://apis.preprod. aemo .com.au:9319/ws/gbb/report/v1/reportName with
https://apis.preprod.marketnet.net.au:9319/ws/gbb/report/v1/reportName
- Report name URLs are case-sensitive. Resource Name is always camelCase.
