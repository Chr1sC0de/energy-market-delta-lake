---
{
  "chunk_id": "chunk-ba68f493576fcf0fb4e6a741",
  "chunk_ordinal": 339,
  "chunk_text_sha256": "c649bbdec57e733c75a9cdc4106042d83e1887cb82b5ec4e1761d5837e9343f9",
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
              "b": 289.84745826927224,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 528.0952000000001,
              "t": 312.58086291015627
            },
            "charspan": [
              0,
              117
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/texts/1356"
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
              "b": 231.88745826927232,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 415.03888,
              "t": 278.14086291015633
            },
            "charspan": [
              0,
              118
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/texts/1357"
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
              "b": 186.7674582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 441.43888000000004,
              "t": 220.3008629101563
            },
            "charspan": [
              0,
              237
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/texts/1358"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-ba68f493576fcf0fb4e6a741.md",
  "heading_path": [
    "10.10.4. Residual surplus and shortfall allocation based on withdrawals"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-ba68f493576fcf0fb4e6a741.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400.md"
}
---

The shortfall/surplus allocation to Trading Participant p based on withdrawals for the hub for the billing period is:
```
If  p'  d  BP {  k  SN  cf(k) AQ U (p',d,cf(k)) +  k  SP  cf(k) AQ S (p',d,cf(k))  } = 0 WDA(p) = 0 Otherwise
```
```
WDA(p) = {NMB - p' DVA(p') +  d  p' VarC(p',d)} ×  [  d  BP {  k  SN  cf(k) AQ U (p,d,cf(k)) +  k  SP  cf(k) AQ S (p,d,cf(k)) } / (  p'  d  BP {  k  SN  cf(k) AQ U (p',d,cf(k)) +  k  SP  cf(k) AQ S (p',d,cf(k))  } ) ]
```
