---
{
  "chunk_id": "chunk-40f6ae33b2060bad174e4f5e",
  "chunk_ordinal": 551,
  "chunk_text_sha256": "80f7d551046a5963b40ba99f3ff002e4f513309d5a97df5e509e97f9ca3d5ec0",
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
              "b": 200.12457275390625,
              "coord_origin": "BOTTOMLEFT",
              "l": 71.24911499023438,
              "r": 530.73828125,
              "t": 421.8838195800781
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 164
          }
        ],
        "self_ref": "#/tables/126"
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
              "b": 159.81998291015634,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 522.8019999999999,
              "t": 184.19598291015632
            },
            "charspan": [
              0,
              120
            ],
            "page_no": 164
          }
        ],
        "self_ref": "#/texts/2050"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-40f6ae33b2060bad174e4f5e.md",
  "heading_path": [
    "4.6.3. Customer Details Request (CDR)"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-40f6ae33b2060bad174e4f5e.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

TRANSACTION DEFINITION TABLE CROSS- REFERENCE, 1 = THIS INTERFACE REALISES THE FOLLOWING TRANSACTIONS FROM THE GPTWG TRANSACTION DEFINITION TABLE: • 72 - CUSTOMER DETAILS REQUEST. Trigger, 1 = This interface is triggered when a Network Operator reasonably believes that the information in the CustomerDetailsNotification has not been previously provided in a Notification transaction or that the information they hold is or may be incorrect.. Pre-conditions, 1 = None. Post-conditions, 1 = Retailer issues updated customer details via the CDN transation.. Transaction acknowledgment specific event codes, 1 = 3689 (Also the generic event codes 3603, 3659, 3662, 3673 can be used)
The CustomerDetailsRequest transaction is used by the Network Operator to notify a Retailer to provide a CDN transaction
