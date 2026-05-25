---
{
  "chunk_id": "chunk-8e42c63bdc6ae83be9b986b4",
  "chunk_ordinal": 811,
  "chunk_text_sha256": "2fc0fb34c6942265e612b2a18115d1f7ab1758c2de553e24ce53dd53c6745831",
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
              "b": 266.04998291015636,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 530.0439999999999,
              "t": 345.62598291015627
            },
            "charspan": [
              0,
              574
            ],
            "page_no": 239
          }
        ],
        "self_ref": "#/texts/2381"
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
              "b": 197.13998291015628,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 529.9899999999998,
              "t": 249.14598291015625
            },
            "charspan": [
              0,
              317
            ],
            "page_no": 239
          }
        ],
        "self_ref": "#/texts/2382"
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
              "b": 142.05998291015635,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 529.7839999999993,
              "t": 180.35598291015629
            },
            "charspan": [
              0,
              236
            ],
            "page_no": 239
          }
        ],
        "self_ref": "#/texts/2383"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-8e42c63bdc6ae83be9b986b4.md",
  "heading_path": [
    "Complete MIRN Listing (T299) -(For SA)."
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-8e42c63bdc6ae83be9b986b4.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

The Network Operator must make available to Retailers a listing of all distribution metering supply points that have a MIRN assigned and a MIRN status of either Registered (up stand installed), Commissioned  (meter  installed)  or  Decommissioned  (meter  removed  or  meter  installed  but delivery point is disconnected). The Network Operator must ensure that all data fields as per Transaction 299 that are available in their database are transferred to the Complete MIRN listing irrespective of whether the data field is designated as O (optional) in the table for T299.
The  Network  Operator  must  ensure  that  the  complete  MIRN  listing  file  is  encrypted  and compressed (see section 4 of the FRC CSV File Format Specifications for allowable compression formats) in a way that when the Retailer retrieves the file it can be decrypted and uncompressed using the 'WinZip' utility.
The Network Operator will utilise the CSV fields and formats consistent with the fields and formats that are used in the aseXML schema applicable for a MIRN Discovery response which is defined in section 4.3.2.3A (NMIDiscoveryResponse).
