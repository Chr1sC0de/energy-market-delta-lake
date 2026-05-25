---
{
  "chunk_id": "chunk-b17e8ff0b34b6eff127ff9fd",
  "chunk_ordinal": 668,
  "chunk_text_sha256": "be47ab7e5dfa3bef7eccfb82271d149936c90b02e874a8cba42991a95f81dff0",
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
              "b": 97.0423583984375,
              "coord_origin": "BOTTOMLEFT",
              "l": 66.97798919677734,
              "r": 804.5712280273438,
              "t": 502.9158020019531
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 206
          }
        ],
        "self_ref": "#/tables/168"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-b17e8ff0b34b6eff127ff9fd.md",
  "heading_path": [
    "CSV Data Elements 2"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-b17e8ff0b34b6eff127ff9fd.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

Estimation_Substitution_Type, Element Name = Estimation/Substitution Type. Estimation_Substitution_Type, Description = Indicator identifying the type of estimation/substitution applied.. Estimation_Substitution_Type, Attributes /Format = String. Estimation_Substitution_Type, Logical Length/ Decimal Length = 2. Estimation_Substitution_Type, Allowed Values = 'E1' = Estimation method 1 'E2' = Estimation method 2 'E3' = RB/DB agreed value 'S1' = Substitution method 1 'S2' = Substitution method 2 'S3' = RB/DB agreed substituted value In SA: - "E1/S1" = Type 1 estimation/substitution method in the ESCOSA Metering Code (a calculation based on Same Time Last Year) - "E2/S2" value for Estimation_Substitution_Type means Type 3 estimation/substitution method in the ESCOSA Metering Code (a calculation based on customer class) - "E3/S3" value for Estimation_Substitution_Type means Type 4 estimation/substitution method in the ESCOSA Metering Code (a substitution method only and is a value agreed by RB and DB).. Expected_MHQ, Element Name = Expected MHQ.
