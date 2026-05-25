---
{
  "chunk_id": "chunk-d4c179b86d1e8aa00ef9a667",
  "chunk_ordinal": 133,
  "chunk_text_sha256": "17e3055d2480db066ec3294d3457fc83e882c3733b0fc1d2741af504ab1c04d1",
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
        "label": "table",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 107.29229736328125,
              "coord_origin": "BOTTOMLEFT",
              "l": 71.0804443359375,
              "r": 545.5087280273438,
              "t": 749.6057891845703
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 48
          }
        ],
        "self_ref": "#/tables/50"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-1-csv-data-format-specifications-clean-effective-79e2cf2040aa/sha256-1cdb596c8d9311ba39c363e90ef0b6f2f1e239872709c9092a0afe63d8ad2143/chunk-d4c179b86d1e8aa00ef9a667.md",
  "heading_path": [
    "7. DATA DICTIONARY"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-1-csv-data-format-specifications-clean-effective-79e2cf2040aa/sha256-1cdb596c8d9311ba39c363e90ef0b6f2f1e239872709c9092a0afe63d8ad2143/chunk-d4c179b86d1e8aa00ef9a667.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-1-csv-data-format-specifications-clean-effective-79e2cf2040aa/sha256-1cdb596c8d9311ba39c363e90ef0b6f2f1e239872709c9092a0afe63d8ad2143.md"
}
---

FORMAT = Date. Date_of_Future_Read_N, LENGTH / DECIMAL PLACES = 10. Date_of_Future_Read_N, ALLOWED VALUES / COMMENTS = ccyy-MM-dd Note, suffix "N" must be replaced with the future date ordinal. Date_Updated, ATTRIBUTE / FORMAT = Date. Date_Updated, LENGTH / DECIMAL PLACES = 10. Date_Updated, ALLOWED VALUES / COMMENTS = ccyy-MM-dd. Distribution_Tariff, ATTRIBUTE / FORMAT = String. Distribution_Tariff, LENGTH / DECIMAL PLACES = 1. Distribution_Tariff, ALLOWED VALUES / COMMENTS = "V" = Volume "D" = Demand. Duration_of_Outage, ATTRIBUTE / FORMAT = Numeric. Duration_of_Outage, LENGTH / DECIMAL PLACES = 2,0. Duration_of_Outage, ALLOWED VALUES / COMMENTS = . Email_Address, ATTRIBUTE / FORMAT = String. Email_Address, LENGTH / DECIMAL PLACES = 100. Email_Address, ALLOWED VALUES / COMMENTS = . End_Date, ATTRIBUTE / FORMAT = Date. End_Date, LENGTH / DECIMAL PLACES = 10. End_Date, ALLOWED VALUES / COMMENTS = ccyy-MM-dd.
