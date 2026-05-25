---
{
  "chunk_id": "chunk-1ad735fabdb5a7d8130e1215",
  "chunk_ordinal": 288,
  "chunk_text_sha256": "904c008a189d6b54c256dcf60a0dda901bd9cb0665cf70e5d2dcadb7e11a7ebd",
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
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/160"
        },
        "prov": [
          {
            "bbox": {
              "b": 357.299387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 527.4376,
              "t": 395.0408629101563
            },
            "charspan": [
              0,
              223
            ],
            "page_no": 76
          }
        ],
        "self_ref": "#/texts/1296"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/160"
        },
        "prov": [
          {
            "bbox": {
              "b": 293.2193873908079,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 512.93548,
              "t": 345.58086291015627
            },
            "charspan": [
              0,
              288
            ],
            "page_no": 76
          }
        ],
        "self_ref": "#/texts/1297"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/160"
        },
        "prov": [
          {
            "bbox": {
              "b": 258.17938739080796,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 528.68848,
              "t": 281.50086291015623
            },
            "charspan": [
              0,
              110
            ],
            "page_no": 76
          }
        ],
        "self_ref": "#/texts/1298"
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
              "b": 225.05938739080807,
              "coord_origin": "BOTTOMLEFT",
              "l": 178.58,
              "r": 482.4721599999999,
              "t": 246.22086291015626
            },
            "charspan": [
              0,
              119
            ],
            "page_no": 76
          }
        ],
        "self_ref": "#/texts/1299"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c.md",
    "source_manifest_line_number": 44,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/short-term-trading-market-sttm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/sttm-procedures/sttm-procedures-v135.pdf?rev=93f1f406f57a41dab9175821eea6c334&sc_lang=en"
  },
  "content_sha256": "8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c",
  "corpus": "sttm",
  "document_family": "sttm__sttm-procedures-effective-date-22-april-2024",
  "document_family_id": "sttm__sttm-procedures-effective-date-22-april-2024",
  "document_identity": "sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c",
  "document_title": "##### STTM Procedures Effective date 22 April 2024",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c/chunk-1ad735fabdb5a7d8130e1215.md",
  "heading_path": [
    "10.6B Ad hoc payments for contingency gas resettlement"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c/chunk-1ad735fabdb5a7d8130e1215.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c.md"
}
---

- (a) If an ad hoc charge is payable by a Trading Participant under clause 10.6A, an equivalent amount is to be distributed to Trading Participants at the relevant hub by way of ad hoc payments determined under paragraph (b).
- (b) The ad hoc payment for Trading Participant p on gas day d depends on the Trading Participan t's deviation quantity (whether short or long) and the nature of the relevant contingency gas requirement (whether for increased or decreased supply to the hub ), and is determined as follows:
- (i) Calculate the Trading Participant's short deviation quantity fo r the relevant hub and gas day (SDQ(p,d)):
SDQ(p,d) =  k  SP [MAX(0, -1 × DQT(p,d,k))] +  k  SP [MAX(0, -1 × DQF(p,d,k))] +  k  SN [MAX(0, -1 × DQF(p,d,k))]
