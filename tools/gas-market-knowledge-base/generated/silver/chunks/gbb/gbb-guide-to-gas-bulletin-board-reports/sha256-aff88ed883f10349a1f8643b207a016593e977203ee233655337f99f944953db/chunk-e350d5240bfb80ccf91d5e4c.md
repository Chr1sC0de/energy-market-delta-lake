---
{
  "chunk_id": "chunk-e350d5240bfb80ccf91d5e4c",
  "chunk_ordinal": 103,
  "chunk_text_sha256": "3e4a52875794d6b17755de823a8d7df1be6da75b707e72a6baf449033911534b",
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
              "b": 434.3474533864598,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.88,
              "r": 528.0955200000001,
              "t": 458.28085802734375
            },
            "charspan": [
              0,
              146
            ],
            "page_no": 16
          }
        ],
        "self_ref": "#/texts/190"
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
              "b": 413.3474533864598,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.88,
              "r": 491.98888000000005,
              "t": 422.28085802734375
            },
            "charspan": [
              0,
              98
            ],
            "page_no": 16
          }
        ],
        "self_ref": "#/texts/191"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "code",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 85.53884477404245,
              "coord_origin": "BOTTOMLEFT",
              "l": 59.52,
              "r": 378.19,
              "t": 400.1269780273438
            },
            "charspan": [
              0,
              399
            ],
            "page_no": 16
          }
        ],
        "self_ref": "#/texts/192"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "code",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 73.29884477404244,
              "coord_origin": "BOTTOMLEFT",
              "l": 59.52,
              "r": 378.19,
              "t": 744.0969780273439
            },
            "charspan": [
              0,
              937
            ],
            "page_no": 17
          }
        ],
        "self_ref": "#/texts/195"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-e350d5240bfb80ccf91d5e4c.md",
  "heading_path": [
    "4.1.4 Example report"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-e350d5240bfb80ccf91d5e4c.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

The JSON format report displays Facility JSON objects with nested Node JSON objects. Each Node JSON object contains Connection Point JSON objects.
In the following example, a pipeline contains two nodes, one of which contains a connection point.
```
{ "data": { "ActualFlowAndStorageList": [ { "FacilityId": 530038, ' GasDate": "2018-05-12T00:00:00+10:00" "FacilityName": "LNG Storage Dandenong", 'FacilityType': 'STOR', 'State': VIC, "LocationId": 590009, "LocationName": "Gippsland", "Demand": 45, "Supply": 21, "TransferIn": 0, "TransferOut": 0, "HeldInStorage": 2.453, 'CushionGasStorage': 32.232, "LastUpdated": "2018-05-27T14:36:51+10:00" }, {
```
```
