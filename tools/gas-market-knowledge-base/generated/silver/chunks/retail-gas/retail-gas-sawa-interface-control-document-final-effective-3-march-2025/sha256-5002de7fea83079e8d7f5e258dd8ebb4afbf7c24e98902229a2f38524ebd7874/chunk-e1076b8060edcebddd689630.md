---
{
  "chunk_id": "chunk-e1076b8060edcebddd689630",
  "chunk_ordinal": 581,
  "chunk_text_sha256": "94544ea57daef96433a3eeea68dab43972dbf0425dbeabd808d253a6e85927e9",
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
              "b": 458.88400732421866,
              "coord_origin": "BOTTOMLEFT",
              "l": 184.34,
              "r": 662.74,
              "t": 469.21600732421865
            },
            "charspan": [
              0,
              87
            ],
            "page_no": 192
          }
        ],
        "self_ref": "#/texts/2000"
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
              "b": 430.0840073242187,
              "coord_origin": "BOTTOMLEFT",
              "l": 127.58,
              "r": 750.12,
              "t": 440.4160073242187
            },
            "charspan": [
              0,
              131
            ],
            "page_no": 192
          }
        ],
        "self_ref": "#/texts/2001"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "caption",
        "parent": {
          "$ref": "#/tables/131"
        },
        "prov": [
          {
            "bbox": {
              "b": 410.25400732421866,
              "coord_origin": "BOTTOMLEFT",
              "l": 184.34,
              "r": 274.37,
              "t": 420.58600732421866
            },
            "charspan": [
              0,
              16
            ],
            "page_no": 192
          }
        ],
        "self_ref": "#/texts/2002"
      },
      {
        "children": [
          {
            "$ref": "#/texts/2002"
          }
        ],
        "content_layer": "body",
        "label": "table",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 314.1254577636719,
              "coord_origin": "BOTTOMLEFT",
              "l": 126.37765502929688,
              "r": 419.8592529296875,
              "t": 395.62835693359375
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 192
          }
        ],
        "self_ref": "#/tables/131"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-e1076b8060edcebddd689630.md",
  "heading_path": [
    "8.7.8 Provision of MIRNs transferred to ROLR (SA and WA)"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-e1076b8060edcebddd689630.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

Data Flow Definition: Provision of MIRNs transferred to ROLR (PROV-ROLR-TFR)  (WA Only)
This allows for the identification of a bulk list of MIRN  that have been transferred to a new user as the result of an ROLR event.
Physical Mapping

1, Optionality = MIRN. 1, Optionality = MIRN_CHECKSUM. 1, Optionality = MIRN_STATUS. 1, Optionality = USER_GBO_ID
