---
{
  "chunk_id": "chunk-612cec65a653087baeb3bbab",
  "chunk_ordinal": 285,
  "chunk_text_sha256": "946ebaa7513aa2eee2ece1d129058c1d6b8721b8ec06f3107a92d14c31d13754",
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
              "b": 103.00177001953125,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.68035125732422,
              "r": 548.8443603515625,
              "t": 481.1566162109375
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 68
          }
        ],
        "self_ref": "#/tables/52"
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
              "b": 698.1490783691406,
              "coord_origin": "BOTTOMLEFT",
              "l": 108.09683227539062,
              "r": 548.6854858398438,
              "t": 749.4120788574219
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 69
          }
        ],
        "self_ref": "#/tables/53"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-612cec65a653087baeb3bbab.md",
  "heading_path": [
    "4.2.3.4. ServiceOrderRequest"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-612cec65a653087baeb3bbab.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

Transaction Definition Table cross-reference, 1 = This interface realises the following transactions from the Transaction Definition Table: • 87 - Meter Fix Request 'Simple' or 'Complex' Type • 101 - Meter Change Request • 151 - Meter Removal Request • 310 - Service Connection Request • 312 - Service Disconnection Request • 314 - Service Orders for Priority C - K • 316 - Relocate Service Connection Request • 318 - Upgrade Service Size Request • 320 - Upgrade Meter Size Request. Trigger, 1 = 1. User has a requirement for a Network Operator to supply a service 2. Change to Service Order requirement. Pre-conditions, 1 = 1. None 2. Service Order Request has been raised 3. Service Order Request has been raised. Post-conditions, 1 = 1. Network Operator has logged the Service Order and created Work Request 2. Network Operator has logged cancellation request
Transaction acknowledgment specific event codes, 1 = 3601, 3604, 3608, 3613, 3616-3619, 3644, 3675 (Also the generic event codes 3603, 3659, 3662, 3673 can be used)
