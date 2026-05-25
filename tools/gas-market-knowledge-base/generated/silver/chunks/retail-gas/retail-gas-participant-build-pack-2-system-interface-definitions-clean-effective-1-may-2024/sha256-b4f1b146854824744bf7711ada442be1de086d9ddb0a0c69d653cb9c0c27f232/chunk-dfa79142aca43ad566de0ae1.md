---
{
  "chunk_id": "chunk-dfa79142aca43ad566de0ae1",
  "chunk_ordinal": 156,
  "chunk_text_sha256": "9ec6853c3d5f518aa74ce5da6c69431b9c976f2bc901ebbc12d2f12efafb3146",
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
              "b": 523.1392822265625,
              "coord_origin": "BOTTOMLEFT",
              "l": 74.33146667480469,
              "r": 494.13232421875,
              "t": 710.1305847167969
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 51
          }
        ],
        "self_ref": "#/tables/54"
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
              "b": 454.32501095552055,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.5570399999993,
              "t": 494.2270980273438
            },
            "charspan": [
              0,
              234
            ],
            "page_no": 51
          }
        ],
        "self_ref": "#/texts/559"
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
              "b": 430.32501095552055,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 496.00912,
              "t": 440.2270980273438
            },
            "charspan": [
              0,
              87
            ],
            "page_no": 51
          }
        ],
        "self_ref": "#/texts/560"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-dfa79142aca43ad566de0ae1.md",
  "heading_path": [
    "4.1.8.1 Withdrawal Objection Notice Transaction"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-dfa79142aca43ad566de0ae1.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

TRANSACTION DEFINITION TABLE CROSS- REFERENCE, 1 = • 191 WITHDRAWAL OBJECTION NOTICE. Trigger, 1 = Resolved objection.. Pre-conditions, 1 = Objection has been submitted.. Post-conditions, 1 = AEMO is informed on objection withdrawal.. Transaction acknowledgment specific event codes, 1 = 3016, 3029, 3032, 3033
The only party that is allowed to generate a withdrawal of the objection is the Current FRO. Following validation and processing at AEMO, this transaction will instigate a number of notices generated towards all involved participants.
The following data are to be supplied with the Withdrawal Objection Notice transaction:
