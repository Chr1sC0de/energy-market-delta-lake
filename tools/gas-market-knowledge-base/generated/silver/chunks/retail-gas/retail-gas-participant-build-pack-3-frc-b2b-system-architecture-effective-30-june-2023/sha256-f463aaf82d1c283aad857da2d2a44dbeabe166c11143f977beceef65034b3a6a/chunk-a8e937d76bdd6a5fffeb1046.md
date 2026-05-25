---
{
  "chunk_id": "chunk-a8e937d76bdd6a5fffeb1046",
  "chunk_ordinal": 110,
  "chunk_text_sha256": "7cbab36484766660f9cfd9738daf3bb33bc437ddca27f45c21b852be2d2073d5",
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
              "b": 649.4174582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 525.42536,
              "t": 699.7508629101563
            },
            "charspan": [
              0,
              303
            ],
            "page_no": 30
          }
        ],
        "self_ref": "#/texts/494"
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
              "b": 615.8174582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 522.1186399999998,
              "t": 638.5508629101563
            },
            "charspan": [
              0,
              152
            ],
            "page_no": 30
          }
        ],
        "self_ref": "#/texts/495"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a/chunk-a8e937d76bdd6a5fffeb1046.md",
  "heading_path": [
    "Message Service Handler"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a/chunk-a8e937d76bdd6a5fffeb1046.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a.md"
}
---

The gateway Message Service Handler is required to perform conforming ebXML transactions with other participants. This implies appropriately addressed, digitally signed ebXML messages and acknowledgements. Beyond complying with the requirements of the FBS, the actual gateway technology is not mandated.
It is anticipated that participants will deploy an appropriately configured commercially available ebXML gateway solution rather than develop their own.
