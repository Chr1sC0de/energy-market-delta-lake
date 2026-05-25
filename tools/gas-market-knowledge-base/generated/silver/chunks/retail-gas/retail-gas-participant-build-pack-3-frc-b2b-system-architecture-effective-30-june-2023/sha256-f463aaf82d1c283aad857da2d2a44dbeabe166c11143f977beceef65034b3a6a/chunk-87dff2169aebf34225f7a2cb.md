---
{
  "chunk_id": "chunk-87dff2169aebf34225f7a2cb",
  "chunk_ordinal": 38,
  "chunk_text_sha256": "f17ad3d5de2cebe88ed3305b80f594de2f078fd3da9b33dc8c4c1ed8574a2efe",
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
              "b": 705.6974582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 106.22,
              "r": 523.1854399999999,
              "t": 728.4308629101563
            },
            "charspan": [
              0,
              176
            ],
            "page_no": 10
          }
        ],
        "self_ref": "#/texts/164"
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
              "b": 644.4974582692722,
              "coord_origin": "BOTTOMLEFT",
              "l": 106.22,
              "r": 523.2053599999999,
              "t": 694.8308629101564
            },
            "charspan": [
              0,
              330
            ],
            "page_no": 10
          }
        ],
        "self_ref": "#/texts/165"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "caption",
        "parent": {
          "$ref": "#/pictures/17"
        },
        "prov": [
          {
            "bbox": {
              "b": 619.3443566676116,
              "coord_origin": "BOTTOMLEFT",
              "l": 106.22,
              "r": 337.0012,
              "t": 627.4899829101563
            },
            "charspan": [
              0,
              46
            ],
            "page_no": 10
          }
        ],
        "self_ref": "#/texts/166"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a/chunk-87dff2169aebf34225f7a2cb.md",
  "heading_path": [
    "2.3.3. Transaction Exchange Scenario"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a/chunk-87dff2169aebf34225f7a2cb.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a.md"
}
---

The transaction exchange process is an application level process. Transactions are described in an aseXML document; this document is carried as the payload of an ebXML message.
The figure below shows an example of a successful transaction exchange scenario. A transaction, for example a Customer Transfer Request, is sent to AEMO. AEMO acknowledges receipt of the transaction.  Following some internal processing, AEMO issues a transaction to that Participant and this transaction is also duly acknowledged.
Figure 6 Transaction Exchange Sequence Diagram
