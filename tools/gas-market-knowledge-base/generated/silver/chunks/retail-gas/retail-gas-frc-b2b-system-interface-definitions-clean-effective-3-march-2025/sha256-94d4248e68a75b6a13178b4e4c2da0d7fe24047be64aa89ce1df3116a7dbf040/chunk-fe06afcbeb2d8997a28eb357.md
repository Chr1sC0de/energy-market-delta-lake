---
{
  "chunk_id": "chunk-fe06afcbeb2d8997a28eb357",
  "chunk_ordinal": 353,
  "chunk_text_sha256": "84aede2a22d05adb4b2feb45b18447474f9b6f85a585f8bdc0e5532f40867fc5",
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
              "b": 219.06732177734375,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.5394287109375,
              "r": 548.8604125976562,
              "t": 481.87432861328125
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 96
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
              "b": 172.29998291015625,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 529.7719999999993,
              "t": 196.79598291015623
            },
            "charspan": [
              0,
              123
            ],
            "page_no": 96
          }
        ],
        "self_ref": "#/texts/1011"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-fe06afcbeb2d8997a28eb357.md",
  "heading_path": [
    "4.3.2.2. NMIDiscoveryRequest"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-fe06afcbeb2d8997a28eb357.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

Transaction Definition Table cross-reference, 1 = This interface realises the following transactions from the Transaction Definition Table: • 280 - Discovery Request Note: This transaction is only used when an address is used as the input. The NMIStandingDataRequest transaction also realises this transaction when the input is a MIRN.. Trigger, 1 = This interface is triggered when a User requests MIRN Standing Data for a MIRN that they know only by address.. Pre-conditions, 1 = User has an Explicit Informed Consent from the subject customer in respect of the distribution supply point at the address.. Post-conditions, 1 = Network Operator has logged the Discovery Request. Transaction acknowledgment specific event codes, 1 = 3606, 3608, 3638, 3639, 3660 (Also the generic event codes 3603, 3659, 3662, 3673 can be used)
The NMIDiscoveryRequest transaction is used by the User to request a MIRN and MIRN Standing Data from the Network Operator.
