---
{
  "chunk_id": "chunk-c7c7660bcba94d53b73a3b4e",
  "chunk_ordinal": 145,
  "chunk_text_sha256": "24d78e75cbf94fae146c197e77889877c5869848b095cdd67c7771ed50f8fccb",
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
              "b": 540.7499829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 529.9299999999997,
              "t": 592.7559829101563
            },
            "charspan": [
              0,
              351
            ],
            "page_no": 16
          }
        ],
        "self_ref": "#/texts/95"
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
              "b": 459.8699829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 529.9539999999997,
              "t": 511.9659829101563
            },
            "charspan": [
              0,
              319
            ],
            "page_no": 16
          }
        ],
        "self_ref": "#/texts/96"
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
              "b": 406.5899829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 529.6519999999994,
              "t": 431.0859829101563
            },
            "charspan": [
              0,
              137
            ],
            "page_no": 16
          }
        ],
        "self_ref": "#/texts/97"
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
              "b": 353.2899829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.78,
              "r": 527.4159999999999,
              "t": 377.7859829101563
            },
            "charspan": [
              0,
              173
            ],
            "page_no": 16
          }
        ],
        "self_ref": "#/texts/98"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-c7c7660bcba94d53b73a3b4e.md",
  "heading_path": [
    "Time Formats"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-c7c7660bcba94d53b73a3b4e.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

All date/time and time elements in the body of aseXML B2B transactions will be expressed with a Time Zone Designator (TZD).  The time zone selected will be at the discretion of the sending party.    The  sending  party  must  therefore  ensure  that  the  combination  of  time  and  time  zone accurately communicates the point in time being defined.
For  example,  if  a  customer  in  South  Australia  requests  an  appointment  at  9:00am  (Central Australia Standard Time), the data element could contain 09:00:00+09:30 or 09:30+10:00.  It is then up to the receiving party to ensure that they have the ability to convert this time to another time zone if required.
In the case of the CSV data element Last_Modified_Date_Time (as above), the time zone selected is at the discretion of the sending party.
In the case of the CSV element 'Planned_Outage_Time', as this is only included in a manually -prepared email, it will always be in local time without a Time Zone Designator.
