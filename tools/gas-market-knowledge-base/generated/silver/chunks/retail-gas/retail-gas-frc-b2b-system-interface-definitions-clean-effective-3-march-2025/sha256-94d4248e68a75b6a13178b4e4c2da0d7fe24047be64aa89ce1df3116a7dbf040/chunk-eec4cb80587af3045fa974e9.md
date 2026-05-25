---
{
  "chunk_id": "chunk-eec4cb80587af3045fa974e9",
  "chunk_ordinal": 283,
  "chunk_text_sha256": "c7fa33c41a0ac4ed628686ed9c35bc78a65da97e82880a1ea9180f7c3aa6cea8",
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
              "b": 100.77998291015626,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.66,
              "r": 532.1839999999999,
              "t": 152.87598291015627
            },
            "charspan": [
              0,
              375
            ],
            "page_no": 67
          }
        ],
        "self_ref": "#/texts/806"
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
              "b": 693.7799829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.66,
              "r": 532.2319999999997,
              "t": 745.8759829101563
            },
            "charspan": [
              0,
              384
            ],
            "page_no": 68
          }
        ],
        "self_ref": "#/texts/810"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-eec4cb80587af3045fa974e9.md",
  "heading_path": [
    "4.2.3.2. Implied Service Orders"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-eec4cb80587af3045fa974e9.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

In  the  case  of  an  implied  service  order  to  recommission  the  service,  the  corresponding MeterDataNotification transaction will be forwarded to the current user to provide the meter data and meter index. The Reason for Read in the MeterDataNotification will be set to 'OSO' (for a RML or RSD) or INI (for a MRF), and the meter status will be set to 'commissioned'.
In  the  case  of  an  Implied  service  order  to  decommission  the  service,  the  corresponding MeterDataNotification transaction will again be forwarded to the current user to provide the meter data and meter index. The Reason for Read in the MeterDataNotification will be set to 'OSO' (for an AML or DSD), or REM (for a MRM) and the meter status will be set to 'decommissioned'.
