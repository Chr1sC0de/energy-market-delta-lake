---
{
  "chunk_id": "chunk-fb55fdaced2294d24d9a0126",
  "chunk_ordinal": 324,
  "chunk_text_sha256": "eac76f7a33b01f8fc3d3ec879867f90f2c13ac755a07f01d22965f3ac07807d5",
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
              "b": 519.079387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 178.58,
              "r": 524.1538000000003,
              "t": 576.7508629101563
            },
            "charspan": [
              0,
              359
            ],
            "page_no": 93
          }
        ],
        "self_ref": "#/texts/1498"
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
              "b": 500.959387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 153.119,
              "t": 509.7608629101563
            },
            "charspan": [
              0,
              4
            ],
            "page_no": 93
          }
        ],
        "self_ref": "#/texts/1499"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-3-march-2025/sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93/chunk-fb55fdaced2294d24d9a0126.md",
  "heading_path": [
    "10.8.4. MOS decrease cost"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-3-march-2025/sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93/chunk-fb55fdaced2294d24d9a0126.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-3-march-2025/sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93.md"
}
---

MOSXD(d) =  [  p  k  SP  m(k)  j (MOSDC S (p,d,m(k),j) × MOSAD S (p,d,m(k),j)) +  p  k  SP (ORPD(d,k) × (-1 ×  c(k){ MIN(0, OMAQ S (p,d,ct(k))) + MIN(0, OMAQ S (p,d,cf(k))) })) - p MCCC(p,d+2) - p MCOC(p,d+2) ]  /  p  k  SP  c(k) { MIN(0,MAQ S (p,d,ct(k))) + MIN(0,MAQ S (p,d,cf(k))) +  MIN(0, OMAQ S (p,d,ct(k))) + MIN(0, OMAQ S (p,d,cf(k))) }
Else
