---
{
  "chunk_id": "chunk-cae6d9331d0766397ee8f8de",
  "chunk_ordinal": 409,
  "chunk_text_sha256": "d4ec8e46bed3fbb45504dc447d0c614389da5b013a0c35400202f4472ef7d0b0",
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
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/233"
        },
        "prov": [
          {
            "bbox": {
              "b": 76.15901095552056,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 530.4361600000001,
              "t": 98.66109802734377
            },
            "charspan": [
              0,
              176
            ],
            "page_no": 99
          }
        ],
        "self_ref": "#/texts/1653"
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
              "b": 723.6350109555206,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 530.44384,
              "t": 746.1370980273438
            },
            "charspan": [
              0,
              164
            ],
            "page_no": 100
          }
        ],
        "self_ref": "#/texts/1657"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "text",
        "parent": {
          "$ref": "#/groups/234"
        },
        "prov": [
          {
            "bbox": {
              "b": 685.5642379168465,
              "coord_origin": "BOTTOMLEFT",
              "l": 114.62,
              "r": 341.29912,
              "t": 695.7370980273438
            },
            "charspan": [
              0,
              42
            ],
            "page_no": 100
          }
        ],
        "self_ref": "#/texts/1658"
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
              "b": 635.4350109555205,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 141.92912,
              "t": 645.3370980273437
            },
            "charspan": [
              0,
              6
            ],
            "page_no": 100
          }
        ],
        "self_ref": "#/texts/1659"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-retail-market-procedures-qld-clean-effective-30-january-2026/sha256-30adf3d40c1181c03664716b378f62c52896d6129fa2fb7220ce9f469cae7a52.md",
    "source_manifest_line_number": 34,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-retail-markets/procedures-policies-and-guides/queensland",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/retail_markets_and_metering/market-procedures/qld/2025/retail-market-procedures-qld-v23-clean.pdf?rev=05049f0ee3924eb0815b8e757753a153&sc_lang=en"
  },
  "content_sha256": "30adf3d40c1181c03664716b378f62c52896d6129fa2fb7220ce9f469cae7a52",
  "corpus": "retail_gas",
  "document_family": "retail-gas__retail-market-procedures-qld-clean-effective-30-january-2026",
  "document_family_id": "retail-gas__retail-market-procedures-qld-clean-effective-30-january-2026",
  "document_identity": "retail-gas/retail-gas-retail-market-procedures-qld-clean-effective-30-january-2026/sha256-30adf3d40c1181c03664716b378f62c52896d6129fa2fb7220ce9f469cae7a52",
  "document_title": "##### Retail Market Procedures QLD (clean) Effective 30 January 2026",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-retail-market-procedures-qld-clean-effective-30-january-2026/sha256-30adf3d40c1181c03664716b378f62c52896d6129fa2fb7220ce9f469cae7a52/chunk-cae6d9331d0766397ee8f8de.md",
  "heading_path": [
    "2.3. Calculating Daily Load when Meter Readings are not available"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-retail-market-procedures-qld-clean-effective-30-january-2026/sha256-30adf3d40c1181c03664716b378f62c52896d6129fa2fb7220ce9f469cae7a52/chunk-cae6d9331d0766397ee8f8de.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-retail-market-procedures-qld-clean-effective-30-january-2026/sha256-30adf3d40c1181c03664716b378f62c52896d6129fa2fb7220ce9f469cae7a52.md"
}
---

- 2.3.1 Where a meter reading is not available, AEMO must estimate the consumed energy for a basic meter for a second tier supply point based on the weather measured in effective
degree day and the base load and temperature sensitivity factor provided to AEMO by Distributors under clauses 2.8.1(c) and 2.8.1(d) of these Procedures as follows:
Consumed energy d,j  = BLj + (TSFj x EDDd)
Where:
