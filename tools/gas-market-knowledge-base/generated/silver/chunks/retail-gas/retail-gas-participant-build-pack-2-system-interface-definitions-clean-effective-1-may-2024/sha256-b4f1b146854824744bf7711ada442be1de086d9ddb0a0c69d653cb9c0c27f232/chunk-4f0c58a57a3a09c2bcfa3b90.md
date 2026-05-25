---
{
  "chunk_id": "chunk-4f0c58a57a3a09c2bcfa3b90",
  "chunk_ordinal": 218,
  "chunk_text_sha256": "333be171c3147b88866ab374879e71fa5993cc5adaf56e2c12eed65a26250b6e",
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
              "b": 535.5650109555205,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.5981599999998,
              "t": 575.4670980273437
            },
            "charspan": [
              0,
              247
            ],
            "page_no": 82
          }
        ],
        "self_ref": "#/texts/973"
      },
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
              "b": 314.7686767578125,
              "coord_origin": "BOTTOMLEFT",
              "l": 74.3780288696289,
              "r": 527.5250244140625,
              "t": 527.0513305664062
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 82
          }
        ],
        "self_ref": "#/tables/91"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md",
    "source_manifest_line_number": 31,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-retail-markets/procedures-policies-and-guides/victoria",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/retail_markets_and_metering/market-procedures/vic/2024/participant-build-pack-2--system-interface-definitions-v-36-clean.pdf?rev=0420b92c0a5e4d879175ec3003826d7d&sc_lang=en"
  },
  "content_sha256": "b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232",
  "corpus": "retail_gas",
  "document_family": "retail-gas__participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024",
  "document_family_id": "retail-gas__participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024",
  "document_identity": "retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232",
  "document_title": "##### Participant Build Pack 2 - System Interface Definitions (Clean) Effective 1 May 2024",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-4f0c58a57a3a09c2bcfa3b90.md",
  "heading_path": [
    "4.3.1 Overview"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-4f0c58a57a3a09c2bcfa3b90.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

This section describes the transactions that are exchanged among AEMO and Participants in order to synchronise retailer and history data. The table below maps aseXML transactions to transaction types referenced in the Transaction Definition Table.
MeterDataHistoryRequest, TRANSACTION DEFINITION TABLE REF = 47. MeterDataHistoryRequest, TRANSACTION TYPE FROM TRANSACTION DEFINITION TABLE = Request for History. MeterDataNotification, TRANSACTION DEFINITION TABLE REF = 48. MeterDataNotification, TRANSACTION TYPE FROM TRANSACTION DEFINITION TABLE = Energy History Response. NMIStandingDataUpdateN otification, TRANSACTION DEFINITION TABLE REF = 264. NMIStandingDataUpdateN otification, TRANSACTION TYPE FROM TRANSACTION DEFINITION TABLE = Bi-annual Refresh of Base Load and Temperature Sensitivity Factor. NMIStandingDataUpdateR esponse, TRANSACTION DEFINITION TABLE REF = 264A. NMIStandingDataUpdateR esponse, TRANSACTION TYPE FROM TRANSACTION DEFINITION TABLE = Response to Bi-annual Refresh of Base Load and Temperature Sensitivity Factor. MeteredSupplyPointsCoun tUpdate, TRANSACTION DEFINITION TABLE REF = 338. MeteredSupplyPointsCoun tUpdate, TRANSACTION TYPE FROM TRANSACTION DEFINITION TABLE = Number of Metered Supply Points
