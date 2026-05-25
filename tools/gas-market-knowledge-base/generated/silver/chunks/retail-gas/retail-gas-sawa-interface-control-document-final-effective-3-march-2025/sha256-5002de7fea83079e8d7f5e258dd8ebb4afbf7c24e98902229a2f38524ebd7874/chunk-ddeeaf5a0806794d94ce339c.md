---
{
  "chunk_id": "chunk-ddeeaf5a0806794d94ce339c",
  "chunk_ordinal": 167,
  "chunk_text_sha256": "728894101d5671ff4b2539c9833a619477cfef28634be9e55a0952a319b819a8",
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
              "b": 648.0039829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.3619999999996,
              "t": 741.1479829101563
            },
            "charspan": [
              0,
              520
            ],
            "page_no": 35
          }
        ],
        "self_ref": "#/texts/442"
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
              "b": 586.7739829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.3119999999998,
              "t": 638.5359829101563
            },
            "charspan": [
              0,
              284
            ],
            "page_no": 35
          }
        ],
        "self_ref": "#/texts/443"
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
              "b": 539.3739829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.4520000000001,
              "t": 577.3059829101563
            },
            "charspan": [
              0,
              184
            ],
            "page_no": 35
          }
        ],
        "self_ref": "#/texts/444"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-ddeeaf5a0806794d94ce339c.md",
  "heading_path": [
    "Notes:"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-ddeeaf5a0806794d94ce339c.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

Status provides a summary of the success or otherwise of the processing of the  transaction.    A  status  of  'Accept'  denotes  that  the  transaction  was processed successfully and can be considered to have been acted on.  A Status of 'Reject' denotes that the transaction was not processed successfully and the transaction should be considered not processed. Multiple event codes may be sent in an acknowledgement where an incoming transaction is rejected by GRMS following failure of more than one validation step.
The receipt of transaction acknowledgements by the GRMS will not invoke any special system  behaviour. However,  upon  receipt of a negative acknowledgement an email will be sent to the RMA. The RMA will take any additional action required. See Section 3.2.7.2.1 for further details).
See section 2.3.1.2 of the Specification Pack - 'FRC B2M-B2B Hub System Architecture,  Version  2.01,  dated  28 th November 2003' that describes the transaction acknowledgement model.
