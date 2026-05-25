---
{
  "chunk_id": "chunk-f43a72c91c8546afe6a6a78b",
  "chunk_ordinal": 135,
  "chunk_text_sha256": "89aa5862ffbe3989f2761a156fd1cb32a4371985f95848e3edcf3edfd7a0aa91",
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
              "b": 82.99901095552059,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.3927999999995,
              "t": 107.90109802734378
            },
            "charspan": [
              0,
              182
            ],
            "page_no": 39
          }
        ],
        "self_ref": "#/texts/398"
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
              "b": 538.5650109555205,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 466.33912,
              "t": 548.4670980273437
            },
            "charspan": [
              0,
              60
            ],
            "page_no": 40
          }
        ],
        "self_ref": "#/texts/410"
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
              "b": 367.0625,
              "coord_origin": "BOTTOMLEFT",
              "l": 74.23918914794922,
              "r": 506.8396301269531,
              "t": 529.8308715820312
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 40
          }
        ],
        "self_ref": "#/tables/42"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-f43a72c91c8546afe6a6a78b.md",
  "heading_path": [
    "FIGURE 4-9. GENERATING NOTICE OF READ FAILURE ACTIVITY DIAGRAM"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-f43a72c91c8546afe6a6a78b.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

The  following  sequence  diagram  translates  the  process  activities  above  into  aseXML transactions exchange. Read failure notices are realised as CATSDataRequest transactions.
FIGURE 4-10. GENERATING READ FAILURE NOTICE SEQUENCE DIAGRAM
1, ASEXML TXN = CATSDataRequest. 1, TRANSACTION DEFINITION TABLE = Notice of Read Failure. 1, FROM OBJECT = AEMO. 1, TO OBJECT = New FRO. 1, PROCESS FLOW = 6.5.3 -> 6.5.1. 2, ASEXML TXN = CATSDataRequest. 2, TRANSACTION DEFINITION TABLE = Notice of Read Failure. 2, FROM OBJECT = AEMO. 2, TO OBJECT = Current FRO. 2, PROCESS FLOW = 6.5.2 -> 6.5.15. 3, ASEXML TXN = CATSDataRequest. 3, TRANSACTION DEFINITION TABLE = Notice of Read Failure. 3, FROM OBJECT = AEMO. 3, TO OBJECT = Distributor. 3, PROCESS FLOW = 6.5.2 -> 6.5.16
