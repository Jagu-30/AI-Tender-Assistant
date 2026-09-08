# AI Tender Assistant for MSMEs - Project Specification

## 1. Executive Summary
**AI Tender Assistant** is an enterprise-grade AI solution designed for Micro, Small, and Medium Enterprises (MSMEs) in India to discover, evaluate, qualify for, and prepare applications for government tenders.

## 2. Core Problem Statement & Target Audience
- **Target Users**: MSMEs, manufacturers, contractors, suppliers, and service providers.
- **Core Problem**: Government tender documents (RFP/NIT/RFQ) are often 50–200 page unstructured PDFs filled with complex eligibility rules, financial criteria, MSME/GST exemptions, technical parameters, past experience clauses, and strict submission deadlines.
- **Core Product Promises**:
  1. *"Can my business apply for this tender?"* -> Hard rule eligibility verdict (PASS / FAIL / UNKNOWN).
  2. *"Why does this tender match my business?"* -> Multi-component breakdown & granular explanations.
  3. *"What requirements or documents am I missing?"* -> Gap matrix & missing document callouts.
  4. *"How ready am I to apply?"* -> Application readiness index (0–100%).
  5. *"How can I prepare my application?"* -> Verified generator for Cover Letter, Declaration, Technical Response & Checklist.

## 3. High-Level System Architecture
- **Ingestion & OCR**: Sarvam Vision API (with PDF chunking & file hash caching).
- **Intelligence & Schema Extraction**: LLM extraction with strict prompt isolation to avoid injection attacks.
- **Rules Engine**: Deterministic Python execution for MSME, GST, turnover, location, experience, and certificates.
- **Semantic Matching**: Cosine similarity via text embeddings between company products/services and tender requirements.
- **Scoring Engine**: Weighted formula (30% Product, 30% Eligibility, 15% Turnover, 15% Experience, 10% Location) with hard override for mandatory eligibility failures.
- **Application Generation**: Fact-checked generator producing editable documents with zero hallucination.

## 4. System Capabilities & Features
- **MSME Business Profile & Document Locker**: Multi-product store, turnover verification, state/region operation preferences, document tracking (`AVAILABLE`, `MISSING`, `PENDING`, `UNKNOWN`).
- **Tender Upload & Processing Job Engine**: Async processing flow with real-time status updates (`UPLOADED` -> `PROCESSING` -> `EXTRACTING` -> `ANALYZING` -> `MATCHING` -> `COMPLETED`).
- **Interactive Visual Dashboard & Tender Details Page**: Visual match breakdown charts, timeline & deadline intelligence (Asia/Kolkata timezone awareness), risk level analysis (`LOW`, `MEDIUM`, `HIGH`).
- **Demo & Offline Capability**: Built-in sample MSME profile ("ABC Furniture Pvt. Ltd.") and sample tender ("School Furniture Supply") for immediate zero-config walkthrough.
