---
{
  "chunk_id": "chunk-7d75836d7cb55ea620b44ebc",
  "chunk_ordinal": 117,
  "chunk_text_sha256": "522cc4ba5415f40288e68486dfc25e141d1e8c5022f3bbe9245b7e53ac2a5f60",
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
              "b": 292.48745826927234,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 521.6034400000003,
              "t": 384.2208629101563
            },
            "charspan": [
              0,
              583
            ],
            "page_no": 31
          }
        ],
        "self_ref": "#/texts/526"
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
              "b": 231.25745826927232,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 527.64644,
              "t": 281.59086291015626
            },
            "charspan": [
              0,
              375
            ],
            "page_no": 31
          }
        ],
        "self_ref": "#/texts/527"
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
              "b": 197.6574582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 527.8523600000001,
              "t": 220.39086291015633
            },
            "charspan": [
              0,
              171
            ],
            "page_no": 31
          }
        ],
        "self_ref": "#/texts/528"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a/chunk-7d75836d7cb55ea620b44ebc.md",
  "heading_path": [
    "6.3. Digital Signature"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a/chunk-7d75836d7cb55ea620b44ebc.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-3-frc-b2b-system-architecture-effective-30-june-2023/sha256-f463aaf82d1c283aad857da2d2a44dbeabe166c11143f977beceef65034b3a6a.md"
}
---

To create a digital signature for a message, the data to be signed is transformed by an algorithm that takes as input the private key of the sender. Because a transformation determined by the sender's private key can only be undone if the reverse transform takes as a parameter the sender's public key, a recipient of the transformed data can be confident of the origin of the data (the identity of the sender). If the data can be verified using the sender's public key, then it must have been signed using the corresponding private key (to which only the sender should have access).
For signature verification to be meaningful, the verifier must have confidence that the public key does actually belong to the sender. A certificate, issued by the Certificate Authority, is an assertion of the validity of the binding between the certificate's subject and their public key such that other users can be confident that the public key corresponds to the subject.
In the FBS, the ebXML payload (i.e. the aseXML document) will be signed. The ability to do this needs be a feature of the ebXML MSH product that is chosen by participants.
