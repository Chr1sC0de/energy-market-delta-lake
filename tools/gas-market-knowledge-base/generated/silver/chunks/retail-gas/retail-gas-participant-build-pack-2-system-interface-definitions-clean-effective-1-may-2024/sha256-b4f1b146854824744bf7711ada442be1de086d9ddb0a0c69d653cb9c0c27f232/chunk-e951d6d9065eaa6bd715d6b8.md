---
{
  "chunk_id": "chunk-e951d6d9065eaa6bd715d6b8",
  "chunk_ordinal": 123,
  "chunk_text_sha256": "1abeecb850138f489f0a78ba4b25559cb64cb7100f0aeaae9027d3ed44dd76ef",
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
              "b": 528.1417846679688,
              "coord_origin": "BOTTOMLEFT",
              "l": 74.16088104248047,
              "r": 531.28662109375,
              "t": 702.7228240966797
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 34
          }
        ],
        "self_ref": "#/tables/35"
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
              "b": 498.72501095552053,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.68912,
              "t": 523.6270980273438
            },
            "charspan": [
              0,
              183
            ],
            "page_no": 34
          }
        ],
        "self_ref": "#/texts/293"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-e951d6d9065eaa6bd715d6b8.md",
  "heading_path": [
    "4.1.4.2 Response to Delivery of Standing Data Transaction"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-e951d6d9065eaa6bd715d6b8.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

Trigger, • 182A RESPONSE TO STANDING DATA REQUEST = Delivery of standing data. Pre-conditions, • 182A RESPONSE TO STANDING DATA REQUEST = Standing data is successfully validated. Post-conditions, • 182A RESPONSE TO STANDING DATA REQUEST = None. Transaction acknowledgment specific event codes, • 182A RESPONSE TO STANDING DATA REQUEST = None
CATSChangeResponse transaction is used to convey the standing data delivery response. This transaction is sent to the originator of the Change Request. For details see Section 4.1.3.2
