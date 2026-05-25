---
{
  "chunk_id": "chunk-6054d7f8d292eddcc67e48bd",
  "chunk_ordinal": 945,
  "chunk_text_sha256": "316e23a9dad950271e6bf3f9e50910fd55854a06c1a868d5d1a6f1677df76405",
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
              "b": 399.1828399057968,
              "coord_origin": "BOTTOMLEFT",
              "l": 96.384,
              "r": 530.686,
              "t": 437.5459780273438
            },
            "charspan": [
              0,
              181
            ],
            "page_no": 169
          }
        ],
        "self_ref": "#/texts/3077"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "formula",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 350.97354578031315,
              "coord_origin": "BOTTOMLEFT",
              "l": 125.8453505462096,
              "r": 203.31793323961438,
              "t": 385.01132808157104
            },
            "charspan": [
              0,
              15
            ],
            "page_no": 169
          }
        ],
        "self_ref": "#/texts/3078"
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
              "b": 324.3028399057969,
              "coord_origin": "BOTTOMLEFT",
              "l": 124.7,
              "r": 164.036,
              "t": 335.06597802734376
            },
            "charspan": [
              0,
              6
            ],
            "page_no": 169
          }
        ],
        "self_ref": "#/texts/3079"
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
              "b": 150.94989013671875,
              "coord_origin": "BOTTOMLEFT",
              "l": 123.61211395263672,
              "r": 528.7175903320312,
              "t": 310.2645263671875
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 169
          }
        ],
        "self_ref": "#/tables/48"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-retail-market-procedures-wa-clean-effective-date-is-13-august-2025/sha256-b825026ab908da9a71dd5e4e2eab8a21432272dea9ced53703f553b6dece86b2.md",
    "source_manifest_line_number": 36,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-retail-markets/procedures-policies-and-guides/western-australia",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/retail_markets_and_metering/market-procedures/wa/2025/retail-market-procedures-wa-clean.pdf?rev=be10a4bf817447d79a13a62ed8da48e6&sc_lang=en"
  },
  "content_sha256": "b825026ab908da9a71dd5e4e2eab8a21432272dea9ced53703f553b6dece86b2",
  "corpus": "retail_gas",
  "document_family": "retail-gas__retail-market-procedures-wa-clean-effective-date-is-13-august-2025",
  "document_family_id": "retail-gas__retail-market-procedures-wa-clean-effective-date-is-13-august-2025",
  "document_identity": "retail-gas/retail-gas-retail-market-procedures-wa-clean-effective-date-is-13-august-2025/sha256-b825026ab908da9a71dd5e4e2eab8a21432272dea9ced53703f553b6dece86b2",
  "document_title": "##### Retail Market Procedures (WA) (Clean) Effective date is 13 August 2025",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-retail-market-procedures-wa-clean-effective-date-is-13-august-2025/sha256-b825026ab908da9a71dd5e4e2eab8a21432272dea9ced53703f553b6dece86b2/chunk-6054d7f8d292eddcc67e48bd.md",
  "heading_path": [
    "225. Normalisation factor for estimate of basic-metered delivery points withdrawals"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-retail-market-procedures-wa-clean-effective-date-is-13-august-2025/sha256-b825026ab908da9a71dd5e4e2eab8a21432272dea9ced53703f553b6dece86b2/chunk-6054d7f8d292eddcc67e48bd.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-retail-market-procedures-wa-clean-effective-date-is-13-august-2025/sha256-b825026ab908da9a71dd5e4e2eab8a21432272dea9ced53703f553b6dece86b2.md"
}
---

For each sub-network for each gas day D , AEMO must calculate a 'normalisation factor' for the basic-metered delivery points in the sub-network for each historical day i as follows:
<!-- formula-not-decoded -->
where:
NF, 1 = =. NF, 2 = the normalisation factor for the basic-metered delivery points in the sub-network for historical gas day i for gas day D ;. NSL, 1 = =. NSL, 2 = the net system load for the sub-network for historical gas day i for gas day D calculated under clause 223; and. REBW, 1 = =. REBW, 2 = the raw estimated basic-metered withdrawal for each basic-metered delivery point in the sub-network for historical gas day i for gas day D calculated under clause 224.
