---
{
  "chunk_id": "chunk-1c0b0a2dffd99aadd23f5fa3",
  "chunk_ordinal": 502,
  "chunk_text_sha256": "622154dde21183600283df9df75a736e6aa22858e6de0b54a48dc372b0b3e1a7",
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
              "b": 140.16693115234375,
              "coord_origin": "BOTTOMLEFT",
              "l": 74.79759216308594,
              "r": 794.122802734375,
              "t": 501.98693084716797
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 160
          }
        ],
        "self_ref": "#/tables/94"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-1c0b0a2dffd99aadd23f5fa3.md",
  "heading_path": [
    "GasMeterNotification/MeterFix"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-1c0b0a2dffd99aadd23f5fa3.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

MeterData/ SupplyPointCode. SupplyPointCode, AseXML.Data Type = An enumerated list of xsd:string values: 'Basic', 'Interval', 'Transmission'. AnticipatedAnnualConsumptio n, Format. = Integer(13). AnticipatedAnnualConsumptio n, Usage. = Optional / Mandatory for basic MIRNS in WA. AnticipatedAnnualConsumptio n, Usage/ Comments. = This provides the annual volume of gas anticipated to be withdrawn from the delivery point.. AnticipatedAnnualConsumptio n, AseXML.Occurs = 0..1. AnticipatedAnnualConsumptio n, AseXML.Element Path = MasterData/ AnticipatedAnnualCons umption. AnticipatedAnnualConsumptio n, AseXML.Data Type = xsd:integer totalDig='13'. BaseLoad, Format. = Decimal. BaseLoad, Usage. = Optional / Mandatory for basic MIRNS in SA. BaseLoad, Usage/ Comments. = This contains the non sensitive base load for the delivery point.. BaseLoad, AseXML.Occurs = 0..1. BaseLoad,
