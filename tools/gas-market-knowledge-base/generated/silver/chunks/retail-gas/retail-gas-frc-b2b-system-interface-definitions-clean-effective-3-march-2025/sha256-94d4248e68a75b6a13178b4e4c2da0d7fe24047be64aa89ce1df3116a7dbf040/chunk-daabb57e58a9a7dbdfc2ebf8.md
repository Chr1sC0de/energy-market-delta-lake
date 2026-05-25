---
{
  "chunk_id": "chunk-daabb57e58a9a7dbdfc2ebf8",
  "chunk_ordinal": 416,
  "chunk_text_sha256": "a0251521dff1451724a419c64ca4f15466029b6f89cfcb0ff827e24b854122cc",
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
              "b": 469.9359436035156,
              "coord_origin": "BOTTOMLEFT",
              "l": 108.21717834472656,
              "r": 548.5807495117188,
              "t": 732.7260513305664
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 122
          }
        ],
        "self_ref": "#/tables/85"
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
              "b": 423.38998291015633,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 529.5679999999998,
              "t": 447.88598291015626
            },
            "charspan": [
              0,
              113
            ],
            "page_no": 122
          }
        ],
        "self_ref": "#/texts/1193"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-daabb57e58a9a7dbdfc2ebf8.md",
  "heading_path": [
    "4.3.2.5. NMIStandingDataRequest"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-daabb57e58a9a7dbdfc2ebf8.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

Transaction Definition Table cross-reference, 1 = This interface realises the following transactions from the GPTWG Transaction Definition Table: • 280 - Discovery Request Note: This transaction is only used when a MIRN is used as the input. The NMIDiscoveryRequest transaction also realises this transaction when the input is an address.. Trigger, 1 = This interface is triggered when a User requests MIRN Standing Data for a known MIRN.. Pre-conditions, 1 = User has Explicit Informed Consent from the subject customer in respect of the distribution supply point referenced by the MIRN.. Post-conditions, 1 = Network Operator has logged the Standing Data Request. Transaction acknowledgment specific event codes, 1 = 3638, 3660 (Also the generic event codes 3603, 3659, 3662, 3673 can be used)
The NMIStandingDataRequest transaction is used by the User to request MIRN Standing Data from a Network Operator.
