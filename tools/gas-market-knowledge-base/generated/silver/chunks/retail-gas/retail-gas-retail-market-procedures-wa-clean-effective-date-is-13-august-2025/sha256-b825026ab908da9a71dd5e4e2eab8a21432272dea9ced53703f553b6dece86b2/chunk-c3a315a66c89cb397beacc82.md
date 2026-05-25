---
{
  "chunk_id": "chunk-c3a315a66c89cb397beacc82",
  "chunk_ordinal": 1267,
  "chunk_text_sha256": "8cf4b70aaff05197241ec6437fbce5e8fb4dbd1eae5c787cd87788e179f68eb2",
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
              "b": 472.88283990579686,
              "coord_origin": "BOTTOMLEFT",
              "l": 124.7,
              "r": 530.3720000000006,
              "t": 497.44597802734376
            },
            "charspan": [
              0,
              90
            ],
            "page_no": 275
          }
        ],
        "self_ref": "#/texts/4941"
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
              "b": 447.0628399057968,
              "coord_origin": "BOTTOMLEFT",
              "l": 140.06,
              "r": 446.206,
              "t": 457.82597802734375
            },
            "charspan": [
              0,
              56
            ],
            "page_no": 275
          }
        ],
        "self_ref": "#/texts/4942"
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
              "b": 414.34410399419465,
              "coord_origin": "BOTTOMLEFT",
              "l": 153.14,
              "r": 501.922,
              "t": 432.7219780273438
            },
            "charspan": [
              0,
              172
            ],
            "page_no": 275
          }
        ],
        "self_ref": "#/texts/4943"
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
              "b": 392.0241039941946,
              "coord_origin": "BOTTOMLEFT",
              "l": 153.14,
              "r": 454.732,
              "t": 400.0819780273438
            },
            "charspan": [
              0,
              69
            ],
            "page_no": 275
          }
        ],
        "self_ref": "#/texts/4944"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-retail-market-procedures-wa-clean-effective-date-is-13-august-2025/sha256-b825026ab908da9a71dd5e4e2eab8a21432272dea9ced53703f553b6dece86b2/chunk-c3a315a66c89cb397beacc82.md",
  "heading_path": [
    "Step 1.  Calculate the mid-date of the estimation period."
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-retail-market-procedures-wa-clean-effective-date-is-13-august-2025/sha256-b825026ab908da9a71dd5e4e2eab8a21432272dea9ced53703f553b6dece86b2/chunk-c3a315a66c89cb397beacc82.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-retail-market-procedures-wa-clean-effective-date-is-13-august-2025/sha256-b825026ab908da9a71dd5e4e2eab8a21432272dea9ced53703f553b6dece86b2.md"
}
---

Get the Start Date for the estimation period based on the most recent verified meter read.
Mid Date = Start Date + ½ (Estimation Date - Start Date)
{Example: If the date that consumption is to be estimated is for 31 Mar 2003 and the most recent verified meter read is 31 Dec 2002 then the mid period date is 14 Feb 2003.
Mid Date = 31 Dec 2002 + ½ (31 Mar 2003 - 31 Dec 2002) = 14 Feb 2003}
