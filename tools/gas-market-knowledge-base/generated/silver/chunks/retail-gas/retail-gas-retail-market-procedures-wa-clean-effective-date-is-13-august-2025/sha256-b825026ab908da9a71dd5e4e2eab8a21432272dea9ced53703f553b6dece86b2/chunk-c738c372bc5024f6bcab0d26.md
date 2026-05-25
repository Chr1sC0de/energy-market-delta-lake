---
{
  "chunk_id": "chunk-c738c372bc5024f6bcab0d26",
  "chunk_ordinal": 1258,
  "chunk_text_sha256": "5e93e03a8cbd2185f38afa37ac4eadb20ace28dafda297a702ad1c0d1ec50f0f",
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
              "b": 265.2328399057968,
              "coord_origin": "BOTTOMLEFT",
              "l": 153.14,
              "r": 530.6260000000002,
              "t": 331.2259780273438
            },
            "charspan": [
              0,
              343
            ],
            "page_no": 273
          }
        ],
        "self_ref": "#/texts/4908"
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
              "b": 211.83283990579685,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 527.4680000000005,
              "t": 250.1959780273438
            },
            "charspan": [
              0,
              210
            ],
            "page_no": 273
          }
        ],
        "self_ref": "#/texts/4909"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-retail-market-procedures-wa-clean-effective-date-is-13-august-2025/sha256-b825026ab908da9a71dd5e4e2eab8a21432272dea9ced53703f553b6dece86b2/chunk-c738c372bc5024f6bcab0d26.md",
  "heading_path": [
    "\u00b7 Measured P & T with flow computer"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-retail-market-procedures-wa-clean-effective-date-is-13-august-2025/sha256-b825026ab908da9a71dd5e4e2eab8a21432272dea9ced53703f553b6dece86b2/chunk-c738c372bc5024f6bcab0d26.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-retail-market-procedures-wa-clean-effective-date-is-13-august-2025/sha256-b825026ab908da9a71dd5e4e2eab8a21432272dea9ced53703f553b6dece86b2.md"
}
---

These sites have a single flow computer that records the pulses from the flow meter  pulse head, the output from the pressure  and temperature transmitters and calculates Vcr from this data whilst taking account of compressibility.  The latter is calculated using the measured pressure and temperature inputs and stored gas quality parameters.
Thus only those checks that are feasible for the individual site are applied, i.e. there is no trend check for pressure on a fixed factor site, nor is there a Primary to Secondary checks on single device sites.
