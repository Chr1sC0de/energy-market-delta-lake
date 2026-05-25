---
{
  "chunk_id": "chunk-2af3b570f7b38df9f8c6ce50",
  "chunk_ordinal": 228,
  "chunk_text_sha256": "cfff25681008504382239fe1cb123b3c9f718d45a43f074f827642eba2a8b3a6",
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
              "b": 523.4251708984375,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.94961547851562,
              "r": 548.4256591796875,
              "t": 732.9153594970703
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 49
          }
        ],
        "self_ref": "#/tables/39"
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
              "b": 476.7899829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 529.8019999999993,
              "t": 501.2859829101563
            },
            "charspan": [
              0,
              130
            ],
            "page_no": 49
          }
        ],
        "self_ref": "#/texts/531"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-2af3b570f7b38df9f8c6ce50.md",
  "heading_path": [
    "4.1.6.1. MeterDataVerifyRequest"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-2af3b570f7b38df9f8c6ce50.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

Transaction Definition Table cross-reference, 1 = This interface realises the following transactions from the Transaction Definition Table: • 242 - Meter Data Verification Request. Trigger, 1 = The trigger for this transaction could be: • a customer complaint • an anomaly identified by the User. Pre-conditions, 1 = Perceived inconsistency in a User's energy data. Post-conditions, 1 = Network Operator has logged a requirement for data verification.. Transaction acknowledgment specific event codes, 1 = 3646, 3647, 3671 (Also the generic event codes 3603, 3659, 3662, 3673 can be used)
The MeterDataVerifyRequest transaction is used by a User to request confirmation of energy data as supplied by a Network Operator.
