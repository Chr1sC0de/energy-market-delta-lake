---
{
  "chunk_id": "chunk-b4cb71862ae9dc5082d64ffd",
  "chunk_ordinal": 339,
  "chunk_text_sha256": "11e55e4ef671a7e8cc3f9704692b397e4987e28c5161da7d957f802e6f83c2f8",
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
              "b": 150.00543212890625,
              "coord_origin": "BOTTOMLEFT",
              "l": 75.050537109375,
              "r": 790.7886962890625,
              "t": 502.1280746459961
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 96
          }
        ],
        "self_ref": "#/tables/65"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-b4cb71862ae9dc5082d64ffd.md",
  "heading_path": [
    "CATSNotification"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-b4cb71862ae9dc5082d64ffd.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

Participant, Format. = String (10). Participant, Usage. = Mandatory. Participant, Usage/ Comments. = If 'Role' = 'NO' then: • Contains the GBO Id of the incoming user that initiated the transfer when sent to the Network Operator. If 'Role' = 'USER' or 'ROLR' then: • (1) contains the GBO Id of the current user when sent to the incoming user that initiated the transfer (2) contains the GBO Id of the incoming user that initiated the transfer when sent to the current user. Participant, AseXML.Occurs = 1..1. Participant, AseXML.Element Path = ChangeRequest/Participant. Participant, AseXML.Data Type = xsd:string. RequestID, Format. = Numeric (10). RequestID, Usage. = Mandatory. RequestID, Usage/ Comments. = The unique ID assigned by AEMOto the Transfer Request or error correction. RequestID, AseXML.Occurs = 1..1. RequestID, AseXML.Element Path = ChangeRequest/RequestID. RequestID, AseXML.Data Type = xsd:positiveIntegermaxInclusi ve
