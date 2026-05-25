---
{
  "chunk_id": "chunk-5b75af009b59dec7307fc6ce",
  "chunk_ordinal": 354,
  "chunk_text_sha256": "953c9cf19ffcd33dcff7e743b1589134b59d4615896e69ac707e9f7a5e391e29",
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
              "b": 467.75982666015625,
              "coord_origin": "BOTTOMLEFT",
              "l": 108.10895538330078,
              "r": 529.41259765625,
              "t": 729.1559448242188
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 97
          }
        ],
        "self_ref": "#/tables/72"
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
              "b": 420.9899829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.66,
              "r": 532.3399999999997,
              "t": 445.4859829101563
            },
            "charspan": [
              0,
              187
            ],
            "page_no": 97
          },
          {
            "bbox": {
              "b": 721.3799829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.66,
              "r": 529.7479999999995,
              "t": 745.8759829101563
            },
            "charspan": [
              188,
              296
            ],
            "page_no": 98
          }
        ],
        "self_ref": "#/texts/1016"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "caption",
        "parent": {
          "$ref": "#/pictures/145"
        },
        "prov": [
          {
            "bbox": {
              "b": 386.37533563742903,
              "coord_origin": "BOTTOMLEFT",
              "l": 186.5,
              "r": 411.28000000000003,
              "t": 394.7529029101563
            },
            "charspan": [
              0,
              45
            ],
            "page_no": 98
          }
        ],
        "self_ref": "#/texts/1020"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-5b75af009b59dec7307fc6ce.md",
  "heading_path": [
    "Transaction Data Elements"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-5b75af009b59dec7307fc6ce.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

Data Element, Received From:.Sent To: = VIC & SA/WA: Mandatory / Optional / Not Required. Data Element, NMIDiscoveryRequest.User.Network Operator = Usage. JurisdictionCode, Received From:.Sent To: = M. JurisdictionCode, NMIDiscoveryRequest.User.Network Operator = SA: Literal 'SGI' WA Literal 'WGI' VIC: Literal "VGI" Not currently used by the Gas Industry. Required in this transaction for convergence with current aseXML schema. Address, Received From:.Sent To: = M. Address, NMIDiscoveryRequest.User.Network Operator = Contains search data in aseXML "AustralianAddressSearch" structured format.
The transaction is implemented as the existing NMIDiscoveryRequest transaction in aseXML. Due to harmonisation with Electricity aseXML, additional fields in the schema appear in the below diagram, however for Gas the only valid search field is Address. The transaction is in the following format:
Figure 4-42 NMIDiscoveryRequest aseXML schema
