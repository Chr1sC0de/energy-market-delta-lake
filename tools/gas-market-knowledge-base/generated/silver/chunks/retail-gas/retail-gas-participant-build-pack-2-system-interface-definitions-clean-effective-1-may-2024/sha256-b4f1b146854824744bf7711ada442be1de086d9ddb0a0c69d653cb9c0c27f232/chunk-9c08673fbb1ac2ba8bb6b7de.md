---
{
  "chunk_id": "chunk-9c08673fbb1ac2ba8bb6b7de",
  "chunk_ordinal": 154,
  "chunk_text_sha256": "e800136ea532a24b07079ea0a9baec3f04a4cc3ce0475a9a443cc6d01fc5adb3",
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
              "b": 253.20562744140625,
              "coord_origin": "BOTTOMLEFT",
              "l": 73.783203125,
              "r": 508.3265380859375,
              "t": 517.6866149902344
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 50
          }
        ],
        "self_ref": "#/tables/53"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-9c08673fbb1ac2ba8bb6b7de.md",
  "heading_path": [
    "FIGURE 4-13. CLEARING OBJECTION ACTIVITY DIAGRAM"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-9c08673fbb1ac2ba8bb6b7de.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

1, ASEXML TXN = CATSObjecti onWithdrawal. 1, TRANSACTI ON DEFINITION TABLE = Withdrawal Objection Notice. 1, FROM OBJECT = Current FRO. 1, TO OBJECT = AEMO. 1, PROCESS FLOW = 6.3.7 -> 6.3.8. 2, ASEXML TXN = CATSNotificat ion. 2, TRANSACTI ON DEFINITION TABLE = Objection Withdrawal Notification. 2, FROM OBJECT = AEMO. 2, TO OBJECT = New FRO. 2, PROCESS FLOW = 6.3.23 -> 6.3.19. 3, ASEXML TXN = CATSNotificat ion. 3, TRANSACTI ON DEFINITION TABLE = Objection Withdrawal Notification. 3, FROM OBJECT = AEMO. 3, TO OBJECT = Current FRO. 3, PROCESS FLOW = 6.3.23 -> 6.3.21. 4, ASEXML TXN = CATSNotificat ion. 4, TRANSACTI ON DEFINITION TABLE = Objection Withdrawal Notification. 4, FROM OBJECT = AEMO. 4, TO OBJECT = Distributor. 4, PROCESS FLOW = 6.3.23 -> 6.3.18
