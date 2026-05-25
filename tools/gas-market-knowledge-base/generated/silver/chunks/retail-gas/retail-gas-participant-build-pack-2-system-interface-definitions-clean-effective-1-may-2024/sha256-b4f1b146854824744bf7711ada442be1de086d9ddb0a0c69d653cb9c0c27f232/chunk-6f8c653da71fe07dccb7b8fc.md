---
{
  "chunk_id": "chunk-6f8c653da71fe07dccb7b8fc",
  "chunk_ordinal": 306,
  "chunk_text_sha256": "f6e573af645e684a4b055437624327083eab9bc0f540b08d75dc14ba6d6346d7",
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
              "b": 421.9250109555206,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.5243999999996,
              "t": 476.8270980273438
            },
            "charspan": [
              0,
              369
            ],
            "page_no": 123
          }
        ],
        "self_ref": "#/texts/1334"
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
              "b": 382.90501095552054,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.4466399999998,
              "t": 407.8270980273438
            },
            "charspan": [
              0,
              117
            ],
            "page_no": 123
          }
        ],
        "self_ref": "#/texts/1335"
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
              "b": 137.83831787109375,
              "coord_origin": "BOTTOMLEFT",
              "l": 74.28787994384766,
              "r": 258.3940124511719,
              "t": 375.056640625
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 123
          }
        ],
        "self_ref": "#/tables/130"
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
              "b": 731.5550109555205,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 482.44912,
              "t": 741.4570980273437
            },
            "charspan": [
              0,
              83
            ],
            "page_no": 124
          }
        ],
        "self_ref": "#/texts/1339"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md",
    "source_manifest_line_number": 31,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-retail-markets/procedures-policies-and-guides/victoria",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/retail_markets_and_metering/market-procedures/vic/2024/participant-build-pack-2--system-interface-definitions-v-36-clean.pdf?rev=0420b92c0a5e4d879175ec3003826d7d&sc_lang=en"
  },
  "content_sha256": "b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232",
  "corpus": "retail_gas",
  "document_family": "retail-gas__participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024",
  "document_family_id": "retail-gas__participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024",
  "document_identity": "retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232",
  "document_title": "##### Participant Build Pack 2 - System Interface Definitions (Clean) Effective 1 May 2024",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-6f8c653da71fe07dccb7b8fc.md",
  "heading_path": [
    "A.3 Decimal Datatypes"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-6f8c653da71fe07dccb7b8fc.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

Enter decimal / numeric data as a string of digits preceded by an optional plus or minus sign and including an optional decimal point. If the value exceeds either the precision or scale specified for the column, the database server may truncate data and return an error message. Exact numeric types with a scale of 0 ( Integer ) - are displayed without a decimal point.
This table shows some valid entries for a datatype of Numeric(5,3) and indicates how these values would be displayed:
12.345, VALUE DISPLAYED = 12.345. +12.345, VALUE DISPLAYED = 12.345. -12.345, VALUE DISPLAYED = -12.345. 12.345000, VALUE DISPLAYED = 12.345. 12.1, VALUE DISPLAYED = 12.100. 12, VALUE DISPLAYED = 12.000. 12.0, VALUE DISPLAYED = 12.000. 0, VALUE DISPLAYED = 0
This table shows some invalid entries for a column with a datatype of Numeric(5,3):
