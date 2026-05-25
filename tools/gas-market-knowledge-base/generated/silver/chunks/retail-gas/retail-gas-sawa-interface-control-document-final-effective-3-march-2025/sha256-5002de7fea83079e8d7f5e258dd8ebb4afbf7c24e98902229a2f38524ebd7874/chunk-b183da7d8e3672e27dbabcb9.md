---
{
  "chunk_id": "chunk-b183da7d8e3672e27dbabcb9",
  "chunk_ordinal": 205,
  "chunk_text_sha256": "06e404d2d2456a2a02a79a15ae892244adfc3c92e4fa1548091edbae5ff45207",
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
              "b": 85.82398291015625,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.5,
              "t": 137.5759829101563
            },
            "charspan": [
              0,
              310
            ],
            "page_no": 45
          },
          {
            "bbox": {
              "b": 717.0039829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.3479999999996,
              "t": 741.1359829101564
            },
            "charspan": [
              311,
              455
            ],
            "page_no": 46
          }
        ],
        "self_ref": "#/texts/614"
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
              "b": 697.2039829101564,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 291.89,
              "t": 707.5359829101563
            },
            "charspan": [
              0,
              29
            ],
            "page_no": 46
          }
        ],
        "self_ref": "#/texts/619"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-b183da7d8e3672e27dbabcb9.md",
  "heading_path": [
    "Participants Push Message to GRMS"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-b183da7d8e3672e27dbabcb9.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

Market Participants will create a csv message file (with a .CSV extension note the case), compress it using zip, change the file extension to .TMP and push it to their Inbox. Whilst the file is being created it has the file name suffix .TMP.  Once the file transfer is  complete the file will be renamed in one atomic (uninterruptible) operation (rather than a copy and a rename). The file will be renamed to change the file name suffix from .TMP to .ZIP.
Filename format for file is :
