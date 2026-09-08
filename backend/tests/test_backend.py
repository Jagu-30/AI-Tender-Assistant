import pytest
from app.models.models import BusinessProfile, BusinessProduct
from app.services.eligibility_engine import EligibilityEngine
from app.services.scoring_engine import ScoringEngine
from app.services.gap_engine import RequirementGapEngine
from app.services.application_service import ApplicationAssistantService
from app.services.embedding_service import SemanticMatchingEngine

def test_eligibility_engine_pass():
    engine = EligibilityEngine()
    bus = BusinessProfile(
        company_name="Test Company",
        annual_turnover=5000000.0, # ₹50L
        is_msme_registered=True,
        has_gst_registration=True,
        state_location="Maharashtra",
        years_in_business=5
    )
    tender_el = {
        "minimum_turnover": 1000000.0, # ₹10L
        "msme_required": True,
        "gst_required": True,
        "allowed_locations": ["Maharashtra"],
        "min_experience_years": 2
    }
    result = engine.evaluate(bus, tender_el)
    assert result["status"] == "ELIGIBLE"
    assert result["score"] == 100.0

def test_eligibility_engine_fail_turnover():
    engine = EligibilityEngine()
    bus = BusinessProfile(
        company_name="Small Business",
        annual_turnover=500000.0, # ₹5L
        is_msme_registered=True,
        has_gst_registration=True,
        state_location="Maharashtra"
    )
    tender_el = {
        "minimum_turnover": 1000000.0, # ₹10L required
        "msme_required": True,
        "gst_required": True
    }
    result = engine.evaluate(bus, tender_el)
    assert result["status"] == "NOT_ELIGIBLE"

def test_scoring_engine_weights():
    scoring = ScoringEngine()
    bus = BusinessProfile(
        company_name="ABC Furniture",
        annual_turnover=5000000.0,
        is_msme_registered=True,
        has_gst_registration=True,
        state_location="Maharashtra",
        govt_experience_years=3
    )
    bus.products = [
        BusinessProduct(name="Desks"),
        BusinessProduct(name="Chairs"),
        BusinessProduct(name="Tables"),
        BusinessProduct(name="Cabinets")
    ]
    tender_data = {
        "title": "School Furniture Supply",
        "tender_id": "TENDER-001",
        "location": "Maharashtra",
        "products": ["Classroom Desks", "Student Seating Chairs"],
        "eligibility": {
            "minimum_turnover": 1000000.0,
            "msme_required": True,
            "gst_required": True,
            "min_experience_years": 2
        }
    }
    match_result = scoring.calculate_match(bus, tender_data)
    assert match_result["overall_score"] > 80.0
    assert match_result["eligibility_status"] == "ELIGIBLE"
    assert match_result["match_category"] in ["STRONG_MATCH", "GOOD_MATCH"]

def test_gap_engine():
    gap = RequirementGapEngine()
    bus = BusinessProfile(
        company_name="ABC Furniture",
        annual_turnover=5000000.0,
        has_gst_registration=True,
        is_msme_registered=True
    )
    bus.documents = []
    tender_data = {
        "required_documents": [
            "GST Registration Certificate",
            "MSME Udyam Certificate",
            "Audited Financial Statements",
            "Previous Experience Certificate"
        ],
        "deadline": "2026-09-20T17:00:00+05:30",
        "eligibility": {"minimum_turnover": 1000000.0}
    }
    res = gap.analyze_gap(bus, tender_data)
    assert res["readiness_percentage"] >= 50.0
    assert "Previous Experience Certificate" in res["missing_documents"]
    assert res["urgency_status"] in ["SAFE", "ATTENTION", "URGENT"]
