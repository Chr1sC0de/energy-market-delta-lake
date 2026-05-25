---
{
  "chunk_id": "chunk-ed4b98a0bbdc7be838d5aab1",
  "chunk_ordinal": 715,
  "chunk_text_sha256": "43a5fdd9a3f63eb0b063db78a59a1b96a6fd4cd22b7631c9fc9a3db984326488",
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
              "b": 99.7115478515625,
              "coord_origin": "BOTTOMLEFT",
              "l": 122.04134368896484,
              "r": 527.7903442382812,
              "t": 517.9484252929688
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 218
          }
        ],
        "self_ref": "#/tables/180"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-ed4b98a0bbdc7be838d5aab1.md",
  "heading_path": [
    "Appendix B. aseXML Standard Event Codes"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-ed4b98a0bbdc7be838d5aab1.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

, Code = 0. , Description = Success, OK, Accepted, etc.. , Notes = Any class. Message (1-99), Code = 1. Message (1-99), Description = Not well formed. Message (1-99), Notes = . , Code = 2. , Description = Schema validation failure. , Notes = . , Code = 3. , Description = Transaction not supported within Transaction Group. , Notes = The transaction is not supported by the receiving system in the context of the provided transaction group. , Code = 4. , Description = Transaction version not supported. , Notes = . , Code = 5. , Description = Uncompression failure. , Notes = This covers both errors in the uncompress ion process and the absence of the appropriate file within the compressed format container. , Code = 6. , Description = Message too big. , Notes = . , Code = 7. , Description = Header mismatch. , Notes = Information provided by transport layer is inconsistent with the message header. , Code = 8. , Description = Incorrect market. , Notes = The system to which the message is addressed does not handle the market indicated in the header. , Code = 9. , Description = Unknown Transaction Group.
