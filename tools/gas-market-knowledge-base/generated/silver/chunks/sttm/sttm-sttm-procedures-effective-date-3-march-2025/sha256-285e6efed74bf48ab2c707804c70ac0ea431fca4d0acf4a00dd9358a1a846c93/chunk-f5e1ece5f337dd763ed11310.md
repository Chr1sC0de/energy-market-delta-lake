---
{
  "chunk_id": "chunk-f5e1ece5f337dd763ed11310",
  "chunk_ordinal": 91,
  "chunk_text_sha256": "805054d8021686735fd5599822e69936a55cde3cf292c96f24f79ed95582c199",
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
              "b": 484.159387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 160.22,
              "r": 529.0184800000001,
              "t": 667.2308629101564
            },
            "charspan": [
              0,
              1021
            ],
            "page_no": 30
          }
        ],
        "self_ref": "#/texts/445"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-3-march-2025/sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93/chunk-f5e1ece5f337dd763ed11310.md",
  "heading_path": [
    "6.5.6. Tie-breaking"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-3-march-2025/sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93/chunk-f5e1ece5f337dd763ed11310.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-3-march-2025/sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93.md"
}
---

Example : Suppose that the last bids and offers scheduled at the hub price must supply demand of 20 TJ at the hub .  Offer 1 on pipeline 1 has offered 20 TJ at a cost of $3/GJ and with low haulage priority. Pipeline 1 has scheduled pipeline flows away from the hub of 10 TJ and Offer 1 on pipeline 1 is the only supply source on pipeline 1 that can supply it. Offer 2 on pipeline 2 has offered 10 TJ at a cost of $3/GJ and with high haulage priority. Offer 3 on pipeline 2 has offered 20 TJ at a cost of $3/GJ and with low haulage priority. The first 10 TJ of Offer 1 is committed to serving gas flowing from the hub , so the tie is between the remaining 10 TJ on pipeline 1 and 30 TJ on pipeline 2.  Of the quantity subject to the tie, Pipeline 1 will get 5 TJ and Pipeline 2 will get 15 TJ. The solution taken is allow 15 TJ of flow from pipeline 1 (offset by 10 TJ of flow away from the hub ) and 15 TJ on pipeline 2, with a net flow into the hub of 20 TJ.
