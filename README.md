# AI Tender Assistant for MSMEs

> Enterprise AI solution for Micro, Small, and Medium Enterprises (MSMEs) in India to discover, evaluate, qualify for, and prepare applications for government tenders.

---

## 1. Executive Summary & Problem Statement

Government tenders (RFPs, NITs, RFQs) are typically 50 to 200 page complex PDF documents containing intricate eligibility criteria, turnover limits, MSME/GST exemptions, technical parameters, past experience clauses, and strict submission deadlines. Small business owners cannot afford to read hundreds of pages manually to figure out if they qualify.

**AI Tender Assistant** resolves this by automating document extraction via Sarvam Vision OCR, running a deterministic Python eligibility rules engine, computing 5-factor weighted vector match scores, analyzing document requirement gaps, and generating verified, editable application documents (Cover Letter, Declaration, Technical Response, Checklist).

---

## 2. Tech Stack

- **Frontend**: Next.js 14+ (App Router), React 18, TypeScript, Tailwind CSS, Lucide icons, Recharts.
- **Backend**: Python 3.11+, FastAPI, Pydantic V2, SQLAlchemy 2.0 Async, Alembic.
- **Database**: PostgreSQL / SQLite (with asyncpg / aiosqlite fallback).
- **AI & Vision**: Sarvam Vision API abstraction, sentence embeddings vector cosine similarity, LLM intelligence extraction.
- **DevOps**: Docker, Docker Compose, Uvicorn.
- **Testing**: Pytest unit & integration suite.

---

## 3. Key Features

- **MSME Business Profile & Document Locker**: Turnovers, MSME registration number, GSTIN, operating states, catalog of business products, and document verification tracking (`AVAILABLE`, `MISSING`, `PENDING`, `UNKNOWN`).
- **Sarvam Vision Ingestion Pipeline**: Handles multi-page PDFs, table extraction, citation indexing (page numbers and sections), file hash deduplication caching.
- **Deterministic Hard Rule Eligibility**: Python validator enforcing mandatory MSME, GST, turnover, and experience thresholds with instant verdict (`PASS` / `FAIL`).
- **5-Factor Weighted Matching Formula**:
  $$\text{Final Score} = \text{Product} \times 0.30 + \text{Eligibility} \times 0.30 + \text{Turnover} \times 0.15 + \text{Experience} \times 0.15 + \text{Location} \times 0.10$$
  *Hard Rule Override*: If mandatory eligibility fails, overall status is forced to `NOT ELIGIBLE` regardless of product score.
- **Requirement Gap Analysis & Readiness**: Computes $\frac{\text{Available Required Docs}}{\text{Total Required Docs}}$ readiness index and computes risk level (`LOW`, `MEDIUM`, `HIGH`).
- **Deadline Intelligence**: Asia/Kolkata timezone awareness with countdown status (`SAFE`, `ATTENTION`, `URGENT`, `CLOSED`).
- **Application Assistant Generator**: Fact-checked generator for Cover Letter, Declaration, Technical Response, and Checklist with zero hallucination.

---

## 4. Local Setup & Running Instructions

### Backend Setup (FastAPI)
```bash
cd backend
python -m venv venv
# On Windows PowerShell:
venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m pytest
uvicorn app.main:app --reload --port 8000
```
API Documentation available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### Frontend Setup (Next.js)
```bash
cd frontend
npm install
npm run build
npm run dev
```
Access UI at: [http://localhost:3000](http://localhost:3000)

### Docker Deployment
```bash
docker compose up --build
```

---

## 5. Sample Walkthrough Data

The platform comes pre-seeded with a sample MSME profile and tender for instant walkthrough:
- **Sample Business**: ABC Furniture Pvt. Ltd. (₹50 Lakhs turnover, MSME Registered, GST Active, Location: Maharashtra, Products: Desks, Chairs, Tables, Cabinets).
- **Sample Tender**: School Furniture Supply & Installation (Budget: ₹25 Lakhs, Min Turnover: ₹10 Lakhs, MSME & GST Mandatory, Location: Maharashtra).
- **Triggering Seed**: Click **"Seed Demo Profile & Tender"** in the top navigation bar or trigger `GET /api/v1/seed/sample`.

---

## 6. Legal & Trust Disclaimer

*AI-generated tender analysis is provided for assistance and should be verified against the official tender document before submission.*
