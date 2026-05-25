---
{
  "chunk_id": "chunk-0111c0ee9bf48ddcdc682fa6",
  "chunk_ordinal": 85,
  "chunk_text_sha256": "5b6b74b757c519256060692181a1fa2ac137e0b5b7d7341e5a15c617fb642303",
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
              "b": 115.19745826927226,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 493.18888000000004,
              "t": 137.95086291015627
            },
            "charspan": [
              0,
              169
            ],
            "page_no": 24
          }
        ],
        "self_ref": "#/texts/392"
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
              "b": 81.59745826927235,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 529.3296799999999,
              "t": 104.33086291015627
            },
            "charspan": [
              0,
              178
            ],
            "page_no": 24
          },
          {
            "bbox": {
              "b": 709.6574582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 515.1586,
              "t": 746.1908629101564
            },
            "charspan": [
              179,
              396
            ],
            "page_no": 25
          }
        ],
        "self_ref": "#/texts/393"
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
              "b": 648.4574582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 514.30876,
              "t": 698.7908629101563
            },
            "charspan": [
              0,
              299
            ],
            "page_no": 25
          }
        ],
        "self_ref": "#/texts/397"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a/chunk-0111c0ee9bf48ddcdc682fa6.md",
  "heading_path": [
    "4.4.2. TraceHeader element"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a/chunk-0111c0ee9bf48ddcdc682fa6.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a.md"
}
---

While the From and To elements contain participant addresses, routing between two participants via the hub is achieved by configuring the TraceHeader to address the hub.
The TraceHeader element contains information about a single transmission of a message between two instances of a MSH.  If a message traverses multiple hops by passing through one or more intermediate MSH nodes as it travels between the From Party MSH and the To Party MSH, then each transmission over each successive 'hop' results in the addition of a new TraceHeader element by the Sending MSH .
In the FBS participants will send messages with one intermediate hop, that being the hub. Methodology for doing this is described in the ebXML Messaging Service Specification V1.0 . The hub address to be used in this field is specified in Section 4.4.2 of the FRC B2B System Specifications document.
