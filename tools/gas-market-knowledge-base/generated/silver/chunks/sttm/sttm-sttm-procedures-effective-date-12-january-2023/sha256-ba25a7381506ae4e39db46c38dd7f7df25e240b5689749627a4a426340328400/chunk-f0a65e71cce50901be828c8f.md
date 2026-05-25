---
{
  "chunk_id": "chunk-f0a65e71cce50901be828c8f",
  "chunk_ordinal": 336,
  "chunk_text_sha256": "c7a422c836710d3ea1e30893de2828a7782bdd0345d86496f2cfedcbcf499437",
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
        "label": "code",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 601.7774582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 448.05147999999997,
              "t": 683.6708629101563
            },
            "charspan": [
              0,
              371
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/texts/1347"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "code",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 601.7774582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 223.49,
              "r": 517.4288799999999,
              "t": 745.4708629101564
            },
            "charspan": [
              0,
              79
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/texts/1348"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-f0a65e71cce50901be828c8f.md",
  "heading_path": [
    "Where:"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-f0a65e71cce50901be828c8f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400.md"
}
---

```
If DPFlag(d) = 0 then LI(d,k) = 1 and LD(d,k) = 1 for all k  SP and all k  if DPFlag(d) = 1 and NMB ≥ 0 then LI(d,k) = 1 and LD(d,k) = 1 for all k  if DPFlag(d) = 1 and NMB <0 then LI(d,k) = 0 and LD(d,k) = 1 for all k  if DPFlag(d) = 1 and NMB ≥ 0 then LI(d,k) = 1 and LD(d,k) = 1 for all k  if DPFlag(d) = 1 and NMB < 0 then LI(d,k) = 0 and LD(d,k) = 1 for all k 
```
```
SN  [MAX(0,DQF(p,d,k)) × LI(d,k) -  MIN(0,DQF(p,d,k)) × LD(d,k)] SN SP SP SN SN
```
