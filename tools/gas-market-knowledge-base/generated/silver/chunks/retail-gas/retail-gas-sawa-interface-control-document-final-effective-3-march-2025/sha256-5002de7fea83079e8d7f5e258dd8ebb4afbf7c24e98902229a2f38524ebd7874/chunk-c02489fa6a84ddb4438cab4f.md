---
{
  "chunk_id": "chunk-c02489fa6a84ddb4438cab4f",
  "chunk_ordinal": 201,
  "chunk_text_sha256": "3ca39f7ed76f54c9cc92918077563908c0ddb07cb9a5d62555b81348faf20c37",
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
              "b": 536.9739829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.4639999999999,
              "t": 574.9059829101564
            },
            "charspan": [
              0,
              186
            ],
            "page_no": 44
          }
        ],
        "self_ref": "#/texts/584"
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
              "b": 503.37107381924716,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.132,
              "t": 527.5059829101564
            },
            "charspan": [
              0,
              142
            ],
            "page_no": 44
          }
        ],
        "self_ref": "#/texts/585"
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
              "b": 428.3539829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.338,
              "t": 493.90598291015624
            },
            "charspan": [
              0,
              383
            ],
            "page_no": 44
          }
        ],
        "self_ref": "#/texts/586"
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
              "b": 380.9539829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.3359999999999,
              "t": 418.88598291015626
            },
            "charspan": [
              0,
              195
            ],
            "page_no": 44
          }
        ],
        "self_ref": "#/texts/587"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-c02489fa6a84ddb4438cab4f.md",
  "heading_path": [
    "Timestamps"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-c02489fa6a84ddb4438cab4f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

A file is deemed to have been received by the GRMS at the moment when it has been renamed from .tmp to .zip in the market participant's in directory, as described in 3.4.2.1 and 3.4.3.1.
A file is deemed to have been sent by the GRMS at the moment it has been named either .zip or .ack or .dup in the participant's out directory.
All datetime type information including the datetime implied in the outgoing csv  filename  (see  section  3.4.3.1),  any  datetimes  used  in  the  transactions within a csv file and the timestamps within csv acknowledgements will be sent  from  the  GRMS  in  Market  Standard  Time.  That  is  to  say,  all  time information will be sent from the GRMS as in the GMT+10 time zone.
The timestamp implied in the outgoing csv filename is the message creation time, rather than the business process transaction time, although these should be very close under normal circumstances.
