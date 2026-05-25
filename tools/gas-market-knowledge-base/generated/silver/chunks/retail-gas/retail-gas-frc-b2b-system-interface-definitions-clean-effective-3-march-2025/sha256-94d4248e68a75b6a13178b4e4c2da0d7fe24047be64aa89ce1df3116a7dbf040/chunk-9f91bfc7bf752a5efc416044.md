---
{
  "chunk_id": "chunk-9f91bfc7bf752a5efc416044",
  "chunk_ordinal": 451,
  "chunk_text_sha256": "f74ca100b129e5f33b045db210cc11b0c65d6507864502cff94db68ff39917ba",
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
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/13"
        },
        "prov": [
          {
            "bbox": {
              "b": 385.6899829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 529.9659999999996,
              "t": 423.88598291015626
            },
            "charspan": [
              0,
              228
            ],
            "page_no": 135
          }
        ],
        "self_ref": "#/texts/1354"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/13"
        },
        "prov": [
          {
            "bbox": {
              "b": 338.2899829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 529.6999999999994,
              "t": 376.5859829101563
            },
            "charspan": [
              0,
              205
            ],
            "page_no": 135
          }
        ],
        "self_ref": "#/texts/1355"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/13"
        },
        "prov": [
          {
            "bbox": {
              "b": 304.80998291015635,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 530.0319999999997,
              "t": 329.3059829101562
            },
            "charspan": [
              0,
              176
            ],
            "page_no": 135
          }
        ],
        "self_ref": "#/texts/1356"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-9f91bfc7bf752a5efc416044.md",
  "heading_path": [
    "Note:"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-9f91bfc7bf752a5efc416044.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

1. In SA, a MIRN that requires an address and a Customer Classification change must be sent in two transactions. Each record in the CSV must only include either a change to the address or a change to the customer classification.
2. In  SA, If  Customer Classification but not the address details for a MIRN is changing, the Retailer should send only a Customer Classification Code change record and not the address change transaction.
3. The address elements in the CSV data align to the format and procedures of the address schema in aseXML, which in turn aligns to AS4590.   The elements are identified below:
