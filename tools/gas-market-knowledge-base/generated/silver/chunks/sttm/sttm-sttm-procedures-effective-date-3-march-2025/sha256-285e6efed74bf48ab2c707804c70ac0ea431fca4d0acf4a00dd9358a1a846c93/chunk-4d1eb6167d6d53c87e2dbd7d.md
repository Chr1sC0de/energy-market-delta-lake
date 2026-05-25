---
{
  "chunk_id": "chunk-4d1eb6167d6d53c87e2dbd7d",
  "chunk_ordinal": 296,
  "chunk_text_sha256": "1bfa731fc86e7fbb3db4e653ec76cbe8cd9b379968484b819601adecc7007276",
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
              "b": 228.29938739080808,
              "coord_origin": "BOTTOMLEFT",
              "l": 178.58,
              "r": 482.4721599999999,
              "t": 249.46086291015627
            },
            "charspan": [
              0,
              119
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/texts/1360"
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
              "b": 162.629387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 178.58,
              "r": 506.9286400000001,
              "t": 183.7908629101563
            },
            "charspan": [
              0,
              104
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/texts/1362"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/162"
        },
        "prov": [
          {
            "bbox": {
              "b": 129.98938739080802,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 504.37395999999984,
              "t": 153.3108629101563
            },
            "charspan": [
              0,
              110
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/texts/1363"
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
              "b": 97.47338739080806,
              "coord_origin": "BOTTOMLEFT",
              "l": 178.58,
              "r": 490.15901999999994,
              "t": 118.39086291015633
            },
            "charspan": [
              0,
              89
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/texts/1364"
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
              "b": 79.35338739080805,
              "coord_origin": "BOTTOMLEFT",
              "l": 176.06,
              "r": 210.50900000000001,
              "t": 88.15486291015623
            },
            "charspan": [
              0,
              6
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/texts/1365"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-3-march-2025/sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93.md",
    "source_manifest_line_number": 45,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/short-term-trading-market-sttm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/amendments-to-sttm-and-retail-market-procedures/decision/sttm-procedures-v150.pdf?rev=7f91b14f6cca4ca7bf1e7705ef8362c2&sc_lang=en"
  },
  "content_sha256": "285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93",
  "corpus": "sttm",
  "document_family": "sttm__sttm-procedures-effective-date-3-march-2025",
  "document_family_id": "sttm__sttm-procedures-effective-date-3-march-2025",
  "document_identity": "sttm/sttm-sttm-procedures-effective-date-3-march-2025/sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93",
  "document_title": "##### STTM Procedures Effective date 3 March 2025",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-3-march-2025/sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93/chunk-4d1eb6167d6d53c87e2dbd7d.md",
  "heading_path": [
    "10.6.2. Ad hoc payments for contingency gas resettlement"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-3-march-2025/sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93/chunk-4d1eb6167d6d53c87e2dbd7d.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-3-march-2025/sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93.md"
}
---

```
SDQ(p,d) =  k  SP [MAX(0, -1 × DQT(p,d,k))] +  k  SP [MAX(0, -1 × DQF(p,d,k))] +  k  SN [MAX(0, -1 × DQF(p,d,k))]
```
LDQ(p,d) =  k  SP [MAX(0, DQT(p,d,k))] +  k  SP [MAX(0, DQF(p,d,k))] +  k  SN [MAX(0, DQF(p,d,k))]
- (iii) Trading Participant 's ad hoc payment where contingency gas was required to increase supply to the hub :
AHP(p,d) = MAX (0, MIN(PDevNT(p,d,k) - RDevN(d), ∑ p AHC(p,d) / ∑ p SDQ(p,d)) x SDQ(p,d))
Where:
