---
{
  "chunk_id": "chunk-ce387aaf33da768e8ee848df",
  "chunk_ordinal": 533,
  "chunk_text_sha256": "8f2fc0440fc5b2613e71cb04c8f7495f0ab8686624e7f6f3b369a44f6d99faed",
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
              "b": 307.5229797363281,
              "coord_origin": "BOTTOMLEFT",
              "l": 74.9992904663086,
              "r": 793.9035034179688,
              "t": 501.8934326171875
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 172
          }
        ],
        "self_ref": "#/tables/109"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-ce387aaf33da768e8ee848df.md",
  "heading_path": [
    "GasMeterNotification/MIRNStatusUpdate"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-ce387aaf33da768e8ee848df.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

MIRNStatus, Format. = String(Enum) 'Registered' = a service inlet has been installed at the delivery point 'Commissioned'=Commissioned and not decommissioned or permanently removed (including after the delivery point has been reconnected) 'Decommissioned'= disconnected (temporary) 'Deregistered'= Permanently Removed. MIRNStatus, Usage. = Mandatory. MIRNStatus, Usage/ Comments. = The MIRN status must be 'Commissioned'. MIRNStatus, AseXML.Occurs = 0..1. MIRNStatus, AseXML.Element Path = MasterData/MIRNStatus. MIRNStatus, AseXML.Data Type = An enumerated list of xsd:string values: 'Registered', 'Commissioned', 'Decommissioned', 'Deregistered'. DateServiceOrderCompleted, Format. = Date (10) ccyy-mm-dd. DateServiceOrderCompleted, Usage. = Mandatory. DateServiceOrderCompleted, Usage/ Comments. = Provides the date on which the MIRN Status was changed, that is when the MIRN was disconnected.. DateServiceOrderCompleted,
