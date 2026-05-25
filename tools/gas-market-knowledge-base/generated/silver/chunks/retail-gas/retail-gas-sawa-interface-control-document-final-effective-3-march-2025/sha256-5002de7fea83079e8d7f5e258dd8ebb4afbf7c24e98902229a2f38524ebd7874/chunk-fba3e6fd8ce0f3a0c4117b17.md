---
{
  "chunk_id": "chunk-fba3e6fd8ce0f3a0c4117b17",
  "chunk_ordinal": 401,
  "chunk_text_sha256": "60cf9832ca26aca8f636083ca8d407221a3887f097a7029681926260d494ec31",
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
              "b": 245.44046020507812,
              "coord_origin": "BOTTOMLEFT",
              "l": 75.02967834472656,
              "r": 793.7985229492188,
              "t": 424.0281066894531
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 124
          }
        ],
        "self_ref": "#/tables/76"
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
              "b": 302.89788818359375,
              "coord_origin": "BOTTOMLEFT",
              "l": 74.90705108642578,
              "r": 793.9712524414062,
              "t": 501.80445098876953
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 125
          }
        ],
        "self_ref": "#/tables/77"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-fba3e6fd8ce0f3a0c4117b17.md",
  "heading_path": [
    "CATSObjectionRequest"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-fba3e6fd8ce0f3a0c4117b17.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

Role, AseXML.Data Type = xsd:string xsd:max'Length ="4"
ObjectionCode, Format. = String (8) 'DECLINED'. ObjectionCode, Usage. = Mandatory. ObjectionCode, Usage/ Comments. = Must be a valid objection reason code. 'DECLINED' = No Haulage Contract is in place for TFR-OBJ-NO 'DECLINED' = The ROLR fee has not been paid for TFR-OBJ-ROLR 'DECLINED' = The original delivery point transaction is believed to be correct/ the correction notice contains incorrect information for ECNET- OBJ-CU and ECNET-OBJ- NO. ObjectionCode, AseXML.Occurs = 1..1. ObjectionCode, AseXML.Element Path = ObjectionCode. ObjectionCode, AseXML.Data Type = Xsd:string xsd:length ="8"
