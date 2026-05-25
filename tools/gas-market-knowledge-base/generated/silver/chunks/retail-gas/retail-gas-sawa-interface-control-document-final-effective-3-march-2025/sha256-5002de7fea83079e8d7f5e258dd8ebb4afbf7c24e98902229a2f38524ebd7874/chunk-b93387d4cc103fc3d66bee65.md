---
{
  "chunk_id": "chunk-b93387d4cc103fc3d66bee65",
  "chunk_ordinal": 299,
  "chunk_text_sha256": "0b59b26234ba4ae55e4fce0f3622f65bf2186976e2cf15724285638b93ddc6d5",
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
              "b": 193.54714965820312,
              "coord_origin": "BOTTOMLEFT",
              "l": 75.1470718383789,
              "r": 793.6951293945312,
              "t": 424.06700134277344
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 76
          }
        ],
        "self_ref": "#/tables/54"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-b93387d4cc103fc3d66bee65.md",
  "heading_path": [
    "CATSDataRequest"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-b93387d4cc103fc3d66bee65.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

Role, Format. = String(4) 'USER' - User 'NO' - Network operator 'GRMS' - The Gas Retail Market System.. Role, Usage. = Mandatory. Role, Usage/ Comments. = The role assigned to the Sender. In this case 'GRMS'. Role, AseXML.Occurs = 1..1. Role, AseXML.Element Path = Role. Role, AseXML.Data Type = xsd:string xsd:maxLength ="4". RoleStatus, Format. = String(Enum) 'N' = New (incoming) 'C' = Current. RoleStatus, Usage. = Mandatory. RoleStatus, Usage/ Comments. = In this case 'N'.. RoleStatus, AseXML.Occurs = 1..1. RoleStatus, AseXML.Element Path = RoleStatus. RoleStatus, AseXML.Data Type = Enumerated list of xsd:string "N", "C".. InitiatingRequestID, Format. = Numeric (10). InitiatingRequestID, Usage. = Mandatory. InitiatingRequestID, Usage/ Comments. =
