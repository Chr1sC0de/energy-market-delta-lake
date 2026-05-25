---
{
  "chunk_id": "chunk-7fe2ec9e38e7411b2f475ca5",
  "chunk_ordinal": 163,
  "chunk_text_sha256": "93e98f464435092acf5a0cd4e572ad58c2889255f0476d0b5f06176c2a255837",
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
              "b": 523.12646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 74.34300994873047,
              "r": 494.318115234375,
              "t": 710.4424285888672
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 55
          }
        ],
        "self_ref": "#/tables/58"
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
              "b": 493.32501095552055,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.5583999999997,
              "t": 518.2270980273438
            },
            "charspan": [
              0,
              100
            ],
            "page_no": 55
          }
        ],
        "self_ref": "#/texts/630"
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
              "b": 469.32501095552055,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 481.24912,
              "t": 479.2270980273438
            },
            "charspan": [
              0,
              83
            ],
            "page_no": 55
          }
        ],
        "self_ref": "#/texts/631"
      },
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
              "b": 286.3443603515625,
              "coord_origin": "BOTTOMLEFT",
              "l": 74.36921691894531,
              "r": 494.9212951660156,
              "t": 460.85906982421875
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 55
          }
        ],
        "self_ref": "#/tables/59"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-7fe2ec9e38e7411b2f475ca5.md",
  "heading_path": [
    "4.1.9.1 Withdrawal Transfer Notice"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-7fe2ec9e38e7411b2f475ca5.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

TRANSACTION DEFINITION TABLE CROSS- REFERENCE, 1 = • 205 WITHDRAWAL TRANSFER NOTICE (TO AEMO). Trigger, 1 = None.. Pre-conditions, 1 = Transfer has not been completed.. Post-conditions, 1 = AEMO has been notified of transfer withdrawal.. Transaction acknowledgment specific event codes, 1 = 3025, 3026
The Withdrawal Transfer Notice transaction is realised with CATSChangeWithdrawal aseXML transaction.
The following data elements are to be supplied with the Withdrawal Transfer Notice:
RequestID, CATSCHANGEWITHDRAWAL.Received From:.Sent To:.Mandatory / Optional / Not Required = M. RequestID, New FRO.AEMO.Usage = The ID assigned by AEMO to the Change Request.
