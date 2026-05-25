---
{
  "chunk_id": "chunk-b8d75b82500b7c8ab11ef61f",
  "chunk_ordinal": 445,
  "chunk_text_sha256": "8071bd133cd0187bd3077838254689b658b228ac639a69ee6ba2055108f6acc9",
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
              "b": 488.52069091796875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.38021087646484,
              "r": 527.3760375976562,
              "t": 749.7579040527344
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 101
          }
        ],
        "self_ref": "#/tables/146"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-b8d75b82500b7c8ab11ef61f.md",
  "heading_path": [
    "5.5.25. INT725 - Trading Participant MOS Offer Confirmation"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-b8d75b82500b7c8ab11ef61f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

facility_name, Not Null = True. facility_name, Primary Key = False. facility_name, Comment = The name of the pipeline which the MOS offer relates to. stack_type, Not Null = True. stack_type, Primary Key = False. stack_type, Comment = This field is a flag to indicate whether this is an Increase MOS offer or a Decrease MOS offer. Valid values are: • I • D. mos_offer_identifier, Not Null = True. mos_offer_identifier, Primary Key = True. mos_offer_identifier, Comment = The unique identifier of the relevant MOS offer. mos_offer_step_number, Not Null = True. mos_offer_step_number, Primary Key = True. mos_offer_step_number, Comment = The number of the MOS offer step (1 - 10). step_price, Not Null = True. step_price, Primary Key = False. step_price, Comment = The price of MOS offer step (1-10). step_quantity, Not Null = True. step_quantity, Primary Key = False. step_quantity,
