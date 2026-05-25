---
{
  "chunk_id": "chunk-1a1282b1db0cc03ec76ee8df",
  "chunk_ordinal": 153,
  "chunk_text_sha256": "5a1f154d3d603225a4b3f440bd5ced8900cd906593f8c61ab02d0f9ffa5b063f",
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
              "b": 297.8250109555206,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.6905599999999,
              "t": 352.7270980273438
            },
            "charspan": [
              0,
              366
            ],
            "page_no": 49
          }
        ],
        "self_ref": "#/texts/540"
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
              "b": 258.8250109555206,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.5363199999995,
              "t": 283.7270980273438
            },
            "charspan": [
              0,
              104
            ],
            "page_no": 49
          }
        ],
        "self_ref": "#/texts/541"
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
              "b": 525.8450109555206,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 388.33912,
              "t": 535.7470980273438
            },
            "charspan": [
              0,
              48
            ],
            "page_no": 50
          }
        ],
        "self_ref": "#/texts/553"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-1a1282b1db0cc03ec76ee8df.md",
  "heading_path": [
    "FIGURE 4-13. CLEARING OBJECTION ACTIVITY DIAGRAM"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-1a1282b1db0cc03ec76ee8df.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

The  realisation  of  the  process  flow  shown  above  is  presented  on  the  following  sequence diagram. The Current FRO sends a CATSObjectionWithdrawal transaction to AEMO. After the processing of this transaction is complete, AEMO will send CATSNotification transaction to all Organisations assigned to a Role for the Change Request, including the Current FRO.
The following sequence diagram translates the process flow above into a sequence of aseXML transactions.
FIGURE 4-14. CLEARING OBJECTION SEQUENCE DIAGRAM
