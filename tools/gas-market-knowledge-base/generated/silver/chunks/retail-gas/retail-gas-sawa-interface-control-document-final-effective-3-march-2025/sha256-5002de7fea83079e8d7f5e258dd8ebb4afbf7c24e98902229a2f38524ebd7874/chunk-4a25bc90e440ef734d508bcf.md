---
{
  "chunk_id": "chunk-4a25bc90e440ef734d508bcf",
  "chunk_ordinal": 210,
  "chunk_text_sha256": "24dd2ddb42bfd76ef38f8fa4a5b0fdd8669776fa851450b396ef366791200d50",
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
              "b": 294.31398291015626,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.314,
              "t": 387.44598291015626
            },
            "charspan": [
              0,
              518
            ],
            "page_no": 47
          }
        ],
        "self_ref": "#/texts/662"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "code",
        "parent": {
          "$ref": "#/groups/16"
        },
        "prov": [
          {
            "bbox": {
              "b": 114.6439829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 509.74,
              "t": 263.4559829101563
            },
            "charspan": [
              0,
              214
            ],
            "page_no": 47
          }
        ],
        "self_ref": "#/texts/663"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-4a25bc90e440ef734d508bcf.md",
  "heading_path": [
    "GRMS Performs Business Level Validation"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-4a25bc90e440ef734d508bcf.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

The  GRMS  will  perform  business  level  validation  as  described  in  the Business Specification on the transaction contained within the csv file. This will include validating the filename (since it contains business information). Once  the  csv  transaction  has  been  validated  the  GRMS  will  place  a  'csv acknowledgement' in the participant's Outbox. The csv acknowledgement will have the same file name as the message filename but with a filename suffix of .ACK. Acknowledgement files will not be zipped.
```
e.g.    Original csv Message : WAGAS_UAI_ALINTARWA_WAGMO_20040501143526.ZIP Or SAGAS_UAI_AGL_REMCO_20040501143526.ZIP csv Ack : WAGAS_UAI_ALINTARWA_WAGMO_20040501143526.ACK Or SAGAS_UAI_AGL_REMCO_20040501143526.ACK
```
