---
{
  "chunk_id": "chunk-b3eeeb9d7d428d7ee526eaac",
  "chunk_ordinal": 144,
  "chunk_text_sha256": "d2638a7056485df06270ca58c73432df8772d2d33ae5ca413661916459ee947e",
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
              "b": 523.0380554199219,
              "coord_origin": "BOTTOMLEFT",
              "l": 74.3275146484375,
              "r": 494.210205078125,
              "t": 710.3913421630859
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 44
          }
        ],
        "self_ref": "#/tables/46"
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
              "b": 439.32501095552055,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.61736,
              "t": 494.2270980273438
            },
            "charspan": [
              0,
              365
            ],
            "page_no": 44
          }
        ],
        "self_ref": "#/texts/479"
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
              "b": 415.32501095552055,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 375.49912,
              "t": 425.2270980273438
            },
            "charspan": [
              0,
              62
            ],
            "page_no": 44
          }
        ],
        "self_ref": "#/texts/480"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-b3eeeb9d7d428d7ee526eaac.md",
  "heading_path": [
    "4.1.7.1 Objection Transaction"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-b3eeeb9d7d428d7ee526eaac.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

Trigger, • 187 OBJECTION = Transfer Notice. Pre-conditions, • 187 OBJECTION = Transfer is in progress. Post-conditions, • 187 OBJECTION = Receipt by AEMO of a transfer request objection. Transaction acknowledgment specific event codes, • 187 OBJECTION = 3018, 3028-3030
The only party that is allowed to generate an objection is the Current FRO. Following validation and  processing  at  AEMO,  this  transaction  will  instigate  a  response  towards  objecting participant  and  a  number  of  notifications  towards  other  involved  participants.  An  objection request is implemented as an aseXML CATSObjectionRequest transaction.
The following must be supplied with the Objection transaction:
