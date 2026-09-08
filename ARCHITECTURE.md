# AI Tender Assistant - System Architecture

## 1. System Topology Overview
The system follows a modular, layer-separated architecture with decoupling between document extraction, rules execution, vector search, and presentation.

```
+-----------------------------------------------------------------------+
|                             FRONTEND                                  |
|  Next.js 14+ (App Router), React, TypeScript, Tailwind CSS, Recharts  |
+------------------------------------+----------------------------------+
                                     | REST API / JSON (JWT Auth)
                                     v
+-----------------------------------------------------------------------+
|                             BACKEND                                   |
|             FastAPI, Pydantic v2, SQLAlchemy 2.0 Async                |
|                                                                       |
|  +-------------------+  +-------------------+  +-------------------+  |
|  | Document Service  |  | Eligibility Engine|  | Scoring Engine    |  |
|  +---------+---------+  +---------+---------+  +---------+---------+  |
|            |                      |                      |            |
|  +---------v---------+  +---------v---------+  +---------v---------+  |
|  | Sarvam Vision API |  | Deterministic     |  | Weighted Formula  |  |
|  | Integration       |  | Rule Validators   |  | Hard Fail Override|  |
|  +-------------------+  +-------------------+  +-------------------+  |
|                                                                       |
|  +-------------------+  +-------------------+  +-------------------+  |
|  | LLM Intelligence  |  | Vector Embeddings |  | Application Asst  |  |
|  | Extraction & Prompts| | Cosine Similarity |  | Cover Letter/Decl |  |
|  +-------------------+  +-------------------+  +-------------------+  |
+------------------------------------+----------------------------------+
                                     | SQL / Vector Queries
                                     v
+-----------------------------------------------------------------------+
|                            DATABASE                                   |
|                PostgreSQL + pgvector / SQLAlchemy Async               |
+-----------------------------------------------------------------------+
```

## 2. Component Breakdown

### A. Document Intelligence Layer (`backend/services/sarvam_service.py` & `document_processor.py`)
- **Document Hash & Cache**: File MD5/SHA256 hashed before upload. If hash matches existing processed tender, reuses extracted schema.
- **Chunking Strategy**: For tenders exceeding page limits (e.g. Sarvam Vision 10-page limitation), documents are split into logical chunks, processed in parallel, and stitched back with page & section index metadata.
- **Provider Abstraction**: Implements `DocumentProvider` abstract base class to support `SarvamVisionProvider` and fallback OCR engines seamlessly.

### B. Structured Tender Extraction (`backend/services/tender_extractor.py`)
- **Prompt Injection Defense**: Untrusted PDF raw text is injected into strict context blocks (`<document_text>`). LLM system prompts strictly forbid instruction execution inside PDF text.
- **Schema Validation**: Outputs validated against Pydantic model `StructuredTenderData`. Unparseable or missing fields default safely to `UNKNOWN` or `NOT_SPECIFIED`.

### C. Deterministic Eligibility Engine (`backend/services/eligibility_engine.py`)
- Python-only deterministic evaluation without LLM ambiguity.
- Rules:
  - Turnover rule: `business.turnover >= tender.min_turnover` -> `PASS`, else `FAIL`.
  - MSME requirement: If required and `business.is_msme == False` -> `FAIL`.
  - GST requirement: If required and `business.has_gst == False` -> `FAIL`.
  - Location rule: State matching & operating region validation.
  - Experience rule: Minimum required years & proof document availability.
- Output: Status (`PASS`, `FAIL`, `UNKNOWN`) and human-readable reason list.

### D. Semantic Product Matching (`backend/services/matching_engine.py`)
- Products & services vectorized using `EmbeddingProvider`.
- Business product vectors matched against tender required product vectors using Cosine Similarity.
- Produces `product_match_score` (0–100%) and itemized match breakdown.

### E. Weighted Match & Scoring Engine
- Strictly enforces weights:
  - Product Match = 30%
  - Eligibility = 30%
  - Location = 10%
  - Turnover = 15%
  - Experience = 15%
- `final_score = product_score * 0.30 + eligibility_score * 0.30 + location_score * 0.10 + turnover_score * 0.15 + experience_score * 0.15`
- **Hard Eligibility Rule**: If Eligibility status is `FAIL`, `overall_eligibility` MUST BE `NOT ELIGIBLE`, regardless of product match score.

### F. Requirement Gap & Risk Engine (`backend/services/gap_engine.py`)
- Cross-references required documents against uploaded business documents in the Document Locker.
- Computes Application Readiness Score: `Available Required Docs / Total Required Docs`.
- Computes Risk Level (`LOW`, `MEDIUM`, `HIGH`) based on missing mandatory documents, tight deadline (< 3 days), and turnover/experience gaps.

### G. Application Assistant (`backend/services/application_service.py`)
- Generates editable Cover Letter, Tender Declaration, Technical Compliance Matrix, and Document Submission Checklist.
- Enforces Zero Hallucination rule: Only uses verified business data or inserts `[REQUIRED INFORMATION]` placeholders.
