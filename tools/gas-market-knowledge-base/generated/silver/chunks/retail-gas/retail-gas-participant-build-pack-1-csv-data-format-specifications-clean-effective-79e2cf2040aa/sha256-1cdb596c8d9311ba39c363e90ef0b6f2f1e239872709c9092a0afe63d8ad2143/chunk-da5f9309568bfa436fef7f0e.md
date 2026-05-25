---
{
  "chunk_id": "chunk-da5f9309568bfa436fef7f0e",
  "chunk_ordinal": 79,
  "chunk_text_sha256": "21aea7d83202b1249bae974259ae4d5769f54211bf6dd8970d2f2dbf91a70cc8",
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
              "b": 450.54745826927234,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 529.5207600000002,
              "t": 488.28086291015626
            },
            "charspan": [
              0,
              246
            ],
            "page_no": 27
          }
        ],
        "self_ref": "#/texts/287"
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
              "b": 97.0496826171875,
              "coord_origin": "BOTTOMLEFT",
              "l": 71.07711029052734,
              "r": 531.702392578125,
              "t": 436.34332275390625
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 27
          }
        ],
        "self_ref": "#/tables/28"
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
              "b": 715.0493392944336,
              "coord_origin": "BOTTOMLEFT",
              "l": 71.57479095458984,
              "r": 531.5696411132812,
              "t": 749.575080871582
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 28
          }
        ],
        "self_ref": "#/tables/29"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-1-csv-data-format-specifications-clean-effective-79e2cf2040aa/sha256-1cdb596c8d9311ba39c363e90ef0b6f2f1e239872709c9092a0afe63d8ad2143/chunk-da5f9309568bfa436fef7f0e.md",
  "heading_path": [
    "6.10 Meter Range Updates (T333)"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-1-csv-data-format-specifications-clean-effective-79e2cf2040aa/sha256-1cdb596c8d9311ba39c363e90ef0b6f2f1e239872709c9092a0afe63d8ad2143/chunk-da5f9309568bfa436fef7f0e.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-1-csv-data-format-specifications-clean-effective-79e2cf2040aa/sha256-1cdb596c8d9311ba39c363e90ef0b6f2f1e239872709c9092a0afe63d8ad2143.md"
}
---

This transaction is used to notify a Retailer to update Meter Attributes such as 'Number of Dials' for a given Meter Number Range etc. It is initiated by the Distributor and is passed to the Retailer and the frequency is approximately 4 per year.
TRANSACTION 333, 1 = TRANSACTION 333. TRANSACTION 333, 2 = TRANSACTION 333. Heading/Column designator, 1 = Mandatory/ Optional. Heading/Column designator, 2 = Comment. Low_Meter_Range, 1 = M. Low_Meter_Range, 2 = . High_Meter_Range, 1 = M. High_Meter_Range, 2 = . Meter_Type_Size_Code, 1 = M. Meter_Type_Size_Code, 2 = . Number_of_Meter_Dials, 1 = M. Number_of_Meter_Dials, 2 = . Capacity_Group, 1 = M. Capacity_Group, 2 = . Meter_Description, 1 = M. Meter_Description, 2 = . Metric_Imperial_Indicator, 1 = M. Metric_Imperial_Indicator, 2 = . Capacity, 1 = M. Capacity, 2 =
Meter_Attachments, 1 = M
