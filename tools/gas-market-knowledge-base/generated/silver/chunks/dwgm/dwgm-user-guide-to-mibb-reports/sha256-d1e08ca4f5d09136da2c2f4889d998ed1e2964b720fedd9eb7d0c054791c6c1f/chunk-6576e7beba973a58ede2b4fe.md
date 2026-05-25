---
{
  "chunk_id": "chunk-6576e7beba973a58ede2b4fe",
  "chunk_ordinal": 1220,
  "chunk_text_sha256": "97cae3afe844f08bd1720d19705d1065b318a203a5676d2bbbf8a1c6a1efa364",
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
              "b": 320.7337646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 463.8236813100001,
              "t": 329.0250146484375
            },
            "charspan": [
              0,
              110
            ],
            "page_no": 187
          }
        ],
        "self_ref": "#/texts/2935"
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
              "b": 280.2337646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 536.43,
              "t": 311.0250146484375
            },
            "charspan": [
              0,
              337
            ],
            "page_no": 187
          }
        ],
        "self_ref": "#/texts/2936"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/173"
        },
        "prov": [
          {
            "bbox": {
              "b": 261.4837646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 61.515,
              "r": 383.69181660000004,
              "t": 269.7750146484375
            },
            "charspan": [
              0,
              77
            ],
            "page_no": 187
          }
        ],
        "self_ref": "#/texts/2937"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/173"
        },
        "prov": [
          {
            "bbox": {
              "b": 241.9837646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 61.515,
              "r": 234.2520573,
              "t": 250.2750146484375
            },
            "charspan": [
              0,
              43
            ],
            "page_no": 187
          }
        ],
        "self_ref": "#/texts/2938"
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
              "b": 210.4837646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 535.5374999999999,
              "t": 230.0250146484375
            },
            "charspan": [
              0,
              173
            ],
            "page_no": 187
          }
        ],
        "self_ref": "#/texts/2939"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md",
    "source_manifest_line_number": 4,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/declared-wholesale-gas-market-dwgm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/april-2024-amendment-to-user-guide-to-mibb-reports/user-guide-to-mibb-reports.pdf?rev=b5b659bce66a4808b505db05ecb0ca13&sc_lang=en"
  },
  "content_sha256": "d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f",
  "corpus": "dwgm",
  "document_family": "dwgm__user-guide-to-mibb-reports",
  "document_family_id": "dwgm__user-guide-to-mibb-reports",
  "document_identity": "dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f",
  "document_title": "##### User Guide to MIBB Reports",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-6576e7beba973a58ede2b4fe.md",
  "heading_path": [
    "Report purpose"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-6576e7beba973a58ede2b4fe.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

INT-293 MeterFix NAC Report is generated to notify retailers of lost sites prior to receiving any meter reads.
When a MeterFix request is processed there is a possibility that it will fail with a NAC response. This produces an alarm with a 3413 alarm code. Furthermore, there are two types of NACs that can occur, both with the 3413 code. Unfortunately, they can only be differentiated by examining the alarm description. Two descriptions are used:
- l Meter Fix MIRN is or has been processed by existing Retailer Change Request
- l MIRN already exists as a second tier site
The difference is important since only retailers will receive the alarms with the first description and only distributes will receive the alarms with the second description.
