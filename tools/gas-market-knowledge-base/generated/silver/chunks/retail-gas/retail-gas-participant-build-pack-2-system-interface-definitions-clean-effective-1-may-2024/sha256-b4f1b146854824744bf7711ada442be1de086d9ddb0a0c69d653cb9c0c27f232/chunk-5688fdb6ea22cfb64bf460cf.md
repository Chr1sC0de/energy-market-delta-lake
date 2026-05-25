---
{
  "chunk_id": "chunk-5688fdb6ea22cfb64bf460cf",
  "chunk_ordinal": 126,
  "chunk_text_sha256": "d7b4945bf853e18cee94d8210d5cd5e04d322d5329fa30b7c9dfbf55e6136c1b",
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
              "b": 522.6656494140625,
              "coord_origin": "BOTTOMLEFT",
              "l": 74.02754974365234,
              "r": 531.7736206054688,
              "t": 710.3813934326172
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 36
          }
        ],
        "self_ref": "#/tables/37"
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
              "b": 493.32501095552055,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.3707199999997,
              "t": 518.2270980273438
            },
            "charspan": [
              0,
              114
            ],
            "page_no": 36
          }
        ],
        "self_ref": "#/texts/347"
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
              "b": 469.32501095552055,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 488.68912,
              "t": 479.2270980273438
            },
            "charspan": [
              0,
              86
            ],
            "page_no": 36
          }
        ],
        "self_ref": "#/texts/348"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-5688fdb6ea22cfb64bf460cf.md",
  "heading_path": [
    "4.1.5.1 Alternative Transfer Date Transaction"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-5688fdb6ea22cfb64bf460cf.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

Trigger, • 214 ALTERNATIVE TRANSFER DATE (FROM NEW FRO) = Notice of Read Failure. Pre-conditions, • 214 ALTERNATIVE TRANSFER DATE (FROM NEW FRO) = An Alternative Transfer Date request is issued within 10 days from Read Failure Notice. Post-conditions, • 214 ALTERNATIVE TRANSFER DATE (FROM NEW FRO) = Receipt by AEMO of a valid alternative transfer date. Transaction acknowledgment specific event codes, • 214 ALTERNATIVE TRANSFER DATE (FROM NEW FRO) = 3000-3006, 3008-3013, 3016, 3018, 3019-3023,3034, 3035- 3038, 3041
Alternative  Transfer  Date  transaction  is  implemented  in  terms  of  a  CATSChangeRequest aseXML transaction.
The following data need to be supplied with the Alternative Transfer Date transaction:
