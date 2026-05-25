---
{
  "chunk_id": "chunk-21f6dfd9f9f537f26eb5943c",
  "chunk_ordinal": 286,
  "chunk_text_sha256": "b38caea8fd47c5aeffd418e969f7d03af078c6d10f35cab4e209a8619a031202",
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
              "b": 637.4999829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 532.4239999999995,
              "t": 675.7959829101562
            },
            "charspan": [
              0,
              223
            ],
            "page_no": 69
          }
        ],
        "self_ref": "#/texts/818"
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
              "b": 590.2199829101562,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 529.8139999999994,
              "t": 628.3959829101562
            },
            "charspan": [
              0,
              192
            ],
            "page_no": 69
          }
        ],
        "self_ref": "#/texts/819"
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
              "b": 542.7899829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 529.5559999999997,
              "t": 581.0859829101563
            },
            "charspan": [
              0,
              275
            ],
            "page_no": 69
          }
        ],
        "self_ref": "#/texts/820"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-21f6dfd9f9f537f26eb5943c.md",
  "heading_path": [
    "4.2.3.4. ServiceOrderRequest"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-21f6dfd9f9f537f26eb5943c.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

The ServiceOrderRequest transaction requests the provision of a service by a Network Operator. It  is  also  used  to  cancel  an  existing  Service  Order  via  an  'actionType'  attribute  within  the transaction element.
In relation to WA further detailed usage notes for the ServiceOrderRequest transaction are contained in  the  Service Order  Specifications  which  are  contained  in  the  Specification Pack.
Note:  where  a  ServiceOrderRequest  transaction  is  provided  to  a  Network  Operator  in  South Australia, the Network Operator will use the CustomerCharacterisation field to provide the initial customer classification as prescribed under the National Energy Retail Law.
