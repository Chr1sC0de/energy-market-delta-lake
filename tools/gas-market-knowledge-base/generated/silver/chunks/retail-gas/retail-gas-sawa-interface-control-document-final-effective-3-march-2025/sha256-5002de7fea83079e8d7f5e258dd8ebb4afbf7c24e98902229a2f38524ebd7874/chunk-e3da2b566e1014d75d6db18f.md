---
{
  "chunk_id": "chunk-e3da2b566e1014d75d6db18f",
  "chunk_ordinal": 198,
  "chunk_text_sha256": "c8dbed4784946b512acad1ee3111fe21124d6020108a030e484ebf96587a4934",
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
              "b": 319.7539829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.4879999999999,
              "t": 371.4979829101563
            },
            "charspan": [
              0,
              267
            ],
            "page_no": 43
          }
        ],
        "self_ref": "#/texts/570"
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
              "b": 272.32398291015625,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.2759999999996,
              "t": 310.28598291015624
            },
            "charspan": [
              0,
              211
            ],
            "page_no": 43
          }
        ],
        "self_ref": "#/texts/571"
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
              "b": 211.12398291015631,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.2879999999999,
              "t": 262.8559829101563
            },
            "charspan": [
              0,
              250
            ],
            "page_no": 43
          }
        ],
        "self_ref": "#/texts/572"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-e3da2b566e1014d75d6db18f.md",
  "heading_path": [
    "Polling Frequency"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-e3da2b566e1014d75d6db18f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

The maximum permitted frequency of participants polling their out directory is to be 30 seconds, if polled by an automatic process, or an average of 30 seconds, if polled manually.  Participants are free to poll the out directory less frequently than this if desired.
This interface is not designed with the same scalability, and performance in mind as the ebXML interface, and as such, high frequency  continuous polling or very high volumes of transactions are not anticipated.
The GRMS will endeavour to poll participants' inboxes every 10 seconds. This may vary depending on system loads, the number of files in the inboxes etc. The Market expectation is that this polling should happen at least once a minute as a worst case.
