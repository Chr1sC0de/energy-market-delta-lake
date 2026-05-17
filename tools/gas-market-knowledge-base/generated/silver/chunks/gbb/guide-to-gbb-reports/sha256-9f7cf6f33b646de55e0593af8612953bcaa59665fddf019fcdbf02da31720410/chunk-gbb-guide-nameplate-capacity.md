---
{
  "chunk_id": "chunk-gbb-guide-nameplate-capacity",
  "chunk_ordinal": 6,
  "chunk_text_sha256": "a9f7d2aeb231f23e45fcbf276372bed54180899b543ab8cda0cb5e4a25ec3bc9",
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
        "source_text_line_end": 890,
        "source_text_line_start": 836
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/gbb/guide-to-gbb-reports/sha256-9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410.md",
    "source_manifest_line_number": 4,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-bulletin-board-gbb/procedures-policies-and-guides/procedures-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/amendments-to-gbb-procedures-for-renewable-gas/decision/guide-to-gas-bulletin-board-reports-v23.pdf?rev=583464be2e9642a0aed11973b1e09a80&sc_lang=en"
  },
  "content_sha256": "9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410",
  "corpus": "gbb",
  "document_family": "gbb__guide-to-gas-bulletin-board-reports",
  "document_family_id": "gbb__guide-to-gas-bulletin-board-reports",
  "document_identity": "gbb/guide-to-gbb-reports/sha256-9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410",
  "document_title": "Guide to Gas Bulletin Board Reports",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/gbb/guide-to-gbb-reports/sha256-9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410/chunk-gbb-guide-nameplate-capacity.md",
  "heading_path": [
    "Guide to Gas Bulletin Board Reports",
    "Nameplate capacity report"
  ],
  "path": "generated/silver/chunks/gbb/guide-to-gbb-reports/sha256-9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410/chunk-gbb-guide-nameplate-capacity.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/guide-to-gbb-reports/sha256-9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410.md"
}
---

• From Gas Date

           • To Gas Date

           • Capacity Type

4.5.4. Example report
           Vist the AEMO developer portal for example for HTTPS GET request examples.

4.6. Nameplate Rating
4.6.1. Description
 Transaction report GASBB_NAMEPLATE_RATING_FULL_LIST / GASBB_NAMEPLATE_RATING_CURRENT
 name
 Purpose                This report displays the standing nameplate capacity of all BB facilities and BB compression facility.
                        Nameplate rating relates to maximum daily quantities in TJ under normal operating conditions.
 Production GASBB_NAMEPLATE_RATING_FULL_LIST is updated annually /
 frequency GASBB_NAMEPLATE_RATING_CURRENT is updated within 30 minutes of receiving new data.
 Report period GASBB_NAMEPLATE_RATING_FULL_LIST contains historical records /
                        GASBB_NAMEPLATE_RATING_CURRENT contains the current nameplate.

4.6.2. Data report format

           The following fields are provided in the report.

 Data element Description Data type Example / Allowed
                                                                                                        values
 FacilityName Facility name associated with the Facility Id. varchar(100) APLNG Pipeline

AEMO | 3 March 2025                                                                                                  Page 16 of 45

Guide to Gas Bulletin Board Reports

 Data element Description Data type Example / Allowed
                                                                                                    values
 FacilityId A unique AEMO defined Facility identifier. Int 520345
 FacilityType Facility type associated with the Facility Id. varchar(40) PIPE; PROD; STOR
 CapacityType Capacity type can be either:                                varchar(20) STORAGE; MDQ
                        • Storage: Holding capacity in storage, or
                        • MDQ: Daily maximum firm capacity (name plate)
                          under the expected operating conditions adjusted
                          for any facility that is ‘mothballed’,
                          decommissioned or down-rated and / or cannot
                          be recalled within 1 week, planned maintenance
                          excepted. Reflects any long terms changes
                          (greater than 12 months).
 CapacityQuantity Standing capacity quantity in TJ to three decimal number(18,3)    32.232
                        places. Three decimal places is not required if the 25.5 (if the value is
