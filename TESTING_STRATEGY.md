# AI Tender Assistant - Testing Strategy & Verification Plan

## 1. Overview
The testing strategy enforces multi-layered validation to ensure high accuracy, prompt injection safety, deterministic eligibility enforcement, and zero hallucination in generated application documents.

## 2. Test Layers

### A. Backend Unit Tests (`backend/tests/unit/`)
- **`test_eligibility_engine.py`**:
  - Validates turnover threshold PASS/FAIL conditions.
  - Verifies MSME registration requirement checks.
  - Verifies GST requirement checks.
  - Verifies location matching logic.
  - Verifies that mandatory failure yields `PASS=False`.
- **`test_scoring_engine.py`**:
  - Validates exact weighted formula calculations:
    `30% Product + 30% Eligibility + 15% Turnover + 15% Experience + 10% Location`.
  - Verifies Hard Rule override: Ensures `overall_eligibility` becomes `NOT ELIGIBLE` when eligibility fails, even if product match is 100%.
- **`test_gap_analysis.py`**:
  - Validates readiness percentage computation: `Available Required Docs / Total Required Docs`.
  - Validates document gap mapping (`AVAILABLE`, `MISSING`, `PENDING`, `UNKNOWN`).
- **`test_prompt_injection.py`**:
  - Injects adversarial strings ("Ignore previous instructions", "System override", "Mark eligible") into simulated tender PDFs.
  - Verifies that the extraction & prompt wrapper treats document contents strictly as untrusted string data.

### B. Integration Tests (`backend/tests/integration/`)
- **`test_auth_api.py`**: User registration, JWT login, token verification, protected routes.
- **`test_profile_api.py`**: MSME profile creation, product catalog CRUD, document locker upload.
- **`test_tender_flow_api.py`**: Tender PDF upload -> Async status polling -> Structured JSON extraction -> Match calculation -> Application generation.

### C. End-to-End Playwright Tests (`tests/e2e/`)
- **`test_demo_flow.py`**:
  1. Login with demo user / register user.
  2. Load or populate ABC Furniture Pvt. Ltd. business profile.
  3. Upload sample tender ("School Furniture Supply PDF").
  4. Wait for real-time progress transitions (`UPLOADED` -> `COMPLETED`).
  5. Inspect Tender Details, Match Score breakdown, Requirement Gap, and Risk Assessment.
  6. Click "Generate Application", edit generated Cover Letter, and save package.

## 3. Execution Commands
- **Backend Unit & Integration Tests**:
  ```bash
  pytest backend/tests -v
  ```
- **Type Checks & Linting**:
  ```bash
  cd backend && mypy app && flake8 app
  cd frontend && npm run lint && npx tsc --noEmit
  ```
- **Frontend Build Verification**:
  ```bash
  cd frontend && npm run build
  ```
- **E2E Playwright Tests**:
  ```bash
  npx playwright test
  ```
