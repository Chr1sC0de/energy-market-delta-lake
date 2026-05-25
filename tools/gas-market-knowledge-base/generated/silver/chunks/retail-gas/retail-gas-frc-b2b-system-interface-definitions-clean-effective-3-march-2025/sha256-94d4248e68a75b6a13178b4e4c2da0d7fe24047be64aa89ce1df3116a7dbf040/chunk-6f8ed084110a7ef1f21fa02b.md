---
{
  "chunk_id": "chunk-6f8ed084110a7ef1f21fa02b",
  "chunk_ordinal": 192,
  "chunk_text_sha256": "4dcd6b19d2917e8b971b09d8657d69a9a6d8c947774092ba787e2c88e955ccf1",
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
              "b": 392.17510986328125,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.73889923095703,
              "r": 563.2655029296875,
              "t": 492.65582275390625
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 37
          }
        ],
        "self_ref": "#/tables/29"
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
              "b": 331.8099829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.66,
              "r": 529.6459999999995,
              "t": 370.1059829101563
            },
            "charspan": [
              0,
              239
            ],
            "page_no": 37
          }
        ],
        "self_ref": "#/texts/387"
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
              "b": 312.1299829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.66,
              "r": 415.246,
              "t": 322.8259829101562
            },
            "charspan": [
              0,
              68
            ],
            "page_no": 37
          }
        ],
        "self_ref": "#/texts/388"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "caption",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 140.82533563742902,
              "coord_origin": "BOTTOMLEFT",
              "l": 174.62,
              "r": 423.28000000000003,
              "t": 149.20290291015635
            },
            "charspan": [
              0,
              54
            ],
            "page_no": 37
          }
        ],
        "self_ref": "#/texts/396"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-6f8ed084110a7ef1f21fa02b.md",
  "heading_path": [
    "Process Sequence"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-6f8ed084110a7ef1f21fa02b.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

1, aseXML Transaction = SpecialReadRequest. 1, From Object = User. 1, To Object = FRC Hub. 1, Process Flow = MR4A. 2, aseXML Transaction = SpecialReadRequest. 2, From Object = FRC Hub. 2, To Object = Network Operator. 2, Process Flow = MR4A. 3, aseXML Transaction = SpecialReadResponse. 3, From Object = Network Operator. 3, To Object = FRC Hub. 3, Process Flow = MR4A. 4, aseXML Transaction = SpecialReadResponse. 4, From Object = FRC Hub. 4, To Object = User. 4, Process Flow = MR4A
If  the  User  identifies  that  the  Special  Read  is  no  longer  required,  the  User  will  forward  a SpecialReadRequest transaction to the Network Operator with the actionType set to 'Cancel' to identify that this is a cancellation.
The diagram below shows the sequence of events for this transaction:
Figure 4-15 Special Read Cancellation Sequence Diagram
