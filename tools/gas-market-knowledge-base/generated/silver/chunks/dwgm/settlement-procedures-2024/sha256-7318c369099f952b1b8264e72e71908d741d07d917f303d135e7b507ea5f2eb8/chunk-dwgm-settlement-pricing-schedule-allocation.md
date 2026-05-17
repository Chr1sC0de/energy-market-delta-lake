---
{
  "chunk_id": "chunk-dwgm-settlement-pricing-schedule-allocation",
  "chunk_ordinal": 1,
  "chunk_text_sha256": "501b4dc71b9f1dc6ced259ffa388354ebd537a1c29c3e02e490083657b39b198",
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
        "source_text_line_end": 678,
        "source_text_line_start": 597
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/dwgm/settlement-procedures-2024/sha256-7318c369099f952b1b8264e72e71908d741d07d917f303d135e7b507ea5f2eb8.md",
    "source_manifest_line_number": 2,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/declared-wholesale-gas-market-dwgm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/amendments-to-the-gas-compensation-regime-for-the-dwgm-ecgs-and-sttm/decision-documents/wholesale-market-settlement-procedures-v20.pdf?rev=0c93eb164fe14cb1aa88b1b2166b6cb3&sc_lang=en"
  },
  "content_sha256": "7318c369099f952b1b8264e72e71908d741d07d917f303d135e7b507ea5f2eb8",
  "corpus": "dwgm",
  "document_family": "dwgm__wholesale-market-settlement-procedures-victoria-this-document-contains-the-ancillary-payment-procedures-uplift-payment-procedures-compensation-procedures-and-distribution-uafg-procedures-this-procedure-is-effective-from-31-july-2024",
  "document_family_id": "dwgm__wholesale-market-settlement-procedures-victoria-this-document-contains-the-ancillary-payment-procedures-uplift-payment-procedures-compensation-procedures-and-distribution-uafg-procedures-this-procedure-is-effective-from-31-july-2024",
  "document_identity": "dwgm/settlement-procedures-2024/sha256-7318c369099f952b1b8264e72e71908d741d07d917f303d135e7b507ea5f2eb8",
  "document_title": "Wholesale Market Settlement Procedures (Victoria) Effective 31 July 2024",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/dwgm/settlement-procedures-2024/sha256-7318c369099f952b1b8264e72e71908d741d07d917f303d135e7b507ea5f2eb8/chunk-dwgm-settlement-pricing-schedule-allocation.md",
  "heading_path": [
    "Wholesale Market Settlement Procedures (Victoria) Effective 31 July 2024",
    "Pricing and operating schedule allocation"
  ],
  "path": "generated/silver/chunks/dwgm/settlement-procedures-2024/sha256-7318c369099f952b1b8264e72e71908d741d07d917f303d135e7b507ea5f2eb8/chunk-dwgm-settlement-pricing-schedule-allocation.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/settlement-procedures-2024/sha256-7318c369099f952b1b8264e72e71908d741d07d917f303d135e7b507ea5f2eb8.md"
}
---

For adjusted bid steps where the cumulative bid quantity for a pricing schedule and operating
         schedule exceeds the maximum bid quantity for that schedule the bid price is set equal to the
         bid price of the maximum bid step for that schedule.

         If AEMO has limited the market price to the administered price cap for a schedule in
         accordance with Rule 239(5) then the bid prices associated with the adjusted bid steps for that
         schedule are capped at the administered price cap.

2.5.        Determination and allocation of quantities to adjusted bid
            steps
2.5.1. Pricing schedule – determination of effective pricing schedule quantities for
            ancillary payments

         For each Market Participant, the effective pricing schedule quantity used by AEMO in
         calculating ancillary payments for that Market Participant’s pricing schedule controllable
         quantity at each system injection and withdrawal point is:

AEMO | 31 July 2024                                                                                          Page 10 of 59

Wholesale Market Settlement Procedures (Victoria)

         (a)    for the initial pricing schedule of the gas day, equal to the pricing schedule quantity
                produced at the start of the gas day; and

         (b)    for each subsequent updated pricing schedule of the gas day, equal to:

                (i)    the pricing schedule quantity for the scheduling horizon of that subsequent
                       updated pricing schedule

                plus

                (ii)   the sum of each pricing schedule quantity for each relevant scheduling interval for
                       each of the previous pricing schedules.

2.5.2.    Pricing schedule – allocation of effective pricing schedule quantities to
          adjusted bid steps

         The pricing schedule controllable quantities determined under clause 2.5.1 for a Market
         Participant for each pricing schedule are allocated to the adjusted bid steps of the bid that
         applied for that pricing schedule in order of increasing price for injections and decreasing price
         for withdrawals.

         Effective pricing schedule quantities should be allocated to each adjusted bid step including
         adjusted bid steps where the cumulative quantity for that adjusted bid step exceeds the
         maximum bid quantity.

2.5.3.    Operating schedule – determination of operating schedule quantities for
          ancillary payments

         For each Market Participant, the operating schedule quantity used by AEMO in calculating
         ancillary payments for that Market Participant’s operating schedule controllable injection or
         operating schedule controllable withdrawal is:

         (a)    for the initial operating schedule of the gas day, equal to the operating schedule quantity
                produced at the start of the gas day; and

         (b)    for each subsequent operating schedule of the gas day, equal to:

                (i)    the operating schedule quantity of that subsequent operating schedule for the
                       scheduling horizon

                plus

                (ii)   the sum of each operating schedule quantity for each scheduling interval related to
                       each of the previous operating schedules.

         If an ad hoc operating schedule is produced to replace an already approved operating
         schedule, then the schedule quantity for the scheduling interval in that ad hoc operating
         schedule will be used to calculate the operating schedule quantities.

2.5.4.    Operating schedule – allocation of operating schedule quantities to adjusted
          bids steps

         The operating schedule controllable quantities determined under clause 2.5.3 for a Market
         Participant for each operating schedule are allocated to the adjusted bid steps of the bid that
