from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

# --- Auth Schemas ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# --- Business Product Schemas ---
class BusinessProductCreate(BaseModel):
    name: str
    category: Optional[str] = None
    description: Optional[str] = None

class BusinessProductResponse(BaseModel):
    id: str
    name: str
    category: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True

# --- Business Document Schemas ---
class BusinessDocumentCreate(BaseModel):
    document_name: str
    document_type: str
    verification_status: str = "AVAILABLE"
    issue_date: Optional[str] = None

class BusinessDocumentResponse(BaseModel):
    id: str
    document_name: str
    document_type: str
    verification_status: str
    file_path: Optional[str] = None
    issue_date: Optional[str] = None

    class Config:
        from_attributes = True

class BusinessDocumentUpdate(BaseModel):
    document_name: Optional[str] = None
    document_type: Optional[str] = None
    verification_status: Optional[str] = None
    issue_date: Optional[str] = None

# --- Business Profile Schemas ---
class BusinessProfileCreate(BaseModel):
    company_name: str
    business_category: Optional[str] = "Manufacturer"
    description: Optional[str] = None
    annual_turnover: float = 0.0
    is_msme_registered: bool = False
    msme_registration_number: Optional[str] = None
    has_gst_registration: bool = True
    gstin: Optional[str] = None
    state_location: str = "Maharashtra"
    operating_regions: List[str] = ["Maharashtra"]
    years_in_business: int = 1
    govt_experience_years: int = 0
    certifications: List[str] = []
    manufacturing_capacity: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

class BusinessProfileResponse(BusinessProfileCreate):
    id: str
    user_id: str
    completeness_score: int = 100
    products: List[BusinessProductResponse] = []
    documents: List[BusinessDocumentResponse] = []

    class Config:
        from_attributes = True

# --- Structured Tender Extracted Data ---
class SourceCitation(BaseModel):
    page: Optional[int] = None
    section: Optional[str] = None
    source_text: Optional[str] = None

class TenderEligibilityRule(BaseModel):
    msme_required: bool = False
    gst_required: bool = True
    minimum_turnover: float = 0.0
    allowed_locations: List[str] = []
    min_experience_years: int = 0

class StructuredTenderData(BaseModel):
    title: str
    tender_id: str
    organization: Optional[str] = "Government Department"
    budget: float = 0.0
    deadline: Optional[str] = None
    location: Optional[str] = None
    products: List[str] = []
    eligibility: TenderEligibilityRule = Field(default_factory=TenderEligibilityRule)
    required_documents: List[str] = []
    technical_specs: Dict[str, Any] = Field(default_factory=dict)
    source_citations: Dict[str, SourceCitation] = Field(default_factory=dict)

# --- Match Analysis Schemas ---
class ReasonItem(BaseModel):
    category: str # MATCHED, FAILED, MISSING, WARNING
    reason: str
    source_citation: Optional[SourceCitation] = None

class MatchResponse(BaseModel):
    match_id: str
    tender_id: str
    tender_title: str
    organization: Optional[str]
    budget: float
    deadline: Optional[str]
    location: Optional[str]
    overall_score: float
    product_score: float
    eligibility_score: float
    location_score: float
    turnover_score: float
    experience_score: float
    eligibility_status: str
    match_category: str
    risk_level: str
    readiness_percentage: float
    reasons: List[ReasonItem] = []
    missing_documents: List[str] = []
    available_documents: List[str] = []
    gap_matrix: List[Dict[str, Any]] = []
    days_remaining: int = 0
    urgency_status: str = "SAFE"

# --- Application Generation Schemas ---
class ApplicationGenerateRequest(BaseModel):
    match_id: Optional[str] = None
    tender_id: Optional[str] = None
    business_id: Optional[str] = None

class GeneratedApplicationResponse(BaseModel):
    id: str
    match_id: str
    cover_letter_content: str
    declaration_content: str
    technical_response_content: str
    document_checklist: List[Dict[str, Any]]
    is_edited: bool = False

    class Config:
        from_attributes = True

class ApplicationUpdateRequest(BaseModel):
    cover_letter_content: Optional[str] = None
    declaration_content: Optional[str] = None
    technical_response_content: Optional[str] = None
    document_checklist: Optional[List[Dict[str, Any]]] = None
    is_edited: Optional[bool] = True
