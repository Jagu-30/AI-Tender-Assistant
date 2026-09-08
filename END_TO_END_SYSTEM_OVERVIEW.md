# AI Tender Assistant - End-to-End Technical & Architecture Overview

> Enterprise AI solution for Micro, Small, and Medium Enterprises (MSMEs) in India to discover, evaluate, qualify for, and prepare applications for government tenders.

---

## 1. Technology Stack

### **Frontend**
- **Framework**: Next.js 14+ (App Router), React 18, TypeScript.
- **Styling**: Tailwind CSS & Vanilla CSS (supporting dynamic glassmorphism, responsive dashboards, modern typography).
- **UI Components & Icons**: Lucide React icons, `clsx`, `tailwind-merge`.
- **Data Visualization**: Recharts (radar charts for eligibility parameters, score breakdown, readiness indexes).

### **Backend**
- **Framework**: Python 3.11+, FastAPI (Async RESTful API architecture).
- **Data Validation & Schemas**: Pydantic V2 (strict typing, schema enforcement, JSON validation).
- **ORM & Database Drivers**: SQLAlchemy 2.0 Async with `asyncpg` (PostgreSQL) and `aiosqlite` (SQLite fallback).
- **Authentication**: JSON Web Tokens (JWT) using `python-jose` and `passlib` with `bcrypt`.
- **HTTP Client**: `httpx` for asynchronous requests to external AI APIs.

### **Database & Storage**
- **Database**: PostgreSQL with `pgvector` extension for vector similarity search (or SQLite fallback for dev/demo mode).
- **File Storage**: Hash-deduplicated file storage service (`storage_service.py`) for PDF tenders and MSME uploaded certificates.

### **DevOps & Containerization**
- **Docker & Docker Compose**: Unified service orchestration for Next.js frontend and FastAPI backend (Uvicorn server).

---

## 2. AI Models & Intelligence Engines

### **A. Vision & Document OCR Engine**
- **Sarvam Vision API** (`api.sarvam.ai/v1/vision/ocr` via `sarvam_service.py`):
  - Purpose-built Vision OCR engine optimized for Indian government tender PDFs (RFPs, NITs, complex multi-column schedules).
  - Multi-page chunking strategy for long documents with citation metadata (page numbers and section headers).

### **B. Semantic Embedding & Product Matcher**
- **Vector Cosine Similarity & Jaccard Engine** (`embedding_service.py`):
  - Converts MSME catalog items and tender requirements into vector embeddings to measure semantic similarity.
  - Matches product variations (e.g. *"Teakwood Desk"* vs *"Classroom Furniture Dual Seating Table"*).

### **C. Structured Information Extraction & Application Generator**
- **LLM Structured Extractor** (`tender_extractor.py`):
  - Pluggable provider architecture (`LLM_PROVIDER`) supporting OpenAI GPT-4o, Claude 3.5 Sonnet, Sarvam AI, or local models.
  - Generates strict Pydantic JSON schemas (`StructuredTenderData`).
  - **Prompt Injection Defense**: Raw PDF text is isolated inside `<document_text>` XML tags with system instructions forbidding execution of malicious prompts contained in tender text.
- **Zero-Hallucination Application Assistant** (`application_service.py`):
  - Generates Cover Letters, Tender Declarations, Technical Compliance Matrices, and Checklists using verified user business data.
  - Surfacing missing data as explicit `[REQUIRED INFORMATION]` placeholders rather than hallucinating facts.

---

## 3. End-to-End Working Mechanism (Data & Execution Flow)

```
+-----------------------------------------------------------------------------------+
|                                 1. MSME USER PROFILE                              |
|  Business Profile (Turnover, MSME Udyam, GSTIN, States, Catalog) & Locker Docs    |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                                2. TENDER INGESTION                                |
|  Upload PDF -> Check MD5/SHA256 Hash -> Sarvam Vision OCR -> Raw OCR Text          |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        3. STRUCTURED LLM EXTRACTOR                                |
|  Parses OCR Text -> Pydantic Structured Data + Page & Section Citations           |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                     4. DETERMINISTIC ELIGIBILITY ENGINE                           |
|  Python Rules Validation: Turnover >= Min, MSME Req, GST Req, Experience, State   |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                     5. 5-FACTOR WEIGHTED MATCHING ENGINE                          |
|  Calculates weighted composite score. Applies HARD OVERRIDE if eligibility fails. |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                    6. REQUIREMENT GAP & RISK ANALYSIS                             |
|  Cross-references required docs vs Locker. Computes Readiness & Risk (LOW/MED/HIGH)|
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                    7. FACT-CHECKED APPLICATION ASSISTANT                          |
|  Generates Cover Letter, Declaration Form, Technical Matrix, and Checklist         |
+-----------------------------------------------------------------------------------+
```

### Detailed Execution Steps:

1. **Profile Setup & Document Locker**: The MSME registers business profile data and uploads official compliance certificates (GST, MSME Udyam, Audited Financials).
2. **Document Ingestion & Deduplication**: Tender PDF hash is computed. If cached, extraction is reused; otherwise sent to Sarvam Vision API.
3. **Structured Extraction**: Extracted OCR text is converted into validated JSON schema containing tender parameters, specs, required documents, and exact page/clause citations.
4. **Deterministic Hard-Rule Evaluation**: Non-negotiable criteria are evaluated in pure Python:
   - Minimum Turnover Rule: `business.turnover >= tender.min_turnover`
   - Mandatory MSME/GST Status check
   - Operating State & Experience Years check
5. **5-Factor Weighted Scoring Formula**:
   $$\text{Final Score} = \text{Product} \times 0.30 + \text{Eligibility} \times 0.30 + \text{Turnover} \times 0.15 + \text{Experience} \times 0.15 + \text{Location} \times 0.10$$
   *Hard Failure Rule*: If mandatory eligibility fails, overall status is forced to `NOT ELIGIBLE` regardless of product score.
6. **Requirement Gap Analysis**: Calculates Application Readiness Score:
   $$\text{Readiness Index} = \frac{\text{Available Required Docs}}{\text{Total Required Docs}}$$
7. **Document Generation**: Generates editable bid submission files pre-filled with verified facts.
