---
{
  "chunk_id": "chunk-f52be5eac2c7be2d059c8570",
  "chunk_ordinal": 153,
  "chunk_text_sha256": "33b634f12d0ba48b4b58ae5251ce33cbbb21f8e29f6b3658d506f9d7350a2e73",
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
              "b": 75.62398291015631,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.4099999999996,
              "t": 154.9759829101563
            },
            "charspan": [
              0,
              431
            ],
            "page_no": 30
          },
          {
            "bbox": {
              "b": 703.2039829101564,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.2639999999998,
              "t": 741.1359829101564
            },
            "charspan": [
              432,
              605
            ],
            "page_no": 31
          }
        ],
        "self_ref": "#/texts/324"
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
              "b": 628.2039829101564,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.3479999999998,
              "t": 693.7359829101563
            },
            "charspan": [
              0,
              312
            ],
            "page_no": 31
          }
        ],
        "self_ref": "#/texts/330"
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
              "b": 566.9739829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.2639999999998,
              "t": 618.7359829101563
            },
            "charspan": [
              0,
              264
            ],
            "page_no": 31
          }
        ],
        "self_ref": "#/texts/331"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-f52be5eac2c7be2d059c8570.md",
  "heading_path": [
    "3.2.1 Background"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-f52be5eac2c7be2d059c8570.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

'A Standard for Energy Transactions in XML' [ASEXML] provides the basis for the development of the data flows in the Gas Retail Market.  AseXML was developed by the Combined Gas and Electricity IT Architecture Working Group of Australia and provides a de-centralised approach to the development of energy transactions.  The standard [ASEXML] describes the use of XML in developing electronic data flows and provides for addressing, acknowledging,  referencing  and  grouping  of  data  flows.    Guidelines  are provided to implement a change management process on the schemas which define the data flows.
This section outlines the concepts in aseXML which support the data flows for the Gas Retail Market.  Though the standard [ASEXML] describes the physical format of messages in aseXML, some of the constructs described in it perform business level functionality and are therefore also described at a logical level.
All  of  the  descriptions  provided  below  are  for  the  purposes  of  illustrating concepts  relevant  to  the  logical  description  of  GRMS  data  flows.    The aseXML standard [ASEXML] and schemas [SCHEMA] are the definitive source of these specifications.
