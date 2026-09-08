# AI Tender Assistant - Database Schema (PostgreSQL / SQLAlchemy)

## Entity Relationship Summary
```
+---------------+        1:1        +-------------------+        1:N        +-------------------+
|     users     |<----------------->| business_profiles |<----------------->| business_products |
+---------------+                   +---------+---------+                   +-------------------+
                                              |
                                              | 1:N                         +-------------------+
                                              +---------------------------->| business_documents|
                                                                            +-------------------+

+---------------+        1:N        +-------------------+        1:N        +-------------------+
|    tenders    |<----------------->| tender_documents  |<----------------->|tender_requirements|
+-------+-------+                   +-------------------+                   +-------------------+
        |
        | 1:N                       +-------------------+                   +-------------------+
        +-------------------------->|  tender_products  |                   |  processing_jobs  |
        |                           +-------------------+                   +-------------------+
        |
        | 1:N                       +-------------------+        1:N        +-------------------+
        +-------------------------->|      matches      |<----------------->|   match_reasons   |
                                    +---------+---------+                   +-------------------+
                                              |
                                              | 1:N                         +-------------------+
                                              +---------------------------->|application_docs   |
                                                                            +-------------------+
```

## Table Specifications

### 1. `users`
- `id`: UUID (Primary Key, default uuid4)
- `email`: VARCHAR(255) (Unique, Indexed, Not Null)
- `hashed_password`: VARCHAR(255) (Not Null)
- `full_name`: VARCHAR(255)
- `is_active`: BOOLEAN (Default True)
- `created_at`: TIMESTAMPTZ (Default NOW())
- `updated_at`: TIMESTAMPTZ (Default NOW())

### 2. `business_profiles`
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key -> `users.id`, Unique, Not Null)
- `company_name`: VARCHAR(255) (Not Null)
- `business_category`: VARCHAR(100) (e.g. "Furniture Manufacturer", "IT Supplier")
- `description`: TEXT
- `annual_turnover`: NUMERIC(15, 2) (In INR, e.g. 5000000.00 for 50 Lakhs)
- `is_msme_registered`: BOOLEAN (Default False)
- `msme_registration_number`: VARCHAR(100)
- `has_gst_registration`: BOOLEAN (Default True)
- `gstin`: VARCHAR(50)
- `state_location`: VARCHAR(100) (e.g. "Maharashtra")
- `operating_regions`: JSONB (List of states/regions)
- `years_in_business`: INT
- `govt_experience_years`: INT
- `certifications`: JSONB (List of certifications e.g. ["ISO 9001", "CE"])
- `manufacturing_capacity`: TEXT
- `contact_email`: VARCHAR(255)
- `contact_phone`: VARCHAR(50)
- `created_at`: TIMESTAMPTZ
- `updated_at`: TIMESTAMPTZ

### 3. `business_products`
- `id`: UUID (Primary Key)
- `business_id`: UUID (Foreign Key -> `business_profiles.id`, Not Null)
- `name`: VARCHAR(255) (Not Null, e.g. "Desks")
- `category`: VARCHAR(100)
- `description`: TEXT
- `embedding`: VECTOR(1536) / JSONB (Vector representation for cosine similarity)
- `created_at`: TIMESTAMPTZ

### 4. `business_documents`
- `id`: UUID (Primary Key)
- `business_id`: UUID (Foreign Key -> `business_profiles.id`, Not Null)
- `document_name`: VARCHAR(255) (Not Null)
- `document_type`: VARCHAR(100) ("GST_CERTIFICATE", "MSME_CERTIFICATE", "FINANCIAL_STATEMENT", "EXPERIENCE_CERTIFICATE", "OTHER")
- `file_path`: VARCHAR(512)
- `verification_status`: VARCHAR(50) ("AVAILABLE", "MISSING", "PENDING", "UNKNOWN")
- `issue_date`: DATE
- `created_at`: TIMESTAMPTZ

### 5. `tenders`
- `id`: UUID (Primary Key)
- `tender_id_code`: VARCHAR(100) (Indexed, e.g. "TENDER-2026-001")
- `title`: VARCHAR(512) (Not Null)
- `organization`: VARCHAR(255)
- `department`: VARCHAR(255)
- `tender_type`: VARCHAR(100)
- `estimated_value`: NUMERIC(15, 2) (Budget in INR)
- `tender_fee`: NUMERIC(12, 2)
- `emd_amount`: NUMERIC(12, 2)
- `issue_date`: DATE
- `closing_date`: TIMESTAMPTZ (Aware of Asia/Kolkata)
- `opening_date`: TIMESTAMPTZ
- `location`: VARCHAR(100)
- `delivery_location`: VARCHAR(100)
- `raw_document_path`: VARCHAR(512)
- `file_hash`: VARCHAR(64) (Indexed, SHA-256 for deduplication)
- `processing_status`: VARCHAR(50) ("UPLOADED", "PROCESSING", "EXTRACTING", "ANALYZING", "MATCHING", "COMPLETED", "FAILED")
- `extracted_json`: JSONB
- `created_at`: TIMESTAMPTZ

### 6. `tender_requirements`
- `id`: UUID (Primary Key)
- `tender_id`: UUID (Foreign Key -> `tenders.id`, Not Null)
- `requirement_type`: VARCHAR(50) ("TURNOVER", "MSME", "GST", "EXPERIENCE", "CERTIFICATION", "LOCATION", "DOCUMENT")
- `is_mandatory`: BOOLEAN (Default True)
- `description`: TEXT
- `threshold_value`: NUMERIC(15, 2)
- `source_page`: INT
- `source_section`: VARCHAR(255)
- `source_text`: TEXT

### 7. `tender_products`
- `id`: UUID (Primary Key)
- `tender_id`: UUID (Foreign Key -> `tenders.id`, Not Null)
- `name`: VARCHAR(255)
- `description`: TEXT
- `quantity`: VARCHAR(100)
- `technical_specs`: JSONB
- `embedding`: VECTOR(1536) / JSONB

### 8. `matches`
- `id`: UUID (Primary Key)
- `business_id`: UUID (Foreign Key -> `business_profiles.id`, Not Null)
- `tender_id`: UUID (Foreign Key -> `tenders.id`, Not Null)
- `overall_score`: NUMERIC(5, 2) (0.00 to 100.00)
- `product_score`: NUMERIC(5, 2)
- `eligibility_score`: NUMERIC(5, 2)
- `location_score`: NUMERIC(5, 2)
- `turnover_score`: NUMERIC(5, 2)
- `experience_score`: NUMERIC(5, 2)
- `eligibility_status`: VARCHAR(50) ("ELIGIBLE", "NOT_ELIGIBLE", "PARTIALLY_ELIGIBLE", "UNKNOWN")
- `match_category`: VARCHAR(50) ("STRONG_MATCH", "GOOD_MATCH", "PARTIAL_MATCH", "LOW_MATCH")
- `risk_level`: VARCHAR(20) ("LOW", "MEDIUM", "HIGH")
- `readiness_percentage`: NUMERIC(5, 2)
- `created_at`: TIMESTAMPTZ

### 9. `match_reasons`
- `id`: UUID (Primary Key)
- `match_id`: UUID (Foreign Key -> `matches.id`, Not Null)
- `category`: VARCHAR(50) ("MATCHED", "FAILED", "MISSING", "WARNING")
- `reason`: TEXT (Human readable explanation)
- `source_citation`: JSONB ({ "page": 4, "section": "Eligibility" })

### 10. `generated_applications`
- `id`: UUID (Primary Key)
- `match_id`: UUID (Foreign Key -> `matches.id`, Not Null)
- `user_id`: UUID (Foreign Key -> `users.id`, Not Null)
- `cover_letter_content`: TEXT
- `declaration_content`: TEXT
- `technical_response_content`: TEXT
- `document_checklist`: JSONB
- `is_edited`: BOOLEAN (Default False)
- `created_at`: TIMESTAMPTZ
- `updated_at`: TIMESTAMPTZ

### 11. `processing_jobs` & `audit_logs`
- `processing_jobs`: Tracks background processing status, step latencies, error traces, and progress percentages.
- `audit_logs`: Log of evaluation runs, score computations, rules triggered, and user actions.
