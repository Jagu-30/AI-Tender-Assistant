# AI Tender Assistant - API Specification

Base URL: `/api/v1`

## 1. Authentication Endpoints
- **POST `/auth/register`**
  - Payload: `{ "email": "user@example.com", "password": "...", "full_name": "John Doe" }`
  - Response: `201 Created` `{ "user_id": "...", "access_token": "...", "token_type": "bearer" }`
- **POST `/auth/login`**
  - Payload: `{ "email": "user@example.com", "password": "..." }`
  - Response: `200 OK` `{ "access_token": "...", "token_type": "bearer" }`
- **POST `/auth/logout`**
  - Response: `200 OK` `{ "message": "Logged out successfully" }`
- **GET `/auth/me`**
  - Response: `200 OK` `{ "id": "...", "email": "...", "full_name": "..." }`

## 2. Business Profile Endpoints
- **POST `/business/profile`** -> Create MSME profile.
- **GET `/business/profile`** -> Retrieve current profile with completeness percentage.
- **PUT `/business/profile`** -> Update business details (Turnover, MSME status, GST, location).

## 3. Product Catalog Endpoints
- **POST `/business/products`** -> Add product/service (Name, Category, Description).
- **GET `/business/products`** -> List all business products.
- **PUT `/business/products/{id}`** -> Update product details.
- **DELETE `/business/products/{id}`** -> Remove product from catalog.

## 4. Business Document Locker Endpoints
- **POST `/documents/upload`** -> Upload verification file (multipart/form-data with type e.g. `GST_CERTIFICATE`).
- **GET `/documents`** -> List all business documents & verification statuses.
- **DELETE `/documents/{id}`** -> Delete document.

## 5. Tender Processing & Ingestion Endpoints
- **POST `/tenders/upload`** -> Upload tender document (PDF/PNG/JPG). Returns `{ "tender_id": "...", "job_id": "...", "status": "UPLOADED" }`.
- **GET `/tenders`** -> Search & filter list of analyzed tenders.
- **GET `/tenders/{id}`** -> Get complete extracted tender details, requirements, source citations.
- **DELETE `/tenders/{id}`** -> Delete tender record.
- **POST `/tenders/{id}/reprocess`** -> Force re-extraction.
- **GET `/tenders/{id}/status`** -> Poll current async job status (`PROCESSING`, `EXTRACTING`, `ANALYZING`, `MATCHING`, `COMPLETED`, `FAILED`).

## 6. Analysis & Matching Endpoints
- **POST `/tenders/{id}/analyze`** -> Run document extraction & requirement structuring.
- **POST `/tenders/{id}/match`** -> Trigger eligibility engine, semantic product vector matching & weighted scoring against current Business Profile.
- **GET `/tenders/{id}/analysis`** -> Get full analysis output (Eligibility, Risk, Gap Analysis, Deadlines).
- **GET `/matches`** -> List user's matched tenders sorted by match score or deadline.
- **GET `/matches/{id}`** -> Get detailed match report with explainable breakdown.

## 7. Application Assistant Endpoints
- **POST `/applications/cover-letter`** -> Generate tender cover letter based on verified facts.
- **POST `/applications/declaration`** -> Generate formal tender declaration.
- **POST `/applications/technical-response`** -> Generate technical compliance statement.
- **GET `/applications/{id}`** -> Get generated application package.
- **PUT `/applications/{id}`** -> Save user edits to generated sections.
- **GET `/applications/{id}/download`** -> Export application package as Markdown / PDF / ZIP.

## 8. Health & System Status
- **GET `/health`** -> `{ "status": "healthy", "database": "connected", "sarvam_status": "configured" }`
- **GET `/seed/sample`** -> Seed sample business ("ABC Furniture Pvt. Ltd.") and sample tender ("School Furniture Supply") for instant demonstration.
