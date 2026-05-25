---
{
  "chunk_id": "chunk-1ad1a3f1b7bffbf6df067b49",
  "chunk_ordinal": 306,
  "chunk_text_sha256": "3178c6e80d4ed6828a48845815d730c049c0ba63dd69b0a75842fd91b201107d",
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
              "b": 109.002685546875,
              "coord_origin": "BOTTOMLEFT",
              "l": 74.9416275024414,
              "r": 793.7384643554688,
              "t": 503.38714599609375
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 80
          }
        ],
        "self_ref": "#/tables/57"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-1ad1a3f1b7bffbf6df067b49.md",
  "heading_path": [
    "Physical Transaction"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-1ad1a3f1b7bffbf6df067b49.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

, String (10) = . , Mandatory = . , If 'Role' = 'NO' then: = • For Transfers (TFR-), contains the GBO Id of the incoming user that initiated the transfer when sent to the Network Operator. • For Error Corrections (ECNET-), contains the GBO Id of the previous user who initiated the error correction when sent to the Network Operator. If 'Role' = 'USER' or 'ROLR' then: • For transfers (TFR-), (1) contains the GBO Id of the incoming user that initiated the transfer when sent to the incoming user (2) contains xsi:nil = 'true' when sent to the current user (We do not communicate the incoming users identity to the current user.) • For error correction, (ECNET-) (1) contains the GBO Id of the incoming user that initiated the transfer when sent to the previous user (2) contains xsi:nil = 'true' when sent to the current user (We do not communicate the. , 1..1 = . , ChangeRequest/Participant = . , xsd:string =
