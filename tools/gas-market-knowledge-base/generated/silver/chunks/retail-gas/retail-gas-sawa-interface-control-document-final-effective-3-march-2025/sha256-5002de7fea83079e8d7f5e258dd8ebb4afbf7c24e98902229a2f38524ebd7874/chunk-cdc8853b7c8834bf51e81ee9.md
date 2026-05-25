---
{
  "chunk_id": "chunk-cdc8853b7c8834bf51e81ee9",
  "chunk_ordinal": 171,
  "chunk_text_sha256": "e38f382c5c2dde68b152bd81b7c3f5c3b36f9e0a717c3ca0122417c71a93ca0a",
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
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/10"
        },
        "prov": [
          {
            "bbox": {
              "b": 619.5639829101564,
              "coord_origin": "BOTTOMLEFT",
              "l": 173.9,
              "r": 527.4639999999998,
              "t": 740.2959829101563
            },
            "charspan": [
              0,
              575
            ],
            "page_no": 36
          }
        ],
        "self_ref": "#/texts/462"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/10"
        },
        "prov": [
          {
            "bbox": {
              "b": 543.6939829101564,
              "coord_origin": "BOTTOMLEFT",
              "l": 173.9,
              "r": 527.4759999999999,
              "t": 609.2559829101564
            },
            "charspan": [
              0,
              307
            ],
            "page_no": 36
          }
        ],
        "self_ref": "#/texts/463"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/10"
        },
        "prov": [
          {
            "bbox": {
              "b": 481.6539829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 173.9,
              "r": 527.2699999999995,
              "t": 533.3859829101564
            },
            "charspan": [
              0,
              253
            ],
            "page_no": 36
          }
        ],
        "self_ref": "#/texts/464"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-cdc8853b7c8834bf51e81ee9.md",
  "heading_path": [
    "3.2.7.1.2 Transaction Acknowledgement Status Field"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-cdc8853b7c8834bf51e81ee9.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

- 'Partial' - a status of 'Partial' would only ever occur when processing CSV data within an aseXML transaction. The only transaction of this type that the GRMS  processes is the MeterDataNotification transaction.  Since  this  has  its  own  MeterDataResponse  transaction which  contains  any  events, it is assumed  that  the transaction acknowledgement sent will always be 'Accept' if the CSV data is readable and 'Reject' if the CSV data is not able to be processed (see Section 3.2.7.1.4). Hence the GRMS never populates the status of an acknowledgement with 'Partial'.
- 'Reject' indicates the transaction was rejected and the GRMS will perform  no  further  processing  of  the  transaction.  In  the  case  of  a request transaction, no response transactions, where normally expected, are generated. The acknowledgement carries at least one event with a severity of 'Error'.
- GRMS  current  functionality  ensures  that  the  status  is  not  set  to 'Accept' if any events are generated. The status is set based on the severity  of  the  Events  associated  with  the  transaction.  This  can  be summed up in the table below:
