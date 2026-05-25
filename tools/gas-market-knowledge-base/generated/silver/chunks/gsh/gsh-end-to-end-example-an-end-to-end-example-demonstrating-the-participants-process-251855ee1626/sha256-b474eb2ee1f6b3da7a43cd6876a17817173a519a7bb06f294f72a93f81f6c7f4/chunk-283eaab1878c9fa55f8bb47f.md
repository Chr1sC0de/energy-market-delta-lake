---
{
  "chunk_id": "chunk-283eaab1878c9fa55f8bb47f",
  "chunk_ordinal": 181,
  "chunk_text_sha256": "afbfe15a1ab098a3df3323955064a09117e35c0929c55423b2b739263252cf34",
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
              "b": 455.5550402523955,
              "coord_origin": "BOTTOMLEFT",
              "l": 72.0,
              "r": 614.44912,
              "t": 465.45712732421873
            },
            "charspan": [
              0,
              112
            ],
            "page_no": 37
          }
        ],
        "self_ref": "#/texts/378"
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
              "b": 431.07504025239547,
              "coord_origin": "BOTTOMLEFT",
              "l": 72.0,
              "r": 259.07912,
              "t": 440.9771273242187
            },
            "charspan": [
              0,
              35
            ],
            "page_no": 37
          }
        ],
        "self_ref": "#/texts/379"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/15"
        },
        "prov": [
          {
            "bbox": {
              "b": 391.20504025239546,
              "coord_origin": "BOTTOMLEFT",
              "l": 90.024,
              "r": 751.8269599999996,
              "t": 415.6271273242187
            },
            "charspan": [
              0,
              184
            ],
            "page_no": 37
          }
        ],
        "self_ref": "#/texts/380"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/15"
        },
        "prov": [
          {
            "bbox": {
              "b": 336.84504025239545,
              "coord_origin": "BOTTOMLEFT",
              "l": 90.024,
              "r": 758.9008,
              "t": 375.7871273242187
            },
            "charspan": [
              0,
              331
            ],
            "page_no": 37
          }
        ],
        "self_ref": "#/texts/381"
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
  "generated_path": "generated/silver/chunks/gsh/gsh-end-to-end-example-an-end-to-end-example-demonstrating-the-participants-process-251855ee1626/sha256-b474eb2ee1f6b3da7a43cd6876a17817173a519a7bb06f294f72a93f81f6c7f4/chunk-283eaab1878c9fa55f8bb47f.md",
  "heading_path": [
    "4.2 Forward Trading Exposure"
  ],
  "path": "generated/silver/chunks/gsh/gsh-end-to-end-example-an-end-to-end-example-demonstrating-the-participants-process-251855ee1626/sha256-b474eb2ee1f6b3da7a43cd6876a17817173a519a7bb06f294f72a93f81f6c7f4/chunk-283eaab1878c9fa55f8bb47f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gsh/gsh-end-to-end-example-an-end-to-end-example-demonstrating-the-participants-process-251855ee1626/sha256-b474eb2ee1f6b3da7a43cd6876a17817173a519a7bb06f294f72a93f81f6c7f4.md"
}
---

Forward trading exposure is an estimate of exposure associated with transactions for gas delivery in the future.
The calculation has two components:
-  Exposure on the Net Position: The difference between a member's buy and seller transactions is their net position.  To estimate the exposure, a margin is applied to the net position.
-  Gain or loss on the offset position: A member's offset position is the quantity of buy transactions that are offset by sell transactions. There is no gas delivery obligation associated with offsetting transaction but they will need to be settled.  As such, any gain or loss on the offset position is incorporated in the exposure.
