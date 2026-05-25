---
{
  "chunk_id": "chunk-ca525a4143ed739ee93ff2a1",
  "chunk_ordinal": 341,
  "chunk_text_sha256": "62dca33bd4bd2c623d9fb5b38a6be1dcc48a91735e6f5ae9f934c57aaaedd28b",
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
              "b": 165.94747924804688,
              "coord_origin": "BOTTOMLEFT",
              "l": 75.12373352050781,
              "r": 790.8999633789062,
              "t": 502.0725555419922
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 97
          }
        ],
        "self_ref": "#/tables/66"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-ca525a4143ed739ee93ff2a1.md",
  "heading_path": [
    "CATSNotification"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-ca525a4143ed739ee93ff2a1.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

ChangeReasonCode, Format. = String (4) 0001 = Prospective transfer, in-situ 0002 = Prospective transfer, move in 0003 = Correction of Transfer. ChangeReasonCode, Usage. = Mandatory. ChangeReasonCode, Usage/ Comments. = One of: • '0002' (move in) to support TFR-PEND- MI-NOTF • '0001' to support TFR-PEND-NOTF • '0003' to support ECNET-PEND- NOTF. ChangeReasonCode, AseXML.Occurs = 1..1. ChangeReasonCode, AseXML.Element Path = ChangeRequest/ChangeDat a/ChangeReasonCode. ChangeReasonCode, AseXML.Data Type = xsd:string xsd:maxLength ="4". ProposedDate, Format. = Date (10) Ccyy-mm-dd. ProposedDate, Usage. = Mandatory. ProposedDate, Usage/ Comments. = For TFR-PEND-NOTF and TFR-PEND-NOTF: The Earliest Change Date supplied in the original transfer request or error correction. For
