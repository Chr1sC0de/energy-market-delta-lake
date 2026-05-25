---
{
  "chunk_id": "chunk-e74b6eef19920f979d1e35ab",
  "chunk_ordinal": 267,
  "chunk_text_sha256": "23d602b1f13d521c8e0cb33c57a749dd30ee7f8070be3b8efd9c06be99142d35",
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
              "b": 581.3150109555205,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 383.53912,
              "t": 591.2170980273437
            },
            "charspan": [
              0,
              60
            ],
            "page_no": 106
          }
        ],
        "self_ref": "#/texts/1262"
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
              "b": 402.43070996104547,
              "coord_origin": "BOTTOMLEFT",
              "l": 146.06,
              "r": 529.38856,
              "t": 570.1525380273438
            },
            "charspan": [
              0,
              488
            ],
            "page_no": 106
          }
        ],
        "self_ref": "#/texts/1263"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-e74b6eef19920f979d1e35ab.md",
  "heading_path": [
    "5.2.8 XML Example Message 8: TransactionAcknowledgement"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-e74b6eef19920f979d1e35ab.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

The distributor acknowledges receipt of the CATSDataRequest.
```
<Header> <From>TXUNET</From> <To description="Victorian Energy Networks Corporation">VENCORP</To> <MessageID>TXUNET-MSG-4</MessageID> <MessageDate>2001-09-24T15:00:24.000+10:00</MessageDate> <TransactionGroup>CATS</TransactionGroup> <Priority>Medium</Priority> <Market>VICGAS</Market> </Header> <Acknowledgements> <TransactionAcknowledgement initiatingTransactionID="VENCORP-TXN-5" receiptID="TXUNET-ACK-2" receiptDate="2001-09-24T15:00:23.000+10:00" status="Accept"/> </Acknowledgements>
```
