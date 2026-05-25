---
{
  "chunk_id": "chunk-a22c8e31fbc3a3f2933a6f3f",
  "chunk_ordinal": 222,
  "chunk_text_sha256": "37e416c3e64697bf5ce407ec4a4b16fe15f27d314071b90964139ec1c6938e21",
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
              "b": 333.43398291015626,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.4339999999999,
              "t": 357.56598291015627
            },
            "charspan": [
              0,
              127
            ],
            "page_no": 50
          }
        ],
        "self_ref": "#/texts/771"
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
              "b": 313.6339829101562,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 288.89,
              "t": 323.9659829101563
            },
            "charspan": [
              0,
              28
            ],
            "page_no": 50
          }
        ],
        "self_ref": "#/texts/772"
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
              "b": 104.52880859375,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.32972717285156,
              "r": 524.60693359375,
              "t": 287.8848876953125
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 50
          }
        ],
        "self_ref": "#/tables/34"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-a22c8e31fbc3a3f2933a6f3f.md",
  "heading_path": [
    "GRMS Puts Message in Participant Outbox"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-a22c8e31fbc3a3f2933a6f3f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

GRMS will create a message (with .CSV extension - note the case), compress it using zip and place it in a participant's Outbox.
Filename format for file is:
The FRC Market, 1 = Either 'WAGAS' or 'SAGAS'. Fixed Character, 1 = [_]. The Flow Reference, 1 = [0-9A-Z]. Fixed Character, 1 = [_]. GBO ID Initiator, 1 = [0-9A-Z]{1,10} ('REMCO' for all SA M2B) ('WAGMO' for all WAM2B). Fixed Character, 1 = [_]. GBO ID Recipient, 1 = [0-9A-Z]{1,10}. Fixed Character, 1 = [_]
