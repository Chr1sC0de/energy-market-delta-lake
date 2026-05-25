---
{
  "chunk_id": "chunk-b6fa3bea0cd895ea15d3fca0",
  "chunk_ordinal": 130,
  "chunk_text_sha256": "b885f3b4fd24ee9fd90bb0d6b8ad46d063d70421fbaa6803ee28a1e12f675e7e",
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
              "b": 429.7550402523955,
              "coord_origin": "BOTTOMLEFT",
              "l": 72.0,
              "r": 760.62912,
              "t": 439.6571273242187
            },
            "charspan": [
              0,
              142
            ],
            "page_no": 18
          }
        ],
        "self_ref": "#/texts/170"
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
              "b": 376.08504025239546,
              "coord_origin": "BOTTOMLEFT",
              "l": 72.0,
              "r": 769.26912,
              "t": 415.0271273242187
            },
            "charspan": [
              0,
              320
            ],
            "page_no": 18
          }
        ],
        "self_ref": "#/texts/171"
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
              "b": 347.9474826833347,
              "coord_origin": "BOTTOMLEFT",
              "l": 72.0,
              "r": 381.05888000000004,
              "t": 356.8808873242187
            },
            "charspan": [
              0,
              66
            ],
            "page_no": 18
          }
        ],
        "self_ref": "#/texts/172"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/gsh/gsh-end-to-end-example-an-end-to-end-example-demonstrating-the-participants-process-251855ee1626/sha256-b474eb2ee1f6b3da7a43cd6876a17817173a519a7bb06f294f72a93f81f6c7f4.md",
    "source_manifest_line_number": 15,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-supply-hub-gsh/exchange-agreement-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/gas_supply_hubs/market_operations/2016/gas-supply-hub-end-to-end-example-v1-0.pdf?rev=95e2eb856bc543d4a7868fa187ea61af&sc_lang=en"
  },
  "content_sha256": "b474eb2ee1f6b3da7a43cd6876a17817173a519a7bb06f294f72a93f81f6c7f4",
  "corpus": "gsh",
  "document_family": "gsh__end-to-end-example-an-end-to-end-example-demonstrating-the-participants-processes-and-transactions-relating-to-a-trade-in-the-gsh",
  "document_family_id": "gsh__end-to-end-example-an-end-to-end-example-demonstrating-the-participants-processes-and-transactions-relating-to-a-trade-in-the-gsh",
  "document_identity": "gsh/gsh-end-to-end-example-an-end-to-end-example-demonstrating-the-participants-process-251855ee1626/sha256-b474eb2ee1f6b3da7a43cd6876a17817173a519a7bb06f294f72a93f81f6c7f4",
  "document_title": "##### End-to-end example An end-to-end example demonstrating the participants, processes and transactions relating to a trade in the GSH.",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/gsh/gsh-end-to-end-example-an-end-to-end-example-demonstrating-the-participants-process-251855ee1626/sha256-b474eb2ee1f6b3da7a43cd6876a17817173a519a7bb06f294f72a93f81f6c7f4/chunk-b6fa3bea0cd895ea15d3fca0.md",
  "heading_path": [
    "3.1.1 Average Price"
  ],
  "path": "generated/silver/chunks/gsh/gsh-end-to-end-example-an-end-to-end-example-demonstrating-the-participants-process-251855ee1626/sha256-b474eb2ee1f6b3da7a43cd6876a17817173a519a7bb06f294f72a93f81f6c7f4/chunk-b6fa3bea0cd895ea15d3fca0.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gsh/gsh-end-to-end-example-an-end-to-end-example-demonstrating-the-participants-process-251855ee1626/sha256-b474eb2ee1f6b3da7a43cd6876a17817173a519a7bb06f294f72a93f81f6c7f4.md"
}
---

The Average Price is an input into the Delivery Variance Settlement (see 3.3.4) as well as the settlement of Energy Reallocations (see 3.4.2).
The Average Price is calculated for each Gas Day and Trading Location and is determined following the end of trading on the specific Gas Day (i.e after the Balance-of-day has finished trading).  The Average Price calculation is a volume weighted average across all transactions covering the Gas Day and Trading Location.
The Average Price calculation does not include pre-matched trades.
