---
{
  "chunk_id": "chunk-5ec6a7f5b2d48fb836ac7b10",
  "chunk_ordinal": 21,
  "chunk_text_sha256": "f43b604421de8d167b4989ac47300e55ca68a54c11725cd4e80a3c2126bf7185",
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
              "b": 110.30938739080807,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 525.9683599999998,
              "t": 148.15086291015632
            },
            "charspan": [
              0,
              218
            ],
            "page_no": 5
          }
        ],
        "self_ref": "#/texts/98"
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
              "b": 89.793387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 146.639,
              "t": 98.59486291015628
            },
            "charspan": [
              0,
              8
            ],
            "page_no": 5
          }
        ],
        "self_ref": "#/texts/99"
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
              "b": 69.27338739080801,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 369.649,
              "t": 78.0748629101563
            },
            "charspan": [
              0,
              62
            ],
            "page_no": 5
          }
        ],
        "self_ref": "#/texts/100"
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
              "b": 716.3893873908081,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 238.5574400000001,
              "t": 745.7108629101564
            },
            "charspan": [
              0,
              63
            ],
            "page_no": 6
          }
        ],
        "self_ref": "#/texts/104"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-5ec6a7f5b2d48fb836ac7b10.md",
  "heading_path": [
    "2.1.5. Treatment of literals"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-5ec6a7f5b2d48fb836ac7b10.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

The CSV import application must be able to parse literals irrespective of whether they are surrounded by double-quotes, single-quotes, or not. If commas are used in the literal, it shall be surrounded by double quotes.
Example:
123,"This is a sample field, This is another sample field",456
123,'This is a sample field',456 123,This is a sample field,456
