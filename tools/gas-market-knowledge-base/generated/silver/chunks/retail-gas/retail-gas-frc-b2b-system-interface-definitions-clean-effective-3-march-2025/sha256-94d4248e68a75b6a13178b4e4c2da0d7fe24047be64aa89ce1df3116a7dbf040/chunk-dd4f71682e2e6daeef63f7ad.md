---
{
  "chunk_id": "chunk-dd4f71682e2e6daeef63f7ad",
  "chunk_ordinal": 872,
  "chunk_text_sha256": "e41931acf9de226431a102f84bf790407999a912f15e9abecf332c35f9f5be2f",
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
              "b": 93.91290283203125,
              "coord_origin": "BOTTOMLEFT",
              "l": 92.50537109375,
              "r": 548.021728515625,
              "t": 749.0388717651367
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 259
          }
        ],
        "self_ref": "#/tables/232"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-dd4f71682e2e6daeef63f7ad.md",
  "heading_path": [
    "4. MIRN Standing Data (T1000)"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-dd4f71682e2e6daeef63f7ad.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

Mandatory Optional = O. Supply_Point_Code, Comment = Required if meter is attached. Current_Read_Date, Mandatory Optional = O. Current_Read_Date, Comment = Required if Basic Meter is attached.. Next_Scheduled_Read_Date, Mandatory Optional = O. Next_Scheduled_Read_Date, Comment = Required if Basic Meter is attached.. Meter_Read_Frequency, Mandatory Optional = O. Meter_Read_Frequency, Comment = Required if Basic Meter is attached.. Next_Scheduled_Special_Read_Date, Mandatory Optional = O. Next_Scheduled_Special_Read_Date, Comment = Optional if Basic Meter is attached. Populated if there is a Special Read appointment booked against this MIRN.. Communication_Equipment_Present, Mandatory Optional = O. Communication_Equipment_Present, Comment = Required if Interval Meter is attached.. Excluded_Services_Charges_Charge_Item_C ategory, Mandatory Optional = O. Excluded_Services_Charges_Charge_Item_C ategory, Comment = Only used for Interval meters. This information may be provided in a subsequent NMIDiscoveryResponse message if the AdditionalDataToFollow element is set to 'true'..
