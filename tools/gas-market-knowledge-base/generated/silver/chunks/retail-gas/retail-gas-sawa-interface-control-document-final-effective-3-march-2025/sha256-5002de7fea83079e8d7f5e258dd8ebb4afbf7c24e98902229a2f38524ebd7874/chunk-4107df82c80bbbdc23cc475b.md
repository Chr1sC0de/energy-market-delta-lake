---
{
  "chunk_id": "chunk-4107df82c80bbbdc23cc475b",
  "chunk_ordinal": 751,
  "chunk_text_sha256": "d3cd3337d94aa14d0202e2b9bbcf3d422f72627b9451e1e1de9c58a1c8e46e80",
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
              "b": 554.2539829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.3359999999997,
              "t": 592.1859829101563
            },
            "charspan": [
              0,
              176
            ],
            "page_no": 246
          }
        ],
        "self_ref": "#/texts/2503"
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
              "b": 493.05398291015626,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.2519999999998,
              "t": 544.7859829101563
            },
            "charspan": [
              0,
              224
            ],
            "page_no": 246
          }
        ],
        "self_ref": "#/texts/2504"
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
              "b": 418.0339829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.3599999999997,
              "t": 483.58598291015625
            },
            "charspan": [
              0,
              393
            ],
            "page_no": 246
          }
        ],
        "self_ref": "#/texts/2505"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-4107df82c80bbbdc23cc475b.md",
  "heading_path": [
    "10.3.1.7.4 User's deemed withdrawal and Shippers/Swing Service provider's deemed injections"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-4107df82c80bbbdc23cc475b.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

After the end of each gas day the GRMS system allocates the user's estimated total withdrawal less swing gas repayment amount to shippers using the user allocation instruction.
This process first allocates energy quantities to the shipper where the type of the allocation is quantity and in the order of the ALLOCATION_PRECEDENCE. The requests with the lowest precedence number will get applied first.
There could be three outcomes of this first stage of the process. Not all of the quantity requests are applied because there is not enough energy to allocate to  all  of  the  quantity  requests.  The  exact  UETW  amount  is  allocated  to quantity  requests.  Finally  there  could  be  some  remaining  quantity.  This remaining quantity is allocated using the requests given by percentage.
