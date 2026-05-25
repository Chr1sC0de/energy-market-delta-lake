---
{
  "chunk_id": "chunk-9bb0344d24ecb3eb0d3b860a",
  "chunk_ordinal": 202,
  "chunk_text_sha256": "544adff8fb9bced392a9fc9dee6fcacaa26e0a4c1e7c6c538a87c3e0e6779ef7",
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
              "b": 305.95398291015636,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.2459999999999,
              "t": 371.4859829101563
            },
            "charspan": [
              0,
              342
            ],
            "page_no": 44
          }
        ],
        "self_ref": "#/texts/588"
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
              "b": 244.72398291015634,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.4519999999999,
              "t": 296.4859829101563
            },
            "charspan": [
              0,
              291
            ],
            "page_no": 44
          }
        ],
        "self_ref": "#/texts/589"
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
              "r": 527.228,
              "t": 235.25598291015626
            },
            "charspan": [
              0,
              99
            ],
            "page_no": 44
          }
        ],
        "self_ref": "#/texts/590"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "code",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 92.42398291015627,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 511.66,
              "t": 201.77598291015624
            },
            "charspan": [
              0,
              126
            ],
            "page_no": 44
          }
        ],
        "self_ref": "#/texts/591"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-9bb0344d24ecb3eb0d3b860a.md",
  "heading_path": [
    "Timestamps"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-9bb0344d24ecb3eb0d3b860a.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

The time zone selected for date/time stamps in the body of csv transactions sent to the GRMS will be at the discretion of the sending party. The sending party must therefore ensure that the combination of the time and time zone accurately communicates the point in time being defined. There are no such time/date fields identified at present.
The format used for all datetime type information (apart from the date/time stamp implied in the outgoing csv filename - see section 3.4.3.1 for further details  of  this)  will  be  in  line  with  ISO  8601  Date  and  Time  Format  (see http://www.w3.org/TR/xmlschema-2/#isoformats). i.e.
Complete  date  plus  hours,  minutes,  seconds  and  (an  optional)  decimal fraction of a second:
```
YYYY-MM-DDThh:mm:ssTZD (eg 2004-06-23T21:36:57.000+10:00) where: hh   = two digits of hour (00 through 23) (am/pm NOT allowed)
```
