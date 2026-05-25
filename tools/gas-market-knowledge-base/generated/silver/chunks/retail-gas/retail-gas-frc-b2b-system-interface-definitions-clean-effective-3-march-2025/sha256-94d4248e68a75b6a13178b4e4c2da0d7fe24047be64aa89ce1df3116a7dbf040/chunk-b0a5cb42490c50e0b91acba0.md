---
{
  "chunk_id": "chunk-b0a5cb42490c50e0b91acba0",
  "chunk_ordinal": 224,
  "chunk_text_sha256": "b368e8c205af6baeb7a1b2b7e299b298c98345fe0d37c7455c16bf0a528448b1",
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
              "b": 690.7799829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 526.0159999999994,
              "t": 729.0759829101563
            },
            "charspan": [
              0,
              220
            ],
            "page_no": 47
          }
        ],
        "self_ref": "#/texts/487"
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
              "b": 670.9799829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 380.806,
              "t": 681.6759829101563
            },
            "charspan": [
              0,
              64
            ],
            "page_no": 47
          }
        ],
        "self_ref": "#/texts/488"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "caption",
        "parent": {
          "$ref": "#/pictures/67"
        },
        "prov": [
          {
            "bbox": {
              "b": 396.71533563742906,
              "coord_origin": "BOTTOMLEFT",
              "l": 182.18,
              "r": 415.72,
              "t": 405.09290291015634
            },
            "charspan": [
              0,
              52
            ],
            "page_no": 47
          }
        ],
        "self_ref": "#/texts/489"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-b0a5cb42490c50e0b91acba0.md",
  "heading_path": [
    "4.1.6. Meter Data Verification"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-b0a5cb42490c50e0b91acba0.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

The Meter Data Verification transactions are used when a User needs to seek verification of the meter data from a Network Operator.  This may be as the result of a customer complaint or an anomaly identified by the User.
The activity diagram below is a high level view of this process:
Figure 4-18 Meter Data Verification Activity Diagram
