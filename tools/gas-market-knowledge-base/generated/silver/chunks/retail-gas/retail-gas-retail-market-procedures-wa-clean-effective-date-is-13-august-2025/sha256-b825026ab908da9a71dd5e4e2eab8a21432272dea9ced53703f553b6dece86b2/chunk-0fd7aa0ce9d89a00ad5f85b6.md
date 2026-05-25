---
{
  "chunk_id": "chunk-0fd7aa0ce9d89a00ad5f85b6",
  "chunk_ordinal": 1272,
  "chunk_text_sha256": "de3eb9b1c2633711f64cd162303751e08b0ad47e11815c46f6d1f7d35a367a8f",
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
              "b": 352.5028399057968,
              "coord_origin": "BOTTOMLEFT",
              "l": 124.7,
              "r": 530.3000000000004,
              "t": 377.06597802734376
            },
            "charspan": [
              0,
              105
            ],
            "page_no": 276
          }
        ],
        "self_ref": "#/texts/4961"
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
              "b": 309.3441039941947,
              "coord_origin": "BOTTOMLEFT",
              "l": 153.14,
              "r": 501.45800000000014,
              "t": 338.1619780273438
            },
            "charspan": [
              0,
              189
            ],
            "page_no": 276
          }
        ],
        "self_ref": "#/texts/4962"
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
              "b": 249.1934814453125,
              "coord_origin": "BOTTOMLEFT",
              "l": 152.60433959960938,
              "r": 527.3851928710938,
              "t": 305.99072265625
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 276
          }
        ],
        "self_ref": "#/tables/90"
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
              "b": 217.15410399419466,
              "coord_origin": "BOTTOMLEFT",
              "l": 153.14,
              "r": 501.4040000000002,
              "t": 235.5319780273437
            },
            "charspan": [
              0,
              95
            ],
            "page_no": 276
          }
        ],
        "self_ref": "#/texts/4963"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-retail-market-procedures-wa-clean-effective-date-is-13-august-2025/sha256-b825026ab908da9a71dd5e4e2eab8a21432272dea9ced53703f553b6dece86b2/chunk-0fd7aa0ce9d89a00ad5f85b6.md",
  "heading_path": [
    "Step 1.  Retrieve the same time last period meter reading interval"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-retail-market-procedures-wa-clean-effective-date-is-13-august-2025/sha256-b825026ab908da9a71dd5e4e2eab8a21432272dea9ced53703f553b6dece86b2/chunk-0fd7aa0ce9d89a00ad5f85b6.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-retail-market-procedures-wa-clean-effective-date-is-13-august-2025/sha256-b825026ab908da9a71dd5e4e2eab8a21432272dea9ced53703f553b6dece86b2.md"
}
---

Retrieve the verified meter read with a meter read date prior to the Start Date of the Estimation period.
{Example: If the date that consumption is to be estimated for is 31 Mar 2003 and the most recent verified meter read is 31 Dec 2002 then search for the next most recent verified meter read.
Estimation Date, 1 = Most recent verified meter read date. Estimation Date, 2 = Next most recent verified meter read. 31 Mar 2003, 1 = 31 Dec 2002. 31 Mar 2003, 2 = 30 Sep 2002
Therefore the same time last period meter reading interval will be 30 Sep 2002 to 31 Dec 2002.}
