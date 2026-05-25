---
{
  "chunk_id": "chunk-e3c21cea2f6335e1cc6d02c0",
  "chunk_ordinal": 226,
  "chunk_text_sha256": "b51ada91541d3e2e0a7239af23f11cf8145ffcd395ff740825365883e47f6222",
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
              "b": 536.0699829101562,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 530.116,
              "t": 588.1959829101563
            },
            "charspan": [
              0,
              294
            ],
            "page_no": 48
          }
        ],
        "self_ref": "#/texts/513"
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
              "b": 447.50998291015634,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 529.8499999999992,
              "t": 527.0859829101563
            },
            "charspan": [
              0,
              516
            ],
            "page_no": 48
          }
        ],
        "self_ref": "#/texts/514"
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
              "b": 427.7099829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 429.046,
              "t": 438.4059829101563
            },
            "charspan": [
              0,
              70
            ],
            "page_no": 48
          }
        ],
        "self_ref": "#/texts/515"
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
              "b": 188.70533563742902,
              "coord_origin": "BOTTOMLEFT",
              "l": 157.82,
              "r": 440.08,
              "t": 197.08290291015624
            },
            "charspan": [
              0,
              61
            ],
            "page_no": 48
          }
        ],
        "self_ref": "#/texts/525"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-e3c21cea2f6335e1cc6d02c0.md",
  "heading_path": [
    "Process Sequence"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-e3c21cea2f6335e1cc6d02c0.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

When the Network Operator has determined the correct meter data a MeterDataVerifyResponse transaction is generated and forwarded to the User.  This transaction contains the current index value and an adjustment reason. If the data has not been adjusted the AdjustmentReason will be "No Change".
In addition, if an adjustment is required the adjusted energy data is forwarded to the User via a scheduled MeterDataNotification transaction.  The adjusted data will supersede the data that was previously provided for the timeframe in question.  However, depending on the process used by the Network Operator to obtain the adjusted data, the Current Read Date may differ from that provided  in  the  superseded  data.    The  User  will  have  to  decide  how  to  use  this  data  in  the customer's billing cycle.
The diagram below shows the sequence of events for these transactions:
Figure 4-20 Meter Data Verification Response Sequence Diagram
