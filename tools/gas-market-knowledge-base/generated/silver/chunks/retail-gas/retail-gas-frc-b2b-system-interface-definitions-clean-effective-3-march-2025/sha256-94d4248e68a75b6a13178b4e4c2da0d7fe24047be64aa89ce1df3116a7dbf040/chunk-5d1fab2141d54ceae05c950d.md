---
{
  "chunk_id": "chunk-5d1fab2141d54ceae05c950d",
  "chunk_ordinal": 174,
  "chunk_text_sha256": "ce5d87d1b6705d7e1c49f797e35c6e51ed22fea8385eca65f0eaa2a66bb59a3b",
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
              "b": 589.3799829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 530.116,
              "t": 668.9559829101563
            },
            "charspan": [
              0,
              564
            ],
            "page_no": 29
          }
        ],
        "self_ref": "#/texts/259"
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
              "b": 528.2699829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 530.0259999999997,
              "t": 580.3659829101563
            },
            "charspan": [
              0,
              333
            ],
            "page_no": 29
          }
        ],
        "self_ref": "#/texts/260"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-5d1fab2141d54ceae05c950d.md",
  "heading_path": [
    "Process Sequence"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-5d1fab2141d54ceae05c950d.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

For a basic meter, the Network Operator will provide the required data via a MeterDataNotification transaction.    This  may  be  either  a  special  transaction  in  response  to  this  request  or  the  next scheduled transaction. .  For an interval meter the Network Operator will provide the required data via an INTERVALMETERDATA CSV file.  This may be either a special file in response to this request  or  part  of  the  next  scheduled  INTERVALMETERDATA  CSV  file.    The  data  can  be downloaded from a secure web site operated by the Network Operator.
Note:  There is no defined method for a Network Operator to notify a User of errors in the Missing Data Request transaction (eg. Network Operator is not responsible for requested MIRN).  It is a User's responsibility to escalate the request via a manual process if a Meter Data Notification transaction is not satisfying the request.
