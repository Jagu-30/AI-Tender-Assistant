# Bug Report & Debugging Log

Summary of bugs identified during local system verification, root cause analysis, fixes applied, and current verification status.

---

### BUG-001: Missing `email-validator` Dependency
- **Description**: FastAPI startup failed when loading Pydantic `EmailStr` schemas in `auth.py`.
- **Severity**: HIGH
- **Root Cause**: `email-validator` package was not installed in Python environment or listed in `requirements.txt`.
- **Fix**: Installed `email-validator` via `pip install email-validator` and updated `backend/requirements.txt`.
- **Verification Status**: FIXED (FastAPI server initializes cleanly).

---

### BUG-002: API Base Route Prefix Mismatch (`/api` vs `/api/v1`)
- **Description**: Frontend requests to `/api/v1/health` returned HTTP 404 Not Found.
- **Severity**: MEDIUM
- **Root Cause**: `API_V1_STR` in `backend/app/core/config.py` was set to `"/api"` instead of `"/api/v1"`.
- **Fix**: Updated `API_V1_STR = "/api/v1"` in `config.py`.
- **Verification Status**: FIXED (`GET /api/v1/health` returns HTTP 200).

---

### BUG-003: Passlib Bcrypt Backend Compatibility Error on Python 3.13
- **Description**: `seed_sample_data` threw HTTP 500 `passlib.exc.MissingBackendError: bcrypt: no backends available`.
- **Severity**: HIGH
- **Root Cause**: Passlib's legacy bcrypt backend inspection relies on `bcrypt.__about__.__version__` which was deprecated in modern `bcrypt` under Python 3.13.
- **Fix**: Replaced passlib `CryptContext` in `backend/app/core/security.py` with standard `bcrypt.hashpw` and `bcrypt.checkpw`.
- **Verification Status**: FIXED (`GET /api/v1/seed/sample` seeds user and profile successfully).

---

### BUG-004: Missing `GET /business/products` Endpoint
- **Description**: Fetching product catalog returned `HTTP 405 Method Not Allowed`.
- **Severity**: MEDIUM
- **Root Cause**: Route decorator `@router.get("/products")` was missing in `backend/app/api/profile.py`.
- **Fix**: Implemented `list_products` handler in `profile.py`.
- **Verification Status**: FIXED (`GET /api/v1/business/products` returns HTTP 200 with product list).

---

### BUG-005: Missing `POST /tenders/{id}/analyze` Endpoint Alias
- **Description**: Ingestion pipeline calling `/tenders/{id}/analyze` returned `HTTP 404 Not Found`.
- **Severity**: MEDIUM
- **Root Cause**: Only `/tenders/{id}/match` was decorated in `matching.py`.
- **Fix**: Added `@router.post("/tenders/{tender_id}/analyze")` decorator.
- **Verification Status**: FIXED (`POST /api/v1/tenders/{id}/analyze` returns HTTP 200).

---

### BUG-006: Missing Individual Document Endpoints in `applications.py`
- **Description**: `POST /applications/cover-letter` returned `HTTP 405 Method Not Allowed`.
- **Severity**: MEDIUM
- **Root Cause**: Only `/applications/generate` was registered in `applications.py`.
- **Fix**: Added route decorators for `/cover-letter`, `/declaration`, `/technical-response`, and made request schema parameters flexible.
- **Verification Status**: FIXED (`POST /applications/cover-letter` returns HTTP 200).

---

### BUG-007: Missing `/auth/register` Route in Next.js Frontend
- **Description**: Navigating to `http://localhost:3000/auth/register` returned `HTTP 404 Not Found`.
- **Severity**: LOW
- **Root Cause**: `app/auth/register/page.tsx` was missing.
- **Fix**: Created `frontend/app/auth/register/page.tsx`.
- **Verification Status**: FIXED (`http://localhost:3000/auth/register` returns HTTP 200).
