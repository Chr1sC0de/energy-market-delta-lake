---
{
  "chunk_id": "chunk-641f3f5ea9632b0a9c94fd0b",
  "chunk_ordinal": 259,
  "chunk_text_sha256": "3cfa06ebcc75aff143a31ff2404db5954420da45745ca53db9aa3489db492e7b",
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
              "b": 290.1140073242187,
              "coord_origin": "BOTTOMLEFT",
              "l": 127.58,
              "r": 774.0759999999998,
              "t": 328.0780073242187
            },
            "charspan": [
              0,
              296
            ],
            "page_no": 62
          }
        ],
        "self_ref": "#/texts/971"
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
              "b": 242.7140073242187,
              "coord_origin": "BOTTOMLEFT",
              "l": 127.58,
              "r": 774.084,
              "t": 280.64600732421866
            },
            "charspan": [
              0,
              325
            ],
            "page_no": 62
          }
        ],
        "self_ref": "#/texts/972"
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
              "b": 209.11400732421873,
              "coord_origin": "BOTTOMLEFT",
              "l": 127.58,
              "r": 774.0880000000001,
              "t": 233.24600732421868
            },
            "charspan": [
              0,
              280
            ],
            "page_no": 62
          }
        ],
        "self_ref": "#/texts/973"
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
              "b": 175.5140073242187,
              "coord_origin": "BOTTOMLEFT",
              "l": 127.58,
              "r": 774.0519999999998,
              "t": 199.64600732421871
            },
            "charspan": [
              0,
              164
            ],
            "page_no": 62
          }
        ],
        "self_ref": "#/texts/974"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-641f3f5ea9632b0a9c94fd0b.md",
  "heading_path": [
    "8.1 Transfer and Change of Standing Data (Erroneous  Transfer Correction)"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-641f3f5ea9632b0a9c94fd0b.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

The Transfer section of the [ RMP ] deals with the transfer of customers from one user (current user) to another user (incoming user). Since the customer is assigned a delivery point this is equivalent to transferring gas deliveries at a delivery point from the current user to the incoming user.
When looking for a candidate aseXML transaction to support a required Transfer logical flow the approach will be to try and re-use a suitable transaction from the CATS (CustomerTransfer) application. Where technically feasible this will be the CATS transaction as used in the Victorian gas market for a similar data exchange.
An 'erroneous transfer correction' is a request initiated by the user that was previously associated with a delivery point. This is a request to correct a transfer that may have occurred in error. The process that follows this request is precisely the same as that for a transfer.
Throughout this section reference is made to the 'previous' user. Such a user is conceptually the same as the incoming user, as referred to in the transfer process.
