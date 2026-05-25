---
{
  "chunk_id": "chunk-6e932ad940eab1e250b103dd",
  "chunk_ordinal": 239,
  "chunk_text_sha256": "31ea0735d194e29c86f735e966cc58aea3ea6fef6bfab04cee9da00f569e380a",
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
              "b": 410.9690246582031,
              "coord_origin": "BOTTOMLEFT",
              "l": 108.08258819580078,
              "r": 529.950439453125,
              "t": 749.7557830810547
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 52
          }
        ],
        "self_ref": "#/tables/43"
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
              "b": 350.88998291015633,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 494.76799999999974,
              "t": 389.18598291015627
            },
            "charspan": [
              0,
              190
            ],
            "page_no": 52
          }
        ],
        "self_ref": "#/texts/553"
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
              "b": 331.0899829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 289.346,
              "t": 341.7859829101563
            },
            "charspan": [
              0,
              43
            ],
            "page_no": 52
          }
        ],
        "self_ref": "#/texts/554"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "caption",
        "parent": {
          "$ref": "#/pictures/79"
        },
        "prov": [
          {
            "bbox": {
              "b": 239.735335637429,
              "coord_origin": "BOTTOMLEFT",
              "l": 178.22,
              "r": 419.56,
              "t": 248.11290291015632
            },
            "charspan": [
              0,
              49
            ],
            "page_no": 52
          }
        ],
        "self_ref": "#/texts/555"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-6e932ad940eab1e250b103dd.md",
  "heading_path": [
    "Transaction Data Elements"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-6e932ad940eab1e250b103dd.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

O. Event, MeterDataVerifyResponse.Network Operator.User.Usage = May be repeated any number of times. The Event element will identify any errors occurring in the processing of the request record.
The transaction is implemented as the MeterDataVerifyResponse transaction in aseXML utilising the xsi:type="ase:GasMeterVerifyResponseData" construct for the MeterVerifyResponseData element.
The transaction is in the following format:
Figure 4-23 MeterDataVerifyResponse aseXML schema
