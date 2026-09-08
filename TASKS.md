# AI Tender Assistant - Implementation Phases & Task Breakdown

## Phase 0: Planning & Specification [COMPLETED]
- [x] Inspect workspace and initialize project structure
- [x] Create PROJECT_SPEC.md, ARCHITECTURE.md, DATABASE_SCHEMA.md, API_SPEC.md, TASKS.md, TESTING_STRATEGY.md
- [x] Establish implementation plan and obtain approval

## Phase 1: Environment & Scaffolding
- [ ] Backend FastAPI directory scaffolding (`backend/app`, `backend/core`, `backend/models`, etc.)
- [ ] Frontend Next.js 14+ directory scaffolding (`frontend/app`, `frontend/components`, etc.)
- [ ] Database configuration (PostgreSQL connection, Async SQLAlchemy 2.0, Alembic setup)
- [ ] Docker & Docker Compose setup (`docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`)
- [ ] Environment file `.env.example` setup

## Phase 2: Core Data Models, Authentication & Business Profile
- [ ] User authentication models, JWT security, registration/login endpoints
- [ ] Business Profile schema, models, services & API endpoints
- [ ] Business Products catalog management (CRUD)
- [ ] Business Document Locker with verification status tracking (`AVAILABLE`, `MISSING`, `PENDING`, `UNKNOWN`)
- [ ] Sample Data Seeder: ABC Furniture Pvt. Ltd. (₹50L turnover, MSME, GST, Furniture products)

## Phase 3: Tender Upload, File Storage & Processing Job Tracking
- [ ] File upload API with validation (PDF, PNG, JPG, size limit, hash deduplication)
- [ ] Secure storage service with path traversal defense
- [ ] Async Processing Job tracker (`UPLOADED`, `PROCESSING`, `EXTRACTING`, `ANALYZING`, `MATCHING`, `COMPLETED`, `FAILED`)

## Phase 4: Sarvam Vision Integration & Document Intelligence
- [ ] Provider abstraction (`DocumentProvider`, `SarvamVisionProvider`)
- [ ] Sarvam Vision API integration with `SARVAM_API_KEY` environment variable
- [ ] PDF document chunking & stitching for long tenders (> 10 pages)
- [ ] Text, table, heading, and page citation extraction normalize pipeline

## Phase 5: Structured Tender Extraction & Intelligence
- [ ] Validated Pydantic schema `StructuredTenderData`
- [ ] LLM extraction service (`tender_extraction.py` prompt with strict prompt isolation against injection)
- [ ] Extraction of eligibility, turnover, experience, dates, budget, required documents, and source citations
- [ ] Sample Tender Seeder: School Furniture Supply (₹25L budget, ₹10L turnover requirement, MSME, GST, experience)

## Phase 6: Deterministic Eligibility Engine
- [ ] Python rules validator (`eligibility_engine.py`)
- [ ] Hard rule checks: MSME requirement, GST requirement, Turnover threshold, Location, Experience
- [ ] Returns deterministic verdict (`PASS`, `FAIL`, `UNKNOWN`) and human-readable reason list

## Phase 7: Semantic Product Vector Matching
- [ ] Embeddings service abstraction (`EmbeddingProvider`, `SentenceTransformer` / `OpenAI`)
- [ ] Product vector comparison (Business product vectors vs Tender requirement vectors)
- [ ] Cosine similarity computation returning `product_match_score` (0-100%) with matching explanations

## Phase 8: Weighted Matching & Explainable Scoring Engine
- [ ] Weighted formula implementation:
  `final_score = product_score * 0.30 + eligibility_score * 0.30 + location_score * 0.10 + turnover_score * 0.15 + experience_score * 0.15`
- [ ] **Hard Override Rule**: Enforce `overall_eligibility = NOT ELIGIBLE` when mandatory eligibility checks fail
- [ ] Match classification (Strong 90-100, Good 75-89, Partial 60-74, Low <60)
- [ ] Rich explainability payload generator (Why matched / Why failed)

## Phase 9: Requirement Gap, Readiness, Risk & Deadline Intelligence
- [ ] Requirement Gap Analysis (Compare tender required docs vs business document locker)
- [ ] Application Readiness percentage computation
- [ ] Risk level computation (`LOW`, `MEDIUM`, `HIGH`)
- [ ] Deadline intelligence with Asia/Kolkata timezone awareness and countdown status (`SAFE`, `ATTENTION`, `URGENT`, `CLOSED`)

## Phase 10: Enterprise SaaS Frontend & UI Components
- [ ] Modern Next.js UI theme, navigation, and landing page
- [ ] Protected MSME Dashboard (KPI cards, recommended tenders, readiness metrics)
- [ ] Business Profile & Document Locker UI with upload & edit capabilities
- [ ] Tender Upload modal with live step-by-step progress tracking
- [ ] Premium Tender Details Page with visual score charts, match breakdown, and source citation links

## Phase 11: Application Assistant Generator
- [ ] Verified prompt templates (`cover_letter.py`, `declaration.py`, `technical_response.py`)
- [ ] Fact-checked generation with `[REQUIRED INFORMATION]` placeholders for missing facts
- [ ] Interactive draft editor UI (Edit, Save, Regenerate, Download as Markdown/PDF)
- [ ] Required document submission checklist UI

## Phase 12: Testing, Security & Verification
- [ ] Pytest backend unit & integration test suite (Auth, Profile, Eligibility, Scoring, Application)
- [ ] Playwright E2E test suite covering full user journey
- [ ] Security audit (Prompt injection defense, path traversal, API auth)
- [ ] Production build verification & linting checks
