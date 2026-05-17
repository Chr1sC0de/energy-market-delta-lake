---
{
  "chunk_id": "chunk-sttm-procedures-settlement-amounts",
  "chunk_ordinal": 8,
  "chunk_text_sha256": "2b7152366461c0408d200d03d627753338cff9515a1b6d27fb1b472e287af6d8",
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
        "extraction": "pdftotext-layout-seed",
        "label": "text",
        "source_text_line_end": 4339,
        "source_text_line_start": 4318
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/sttm/sttm-procedures-2025/sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93.md",
    "source_manifest_line_number": 5,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/short-term-trading-market-sttm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/amendments-to-sttm-and-retail-market-procedures/decision/sttm-procedures-v150.pdf?rev=7f91b14f6cca4ca7bf1e7705ef8362c2&sc_lang=en"
  },
  "content_sha256": "285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93",
  "corpus": "sttm",
  "document_family": "sttm__sttm-procedures-effective-date-3-march-2025",
  "document_family_id": "sttm__sttm-procedures-effective-date-3-march-2025",
  "document_identity": "sttm/sttm-procedures-2025/sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93",
  "document_title": "STTM Procedures Effective 3 March 2025",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/sttm/sttm-procedures-2025/sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93/chunk-sttm-procedures-settlement-amounts.md",
  "heading_path": [
    "STTM Procedures Effective 3 March 2025",
    "Settlement amounts for gas days"
  ],
  "path": "generated/silver/chunks/sttm/sttm-procedures-2025/sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93/chunk-sttm-procedures-settlement-amounts.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-procedures-2025/sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93.md"
}
---

for withdrawals from the hub on market facility k. This value is determined in clause
                      10.8.5(b).
 PDevNT(p,d,k)        The deviation price for a short deviation quantity for Trading Participant p on gas day d
                      for supply to the hub on market facility k. This value is determined in clause 10.8.5(d).
 PDevPF(p,d,k)        The deviation price for a long deviation quantity for Trading Participant p on gas day d
                      for withdrawals from the hub on market facility k. This value is determined in clause
                      10.8.5(a).
 PDevPT(p,d,k)        The deviation price for a long deviation quantity for Trading Participant p on gas day d
                      for supply to the hub on market facility k. This value is determined in clause 10.8.5(c).
 PVarC(p,d) The variation charge for Trading Participant p for gas day d for a hub, determined using
                      the percentage method. This term is greater than or equal to zero. This value is
                      determined in clause 10.5.3(b).
 PVarF(f) The factor for step f of the percentage method variation settlement function. These
                      factors increase with increasing variation quantity and are the factors for the variation
                      percentage range in rule 463 corresponding to step f.
 PVarR(f) The percentage boundary between step f and step f+1 for the percentage method
                      variation settlement function. These are positive values and correspond to the most
                      positive values specified in the variation percentage range in rule 463 corresponding to
                      step f. This term is neither defined nor used for f=Maxf.
 PVarU(p,d,f) The variation quantity of step f for Trading Participant p percentage method variations
                      on gas day d for a hub. This term is greater than or equal to zero. This value is
                      determined in clause 10.5.3(a).
