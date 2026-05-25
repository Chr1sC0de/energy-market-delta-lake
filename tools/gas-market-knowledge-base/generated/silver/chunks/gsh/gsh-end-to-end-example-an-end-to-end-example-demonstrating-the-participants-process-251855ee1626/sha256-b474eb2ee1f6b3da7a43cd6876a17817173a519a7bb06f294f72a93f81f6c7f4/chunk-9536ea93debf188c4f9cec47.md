---
{
  "chunk_id": "chunk-9536ea93debf188c4f9cec47",
  "chunk_ordinal": 121,
  "chunk_text_sha256": "f7b2805a643259dd67d2500adc1a0ea17b85aea0472ff073e9686449aa6bf9f9",
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
              "b": 336.6050402523955,
              "coord_origin": "BOTTOMLEFT",
              "l": 72.0,
              "r": 753.3784000000003,
              "t": 361.0271273242187
            },
            "charspan": [
              0,
              157
            ],
            "page_no": 13
          }
        ],
        "self_ref": "#/texts/120"
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
              "b": 297.4850402523955,
              "coord_origin": "BOTTOMLEFT",
              "l": 72.0,
              "r": 725.08912,
              "t": 321.9071273242187
            },
            "charspan": [
              0,
              281
            ],
            "page_no": 13
          }
        ],
        "self_ref": "#/texts/121"
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
              "b": 243.82504025239552,
              "coord_origin": "BOTTOMLEFT",
              "l": 72.0,
              "r": 735.9447999999999,
              "t": 282.76712732421873
            },
            "charspan": [
              0,
              296
            ],
            "page_no": 13
          }
        ],
        "self_ref": "#/texts/122"
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
              "b": 190.18504025239554,
              "coord_origin": "BOTTOMLEFT",
              "l": 72.0,
              "r": 753.2051200000002,
              "t": 229.1271273242187
            },
            "charspan": [
              0,
              339
            ],
            "page_no": 13
          }
        ],
        "self_ref": "#/texts/123"
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
  "generated_path": "generated/silver/chunks/gsh/gsh-end-to-end-example-an-end-to-end-example-demonstrating-the-participants-process-251855ee1626/sha256-b474eb2ee1f6b3da7a43cd6876a17817173a519a7bb06f294f72a93f81f6c7f4/chunk-9536ea93debf188c4f9cec47.md",
  "heading_path": [
    "2.3.2 Assign Delivery Point to Sell Positions"
  ],
  "path": "generated/silver/chunks/gsh/gsh-end-to-end-example-an-end-to-end-example-demonstrating-the-participants-process-251855ee1626/sha256-b474eb2ee1f6b3da7a43cd6876a17817173a519a7bb06f294f72a93f81f6c7f4/chunk-9536ea93debf188c4f9cec47.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gsh/gsh-end-to-end-example-an-end-to-end-example-demonstrating-the-participants-process-251855ee1626/sha256-b474eb2ee1f6b3da7a43cd6876a17817173a519a7bb06f294f72a93f81f6c7f4.md"
}
---

The delivery point relevant to a net delivery position is determined based on the delivery point submitted by a seller at the time of their order submission.
The seller can enter into multiple transactions for gas day selecting a different delivery point for each transaction.  As such, a Trading Participant's offsetting buy and sell transactions could result in a net sell position that could be attributable to multiple delivery points.
In this event, the seller's net position is split by delivery point.  The splitting by net delivery point ensures that each matched gas delivery obligation has a specific delivery point.  The delivery point(s) associated with the most recent transactions is assigned to the net delivery position.
In the example, Participant 5 has an aggregate sale quantity of 19,000 GJ and a net sell position of 12,000.   Multiple delivery points can be attributed to this net position.  As illustrated below in Table 10, the delivery points associated with the most recent transactions are retrieved and then used to split the net delivery position.
