---
{
  "chunk_id": "chunk-54cc2ada225e4a7c20be7c6b",
  "chunk_ordinal": 245,
  "chunk_text_sha256": "84d73687aa4442d6ead6bf44f2d65ba087f4d0843c4b9dff2cb093f80c880947",
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
              "b": 441.9899829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 530.0139999999997,
              "t": 521.5659829101563
            },
            "charspan": [
              0,
              550
            ],
            "page_no": 54
          }
        ],
        "self_ref": "#/texts/571"
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
              "b": 422.1899829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 347.926,
              "t": 432.88598291015626
            },
            "charspan": [
              0,
              55
            ],
            "page_no": 54
          }
        ],
        "self_ref": "#/texts/572"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "caption",
        "parent": {
          "$ref": "#/pictures/83"
        },
        "prov": [
          {
            "bbox": {
              "b": 169.14533563742907,
              "coord_origin": "BOTTOMLEFT",
              "l": 195.65,
              "r": 402.28000000000003,
              "t": 177.5229029101563
            },
            "charspan": [
              0,
              45
            ],
            "page_no": 54
          }
        ],
        "self_ref": "#/texts/573"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-54cc2ada225e4a7c20be7c6b.md",
  "heading_path": [
    "4.1.7. Account Creation"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-54cc2ada225e4a7c20be7c6b.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

When a customer transfers to a new (incoming) User the Network Operator passes the necessary data to the incoming User to enable that User to create an account for the customer (note: in South  Australia,  part  of  the  data  required  by  Users  is  provided  through  the  MIRN  Discovery Process).  The Account Creation transaction contains some meter read data and some site data. The outgoing User is provided with the final meter read data as part of the process.  Account Creation transactions are provided for both basic and interval meters.
The diagram below is a high level view of this process:
Figure 4-25 Account Creation Activity Diagram
