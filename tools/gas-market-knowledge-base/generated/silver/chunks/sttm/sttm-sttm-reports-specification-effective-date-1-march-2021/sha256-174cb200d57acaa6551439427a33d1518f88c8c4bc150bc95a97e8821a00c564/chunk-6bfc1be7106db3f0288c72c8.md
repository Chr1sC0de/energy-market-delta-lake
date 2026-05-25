---
{
  "chunk_id": "chunk-6bfc1be7106db3f0288c72c8",
  "chunk_ordinal": 50,
  "chunk_text_sha256": "ea66b9ed29b8a066c1ba3f24026df9da355840fbed077a83110029ade626ca2f",
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
              "b": 410.757080078125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.36498260498047,
              "r": 527.1158447265625,
              "t": 749.2548294067383
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 16
          }
        ],
        "self_ref": "#/tables/12"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md",
    "source_manifest_line_number": 46,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/short-term-trading-market-sttm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/sttm/policies/sttm-reports-specifications-v190.pdf?rev=ee0167ede9c94105b170ff3edcc2fc99&sc_lang=en"
  },
  "content_sha256": "174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564",
  "corpus": "sttm",
  "document_family": "sttm__sttm-reports-specification-effective-date-1-march-2021",
  "document_family_id": "sttm__sttm-reports-specification-effective-date-1-march-2021",
  "document_identity": "sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564",
  "document_title": "##### STTM Reports Specification Effective date 1 March 2021",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-6bfc1be7106db3f0288c72c8.md",
  "heading_path": [
    "2.2. File Naming Convention"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-6bfc1be7106db3f0288c72c8.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

Fixed Character, Regular Expression = [_] (underscore). Report version number, Regular Expression = v[0-9]{1,2}. Fixed Character, Regular Expression = [_] (underscore). Report name (greater than or equal to 9 characters and less than or equal to 52 characters long) uniquely identifying the report, Regular Expression = ([a-z0-9_\-\\_]{9,52}). Fixed Character, Regular Expression = [_] (underscore). Suffix to identify that this file is report, Regular Expression = 'rpt'. Fixed Character, Regular Expression = [_] (underscore). Participant Company Id or 1 if it is a public report, Regular Expression = [0-9]{1,3}. Fixed Character, Regular Expression = [_] (underscore). Fixed Character, Regular Expression = [~] (tilde). Date/timestamp in the format YYYYMMDDhhmmss when the file has been generated, 24 hour format market time, Regular Expression =
