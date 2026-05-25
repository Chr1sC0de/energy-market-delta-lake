---
{
  "chunk_id": "chunk-f0cca5471daad282128af0ef",
  "chunk_ordinal": 284,
  "chunk_text_sha256": "960fc774f77e7f603a32c2fb37f758d1ceabafa6cf97996398dcc10f97cb6d47",
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
              "b": 699.7387646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 537.87,
              "t": 753.0300146484376
            },
            "charspan": [
              0,
              511
            ],
            "page_no": 50
          }
        ],
        "self_ref": "#/texts/660"
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
              "b": 659.2387646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 541.1924999999999,
              "t": 690.0300146484376
            },
            "charspan": [
              0,
              258
            ],
            "page_no": 50
          }
        ],
        "self_ref": "#/texts/661"
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
              "b": 641.2387646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 350.1255,
              "t": 649.5300146484376
            },
            "charspan": [
              0,
              73
            ],
            "page_no": 50
          }
        ],
        "self_ref": "#/texts/662"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-f0cca5471daad282128af0ef.md",
  "heading_path": [
    "Report purpose"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-f0cca5471daad282128af0ef.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

This report contains information regarding any supply and demand point constraints (SDPCs) that are current in the scheduling processes used in the DTS. These constraints are part of the configuration of the network that can be manually set by the AEMO Schedulers and form one of the inputs to the schedule generation process. This report contains supply point constraints, which selectively constrain injection bids at system injection points where the facility operator has registered multiple supply sources.
Traders can use this information to understand the network-based restrictions that will constrain their ability to offer or withdraw gas in the market on a given day. Note these constraints can be applied intraday and reflect conditions from a point in time.
Also see "INT111 - Supply and Demand Point Constraint (SDPC)" on page 36.
