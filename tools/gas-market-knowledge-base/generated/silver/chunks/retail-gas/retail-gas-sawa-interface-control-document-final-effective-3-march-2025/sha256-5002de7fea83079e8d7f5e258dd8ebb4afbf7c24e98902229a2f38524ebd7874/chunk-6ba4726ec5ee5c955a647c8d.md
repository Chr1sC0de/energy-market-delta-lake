---
{
  "chunk_id": "chunk-6ba4726ec5ee5c955a647c8d",
  "chunk_ordinal": 655,
  "chunk_text_sha256": "07dced96e2065d077afda62a9558e29dfa231518f36fae31a9cec72f242d8663",
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
              "b": 117.4010982333096,
              "coord_origin": "BOTTOMLEFT",
              "l": 127.58,
              "r": 243.62,
              "t": 127.74800732421869
            },
            "charspan": [
              0,
              21
            ],
            "page_no": 212
          },
          {
            "bbox": {
              "b": 392.13400732421866,
              "coord_origin": "BOTTOMLEFT",
              "l": 127.58,
              "r": 544.87,
              "t": 402.46600732421865
            },
            "charspan": [
              22,
              102
            ],
            "page_no": 213
          }
        ],
        "self_ref": "#/texts/2258"
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
              "b": 425.44227600097656,
              "coord_origin": "BOTTOMLEFT",
              "l": 75.25785827636719,
              "r": 793.8818969726562,
              "t": 502.00726318359375
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 213
          }
        ],
        "self_ref": "#/tables/144"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md",
    "source_manifest_line_number": 37,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-retail-markets/procedures-policies-and-guides/western-australia",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/retail_markets_and_metering/market-procedures/sa_and_wa/2025/sawa-interface-control-document-v54.pdf?rev=81d1827dbc8d4f78b3277eb532cafa89&sc_lang=en"
  },
  "content_sha256": "5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874",
  "corpus": "retail_gas",
  "document_family": "retail-gas__sawa-interface-control-document-final-effective-3-march-2025",
  "document_family_id": "retail-gas__sawa-interface-control-document-final-effective-3-march-2025",
  "document_identity": "retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874",
  "document_title": "##### SAWA Interface Control Document (Final) Effective 3 March 2025",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-6ba4726ec5ee5c955a647c8d.md",
  "heading_path": [
    "Physical Transaction"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-6ba4726ec5ee5c955a647c8d.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

MeterDataNotification The following describes the CSV contents of the data element CSVConsumptionData.
RecordCount, Format. = integer(10). RecordCount, Usage. = Mandatory. RecordCount, Usage/ Comments. = Account of the number of records include in the CSV payload.. RecordCount, AseXML.Occurs = 1..1. RecordCount, AseXML.Element Path = RecordCount. RecordCount, AseXML.Data Type = xsd:integer totalDig='10'. CSVConsumptionData, Format. = ComplexType. CSVConsumptionData, Usage. = Mandatory. CSVConsumptionData, Usage/ Comments. = The CSV payload.. CSVConsumptionData, AseXML.Occurs = 1..1. CSVConsumptionData, AseXML.Element Path = CSVConsumptionData. CSVConsumptionData, AseXML.Data Type =
