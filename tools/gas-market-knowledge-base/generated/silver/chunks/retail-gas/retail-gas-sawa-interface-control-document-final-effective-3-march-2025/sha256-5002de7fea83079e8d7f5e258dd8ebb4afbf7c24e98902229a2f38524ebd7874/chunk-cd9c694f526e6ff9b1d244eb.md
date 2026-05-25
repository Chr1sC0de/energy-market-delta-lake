---
{
  "chunk_id": "chunk-cd9c694f526e6ff9b1d244eb",
  "chunk_ordinal": 672,
  "chunk_text_sha256": "97ef9cc649874a351dc5817f114e9e7d38794973924e58fb1405fca723a44a95",
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
              "b": 326.25400732421866,
              "coord_origin": "BOTTOMLEFT",
              "l": 127.58,
              "r": 774.04,
              "t": 377.9860073242187
            },
            "charspan": [
              0,
              408
            ],
            "page_no": 219
          }
        ],
        "self_ref": "#/texts/2306"
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
              "b": 110.859619140625,
              "coord_origin": "BOTTOMLEFT",
              "l": 126.44833374023438,
              "r": 569.6160278320312,
              "t": 320.8730163574219
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 219
          }
        ],
        "self_ref": "#/tables/148"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-cd9c694f526e6ff9b1d244eb.md",
  "heading_path": [
    "Physical Mapping"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-cd9c694f526e6ff9b1d244eb.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

The  data  for  this  flow  must  be  provided  in  an  automated  electronic  file.  The  appropriate  acknowledgement  holds  all  the  events associated with the processing of the interval meter reading file. There is no message similar to 'BSCMR-RESP' as this is covered by the acknowledgement mechanism. Note that for Interval Meters 'GAS_DAY' means the day to which the hourly consumption data relates.
MIRN, Optionality = 1. MIRN_CHECKSUM, Optionality = 1. GAS_DAY, Optionality = 1. SUB_NETWORK_ID, Optionality = 1. CONSUMPTION_HR01, Optionality = 1. CONSUMPTION_HR02, Optionality = 1. CONSUMPTION_HR03, Optionality = 1. CONSUMPTION_HR04, Optionality = 1. CONSUMPTION_HR05, Optionality = 1. CONSUMPTION_HR06, Optionality = 1. CONSUMPTION_HR07, Optionality = 1. CONSUMPTION_HR08, Optionality = 1
