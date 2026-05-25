---
{
  "chunk_id": "chunk-c64ed1fb1cb8d4f459c2ae2f",
  "chunk_ordinal": 342,
  "chunk_text_sha256": "8098faf71b84592061cf7eaccdc6f98fae37e360df820d6d13e06bc0827ca835",
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
              "b": 404.26861572265625,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.22222137451172,
              "r": 527.3507690429688,
              "t": 749.8220520019531
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 112
          }
        ],
        "self_ref": "#/tables/110"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-c64ed1fb1cb8d4f459c2ae2f.md",
  "heading_path": [
    "5.5.5. INT704 - Trading Participant Deviation and Variation Data v2"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-c64ed1fb1cb8d4f459c2ae2f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

charge_method, Not Null = True. charge_method, Primary Key = True. charge_method, Comment = For each facility both the GJ and percentage calculations are performed and the result that is most advantageous to the trading participant is used. This field represents that method either 'GJ or 'percent' • GJ • percent For Release 34 changes, GJ and percentage calculations are not used to calculate deviation charge/payment. The value of this field will be: • R34-changes. charge_payment_type, Not Null = True. charge_payment_type, Primary Key = True. charge_payment_type, Comment = Refers to the charge type (DVC) Deviation Charge or (DVP) Deviation Payment or (VAC) Variation Charge. • DVC • DVP • VAC. charge_payment_desc, Not Null = True. charge_payment_desc, Primary Key = False. charge_payment_desc, Comment = The charge/payment description.. quantity_gj, Not Null = True. quantity_gj, Primary Key = False. quantity_gj, Comment = The quantity in GJ..
