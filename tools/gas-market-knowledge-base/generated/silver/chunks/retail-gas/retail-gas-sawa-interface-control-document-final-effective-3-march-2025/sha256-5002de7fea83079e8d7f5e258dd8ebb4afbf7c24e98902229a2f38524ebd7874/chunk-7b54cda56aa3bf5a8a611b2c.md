---
{
  "chunk_id": "chunk-7b54cda56aa3bf5a8a611b2c",
  "chunk_ordinal": 373,
  "chunk_text_sha256": "58269fd8661a2639dfa63545a4b51d667a4ee90e35a33bbdb9a05a4c681514e1",
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
              "b": 130.68356323242188,
              "coord_origin": "BOTTOMLEFT",
              "l": 75.13958740234375,
              "r": 793.8998413085938,
              "t": 424.1280822753906
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 110
          }
        ],
        "self_ref": "#/tables/71"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-7b54cda56aa3bf5a8a611b2c.md",
  "heading_path": [
    "CATSNotification"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-7b54cda56aa3bf5a8a611b2c.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

Role, Format. = String(4) 'USER' - User 'NO' - Network operator. Role, Usage. = Mandatory. Role, Usage/ Comments. = The role assigned to the recipient, either 'USER' or 'NO'. Role, AseXML.Occurs = 1..1. Role, AseXML.Element Path = Role. Role, AseXML.Data Type = xsd:string xsd:maxLength ="4". RoleStatus, Format. = String(Enum) 'N' = New (incoming) 'C' = Current. RoleStatus, Usage. = Mandatory. RoleStatus, Usage/ Comments. = For TFR-CAN-NOTF, 'C' for current roles and 'N' for the incoming user. For ECNET-CAN- NOTF, 'C' for current roles and for the previous user, this will be 'N', since this previous user can be considered to be the incoming user in this process.. RoleStatus, AseXML.Occurs = 1..1. RoleStatus, AseXML.Element Path = RoleStatus. RoleStatus, AseXML.Data Type =
