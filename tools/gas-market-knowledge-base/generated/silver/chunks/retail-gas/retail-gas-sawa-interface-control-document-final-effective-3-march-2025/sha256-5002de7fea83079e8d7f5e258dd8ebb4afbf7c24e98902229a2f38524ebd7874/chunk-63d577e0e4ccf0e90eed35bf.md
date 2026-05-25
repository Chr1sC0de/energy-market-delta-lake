---
{
  "chunk_id": "chunk-63d577e0e4ccf0e90eed35bf",
  "chunk_ordinal": 447,
  "chunk_text_sha256": "27bd66c6c489012ebbab8aea6da4b862cacbae894804b2cddd83d6415df239e6",
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
              "b": 137.29351806640625,
              "coord_origin": "BOTTOMLEFT",
              "l": 74.77896881103516,
              "r": 794.1239013671875,
              "t": 501.8897399902344
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 141
          }
        ],
        "self_ref": "#/tables/89"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-63d577e0e4ccf0e90eed35bf.md",
  "heading_path": [
    "Physical Transaction"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-63d577e0e4ccf0e90eed35bf.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

'USER','ROLR' and 'NO'.. Role, AseXML.Occurs = 1..1. Role, AseXML.Element Path = RoleAssignments/ RoleAssignment/ Role. Role, AseXML.Data Type = xsd:string maxLen='4'. SupplyPointCode, Format. = String(Enum) 'Basic'=A basic meter 'Interval'=An interval meter. SupplyPointCode, Usage. = Optional. SupplyPointCode, Usage/ Comments. = This provides the information about the type of meter installed at the delivery point.. SupplyPointCode, AseXML.Occurs = 0..1. SupplyPointCode, AseXML.Element Path = MeterData/ SupplyPointCode. SupplyPointCode, AseXML.Data Type = An enumerated list of xsd:string values: 'Basic', 'Interval', 'Transmission'
