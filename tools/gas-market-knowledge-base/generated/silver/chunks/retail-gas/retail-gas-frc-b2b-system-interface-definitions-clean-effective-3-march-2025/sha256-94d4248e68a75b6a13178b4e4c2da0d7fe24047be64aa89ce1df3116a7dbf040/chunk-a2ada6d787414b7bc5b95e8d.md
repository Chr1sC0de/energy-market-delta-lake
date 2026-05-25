---
{
  "chunk_id": "chunk-a2ada6d787414b7bc5b95e8d",
  "chunk_ordinal": 547,
  "chunk_text_sha256": "663db19cb7ad2cb5a9e786a8635812f689b16afa8149b9d7261d6e84a5896036",
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
              "b": 414.99835205078125,
              "coord_origin": "BOTTOMLEFT",
              "l": 106.48406982421875,
              "r": 527.828857421875,
              "t": 749.2696075439453
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 162
          }
        ],
        "self_ref": "#/tables/123"
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
              "b": 365.9850158383331,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 499.74391999999955,
              "t": 390.88710291015633
            },
            "charspan": [
              0,
              88
            ],
            "page_no": 162
          }
        ],
        "self_ref": "#/texts/2031"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "caption",
        "parent": {
          "$ref": "#/pictures/241"
        },
        "prov": [
          {
            "bbox": {
              "b": 447.1499829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 280.706,
              "t": 457.8459829101563
            },
            "charspan": [
              0,
              39
            ],
            "page_no": 163
          }
        ],
        "self_ref": "#/texts/2035"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-a2ada6d787414b7bc5b95e8d.md",
  "heading_path": [
    "Transaction Data Elements"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-a2ada6d787414b7bc5b95e8d.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

, 1 = . , 2 = issues, the number is to be provided in the CustomerDetailsNotification. Not required where the site is vacant.. EmailAddress, 1 = O. EmailAddress, 2 = Required where the Retailer has obtained an email address for the purposes of contacting the Customer for supply issues, the email address is to be provided in the CustomerDetailsNotification. Not required where the site is vacant.. SensitiveLoad, 1 = M. SensitiveLoad, 2 = This field indicates whether or not there are economic, health or safety issues with loss of supply of the connection point.. MovementType, 1 = M. MovementType, 2 = A code that indicates the customer details update status. LastModifiedDateTime, 1 = M. LastModifiedDateTime, 2 = Date and time that the record was updated in the Initiator's system
The transaction is implemented as the CustomerDetailsNotification transaction in aseXML.
Figure 4-70 CustomerDetailsNotification
