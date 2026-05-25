---
{
  "chunk_id": "chunk-7721da1d847aedb916bb15bd",
  "chunk_ordinal": 271,
  "chunk_text_sha256": "da5600b22d0169c276383a094057a4b187f97f16bd31a4ba38979c08c9915787",
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
              "b": 370.55682373046875,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.87946319580078,
              "r": 549.144287109375,
              "t": 457.57928466796875
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 64
          }
        ],
        "self_ref": "#/tables/49"
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
              "b": 310.44998291015634,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.66,
              "r": 529.7179999999994,
              "t": 348.7459829101563
            },
            "charspan": [
              0,
              221
            ],
            "page_no": 64
          }
        ],
        "self_ref": "#/texts/743"
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
              "b": 290.64998291015627,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.66,
              "r": 415.246,
              "t": 301.3459829101563
            },
            "charspan": [
              0,
              68
            ],
            "page_no": 64
          }
        ],
        "self_ref": "#/texts/744"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "caption",
        "parent": {
          "$ref": "#/pictures/99"
        },
        "prov": [
          {
            "bbox": {
              "b": 118.86533563742898,
              "coord_origin": "BOTTOMLEFT",
              "l": 172.1,
              "r": 425.68,
              "t": 127.24290291015632
            },
            "charspan": [
              0,
              55
            ],
            "page_no": 64
          }
        ],
        "self_ref": "#/texts/745"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-7721da1d847aedb916bb15bd.md",
  "heading_path": [
    "Cancellation Process"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-7721da1d847aedb916bb15bd.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

1, aseXML Transaction = ServiceOrderRequest. 1, From Object = User. 1, To Object = FRC Hub. 1, Process Flow = REQ5A. 2, aseXML Transaction = ServiceOrderRequest. 2, From Object = FRC Hub. 2, To Object = Network Operator. 2, Process Flow = REQ5A. 3, aseXML Transaction = ServiceOrderResponse. 3, From Object = Network Operator. 3, To Object = FRC Hub. 3, Process Flow = REQ5A. 4, aseXML Transaction = ServiceOrderResponse. 4, From Object = FRC Hub. 4, To Object = User. 4, Process Flow = REQ5A
If the User  identifies that the service is no longer required, the User  will forward a ServiceOrderRequest transaction to the Network Operator with the actionType set to 'Cancel' to identify that this is a cancellation.
The diagram below shows the sequence of events for this transaction:
Figure 4-31 Service Order Cancellation Sequence Diagram
