---
{
  "chunk_id": "chunk-e6bdbfe5e0a455aaea22ba40",
  "chunk_ordinal": 752,
  "chunk_text_sha256": "b56f3332d2a9a4afd02a5d81e9569af5a34b47e318d1bf97f4034b243eb4c271",
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
        "label": "text",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 315.43398291015626,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.2999999999998,
              "t": 408.56598291015627
            },
            "charspan": [
              0,
              497
            ],
            "page_no": 246
          }
        ],
        "self_ref": "#/texts/2506"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "text",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 254.20398291015636,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.1680000000001,
              "t": 305.9659829101563
            },
            "charspan": [
              0,
              250
            ],
            "page_no": 246
          }
        ],
        "self_ref": "#/texts/2507"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-e6bdbfe5e0a455aaea22ba40.md",
  "heading_path": [
    "10.3.1.7.4 User's deemed withdrawal and Shippers/Swing Service provider's deemed injections"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-e6bdbfe5e0a455aaea22ba40.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

Once the allocation is done the actual allocation proportion can be derived. The actual allocation proportion is the percentage of the quantity allocated to the request against the total quantity being allocated. This actual allocation proportion is used in the business process that allocates the hourly energy of data. Note that when the allocation instruction is given solely in percentages the actual allocation proportion is the same as the original percentages of the allocation instruction.
The  actual  allocation  proportion  is  used  during  the  forecasting  for  South Australia with one difference, it is derived by allocating the total forecasted energy value rather then the UETW value which is not known at the time of forecasting.
