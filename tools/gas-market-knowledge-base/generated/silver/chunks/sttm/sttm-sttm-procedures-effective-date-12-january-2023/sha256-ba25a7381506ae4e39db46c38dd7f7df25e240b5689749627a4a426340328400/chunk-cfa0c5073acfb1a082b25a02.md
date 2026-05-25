---
{
  "chunk_id": "chunk-cfa0c5073acfb1a082b25a02",
  "chunk_ordinal": 289,
  "chunk_text_sha256": "7b6012e695163a8687cf130eb403de4a97b89aaefba67c53a19098bd1d1f57b6",
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
          "$ref": "#/groups/128"
        },
        "prov": [
          {
            "bbox": {
              "b": 643.6574582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 522.6737200000001,
              "t": 680.1908629101564
            },
            "charspan": [
              0,
              223
            ],
            "page_no": 74
          }
        ],
        "self_ref": "#/texts/1094"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/128"
        },
        "prov": [
          {
            "bbox": {
              "b": 582.4574582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 511.66432000000003,
              "t": 632.7908629101563
            },
            "charspan": [
              0,
              287
            ],
            "page_no": 74
          }
        ],
        "self_ref": "#/texts/1095"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/128"
        },
        "prov": [
          {
            "bbox": {
              "b": 548.8274582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 529.31836,
              "t": 571.5908629101564
            },
            "charspan": [
              0,
              109
            ],
            "page_no": 74
          }
        ],
        "self_ref": "#/texts/1096"
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
              "b": 516.0674582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 178.58,
              "r": 485.86204000000004,
              "t": 537.2408629101564
            },
            "charspan": [
              0,
              119
            ],
            "page_no": 74
          }
        ],
        "self_ref": "#/texts/1097"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400.md",
    "source_manifest_line_number": 43,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/short-term-trading-market-sttm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/sttm/policies/sttm-procedures-v134.pdf?rev=f9d5cb1606a240bbb8a3701d76eb7a2f&sc_lang=en"
  },
  "content_sha256": "ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400",
  "corpus": "sttm",
  "document_family": "sttm__sttm-procedures-effective-date-12-january-2023",
  "document_family_id": "sttm__sttm-procedures-effective-date-12-january-2023",
  "document_identity": "sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400",
  "document_title": "##### STTM Procedures Effective date 12 January 2023",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-cfa0c5073acfb1a082b25a02.md",
  "heading_path": [
    "10.6B Ad hoc payments for contingency gas resettlement"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-cfa0c5073acfb1a082b25a02.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400.md"
}
---

- (a) If an ad hoc charge is payable by a Trading Participant under clause 10.6A, an equivalent amount is to be distributed to Trading Participants at the relevant hub by way of ad hoc payments determined under paragraph (b).
- (b) The ad hoc payment for Trading Participant p on gas day d depends on the Trading Participant's deviation quantity (whether short or long) and the nature of the relevant contingency gas requirement (whether for increased or decreased supply to the hub ), and is determined as follows:
- (i) Calculate the Trading Participant's short deviation quantity for the relevant hub and gas day (SDQ(p,d)):
SDQ(p,d) =  k  SP [MAX(0, -1 × DQT(p,d,k))] +  k  SP [MAX(0, -1 × DQF(p,d,k))] +  k  SN [MAX(0, -1 × DQF(p,d,k))]
