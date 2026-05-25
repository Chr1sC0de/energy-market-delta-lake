---
{
  "chunk_id": "chunk-60a5d8a22ffef24d0bb758c3",
  "chunk_ordinal": 43,
  "chunk_text_sha256": "6c9d26cf734d15089403059a660cd19f249ee4912f52e167833579592afe911f",
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
              "b": 237.04745826927228,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 529.9477600000001,
              "t": 260.38086291015634
            },
            "charspan": [
              0,
              137
            ],
            "page_no": 14
          }
        ],
        "self_ref": "#/texts/184"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-1-csv-data-format-specifications-clean-effective-79e2cf2040aa/sha256-1cdb596c8d9311ba39c363e90ef0b6f2f1e239872709c9092a0afe63d8ad2143/chunk-60a5d8a22ffef24d0bb758c3.md",
  "heading_path": [
    "3.2 End of file marker"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-1-csv-data-format-specifications-clean-effective-79e2cf2040aa/sha256-1cdb596c8d9311ba39c363e90ef0b6f2f1e239872709c9092a0afe63d8ad2143/chunk-60a5d8a22ffef24d0bb758c3.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-1-csv-data-format-specifications-clean-effective-79e2cf2040aa/sha256-1cdb596c8d9311ba39c363e90ef0b6f2f1e239872709c9092a0afe63d8ad2143.md"
}
---

The application that parses CSV shall be able to handle End-Of-File mark (EOF, ASCII decimal code 26) at the end of the file, if present.
