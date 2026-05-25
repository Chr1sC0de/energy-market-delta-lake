---
{
  "chunk_id": "chunk-cb009120faf7d4edd558d68b",
  "chunk_ordinal": 186,
  "chunk_text_sha256": "dd5fb8ed1621fc97ac654d8ee6af6c95a84ec67377e9354c6bb8adab4ae3aaee",
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
        "label": "table",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 479.794921875,
              "coord_origin": "BOTTOMLEFT",
              "l": 74.11993408203125,
              "r": 494.01922607421875,
              "t": 710.4929656982422
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 67
          }
        ],
        "self_ref": "#/tables/71"
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
              "b": 450.12501095552057,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.6168799999997,
              "t": 475.0270980273438
            },
            "charspan": [
              0,
              103
            ],
            "page_no": 67
          }
        ],
        "self_ref": "#/texts/815"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md",
    "source_manifest_line_number": 31,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-retail-markets/procedures-policies-and-guides/victoria",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/retail_markets_and_metering/market-procedures/vic/2024/participant-build-pack-2--system-interface-definitions-v-36-clean.pdf?rev=0420b92c0a5e4d879175ec3003826d7d&sc_lang=en"
  },
  "content_sha256": "b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232",
  "corpus": "retail_gas",
  "document_family": "retail-gas__participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024",
  "document_family_id": "retail-gas__participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024",
  "document_identity": "retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232",
  "document_title": "##### Participant Build Pack 2 - System Interface Definitions (Clean) Effective 1 May 2024",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-cb009120faf7d4edd558d68b.md",
  "heading_path": [
    "4.1.12.1 Transfer Request State Change Notification Transaction"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-cb009120faf7d4edd558d68b.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

TRANSACTION DEFINITION TABLE CROSS- REFERENCE, 1 = 232 TRANSFER STATUS UPDATE (TO NEW FRO) 233 TRANSFER STATUS UPDATE (TO CURRENT FRO) 234 TRANSFER STATUS UPDATE (TO DISTRIBUTOR) 235 TRANSFER STATUS UPDATE (TO AFFECTED FRO). Trigger, 1 = Internal processing at AEMO.. Pre-conditions, 1 = The Change Request has passed the end of its Objection Period and has no active objections against it.. Post-conditions, 1 = All Organisations are notified on Change Request state change.. Transaction acknowledgment specific event codes, 1 = 3040
This transaction is realised with the aseXML CATSNotification. For the transaction details see 4.1.3.1.
