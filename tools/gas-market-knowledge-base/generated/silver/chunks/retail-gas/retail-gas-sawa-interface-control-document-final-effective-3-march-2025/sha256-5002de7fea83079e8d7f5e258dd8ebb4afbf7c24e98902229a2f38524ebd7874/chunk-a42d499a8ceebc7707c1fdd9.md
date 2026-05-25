---
{
  "chunk_id": "chunk-a42d499a8ceebc7707c1fdd9",
  "chunk_ordinal": 930,
  "chunk_text_sha256": "a03a60f4318248cb55707124000d5364c41e1e4a9f12a9b77097ee13163832c2",
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
              "b": 536.1339829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.3739999999998,
              "t": 629.2959829101563
            },
            "charspan": [
              0,
              509
            ],
            "page_no": 300
          }
        ],
        "self_ref": "#/texts/3149"
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
              "b": 475.05398291015626,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.3839999999996,
              "t": 526.6659829101563
            },
            "charspan": [
              0,
              265
            ],
            "page_no": 300
          }
        ],
        "self_ref": "#/texts/3150"
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
              "b": 427.63398291015625,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.3599999999998,
              "t": 465.58598291015625
            },
            "charspan": [
              0,
              203
            ],
            "page_no": 300
          }
        ],
        "self_ref": "#/texts/3151"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-a42d499a8ceebc7707c1fdd9.md",
  "heading_path": [
    "10.10.1.6.1 Matching of off-market trades"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-a42d499a8ceebc7707c1fdd9.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

Before the gas day the user off-market trade instruction supplied by users is evaluated  against  the  off-market  confirmation  provided  by  swing  service providers.  The  off-market  requests  are  aggregated  by  the  gas  day,  subnetwork, pipeline, swing service type and swing service provider (supplying the trade). This amount is then compared with the amount supplied by the appropriate swing service provider for the user and the same combination of the gas day, sub-network, pipeline, swing type.
If the amount 'confirmed' by the swing service provider is equal or larger then the total amount 'requested' by the user from the swing service provider, then for each of the user's requests for the swing service provider a matched swing service trade is generated.
If the amount 'confirmed' by the swing service provider is less then the total amount 'requested' by the user from the swing service provider, then none of the user's requests will be matched (approved).
