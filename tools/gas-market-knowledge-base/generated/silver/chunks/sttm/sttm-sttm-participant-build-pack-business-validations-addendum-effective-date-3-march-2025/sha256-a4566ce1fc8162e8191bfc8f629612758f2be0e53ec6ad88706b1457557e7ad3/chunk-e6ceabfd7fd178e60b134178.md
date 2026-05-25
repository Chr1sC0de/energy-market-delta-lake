---
{
  "chunk_id": "chunk-e6ceabfd7fd178e60b134178",
  "chunk_ordinal": 179,
  "chunk_text_sha256": "c9892b1529b4eca3ef5094e17a71b2b981d5b933e3d5c24ba2394fe4ec0f9952",
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
        "label": "caption",
        "parent": {
          "$ref": "#/tables/72"
        },
        "prov": [
          {
            "bbox": {
              "b": 462.35435666761157,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 224.93,
              "t": 470.4999829101563
            },
            "charspan": [
              0,
              33
            ],
            "page_no": 45
          }
        ],
        "self_ref": "#/texts/670"
      },
      {
        "children": [
          {
            "$ref": "#/texts/670"
          }
        ],
        "content_layer": "body",
        "label": "table",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 284.366455078125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.3052978515625,
              "r": 522.2095947265625,
              "t": 458.92730712890625
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 45
          }
        ],
        "self_ref": "#/tables/72"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "caption",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 262.4143566676116,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 281.57,
              "t": 270.55998291015635
            },
            "charspan": [
              0,
              46
            ],
            "page_no": 45
          }
        ],
        "self_ref": "#/texts/671"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3.md",
    "source_manifest_line_number": 41,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/short-term-trading-market-sttm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/amendments-to-sttm-and-retail-market-procedures/decision/sttm-participant-build-pack-business-validations-addendum-v81.pdf?rev=eec7a7dd84b947f7af5164f757b8f62e&sc_lang=en"
  },
  "content_sha256": "a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3",
  "corpus": "sttm",
  "document_family": "sttm__sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025",
  "document_family_id": "sttm__sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025",
  "document_identity": "sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3",
  "document_title": "##### STTM Participant Build Pack Business Validations Addendum Effective date 3 March 2025",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3/chunk-e6ceabfd7fd178e60b134178.md",
  "heading_path": [
    "2.13. Pipeline CTM Data"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3/chunk-e6ceabfd7fd178e60b134178.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3.md"
}
---

Table 52 Pipeline CTM Data Format

mirn, Field type = varchar(10). mirn, M/O/NR = M. mirn, Description = Meter Installation Registration Number. gasdate, Field type = Datetime. gasdate, M/O/NR = M. gasdate, Description = ccyy-mm-dd. consumedenergygj, Field type = Numeric(18,9). consumedenergygj, M/O/NR = M. consumedenergygj, Description = Energy data in Gigajoules. qualityid, Field type = Integer. qualityid, M/O/NR = O. qualityid, Description = Optional - if not supplied Quality Id 205 assumed. For Queensland Pipeline CTM Submissions Quality ID : Description 205 : Normal - Actual Read - PO 206 : Estimated - PO 207 : Substituted - PO
Table 53 Pipeline CTM Data Transaction Context
