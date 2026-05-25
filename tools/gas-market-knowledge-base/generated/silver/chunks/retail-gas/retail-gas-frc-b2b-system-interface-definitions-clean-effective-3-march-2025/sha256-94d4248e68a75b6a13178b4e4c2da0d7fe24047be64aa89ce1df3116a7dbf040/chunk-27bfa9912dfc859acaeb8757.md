---
{
  "chunk_id": "chunk-27bfa9912dfc859acaeb8757",
  "chunk_ordinal": 235,
  "chunk_text_sha256": "2b94b57433cd94077c85ca6874ccd74c9ee15dcebd4b9deed8c37892c45669b0",
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
              "b": 322.70562744140625,
              "coord_origin": "BOTTOMLEFT",
              "l": 108.52848815917969,
              "r": 548.4422607421875,
              "t": 504.77642822265625
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 51
          }
        ],
        "self_ref": "#/tables/41"
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
              "b": 276.2499829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 529.5199999999993,
              "t": 300.7459829101563
            },
            "charspan": [
              0,
              133
            ],
            "page_no": 51
          }
        ],
        "self_ref": "#/texts/548"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-27bfa9912dfc859acaeb8757.md",
  "heading_path": [
    "4.1.6.2. MeterDataVerifyResponse"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-27bfa9912dfc859acaeb8757.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

Transaction Definition Table cross-reference, 1 = This interface realises the following transactions from the Transaction Definition Table: • 243 - Meter Data Verification Response. Trigger, 1 = The trigger for this transaction is a completed investigation following the receipt of a MeterDataGasVerifyDataRequest transaction. Pre-conditions, 1 = Network Operator has a confirmed meter index reading. Post-conditions, 1 = User has a confirmed meter index reading. Transaction acknowledgment specific event codes, 1 = 3602 (Also the generic event codes 3603, 3659, 3662, 3673 can be used)
The  MeterDataVerifyResponse  transaction  is  used  by  a  Network  Operator  to  respond  to  a MeterDataVerifyRequest from a User.
