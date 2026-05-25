---
{
  "chunk_id": "chunk-71acdd2fbf820fdf99f85352",
  "chunk_ordinal": 191,
  "chunk_text_sha256": "34cac9f4d78b132bddb273b60f88f945343aa36148fffa627751819333b58698",
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
              "b": 340.0899829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.66,
              "r": 530.0559999999999,
              "t": 378.38598291015626
            },
            "charspan": [
              0,
              220
            ],
            "page_no": 36
          }
        ],
        "self_ref": "#/texts/368"
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
              "b": 292.80998291015635,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.66,
              "r": 529.8619999999994,
              "t": 331.1059829101563
            },
            "charspan": [
              0,
              216
            ],
            "page_no": 36
          }
        ],
        "self_ref": "#/texts/369"
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
              "b": 735.0599829101562,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.66,
              "r": 415.246,
              "t": 745.7559829101563
            },
            "charspan": [
              0,
              68
            ],
            "page_no": 37
          }
        ],
        "self_ref": "#/texts/373"
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
              "b": 504.35533563742905,
              "coord_origin": "BOTTOMLEFT",
              "l": 181.58,
              "r": 416.32,
              "t": 512.7329029101563
            },
            "charspan": [
              0,
              52
            ],
            "page_no": 37
          }
        ],
        "self_ref": "#/texts/386"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-71acdd2fbf820fdf99f85352.md",
  "heading_path": [
    "Process Sequence"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-71acdd2fbf820fdf99f85352.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

When a User has a requirement for a Special Meter Read a SpecialReadRequest is generated and forwarded to the Network Operator.  The request will contain an actionType set to "New" to identify that this is a new request.
Once the Network Operator has logged the Special Read Request and generated a Work Request Number a SpecialReadResponse containing the Work Request Number is forwarded to the User to provide a reference for the User.
The diagram below shows the sequence of events for this transaction:
Figure 4-14 Special Read Initiation Sequence Diagram
