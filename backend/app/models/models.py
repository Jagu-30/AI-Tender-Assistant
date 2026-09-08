import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Numeric, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    business_profile = relationship("BusinessProfile", back_populates="user", uselist=False)

class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    company_name = Column(String(255), nullable=False)
    business_category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    annual_turnover = Column(Numeric(15, 2), default=0.0) # INR
    is_msme_registered = Column(Boolean, default=False)
    msme_registration_number = Column(String(100), nullable=True)
    has_gst_registration = Column(Boolean, default=True)
    gstin = Column(String(50), nullable=True)
    state_location = Column(String(100), nullable=False, default="Maharashtra")
    operating_regions = Column(JSON, default=list) # e.g. ["Maharashtra", "All India"]
    years_in_business = Column(Integer, default=1)
    govt_experience_years = Column(Integer, default=0)
    certifications = Column(JSON, default=list)
    manufacturing_capacity = Column(Text, nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="business_profile")
    products = relationship("BusinessProduct", back_populates="business", cascade="all, delete-orphan")
    documents = relationship("BusinessDocument", back_populates="business", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="business", cascade="all, delete-orphan")

class BusinessProduct(Base):
    __tablename__ = "business_products"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    business_id = Column(String(36), ForeignKey("business_profiles.id"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    embedding_json = Column(JSON, nullable=True) # Vector list
    created_at = Column(DateTime, default=datetime.utcnow)

    business = relationship("BusinessProfile", back_populates="products")

class BusinessDocument(Base):
    __tablename__ = "business_documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    business_id = Column(String(36), ForeignKey("business_profiles.id"), nullable=False)
    document_name = Column(String(255), nullable=False)
    document_type = Column(String(100), nullable=False) # GST_CERTIFICATE, MSME_CERTIFICATE, FINANCIAL_STATEMENT, EXPERIENCE_CERTIFICATE, OTHER
    file_path = Column(String(512), nullable=True)
    verification_status = Column(String(50), default="AVAILABLE") # AVAILABLE, MISSING, PENDING, UNKNOWN
    issue_date = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    business = relationship("BusinessProfile", back_populates="documents")

class Tender(Base):
    __tablename__ = "tenders"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id_code = Column(String(100), index=True, nullable=False)
    title = Column(String(512), nullable=False)
    organization = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    tender_type = Column(String(100), nullable=True)
    estimated_value = Column(Numeric(15, 2), default=0.0)
    tender_fee = Column(Numeric(12, 2), default=0.0)
    emd_amount = Column(Numeric(12, 2), default=0.0)
    issue_date = Column(String(50), nullable=True)
    closing_date = Column(DateTime, nullable=True)
    opening_date = Column(DateTime, nullable=True)
    location = Column(String(100), nullable=True)
    delivery_location = Column(String(100), nullable=True)
    raw_document_path = Column(String(512), nullable=True)
    file_hash = Column(String(64), index=True, nullable=True)
    processing_status = Column(String(50), default="UPLOADED") # UPLOADED, PROCESSING, EXTRACTING, ANALYZING, MATCHING, COMPLETED, FAILED
    extracted_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    requirements = relationship("TenderRequirement", back_populates="tender", cascade="all, delete-orphan")
    products = relationship("TenderProduct", back_populates="tender", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="tender", cascade="all, delete-orphan")
    jobs = relationship("ProcessingJob", back_populates="tender", cascade="all, delete-orphan")

class TenderRequirement(Base):
    __tablename__ = "tender_requirements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id"), nullable=False)
    requirement_type = Column(String(50), nullable=False) # TURNOVER, MSME, GST, EXPERIENCE, CERTIFICATION, LOCATION, DOCUMENT
    is_mandatory = Column(Boolean, default=True)
    description = Column(Text, nullable=False)
    threshold_value = Column(Numeric(15, 2), nullable=True)
    source_page = Column(Integer, nullable=True)
    source_section = Column(String(255), nullable=True)
    source_text = Column(Text, nullable=True)

    tender = relationship("Tender", back_populates="requirements")

class TenderProduct(Base):
    __tablename__ = "tender_products"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(String(100), nullable=True)
    technical_specs = Column(JSON, nullable=True)
    embedding_json = Column(JSON, nullable=True)

    tender = relationship("Tender", back_populates="products")

class Match(Base):
    __tablename__ = "matches"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    business_id = Column(String(36), ForeignKey("business_profiles.id"), nullable=False)
    tender_id = Column(String(36), ForeignKey("tenders.id"), nullable=False)
    overall_score = Column(Numeric(5, 2), default=0.0) # 0 to 100
    product_score = Column(Numeric(5, 2), default=0.0)
    eligibility_score = Column(Numeric(5, 2), default=0.0)
    location_score = Column(Numeric(5, 2), default=0.0)
    turnover_score = Column(Numeric(5, 2), default=0.0)
    experience_score = Column(Numeric(5, 2), default=0.0)
    eligibility_status = Column(String(50), default="UNKNOWN") # ELIGIBLE, NOT_ELIGIBLE, PARTIALLY_ELIGIBLE, UNKNOWN
    match_category = Column(String(50), default="LOW_MATCH") # STRONG_MATCH, GOOD_MATCH, PARTIAL_MATCH, LOW_MATCH
    risk_level = Column(String(20), default="MEDIUM") # LOW, MEDIUM, HIGH
    readiness_percentage = Column(Numeric(5, 2), default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    business = relationship("BusinessProfile", back_populates="matches")
    tender = relationship("Tender", back_populates="matches")
    reasons = relationship("MatchReason", back_populates="match", cascade="all, delete-orphan")

class MatchReason(Base):
    __tablename__ = "match_reasons"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    match_id = Column(String(36), ForeignKey("matches.id"), nullable=False)
    category = Column(String(50), nullable=False) # MATCHED, FAILED, MISSING, WARNING
    reason = Column(Text, nullable=False)
    source_citation = Column(JSON, nullable=True)

    match = relationship("Match", back_populates="reasons")

class GeneratedApplication(Base):
    __tablename__ = "generated_applications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    match_id = Column(String(36), nullable=False)
    user_id = Column(String(36), nullable=False)
    cover_letter_content = Column(Text, nullable=True)
    declaration_content = Column(Text, nullable=True)
    technical_response_content = Column(Text, nullable=True)
    document_checklist = Column(JSON, default=list)
    is_edited = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id"), nullable=False)
    status = Column(String(50), default="PROCESSING") # UPLOADED, PROCESSING, EXTRACTING, ANALYZING, MATCHING, COMPLETED, FAILED
    step_details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tender = relationship("Tender", back_populates="jobs")
