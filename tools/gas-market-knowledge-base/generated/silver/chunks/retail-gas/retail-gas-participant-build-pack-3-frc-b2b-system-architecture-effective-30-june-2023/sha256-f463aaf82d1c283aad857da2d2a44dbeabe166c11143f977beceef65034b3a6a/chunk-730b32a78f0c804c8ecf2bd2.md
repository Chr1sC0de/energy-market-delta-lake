---
{
  "chunk_id": "chunk-730b32a78f0c804c8ecf2bd2",
  "chunk_ordinal": 102,
  "chunk_text_sha256": "65dd6489040e1023f5899d5e044f25106533bebe027b39651e738adc6d76ed55",
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
              "b": 239.6574582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 525.18412,
              "t": 290.0208629101562
            },
            "charspan": [
              0,
              331
            ],
            "page_no": 28
          }
        ],
        "self_ref": "#/texts/460"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/15"
        },
        "prov": [
          {
            "bbox": {
              "b": 191.6574582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 515.3431999999998,
              "t": 228.07086291015628
            },
            "charspan": [
              0,
              192
            ],
            "page_no": 28
          }
        ],
        "self_ref": "#/texts/461"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/15"
        },
        "prov": [
          {
            "bbox": {
              "b": 143.5374582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 515.3431999999998,
              "t": 180.07086291015628
            },
            "charspan": [
              0,
              190
            ],
            "page_no": 28
          }
        ],
        "self_ref": "#/texts/462"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a/chunk-730b32a78f0c804c8ecf2bd2.md",
  "heading_path": [
    "Generating an acknowledgement message"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a/chunk-730b32a78f0c804c8ecf2bd2.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a.md"
}
---

There is an important clarification to section 9.3.3 of the ebXML Message Service Specification v 1.0. In the FBS implementation of ebXML Message Service the Acknowledgement element will be sent asynchronously and the value of the message header elements must be set as per the ebXML specification with the following clarification.
- The From element must be populated with the To element extracted from the message received and this is the only PartyId element from the message received to be included in this From element.
- The To element must be populated with the From element extracted from the message received and this is the only PartyId element from the message received to be included in this To element.
