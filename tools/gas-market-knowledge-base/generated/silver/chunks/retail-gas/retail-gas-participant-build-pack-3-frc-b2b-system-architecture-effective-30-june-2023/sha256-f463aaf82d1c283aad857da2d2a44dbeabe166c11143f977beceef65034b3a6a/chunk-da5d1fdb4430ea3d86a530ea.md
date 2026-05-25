---
{
  "chunk_id": "chunk-da5d1fdb4430ea3d86a530ea",
  "chunk_ordinal": 50,
  "chunk_text_sha256": "42d380c1c9fdb11b467d3c274d0092befcd4c9b81bd8ef175fd671bbe162ddbc",
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
              "b": 347.2074582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 518.3139199999998,
              "t": 383.7408629101563
            },
            "charspan": [
              0,
              225
            ],
            "page_no": 14
          }
        ],
        "self_ref": "#/texts/238"
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
              "b": 313.6234823134712,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 528.1084000000002,
              "t": 336.34086291015626
            },
            "charspan": [
              0,
              125
            ],
            "page_no": 14
          }
        ],
        "self_ref": "#/texts/239"
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
              "b": 293.8074582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 520.90888,
              "t": 302.74086291015624
            },
            "charspan": [
              0,
              97
            ],
            "page_no": 14
          }
        ],
        "self_ref": "#/texts/240"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a.md",
    "source_manifest_line_number": 32,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-retail-markets/procedures-policies-and-guides/victoria",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/retail_markets_and_metering/market-procedures/vic/gip/build_pack_3/ref--4-participant-build-pack-3-system-architecture-v33-clean.pdf?rev=ce7b279eb01d45a0b38f8120ca1ee195"
  },
  "content_sha256": "f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a",
  "corpus": "retail_gas",
  "document_family": "retail-gas__participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023",
  "document_family_id": "retail-gas__participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023",
  "document_identity": "retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a",
  "document_title": "##### Participant Build Pack 3 - FRC B2B System Architecture Effective 30 June 2023",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a/chunk-da5d1fdb4430ea3d86a530ea.md",
  "heading_path": [
    "2.4.4. Critical time requirements (SA only)"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a/chunk-da5d1fdb4430ea3d86a530ea.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a.md"
}
---

High priority service orders impose some very specific maximum-duration processing times. Specifically for participants these relate to the times available at step 4 in the Message Cycle, and step 11 in the Transaction Cycle.
There is a specific detailed analysis of these times in Section 2.3.2 of the Participant Build Pack 3 - System Specifications
It is important to note there also must be a fallback mechanism for high priority service orders.
