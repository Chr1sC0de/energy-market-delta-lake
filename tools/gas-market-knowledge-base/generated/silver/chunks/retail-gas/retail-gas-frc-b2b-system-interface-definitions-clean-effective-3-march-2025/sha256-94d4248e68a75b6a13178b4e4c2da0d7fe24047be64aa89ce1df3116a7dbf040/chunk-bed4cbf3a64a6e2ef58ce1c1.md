---
{
  "chunk_id": "chunk-bed4cbf3a64a6e2ef58ce1c1",
  "chunk_ordinal": 332,
  "chunk_text_sha256": "2367f1c5eec009b605ee5c515096bb62703af5c6b1ec66168d34b42eafc9302d",
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
              "b": 417.6098327636719,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.99217224121094,
              "r": 545.6676025390625,
              "t": 749.7077941894531
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/tables/67"
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
              "b": 363.6099829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 529.6639999999998,
              "t": 401.7859829101563
            },
            "charspan": [
              0,
              267
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/texts/897"
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
              "b": 343.8099829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 365.8639999999999,
              "t": 354.50598291015626
            },
            "charspan": [
              0,
              59
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/texts/898"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-bed4cbf3a64a6e2ef58ce1c1.md",
  "heading_path": [
    "Transaction Data Elements"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-bed4cbf3a64a6e2ef58ce1c1.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

To:.SA/WA Mandatory/ Optional / Not Required = O. Event, Transaction:.Received From: Sent To:.Victoria Mandatory/ Optional/ Not = O. Event, ServiceOrderResponse.Network Operator User.Victoria Mandatory/ Optional/ Not = O. Event, ServiceOrderResponse.Network Operator User.Usage = May be repeated any number of times. The Event element will identify any errors occurring in the processing of the request record.
The transaction is implemented as the ServiceOrderResponse transaction in aseXML utilising the xsi:type="ase:GasServiceOrderType" construct for the ServiceOrderType element and xsi:type="ase:GasServiceOrderNotificationData" construct for the NotificationData element.
Dog Code should be included within the 'site data' element.
