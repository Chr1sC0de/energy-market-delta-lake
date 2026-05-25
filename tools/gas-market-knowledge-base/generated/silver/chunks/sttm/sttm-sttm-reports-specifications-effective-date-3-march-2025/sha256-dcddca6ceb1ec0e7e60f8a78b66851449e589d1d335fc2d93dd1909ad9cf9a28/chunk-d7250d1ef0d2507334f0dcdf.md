---
{
  "chunk_id": "chunk-d7250d1ef0d2507334f0dcdf",
  "chunk_ordinal": 281,
  "chunk_text_sha256": "20ab2a084a8045f400c90af9d25ee5b92d46790aaf184e1762471cd54ccec221",
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
              "b": 170.86297607421875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.30350494384766,
              "r": 527.3541259765625,
              "t": 561.2022094726562
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 63
          }
        ],
        "self_ref": "#/tables/86"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-d7250d1ef0d2507334f0dcdf.md",
  "heading_path": [
    "5.4.32. INT682 - Settlement MOS and Capacity Data"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-d7250d1ef0d2507334f0dcdf.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

The total allocated quantity - for the facility - for contractedMOS . A positive quantity indicates an increase in flow to the hub; a negative quantity indicates an increase in flow from the hub.. mos_overrun_qty, Not Null = True. mos_overrun_qty, Primary Key = False. mos_overrun_qty, Comment = The total allocated quantity - for the facility - for MOSoverrun. A positive quantity indicates an increase in flow to the hub; a negative quantity indicates an increase in flow from the hub.. firm_not_flowed, Not Null = True. firm_not_flowed, Primary Key = False. firm_not_flowed, Comment = The total quantity of gas offered on firm trading rights "to the hub" but not flowed (based on the effective allocated quantity of gas flowed) for the gas day on the facility. Defined in the STTM settlement equations as TFGNQ(d,k). as_available_flowed, Not Null = True. as_available_flowed, Primary Key = False. as_available_flowed, Comment = The total effective quantity of gas flowed via "as available" trading rights to the hub for the gas day on the facility. Defined in
