---
{
  "chunk_id": "chunk-1ae1c14170ef6cf614dd5f90",
  "chunk_ordinal": 471,
  "chunk_text_sha256": "7e6f5eb0ddc4ec3a42064c443632bb77e4c4c0b7bfb457ea8351f35b2efc0528",
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
              "b": 226.68998291015623,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.66,
              "r": 529.9779999999996,
              "t": 306.26598291015625
            },
            "charspan": [
              0,
              533
            ],
            "page_no": 140
          }
        ],
        "self_ref": "#/texts/1447"
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
              "b": 179.3799829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.66,
              "r": 529.5799999999995,
              "t": 217.55598291015622
            },
            "charspan": [
              0,
              257
            ],
            "page_no": 140
          }
        ],
        "self_ref": "#/texts/1448"
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
              "b": 145.77998291015626,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.66,
              "r": 529.5559999999996,
              "t": 170.27598291015624
            },
            "charspan": [
              0,
              135
            ],
            "page_no": 140
          }
        ],
        "self_ref": "#/texts/1449"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-1ae1c14170ef6cf614dd5f90.md",
  "heading_path": [
    "Process Sequence"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-1ae1c14170ef6cf614dd5f90.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

Depending on the way the dispute has been resolved, cancel and re-bill may follow or no changes to billing details will apply. If a dispute is resolved in the User's favour, a full cancellation of the original  line  item  and  re-bill  (if  applicable)  must  be  sent  to  the  User  in  a  subsequent NetworkDUoSBillingNotification transaction.  Upon the dispute resolution, if additional payment is required, the User will issue a Payment Advice via NetworkDUoSBillingNotification transaction with details attached in CSV format.
A key principle for this process is disputes on individual charge(s), do not cause a NACK of the entire NetworkDUoSBillingNotification transaction, and also do not mean the User can withhold payment of the undisputed charges until the disputes are resolved.
Forward estimates are provided in SA via a 'notice' (not aseXML).  Forward estimates can be disputed but not via an aseXML transaction.
