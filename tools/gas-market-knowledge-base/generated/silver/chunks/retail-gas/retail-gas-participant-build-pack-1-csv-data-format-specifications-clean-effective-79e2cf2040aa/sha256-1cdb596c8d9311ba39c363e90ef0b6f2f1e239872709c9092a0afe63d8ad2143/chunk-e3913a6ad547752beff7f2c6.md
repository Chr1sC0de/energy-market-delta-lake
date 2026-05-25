---
{
  "chunk_id": "chunk-e3913a6ad547752beff7f2c6",
  "chunk_ordinal": 30,
  "chunk_text_sha256": "1e5efe045f2dc732d1a1f44e114403247ee028f294d19afc2b6027fff11f9091",
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
              "b": 252.7674582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 529.7299200000001,
              "t": 275.98086291015625
            },
            "charspan": [
              0,
              171
            ],
            "page_no": 11
          }
        ],
        "self_ref": "#/texts/126"
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
              "b": 211.96745826927236,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 529.5406800000002,
              "t": 235.3008629101563
            },
            "charspan": [
              0,
              144
            ],
            "page_no": 11
          }
        ],
        "self_ref": "#/texts/127"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-1-csv-data-format-specifications-clean-effective-79e2cf2040aa/sha256-1cdb596c8d9311ba39c363e90ef0b6f2f1e239872709c9092a0afe63d8ad2143.md",
    "source_manifest_line_number": 30,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-retail-markets/procedures-policies-and-guides/victoria",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/retail_markets_and_metering/market-procedures/vic/2024/participant-build-pack-1-csv-data-format-specifications-clean.pdf?rev=75d603c0182b4ecbbdfd658be91e2d20&sc_lang=en"
  },
  "content_sha256": "1cdb596c8d9311ba39c363e90ef0b6f2f1e239872709c9092a0afe63d8ad2143",
  "corpus": "retail_gas",
  "document_family": "retail-gas__participant-build-pack-1-csv-data-format-specifications-clean-effective-30-january-2026",
  "document_family_id": "retail-gas__participant-build-pack-1-csv-data-format-specifications-clean-effective-30-january-2026",
  "document_identity": "retail-gas/retail-gas-participant-build-pack-1-csv-data-format-specifications-clean-effective-79e2cf2040aa/sha256-1cdb596c8d9311ba39c363e90ef0b6f2f1e239872709c9092a0afe63d8ad2143",
  "document_title": "##### Participant Build Pack 1 - CSV Data Format Specifications (clean) Effective 30 January 2026",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-1-csv-data-format-specifications-clean-effective-79e2cf2040aa/sha256-1cdb596c8d9311ba39c363e90ef0b6f2f1e239872709c9092a0afe63d8ad2143/chunk-e3913a6ad547752beff7f2c6.md",
  "heading_path": [
    "2.6 Values separator"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-1-csv-data-format-specifications-clean-effective-79e2cf2040aa/sha256-1cdb596c8d9311ba39c363e90ef0b6f2f1e239872709c9092a0afe63d8ad2143/chunk-e3913a6ad547752beff7f2c6.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-1-csv-data-format-specifications-clean-effective-79e2cf2040aa/sha256-1cdb596c8d9311ba39c363e90ef0b6f2f1e239872709c9092a0afe63d8ad2143.md"
}
---

A comma "," is to be used to separate values in CSV file. If a comma shall occur inside a literal, then the entire literal shall be surrounded by double quotes as per 2.4.
No trailing commas are allowed at the end of each line, i.e. the number of value separators in any one row will always be: number_of_values - 1.
