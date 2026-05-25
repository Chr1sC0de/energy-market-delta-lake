---
{
  "chunk_id": "chunk-162b8fb2c7c7eeccdc9e934b",
  "chunk_ordinal": 179,
  "chunk_text_sha256": "2a0b97618268eb6cf9ba5596342104b3a30ba178b2ad274f1d458e5381fe535d",
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
              "b": 78.79901095552054,
              "coord_origin": "BOTTOMLEFT",
              "l": 92.304,
              "r": 527.6223199999997,
              "t": 133.69709802734383
            },
            "charspan": [
              0,
              350
            ],
            "page_no": 61
          },
          {
            "bbox": {
              "b": 701.5550109555205,
              "coord_origin": "BOTTOMLEFT",
              "l": 92.304,
              "r": 527.68624,
              "t": 741.4570980273437
            },
            "charspan": [
              351,
              570
            ],
            "page_no": 62
          }
        ],
        "self_ref": "#/texts/712"
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
              "b": 617.5550109555205,
              "coord_origin": "BOTTOMLEFT",
              "l": 92.304,
              "r": 527.5842399999998,
              "t": 687.4570980273437
            },
            "charspan": [
              0,
              389
            ],
            "page_no": 62
          }
        ],
        "self_ref": "#/texts/716"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md",
    "source_manifest_line_number": 31,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-retail-markets/procedures-policies-and-guides/victoria",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/retail_markets_and_metering/market-procedures/vic/2024/participant-build-pack-2--system-interface-definitions-v-36-clean.pdf?rev=0420b92c0a5e4d879175ec3003826d7d&sc_lang=en"
  },
  "content_sha256": "b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232",
  "corpus": "retail_gas",
  "document_family": "retail-gas__participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024",
  "document_family_id": "retail-gas__participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024",
  "document_identity": "retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232",
  "document_title": "##### Participant Build Pack 2 - System Interface Definitions (Clean) Effective 1 May 2024",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-162b8fb2c7c7eeccdc9e934b.md",
  "heading_path": [
    "4.1.11 Delivering Problem Notice"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-162b8fb2c7c7eeccdc9e934b.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

Only NAK's that contains Event Codes that are listed in appendix C in the CATS category range or Event Codes, 3200, 3202, 202 or -1 will result in the generation of a Problem Notice. The reason AEMO issues a Problem Notice on receipt of a NAK generated against a CATSNotification is it is the only mechanism available to a Current FRO and Distributor such that it can provide feedback about a problem to the New FRO without knowing the identity of the New FRO.  Confidentiality rules that apply in the market prevent AEMO from identifying the New FRO to the Current FRO.
It  should also be noted that the existence of a Problem Notice does not impact, in any way, the CATS processing Procedures associated with a transfer.  It is up to the New FRO to  evaluate  the  impact  of  the  information  provided  in  the  Problem  Notice  and  takes whatever steps are appropriate.  These steps can range from withdrawing the transfer to ignoring the Problem Notice.
