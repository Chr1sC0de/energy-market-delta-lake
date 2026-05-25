---
{
  "chunk_id": "chunk-0820bc9e305a5cdf8e2ebae5",
  "chunk_ordinal": 142,
  "chunk_text_sha256": "dc75ff1ea2f87588d227febe58b76ec16e423451985976e5f4f6590ce4b3b39a",
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
              "b": 81.0098876953125,
              "coord_origin": "BOTTOMLEFT",
              "l": 100.23304748535156,
              "r": 526.2990112304688,
              "t": 748.0326461791992
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 39
          }
        ],
        "self_ref": "#/tables/21"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-0820bc9e305a5cdf8e2ebae5.md",
  "heading_path": [
    "8.1. Cumulative price threshold"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-0820bc9e305a5cdf8e2ebae5.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400.md"
}
---

determined for gas day D=d+1, calculated as Max(0, HP(d));. , 1 = (ii). , 2 = Cy(d) is the contribution of prices determined for gas day D=d, calculated as Max(0, HCGP1(d) - Cx(d-1));. , 1 = (iii). , 2 = Cz(d) is the contribution of prices determined for gas day D=d-1, calculated as: (A) if DPFlag(d) = 1 for gas day D=d-1, then Cz(d) = Max(0, Max(EPP(d), HCGP2(d), MPC(d-1)) - Cy(d-1) - Cx(d-2));. , 1 = (iv). , 2 = HP(d) is, subject to paragraph (d), the ex ante market price determined on gas day d for the gas day D=d+1;. , 1 = (v). , 2 = HCGP1(d) is the highest priced contingency gas offer scheduled for gas day D=d
