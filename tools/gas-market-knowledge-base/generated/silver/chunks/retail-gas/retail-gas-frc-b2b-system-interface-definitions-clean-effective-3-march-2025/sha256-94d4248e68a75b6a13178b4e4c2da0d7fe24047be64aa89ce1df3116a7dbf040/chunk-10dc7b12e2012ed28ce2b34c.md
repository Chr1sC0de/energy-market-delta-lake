---
{
  "chunk_id": "chunk-10dc7b12e2012ed28ce2b34c",
  "chunk_ordinal": 689,
  "chunk_text_sha256": "af0871f9140c24430a227af8ec5be0a7287a834825fb90dc977f6aebdb2c128c",
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
              "b": 95.13931274414062,
              "coord_origin": "BOTTOMLEFT",
              "l": 66.9749526977539,
              "r": 804.7947387695312,
              "t": 502.6727066040039
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 211
          }
        ],
        "self_ref": "#/tables/173"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-10dc7b12e2012ed28ce2b34c.md",
  "heading_path": [
    "CSV Data Elements 2"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-10dc7b12e2012ed28ce2b34c.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

the Network's Tariff (as gazetted by the Regulator). Tariff may be for standing charges, demand, etc. In SA, mostly the same as Distribution_Tariff (aseXML element) - see allowed values. In WA, the 4 digit distribution tariff defined in the RMP with a 6 digit extension making the haulage charges specific for the MIRN. Network_Tariff_Code, Attributes /Format = String. Network_Tariff_Code, Logical Length/ Decimal Length = 10. Network_Tariff_Code, Allowed Values = In SA: 1Demand 2Demand 3Demand 4Demand 5Demand 6Demand 7Demand 8Demand 9Demand 0Demand Commercial Volume Negotiated NegVolume (note this is equivalent to 'NegotiatedVolume' in the Distribution_Tariff aseXML element) In SA, 'Negotiated' is used for both Negotiated Service charges and Term Sheet charges.. New_Fro, Element Name = Party. New_Fro, Description = Contains the initiator of the CATS change request, only when sent to the New User and the Network Operator. New_Fro, Attributes /Format = String. New_Fro,
