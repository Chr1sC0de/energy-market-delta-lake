---
{
  "chunk_id": "chunk-654ac0af9ebfa20761cb29f9",
  "chunk_ordinal": 260,
  "chunk_text_sha256": "fd0f0a867debae126e4df764cab393dfe5c2267f7bab3ccc9c80fc7ad090731d",
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
              "b": 707.5550109555205,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 396.25912,
              "t": 717.4570980273437
            },
            "charspan": [
              0,
              66
            ],
            "page_no": 104
          }
        ],
        "self_ref": "#/texts/1242"
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
              "b": 528.6707099610454,
              "coord_origin": "BOTTOMLEFT",
              "l": 146.06,
              "r": 529.38856,
              "t": 696.4225380273438
            },
            "charspan": [
              0,
              512
            ],
            "page_no": 104
          }
        ],
        "self_ref": "#/texts/1243"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-654ac0af9ebfa20761cb29f9.md",
  "heading_path": [
    "5.2.4 XML Example Message 4:  TransactionAcknowledgement"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-654ac0af9ebfa20761cb29f9.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

The current retailer acknowledges receipt of the CATSNotification.
```
<Header> <From description="Pulse Energy">PULSE</From> <To description="Victorian Energy Networks Corporation">VENCORP</To> <MessageID>PULSE-MSG-4</MessageID> <MessageDate>2001-09-24T15:00:16.000+10:00</MessageDate> <TransactionGroup>CATS</TransactionGroup> <Priority>Medium</Priority> <Market>VICGAS</Market> </Header> <Acknowledgements> <TransactionAcknowledgement initiatingTransactionID="VENCORP-TXN-4" receiptID="PULSE-ACK-2" receiptDate="2001-09-24T15:00:15.000+10:00" status="Accept"/> </Acknowledgements>
```
