---
{
  "chunk_id": "chunk-10968f4c96bd4b1f82ae8eb9",
  "chunk_ordinal": 288,
  "chunk_text_sha256": "b667f08d746d8a2f1ad4caa4fc255083853d60e527af263e7e6b00a9f7d1cda7",
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
              "b": 117.49745826927233,
              "coord_origin": "BOTTOMLEFT",
              "l": 178.58,
              "r": 501.10888,
              "t": 137.95086291015627
            },
            "charspan": [
              0,
              114
            ],
            "page_no": 73
          }
        ],
        "self_ref": "#/texts/1086"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/126"
        },
        "prov": [
          {
            "bbox": {
              "b": 99.37745826927232,
              "coord_origin": "BOTTOMLEFT",
              "l": 178.58,
              "r": 535.76284,
              "t": 108.31086291015629
            },
            "charspan": [
              0,
              72
            ],
            "page_no": 73
          }
        ],
        "self_ref": "#/texts/1087"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/126"
        },
        "prov": [
          {
            "bbox": {
              "b": 87.74145826927236,
              "coord_origin": "BOTTOMLEFT",
              "l": 178.58,
              "r": 337.15888,
              "t": 96.67486291015632
            },
            "charspan": [
              0,
              37
            ],
            "page_no": 73
          }
        ],
        "self_ref": "#/texts/1088"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/127"
        },
        "prov": [
          {
            "bbox": {
              "b": 725.0174582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 178.58,
              "r": 533.71396,
              "t": 745.4708629101564
            },
            "charspan": [
              0,
              114
            ],
            "page_no": 74
          }
        ],
        "self_ref": "#/texts/1092"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400.md",
    "source_manifest_line_number": 43,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/short-term-trading-market-sttm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/sttm/policies/sttm-procedures-v134.pdf?rev=f9d5cb1606a240bbb8a3701d76eb7a2f&sc_lang=en"
  },
  "content_sha256": "ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400",
  "corpus": "sttm",
  "document_family": "sttm__sttm-procedures-effective-date-12-january-2023",
  "document_family_id": "sttm__sttm-procedures-effective-date-12-january-2023",
  "document_identity": "sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400",
  "document_title": "##### STTM Procedures Effective date 12 January 2023",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-10968f4c96bd4b1f82ae8eb9.md",
  "heading_path": [
    "Explanatory Note"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-10968f4c96bd4b1f82ae8eb9.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400.md"
}
---

{  k  SP [MAX(0, (MAX(0, -1 × CQ S (p,d,k, fd='to')) - MAX(0, DQT(p,d,k)) MAX(0, -1 × CQP S  (p,d,k fd='to'))))]
+  k  SP [MAX(0, (MAX(0, CQ S (p,d,k, fd='from')) - MAX(0, DQF(p,d,k))
- MAX(0, CQP S  (p,d,k fd='from'))))]
+  k  SN [MAX(0, (MAX(0, CQ U (p,d,k, fd='from')) - MAX(0, DQF(p,d,k)) - MAX(0, CQP U  (p,d,k fd='from'))))] } )
