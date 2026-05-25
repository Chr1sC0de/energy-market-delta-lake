---
{
  "chunk_id": "chunk-6d606a24de2eb8aa8f1fc1f6",
  "chunk_ordinal": 180,
  "chunk_text_sha256": "e971cb4a954cc563e9cf57bc9bcedad5ec516e0ebeff4672be0833785cd3f18f",
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
              "b": 215.35501095552058,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.3927999999996,
              "t": 240.28709802734375
            },
            "charspan": [
              0,
              149
            ],
            "page_no": 62
          }
        ],
        "self_ref": "#/texts/739"
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
              "b": 575.3150109555205,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 434.17912,
              "t": 585.2170980273437
            },
            "charspan": [
              0,
              55
            ],
            "page_no": 63
          }
        ],
        "self_ref": "#/texts/749"
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
              "b": 404.3703308105469,
              "coord_origin": "BOTTOMLEFT",
              "l": 74.04620361328125,
              "r": 508.2666931152344,
              "t": 543.6333312988281
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 63
          }
        ],
        "self_ref": "#/tables/67"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-6d606a24de2eb8aa8f1fc1f6.md",
  "heading_path": [
    "FIGURE 4-19. DELIVERING PROBLEM NOTICE ACTIVITY DIAGRAM"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-6d606a24de2eb8aa8f1fc1f6.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

The sequence diagram below represents a Problem Notice delivery scenario. The Problem Notice is realised with the CATSChangeAlert aseXML transaction.
FIGURE 4-20. DELIVERING PROBLEM NOTICE SEQUENCE DIAGRAM
1, ASEXML TXN = CATSChange Alert. 1, TRANSACTI ON DEFINITION TABLE = Problem Notice. 1, FROM OBJECT = Current FRO or Distributor. 1, TO OBJECT = AEMO. 1, PROCESS FLOW = 6.6.3 -> 6.6.2 6.6.5 -> 6.6.2. 2, ASEXML TXN = CATSChange Alert. 2, TRANSACTI ON DEFINITION TABLE = Problem Notice. 2, FROM OBJECT = AEMO. 2, TO OBJECT = New FRO. 2, PROCESS FLOW = 6.6.2 -> 6.6.1
