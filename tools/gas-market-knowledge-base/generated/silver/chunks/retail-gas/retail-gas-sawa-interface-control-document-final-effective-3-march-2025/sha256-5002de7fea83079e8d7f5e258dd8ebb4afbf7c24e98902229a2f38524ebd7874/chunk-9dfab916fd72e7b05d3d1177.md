---
{
  "chunk_id": "chunk-9dfab916fd72e7b05d3d1177",
  "chunk_ordinal": 158,
  "chunk_text_sha256": "5b0317319be45018ca685bc9dcee01fe11dcf2f75a071bc1ac9ab8368a4ba9a9",
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
              "b": 611.3508605957031,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.0568084716797,
              "r": 537.8434448242188,
              "t": 745.7188034057617
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 32
          }
        ],
        "self_ref": "#/tables/26"
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
              "b": 551.2539829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 530.4879999999998,
              "t": 589.1859829101563
            },
            "charspan": [
              0,
              238
            ],
            "page_no": 32
          }
        ],
        "self_ref": "#/texts/344"
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
              "b": 462.4539829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.3379999999999,
              "t": 541.7859829101563
            },
            "charspan": [
              0,
              443
            ],
            "page_no": 32
          }
        ],
        "self_ref": "#/texts/345"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-9dfab916fd72e7b05d3d1177.md",
  "heading_path": [
    "3.2.3 Envelope"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-9dfab916fd72e7b05d3d1177.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

, 1.Condition (if O) = Priority. , Name.Condition (if O) = Priority. , Message Header.Range = Priority. , Message Header.1 = O. , Group Ref..Group Optionality = . , MHD.Group Optionality = . , MHD.Group Optionality = Market. , Level.M = Market. , 1.Condition (if O) = Market. , Name.Condition (if O) = Market. , Message Header.Range = Market. , Message Header.1 = 1
The  From  and  To  items  apply  to  every  transaction  within  the  envelope. Where a transaction is to be sent to more than one recipient, the transaction information is required to be sent in separate messages, one to each recipient.
Transaction Group is specified in the message header to identify the set of related transactions which this message contains.   Transaction Groups map onto an 'application' or sub-system.  Within a message, transactions must belong to the same transaction group.  The transaction group in the message header allows the routing function to send the message to the appropriate subsystem without having to interrogate the individual transactions.
