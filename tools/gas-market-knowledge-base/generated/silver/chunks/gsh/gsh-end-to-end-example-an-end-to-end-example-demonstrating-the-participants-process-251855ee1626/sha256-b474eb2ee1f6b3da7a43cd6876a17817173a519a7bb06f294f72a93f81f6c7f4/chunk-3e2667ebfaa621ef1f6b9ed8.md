---
{
  "chunk_id": "chunk-3e2667ebfaa621ef1f6b9ed8",
  "chunk_ordinal": 197,
  "chunk_text_sha256": "40d01fd4dcee14ed449f4113904b6ae601fe55b2ec6f991c82ddbe3e8d2f87d7",
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
              "b": 207.2250402523955,
              "coord_origin": "BOTTOMLEFT",
              "l": 72.0,
              "r": 769.3852800000001,
              "t": 231.64712732421867
            },
            "charspan": [
              0,
              247
            ],
            "page_no": 41
          }
        ],
        "self_ref": "#/texts/425"
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
              "b": 168.07504025239552,
              "coord_origin": "BOTTOMLEFT",
              "l": 72.0,
              "r": 729.8167999999995,
              "t": 192.52712732421867
            },
            "charspan": [
              0,
              177
            ],
            "page_no": 41
          }
        ],
        "self_ref": "#/texts/426"
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
              "b": 143.4750402523955,
              "coord_origin": "BOTTOMLEFT",
              "l": 72.0,
              "r": 721.00912,
              "t": 153.3771273242187
            },
            "charspan": [
              0,
              133
            ],
            "page_no": 41
          }
        ],
        "self_ref": "#/texts/427"
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
  "generated_path": "generated/silver/chunks/gsh/gsh-end-to-end-example-an-end-to-end-example-demonstrating-the-participants-process-251855ee1626/sha256-b474eb2ee1f6b3da7a43cd6876a17817173a519a7bb06f294f72a93f81f6c7f4/chunk-3e2667ebfaa621ef1f6b9ed8.md",
  "heading_path": [
    "4.3 Forward Reallocation"
  ],
  "path": "generated/silver/chunks/gsh/gsh-end-to-end-example-an-end-to-end-example-demonstrating-the-participants-process-251855ee1626/sha256-b474eb2ee1f6b3da7a43cd6876a17817173a519a7bb06f294f72a93f81f6c7f4/chunk-3e2667ebfaa621ef1f6b9ed8.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gsh/gsh-end-to-end-example-an-end-to-end-example-demonstrating-the-participants-process-251855ee1626/sha256-b474eb2ee1f6b3da7a43cd6876a17817173a519a7bb06f294f72a93f81f6c7f4.md"
}
---

The Forward Reallocation Amount is an estimate of the exposure associated with reallocations from the current processing day into the future. Reallocations decrease the exposure of the Credit Participant but increase that of the Debit Participant.
Different equations exist for estimating the exposure for Dollar and Energy Reallocations and there are different equations for the Debit Participant and the Credit Participant.
The exposure is calculated for each reallocation (4.3.1, 4.3.2) and then aggregated into a total Forward Reallocation Amount (4.3.3).
