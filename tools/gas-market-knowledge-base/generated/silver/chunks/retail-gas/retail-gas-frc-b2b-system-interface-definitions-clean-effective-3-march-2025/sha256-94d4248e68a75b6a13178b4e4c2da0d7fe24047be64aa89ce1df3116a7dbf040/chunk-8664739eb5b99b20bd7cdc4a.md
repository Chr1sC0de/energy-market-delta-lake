---
{
  "chunk_id": "chunk-8664739eb5b99b20bd7cdc4a",
  "chunk_ordinal": 868,
  "chunk_text_sha256": "8275fb8f2689d72e053d9ebb3d118948836148c7beb699637bdf8aae652b7b92",
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
              "b": 450.26998291015633,
              "coord_origin": "BOTTOMLEFT",
              "l": 89.424,
              "r": 529.6199999999995,
              "t": 488.56598291015627
            },
            "charspan": [
              0,
              231
            ],
            "page_no": 258
          }
        ],
        "self_ref": "#/texts/2530"
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
              "b": 430.4699829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 89.424,
              "r": 315.38599999999997,
              "t": 441.1659829101563
            },
            "charspan": [
              0,
              49
            ],
            "page_no": 258
          }
        ],
        "self_ref": "#/texts/2531"
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
              "b": 410.7899829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 89.424,
              "r": 296.906,
              "t": 421.4859829101563
            },
            "charspan": [
              0,
              46
            ],
            "page_no": 258
          }
        ],
        "self_ref": "#/texts/2532"
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
              "b": 390.9699829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 89.424,
              "r": 510.556,
              "t": 401.6659829101563
            },
            "charspan": [
              0,
              70
            ],
            "page_no": 258
          }
        ],
        "self_ref": "#/texts/2533"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-8664739eb5b99b20bd7cdc4a.md",
  "heading_path": [
    "3. List of RoLR transfers (T980)"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-8664739eb5b99b20bd7cdc4a.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

After a RoLR event has occurred, AEMO will provide the network operator a list of the MIRNs that have been transferred away from the failed retailer to the designated RoLR(s). AEMO will provide this in the CSV format outline below.
The method of file delivery is FTP from the GRMS.
The following naming convention is to be used.
SAGAS_ROLR_LISTOFROLRTRANSFERS_OriginatorID_RecipientID_CCYYMMDDHHmmSS
