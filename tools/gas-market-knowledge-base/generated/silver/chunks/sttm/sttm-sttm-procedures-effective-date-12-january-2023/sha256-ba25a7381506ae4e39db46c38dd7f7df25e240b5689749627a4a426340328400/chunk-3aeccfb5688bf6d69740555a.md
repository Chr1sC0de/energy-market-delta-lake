---
{
  "chunk_id": "chunk-3aeccfb5688bf6d69740555a",
  "chunk_ordinal": 301,
  "chunk_text_sha256": "6d77390130636fe864cca2c9ba662f93441f87599be734769bb2ab79186838bb",
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
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/137"
        },
        "prov": [
          {
            "bbox": {
              "b": 241.48745826927234,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 512.55892,
              "t": 264.22086291015626
            },
            "charspan": [
              0,
              147
            ],
            "page_no": 76
          }
        ],
        "self_ref": "#/texts/1152"
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
              "b": 196.48745826927234,
              "coord_origin": "BOTTOMLEFT",
              "l": 178.58,
              "r": 483.58888,
              "t": 229.90086291015632
            },
            "charspan": [
              0,
              181
            ],
            "page_no": 76
          }
        ],
        "self_ref": "#/texts/1153"
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
              "b": 142.7396293189961,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 510.55000000000007,
              "t": 188.01198291015635
            },
            "charspan": [
              0,
              343
            ],
            "page_no": 76
          }
        ],
        "self_ref": "#/texts/1154"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/138"
        },
        "prov": [
          {
            "bbox": {
              "b": 109.33745826927225,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 524.8688400000001,
              "t": 132.07086291015628
            },
            "charspan": [
              0,
              94
            ],
            "page_no": 76
          }
        ],
        "self_ref": "#/texts/1155"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-3aeccfb5688bf6d69740555a.md",
  "heading_path": [
    "10.7.3. MOS settlement"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-3aeccfb5688bf6d69740555a.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400.md"
}
---

- (a) The payment to Trading Participant p for MOS provided to the hub under one or more MOS increase offers or MOS decrease offers for gas day d is:
```
MCP(p,d) =  k  SP  m(k)  MOSFP(p,d,m(k)) +  k  SP  m(k)  j  (MOSIC S (p,d,m(k),j) × MOSAI S (p,d,m(k),j)) +  k  SP  m(k)  j  (MOSDC S (p,d,m(k),j) × MOSAD S (p,d,m(k),j))
```
Note : This payment includes a fixed charge for MOS increase offers and MOS decrease offers included in a MOS stack (which will be zero at market commencement) and payments for MOS increases and decreases under MOS increase offers and MOS decrease offers based on the quantities allocated to those MOS increase offers and MOS decrease offers .
- (b) The payment to Trading Participant p for overrun MOS provided to the hub for gas day d is:
