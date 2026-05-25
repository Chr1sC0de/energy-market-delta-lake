---
{
  "chunk_id": "chunk-c73920475fabb66edf621f2c",
  "chunk_ordinal": 406,
  "chunk_text_sha256": "a3f8ade964579e2a28ebde4df027483349b9e1cb3eafdd30733b1df90283cf50",
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
              "b": 171.74071484385797,
              "coord_origin": "BOTTOMLEFT",
              "l": 98.064,
              "r": 515.34856,
              "t": 726.9025429101563
            },
            "charspan": [
              0,
              1667
            ],
            "page_no": 118
          }
        ],
        "self_ref": "#/texts/1125"
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
              "b": 171.74071484385797,
              "coord_origin": "BOTTOMLEFT",
              "l": 98.064,
              "r": 515.34856,
              "t": 726.9025429101563
            },
            "charspan": [
              0,
              1667
            ],
            "page_no": 118
          }
        ],
        "self_ref": "#/texts/1125"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md",
    "source_manifest_line_number": 26,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-retail-markets/procedures-policies-and-guides/western-australia",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/retail_markets_and_metering/market-procedures/sa_and_wa/2025/frc-b2b-system-interface-definitions-v53-clean.pdf?rev=c312fd435a0b46d4ac08cc4b56c74493&sc_lang=en"
  },
  "content_sha256": "94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040",
  "corpus": "retail_gas",
  "document_family": "retail-gas__frc-b2b-system-interface-definitions-clean-effective-3-march-2025",
  "document_family_id": "retail-gas__frc-b2b-system-interface-definitions-clean-effective-3-march-2025",
  "document_identity": "retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040",
  "document_title": "##### FRC B2B System Interface Definitions (Clean) Effective 3 March 2025",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-c73920475fabb66edf621f2c.md",
  "heading_path": [
    "Interval Meter Initial Response"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-c73920475fabb66edf621f2c.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

```
<Header> <From description="Network Operator">XXXXXXXXXX</From> <To description="Retailer">XXXXXXXXXX</To> <MessageID>NETO-MSG-4321</MessageID> <MessageDate>2004-08-14T12:00:00+10:00</MessageDate> <TransactionGroup>NMID</TransactionGroup> <Market>SAGAS</Market> </Header> <Transactions> <Transaction transactionID="NETO-TXN-4321" transactionDate="2004-08-14T12:00:00+10:00" initiatingTransactionID="RETO-TXN-1234"> <NMIDiscoveryResponse version="r4"> <NMIStandingData xsi:type="ase:GasStandingData"
