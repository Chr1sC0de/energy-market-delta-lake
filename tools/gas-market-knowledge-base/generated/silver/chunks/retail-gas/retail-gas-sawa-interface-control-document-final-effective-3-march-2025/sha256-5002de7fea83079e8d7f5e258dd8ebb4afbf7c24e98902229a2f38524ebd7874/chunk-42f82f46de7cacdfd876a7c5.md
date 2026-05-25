---
{
  "chunk_id": "chunk-42f82f46de7cacdfd876a7c5",
  "chunk_ordinal": 182,
  "chunk_text_sha256": "bd663b4dd8d1a82fa38606fe032d9f46bbcdfb6f8ba49629106ef687e12082e0",
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
              "b": 297.55398291015626,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.3739999999998,
              "t": 349.2859829101563
            },
            "charspan": [
              0,
              258
            ],
            "page_no": 39
          }
        ],
        "self_ref": "#/texts/514"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/14"
        },
        "prov": [
          {
            "bbox": {
              "b": 276.7939829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 173.9,
              "r": 433.3,
              "t": 287.12598291015627
            },
            "charspan": [
              0,
              46
            ],
            "page_no": 39
          }
        ],
        "self_ref": "#/texts/515"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/14"
        },
        "prov": [
          {
            "bbox": {
              "b": 228.6439829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 173.9,
              "r": 527.3539999999996,
              "t": 266.5759829101562
            },
            "charspan": [
              0,
              147
            ],
            "page_no": 39
          }
        ],
        "self_ref": "#/texts/516"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/14"
        },
        "prov": [
          {
            "bbox": {
              "b": 194.20398291015636,
              "coord_origin": "BOTTOMLEFT",
              "l": 173.9,
              "r": 527.3179999999999,
              "t": 218.3359829101563
            },
            "charspan": [
              0,
              99
            ],
            "page_no": 39
          }
        ],
        "self_ref": "#/texts/517"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-42f82f46de7cacdfd876a7c5.md",
  "heading_path": [
    "Processing of CATSChangeAlerts"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-42f82f46de7cacdfd876a7c5.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

The  system  will  receive  CATSChangeAlerts  and  forward  them  onto  the Incoming User. See Section 8.1.15 for details of the physical transaction and the  Business  Specification  for  details  of  the  use  of  the  flow.  Current functionality includes
- Accept CATSChangeAlert from the Current User
- The Identification of who is the 'sender' in the CATSChangeAlert  to the Incoming User is supplied in the Alert notification to the Incoming user
- The system only accepts CATSChangeAlerts for transfers but not for error correction transactions.
