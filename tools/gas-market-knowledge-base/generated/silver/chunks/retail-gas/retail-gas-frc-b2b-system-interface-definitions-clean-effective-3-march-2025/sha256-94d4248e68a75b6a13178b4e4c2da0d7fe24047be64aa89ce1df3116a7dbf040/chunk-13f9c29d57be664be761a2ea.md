---
{
  "chunk_id": "chunk-13f9c29d57be664be761a2ea",
  "chunk_ordinal": 448,
  "chunk_text_sha256": "e1fe085985fb8cd632ef8c9e8f24cf980b0bb2e126ad61a4e900097e4936a39a",
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
              "b": 171.2491455078125,
              "coord_origin": "BOTTOMLEFT",
              "l": 108.08950805664062,
              "r": 548.0914916992188,
              "t": 387.5278015136719
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 134
          }
        ],
        "self_ref": "#/tables/97"
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
              "b": 111.21998291015632,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 530.1399999999999,
              "t": 149.39598291015625
            },
            "charspan": [
              0,
              280
            ],
            "page_no": 134
          }
        ],
        "self_ref": "#/texts/1346"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-13f9c29d57be664be761a2ea.md",
  "heading_path": [
    "4.4.3.1. AmendMeterRouteDetails/CSVAmendSiteAddressDetails"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-13f9c29d57be664be761a2ea.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

Transaction Definition Table cross-reference, 1 = This interface realises the following transactions from the Transaction Definition Table: • 68 - Supply Point Information • 69 - Address Information Change from DB. Trigger, 1 = This interface is triggered when a User or a Network Operator changes a customer's address data or customer classification or a User makes a change to a customer's characterisation data.. Pre-conditions, 1 = None. Post-conditions, 1 = Receiving participant has recorded the changed data. Transaction acknowledgment specific event codes, 1 = 3665, 3666, 3667, 3668, 3670, 3672, 3674, 3677 (Also the generic event codes 3603, 3659, 3662, 3673 can be used)
The AmendMeterRouteDetails/CSVAmendSiteAddressDetails transaction is used by the User or Network Operator to  notify  the  other  participant  of  a  change  to  a  customer's  site  address or customer classification or characterisation data.  The data is provided in CSV format.
