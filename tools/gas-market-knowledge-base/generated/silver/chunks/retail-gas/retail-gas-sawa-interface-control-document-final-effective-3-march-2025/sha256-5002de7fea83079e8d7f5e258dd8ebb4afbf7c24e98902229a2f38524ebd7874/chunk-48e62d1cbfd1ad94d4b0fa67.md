---
{
  "chunk_id": "chunk-48e62d1cbfd1ad94d4b0fa67",
  "chunk_ordinal": 313,
  "chunk_text_sha256": "d2327166eeb1852d46a38513d7073bfd9ce9b465250d6d2a48fbed7d59d10863",
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
              "b": 194.56228637695312,
              "coord_origin": "BOTTOMLEFT",
              "l": 74.8558349609375,
              "r": 793.9246826171875,
              "t": 502.02283477783203
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 84
          }
        ],
        "self_ref": "#/tables/61"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-48e62d1cbfd1ad94d4b0fa67.md",
  "heading_path": [
    "Physical Transaction"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-48e62d1cbfd1ad94d4b0fa67.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

ObjectingAction, Format. = String (Enum) 'Raised' or 'Withdrawn'. ObjectingAction, Usage. = Mandatory for : ECNET-WOB-NOTF- OP ECNET-WOB-NOTF- PU TFR-WOB-NOTF-IU TFR-WOB-NOTF-OP Not Required for: TFR-NOTF-CU TFR-NOTF-NO ECNET-NOTF-NO ECNET-NOTF-CU. ObjectingAction, Usage/ Comments. = 'Withdrawn'. ObjectingAction, AseXML.Occurs = 1..1. ObjectingAction, AseXML.Element Path = Objection/ObjectionAction. ObjectingAction, AseXML.Data Type = enumerated list of xsd:string values: "Raised", "Withdrawn". InitiatingRequestID, Format. = Numeric (10). InitiatingRequestID, Usage. = Mandatory for : ECNET-WOB-NOTF- OP ECNET-WOB-NOTF- PU Mandatory for : TFR-WOB-NOTF-IU TFR-WOB-NOTF-OP Not Required for:
