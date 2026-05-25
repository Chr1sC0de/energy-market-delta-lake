---
{
  "chunk_id": "chunk-ccda93dffd5587a7c3137829",
  "chunk_ordinal": 94,
  "chunk_text_sha256": "0a77c9619aa094fc0a0d3549559bb50a2aad76f38677b493c5d4f9cf3b6b7718",
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
              "b": 321.3450109555206,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.3817599999998,
              "t": 361.2470980273438
            },
            "charspan": [
              0,
              236
            ],
            "page_no": 20
          }
        ],
        "self_ref": "#/texts/129"
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
              "b": 63.2196044921875,
              "coord_origin": "BOTTOMLEFT",
              "l": 74.12421417236328,
              "r": 534.960693359375,
              "t": 313.5849609375
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 20
          }
        ],
        "self_ref": "#/tables/19"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-ccda93dffd5587a7c3137829.md",
  "heading_path": [
    "4.1.1 Overview"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-ccda93dffd5587a7c3137829.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

This section describes transactions that provide support for the Customer Administration and Transfer  functionality.  The  table  below  maps  aseXML  transactions  to  transaction  types referenced in the Transaction Definition Table.
CATSChangeRequest, TRANSACTION DEFINITION TABLE REF = 170. CATSChangeRequest, TRANSACTION TYPE FROM TRANSACTION DEFINITION TABLE = Initiate Transfer Request. CATSChangeRequest, TRANSACTION DEFINITION TABLE REF = 182. CATSChangeRequest, TRANSACTION TYPE FROM TRANSACTION DEFINITION TABLE = Response for Request Standing Data. CATSChangeRequest, TRANSACTION DEFINITION TABLE REF = 214. CATSChangeRequest, TRANSACTION TYPE FROM TRANSACTION DEFINITION TABLE = Alternative Transfer Date. CATSNotification, TRANSACTION DEFINITION TABLE REF = 183, 184, 185. CATSNotification, TRANSACTION TYPE FROM TRANSACTION DEFINITION TABLE = Notice of Transfer. CATSNotification, TRANSACTION DEFINITION TABLE REF = 219, 220. CATSNotification, TRANSACTION TYPE FROM TRANSACTION DEFINITION TABLE = Alternative Transfer Date (Notification). CATSNotification, TRANSACTION DEFINITION TABLE REF = 193, 194, 195A. CATSNotification, TRANSACTION TYPE FROM TRANSACTION DEFINITION TABLE = Objection Notification or Objection Withdrawal Notification. CATSNotification, TRANSACTION DEFINITION TABLE REF = 206, 207, 208, 206A. CATSNotification, TRANSACTION TYPE FROM TRANSACTION DEFINITION TABLE = Withdrawal Transfer Notice (Notification)
