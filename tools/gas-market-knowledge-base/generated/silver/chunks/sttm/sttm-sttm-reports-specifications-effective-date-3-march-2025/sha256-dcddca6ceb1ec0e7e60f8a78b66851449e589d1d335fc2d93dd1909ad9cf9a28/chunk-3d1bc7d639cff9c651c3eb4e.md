---
{
  "chunk_id": "chunk-3d1bc7d639cff9c651c3eb4e",
  "chunk_ordinal": 367,
  "chunk_text_sha256": "577694ce42a7601b486d944e1c374bbbfffb5187cdc7152645f06f325df0a523",
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
              "b": 75.36358642578125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.2040786743164,
              "r": 527.3839721679688,
              "t": 649.0863952636719
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 83
          }
        ],
        "self_ref": "#/tables/115"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md",
    "source_manifest_line_number": 47,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/short-term-trading-market-sttm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/amendments-to-sttm-and-retail-market-procedures/decision/sttm-reports-specifications-v191.pdf?rev=30dbf1c556a7486b8c80e244b8690226&sc_lang=en"
  },
  "content_sha256": "dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28",
  "corpus": "sttm",
  "document_family": "sttm__sttm-reports-specifications-effective-date-3-march-2025",
  "document_family_id": "sttm__sttm-reports-specifications-effective-date-3-march-2025",
  "document_identity": "sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28",
  "document_title": "##### STTM Reports Specifications Effective date 3 March 2025",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-3d1bc7d639cff9c651c3eb4e.md",
  "heading_path": [
    "5.5.12. INT709 - Trading Participant Market Schedule Variation"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-3d1bc7d639cff9c651c3eb4e.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

= False. submitter_role, Comment = The role of the submitter with respect to the market schedule variation Valid roles are shipper to the hub, shipper from the hub • STH - Shipper to the hub • SFH - Shipper from the hub • NAH - Network user. submitter_facility_identifier, Not Null = True. submitter_facility_identifier, Primary Key = False. submitter_facility_identifier, Comment = The unique identifier of the submitter's facility .. submitter_facility_name, Not Null = True. submitter_facility_name, Primary Key = False. submitter_facility_name, Comment = The name of the submitter's facility. submitter_mms_impact, Not Null = True. submitter_mms_impact, Primary Key = False. submitter_mms_impact, Comment = Indicates if the MSV results in an (I) increase or (D) decrease of the submitter's modified market schedule (MMS). • I - Increase • D - Decrease. counter_party_identifier, Not Null = True. counter_party_identifier, Primary Key
