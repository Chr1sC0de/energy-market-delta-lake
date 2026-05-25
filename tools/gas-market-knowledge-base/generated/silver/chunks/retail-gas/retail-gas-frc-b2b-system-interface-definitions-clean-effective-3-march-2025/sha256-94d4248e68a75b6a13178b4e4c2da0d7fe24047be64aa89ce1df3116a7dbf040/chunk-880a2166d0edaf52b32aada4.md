---
{
  "chunk_id": "chunk-880a2166d0edaf52b32aada4",
  "chunk_ordinal": 312,
  "chunk_text_sha256": "cee293b8a222fcca31ae33e2c2df285dd8852bcbc77809a3928292aa42e07b1f",
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
              "b": 72.048095703125,
              "coord_origin": "BOTTOMLEFT",
              "l": 108.01502990722656,
              "r": 548.2633056640625,
              "t": 671.1321411132812
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 81
          }
        ],
        "self_ref": "#/tables/61"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md",
    "source_manifest_line_number": 26,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-retail-markets/procedures-policies-and-guides/western-australia",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/retail_markets_and_metering/market-procedures/sa_and_wa/2025/frc-b2b-system-interface-definitions-v53-clean.pdf?rev=c312fd435a0b46d4ac08cc4b56c74493&sc_lang=en"
  },
  "content_sha256": "94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040",
  "corpus": "retail_gas",
  "document_family": "retail-gas__frc-b2b-system-interface-definitions-clean-effective-3-march-2025",
  "document_family_id": "retail-gas__frc-b2b-system-interface-definitions-clean-effective-3-march-2025",
  "document_identity": "retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040",
  "document_title": "##### FRC B2B System Interface Definitions (Clean) Effective 3 March 2025",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-880a2166d0edaf52b32aada4.md",
  "heading_path": [
    "ServiceOrderResponse"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-880a2166d0edaf52b32aada4.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

Transaction Definition Table cross-reference, 1 = This interface realises the following transactions from the Transaction Definition Table: • 87A - Meter Fix Request 'Simple' or 'Complex' Type Response • 92 - Meter Fix Complete • 93 - No Access to Complete Meter Fix • 101A - Meter Change Request Response • 104 - No Access to Complete Meter Change • 108 - Meter Change Completed • 125 - Meter Upgrade Completed • 151A - Meter Removal Request Response • 154 - No Access to Complete Meter Removal • 157 - Meter Removal Complete • 310A - Service Connection Request Response • 311 - Service Connection Complete • 312A - Service Disconnection Request Response • 313 - Service Disconnection Complete • 314A - Service Orders for Priority C - K Response • 315 - Service Orders Completed for Priority A -K • 316A - Relocate Service Connection Request Response • 317 - Relocate Service Complete • 318A - Upgrade Service Size Request Response • 319 - Upgrade Service Size Complete • 320A - Upgrade Meter Size Request Response. Trigger, 1 = 1. Work Request Number generated 2. Service Order Completed, Cancelled, or Attempted with No Access. Pre-conditions, 1 = 1. Network Operator has logged Service Order Request and generated Work Request Number 2. Network Operator has closed Work Request
