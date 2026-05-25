---
{
  "chunk_id": "chunk-1f5d523275072b0cc1e3deec",
  "chunk_ordinal": 270,
  "chunk_text_sha256": "6f0da3b3c096b603b029184cfdc356f885088bcc74014cdb857782aea833e1bd",
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
              "b": 113.41302490234375,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.4511947631836,
              "r": 527.6141357421875,
              "t": 715.7875061035156
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 69
          }
        ],
        "self_ref": "#/tables/49"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-1f5d523275072b0cc1e3deec.md",
  "heading_path": [
    "described in the following table:"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-1f5d523275072b0cc1e3deec.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400.md"
}
---

terms = FSC(op,d,ok,ofd) = FSC(op,d,ok,ofd) + MSV[d, (op,ok,ofd), (rp,rk,rfd)] FSC(rp,d,rk,rfd) = FSC(rp,d,rk,rfd) - MSV[d, (op,ok,ofd), (rp,rk,rfd)]. ok  SN, Originating Participant Direction = ofd='from'. ok  SN, Receiving Participant Facility = rk  SN. ok  SN, Receiving Participant Direction = rfd='from'. ok  SN, Sign of MSV[d, (op,ok,ofd), (rp,rk,rfd)] = >0. ok  SN, Update to Apply to the FSC and CSC terms = FSC(op,d,ok,ofd) = FSC(op,d,ok,ofd) + MSV[d, (op,ok,ofd), (rp,rk,rfd)]
