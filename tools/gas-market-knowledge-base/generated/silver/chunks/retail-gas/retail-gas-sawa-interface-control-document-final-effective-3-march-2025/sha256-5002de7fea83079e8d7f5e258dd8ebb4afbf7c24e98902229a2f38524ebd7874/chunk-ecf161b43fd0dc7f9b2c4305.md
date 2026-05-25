---
{
  "chunk_id": "chunk-ecf161b43fd0dc7f9b2c4305",
  "chunk_ordinal": 233,
  "chunk_text_sha256": "875a02325ad287ea08458bf14e29a2300d7c323dd4d5c7789263edac3b787f18",
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
              "b": 505.8939829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.2279999999998,
              "t": 557.6259829101563
            },
            "charspan": [
              0,
              273
            ],
            "page_no": 53
          }
        ],
        "self_ref": "#/texts/844"
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
              "b": 444.69398291015625,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.5,
              "t": 496.4259829101563
            },
            "charspan": [
              0,
              285
            ],
            "page_no": 53
          }
        ],
        "self_ref": "#/texts/845"
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
              "b": 411.07398291015625,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.3719999999998,
              "t": 435.20598291015625
            },
            "charspan": [
              0,
              132
            ],
            "page_no": 53
          }
        ],
        "self_ref": "#/texts/846"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-ecf161b43fd0dc7f9b2c4305.md",
  "heading_path": [
    "3.6.1 Transport Layer"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-ecf161b43fd0dc7f9b2c4305.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

The  Low  volume  interface  allows  certain  market  participants  to  submit aseXML payload  'snippets'  via  the  ftp  interface.  These  snippets  are  then wrapped in ebXML and submitted to the FRC Hub via the GRMS ebXML gateway, on behalf of the relevant participant.
Transactions and transaction acknowledgements bound for the low volume participants are forwarded by the FRC hub to the GRMS ebXML gateway. The GRMS then strips the aseXML payload out of the ebXML message and forwards the resultant 'snippet' to the low volume participant's XML outbox.
Participants wishing to send ebXML transactions to a low volume participant address their messages to the end participant as normal.
