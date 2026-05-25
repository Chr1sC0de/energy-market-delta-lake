---
{
  "chunk_id": "chunk-efebf52a64efd9d2be8f3758",
  "chunk_ordinal": 90,
  "chunk_text_sha256": "42e420fbde0c0c05c157dfff5184c805ca27784bf171ba20816207fbe34f1c52",
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
              "b": 430.1274582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 529.1263600000002,
              "t": 521.8808629101563
            },
            "charspan": [
              0,
              570
            ],
            "page_no": 26
          }
        ],
        "self_ref": "#/texts/414"
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
              "b": 382.72745826927235,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 523.07836,
              "t": 419.2608629101563
            },
            "charspan": [
              0,
              223
            ],
            "page_no": 26
          }
        ],
        "self_ref": "#/texts/415"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a/chunk-efebf52a64efd9d2be8f3758.md",
  "heading_path": [
    "4.5. Delivery"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a/chunk-efebf52a64efd9d2be8f3758.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a.md"
}
---

The FBS hub performs routing, protocol management, logging, and audit support. It does not participate as a FROM or TO party in the reliable messaging process. It does not act as a storeand-forward interim step in the message acknowledgement cycle. The sender of a message will expect to receive an acknowledgement message from the intended recipient routed via the FBS Hub, but it will not expect an acknowledgement from the hub itself. Under this regime the system provides authenticated and non-repudiable end-to-end delivery of aseXML documents between participants.
Given the error message functionality that forms part of the Reliable Messaging specification, and the message status services, the system will deliver highly dependable, highly automated, self-documenting message delivery.
