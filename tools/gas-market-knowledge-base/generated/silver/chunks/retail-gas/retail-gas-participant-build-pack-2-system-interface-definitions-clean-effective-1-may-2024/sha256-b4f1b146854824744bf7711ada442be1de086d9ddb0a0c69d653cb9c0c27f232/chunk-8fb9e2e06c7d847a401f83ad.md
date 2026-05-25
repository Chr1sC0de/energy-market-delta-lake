---
{
  "chunk_id": "chunk-8fb9e2e06c7d847a401f83ad",
  "chunk_ordinal": 164,
  "chunk_text_sha256": "9038df62965790dafa4bbd8333a8ea9dfbd4f6e75345ffd2a87e9aebb5e23a30",
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
              "b": 454.09716796875,
              "coord_origin": "BOTTOMLEFT",
              "l": 73.75260925292969,
              "r": 494.39007568359375,
              "t": 711.1456604003906
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 56
          }
        ],
        "self_ref": "#/tables/60"
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
              "b": 424.8050109555206,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.3596799999996,
              "t": 449.7070980273438
            },
            "charspan": [
              0,
              108
            ],
            "page_no": 56
          }
        ],
        "self_ref": "#/texts/636"
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
              "b": 400.8050109555206,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 481.24912,
              "t": 410.7070980273438
            },
            "charspan": [
              0,
              83
            ],
            "page_no": 56
          }
        ],
        "self_ref": "#/texts/637"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-8fb9e2e06c7d847a401f83ad.md",
  "heading_path": [
    "4.1.9.2 Withdrawal Transfer Notice (Notification)"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-8fb9e2e06c7d847a401f83ad.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

Trigger, 206 WITHDRAWAL TRANSFER NOTICE (TO CURRENT FRO) 207 WITHDRAWAL TRANSFER NOTICE (TO AFFECTED FRO) 208 WITHDRAWAL TRANSFER NOTICE (TO DISTRIBUTOR) 206A WITHDRAWAL TRANSFER NOTICE (TO NEW FRO) = Withdrawal Transfer Notice. Pre-conditions, 206 WITHDRAWAL TRANSFER NOTICE (TO CURRENT FRO) 207 WITHDRAWAL TRANSFER NOTICE (TO AFFECTED FRO) 208 WITHDRAWAL TRANSFER NOTICE (TO DISTRIBUTOR) 206A WITHDRAWAL TRANSFER NOTICE (TO NEW FRO) = Valid withdrawal notice. Post-conditions, 206 WITHDRAWAL TRANSFER NOTICE (TO CURRENT FRO) 207 WITHDRAWAL TRANSFER NOTICE (TO AFFECTED FRO) 208 WITHDRAWAL TRANSFER NOTICE (TO DISTRIBUTOR) 206A WITHDRAWAL TRANSFER NOTICE (TO NEW FRO) = Terminated transfer. Transaction acknowledgment specific event codes, 206 WITHDRAWAL TRANSFER NOTICE (TO CURRENT FRO) 207 WITHDRAWAL TRANSFER NOTICE (TO AFFECTED FRO) 208 WITHDRAWAL TRANSFER NOTICE (TO DISTRIBUTOR) 206A WITHDRAWAL TRANSFER NOTICE (TO NEW FRO) = 3040
The  Withdrawal  Transfer  Notice  (Notification)  is  realised  with  CATSNotification  aseXML transaction.
The following data elements are to be supplied with the Withdrawal Transfer Notice:
