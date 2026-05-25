---
{
  "chunk_id": "chunk-9fa0dabb1a71e2df9fffe745",
  "chunk_ordinal": 338,
  "chunk_text_sha256": "aeb7ea96e1aeb843f6910b9422495ab74fddb1c1884a0ded630acd94fb8d2623",
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
              "b": 481.74745826927233,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 524.1352,
              "t": 504.4808629101563
            },
            "charspan": [
              0,
              117
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/texts/1351"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "formula",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 423.78745826927235,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 184.46887999999998,
              "t": 470.0408629101563
            },
            "charspan": [
              0,
              40
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/texts/1352"
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
              "b": 403.2674582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 474.94888000000003,
              "t": 412.2008629101563
            },
            "charspan": [
              0,
              75
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/texts/1353"
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
              "b": 349.52962931899606,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 524.8580000000003,
              "t": 394.9419829101563
            },
            "charspan": [
              0,
              414
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/texts/1354"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-9fa0dabb1a71e2df9fffe745.md",
  "heading_path": [
    "10.10.3. Surplus and shortfall allocation based on billing period deviations"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-9fa0dabb1a71e2df9fffe745.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400.md"
}
---

The shortfall/surplus allocation based on deviations for Trading Participant p for the hub for the billing period is:
<!-- formula-not-decoded -->
```
DVA(p) = MAX(0, MIN( AllCAP × DQB(p) , NMB × {DQB(p) / (  p' DQB(p')) } ))
```
Note : The last term allocates NMB in proportion to deviations over the billing period , while the first term caps the allocation for positive NMB values at a rate of AllCAP, the $/GJ cap on positive allocations.  This cap is intended to stop Trading Participants who deviated getting a high proportion of their deviation charges returned to them. Negative NMB values are allocated based on withdrawals in 10.10.4.
