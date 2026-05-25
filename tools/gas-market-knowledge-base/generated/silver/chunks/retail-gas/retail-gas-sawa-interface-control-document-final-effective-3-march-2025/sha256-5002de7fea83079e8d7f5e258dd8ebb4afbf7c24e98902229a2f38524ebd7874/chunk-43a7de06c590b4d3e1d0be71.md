---
{
  "chunk_id": "chunk-43a7de06c590b4d3e1d0be71",
  "chunk_ordinal": 287,
  "chunk_text_sha256": "f6eeb7872fafc8adc59a87a25c744347000cc78f4c0166cdd9f5ecbcfaf336f8",
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
        "label": "code",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 286.31205985723193,
              "coord_origin": "BOTTOMLEFT",
              "l": 127.58,
              "r": 534.046,
              "t": 361.8554873242187
            },
            "charspan": [
              0,
              253
            ],
            "page_no": 71
          }
        ],
        "self_ref": "#/texts/1035"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "caption",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 220.5140073242187,
              "coord_origin": "BOTTOMLEFT",
              "l": 170.18,
              "r": 290.93,
              "t": 230.8460073242187
            },
            "charspan": [
              0,
              21
            ],
            "page_no": 71
          }
        ],
        "self_ref": "#/texts/1036"
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
              "b": 139.48400732421874,
              "coord_origin": "BOTTOMLEFT",
              "l": 127.58,
              "r": 418.51,
              "t": 149.81600732421873
            },
            "charspan": [
              0,
              62
            ],
            "page_no": 71
          }
        ],
        "self_ref": "#/texts/1037"
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
              "b": 119.68400732421867,
              "coord_origin": "BOTTOMLEFT",
              "l": 127.58,
              "r": 774.12,
              "t": 130.01600732421866
            },
            "charspan": [
              0,
              132
            ],
            "page_no": 71
          }
        ],
        "self_ref": "#/texts/1038"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-43a7de06c590b4d3e1d0be71.md",
  "heading_path": [
    "8.1.3.3.1 AseXML Example"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-43a7de06c590b4d3e1d0be71.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

```
<CATSChangeRequest version="r29"> <ChangeReasonCode>0003</ChangeReasonCode> <ProposedDate>2004-06-10</ProposedDate> <NMIStandingData xsi:type="ase:GasStandingData" version="r40"> <NMI checksum="5">5000000006</NMI> </NMIStandingData> </CATSChangeRequest>
```
8.1.3.3.2 Event Codes
Note: In all cases the severity of each event will be 'Error'.
Note: Multiple event codes may be sent where the transaction is rejected by GRMS following failure of more than one validation step.
