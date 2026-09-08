from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.models import BusinessProfile, Tender, Match, MatchReason
from app.schemas.schemas import MatchResponse, ReasonItem
from app.services.scoring_engine import ScoringEngine
from app.services.gap_engine import RequirementGapEngine

router = APIRouter(tags=["Match & Analysis"])

scoring_engine = ScoringEngine()
gap_engine = RequirementGapEngine()

@router.post("/tenders/{tender_id}/match")
@router.post("/tenders/{tender_id}/analyze")
@router.get("/tenders/{tender_id}/analysis")
async def analyze_and_match(tender_id: str, db: AsyncSession = Depends(get_db)):
    res_b = await db.execute(
        select(BusinessProfile)
        .options(selectinload(BusinessProfile.products), selectinload(BusinessProfile.documents))
    )
    business = res_b.scalars().first()
    if not business:
        raise HTTPException(status_code=400, detail="Business Profile required for match analysis")

    res_t = await db.execute(select(Tender).where(Tender.id == tender_id))
    tender = res_t.scalars().first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    tender_data = tender.extracted_json or {
        "title": tender.title,
        "tender_id": tender.tender_id_code,
        "organization": tender.organization,
        "budget": float(tender.estimated_value or 1000000.0),
        "deadline": "2026-09-30T17:00:00+05:30",
        "location": tender.location or "All India",
        "products": [tender.title],
        "eligibility": {"minimum_turnover": float(tender.estimated_value or 1000000.0) * 0.4, "msme_required": True, "gst_required": True},
        "required_documents": ["GST Registration Certificate", "MSME Udyam Certificate", "Audited Financial Statements", "Prior Experience Proof"]
    }

    # Execute Scoring & Gap Engine
    score_result = scoring_engine.calculate_match(business, tender_data)
    gap_result = gap_engine.analyze_gap(business, tender_data)

    # Save or update Match record
    res_m = await db.execute(
        select(Match)
        .where(Match.business_id == business.id, Match.tender_id == tender.id)
    )
    match_rec = res_m.scalars().first()
    if not match_rec:
        match_rec = Match(business_id=business.id, tender_id=tender.id)
        db.add(match_rec)

    match_rec.overall_score = score_result["overall_score"]
    match_rec.product_score = score_result["product_score"]
    match_rec.eligibility_score = score_result["eligibility_score"]
    match_rec.location_score = score_result["location_score"]
    match_rec.turnover_score = score_result["turnover_score"]
    match_rec.experience_score = score_result["experience_score"]
    match_rec.eligibility_status = score_result["eligibility_status"]
    match_rec.match_category = score_result["match_category"]
    match_rec.risk_level = gap_result["risk_level"]
    match_rec.readiness_percentage = gap_result["readiness_percentage"]

    await db.commit()
    await db.refresh(match_rec)

    reasons_list = [ReasonItem(category=r["category"], reason=r["reason"]) for r in score_result["reasons"]]

    return MatchResponse(
        match_id=match_rec.id,
        tender_id=tender.id,
        tender_title=tender.title,
        organization=tender.organization,
        budget=float(tender.estimated_value or 0),
        deadline=tender_data.get("deadline", "2026-09-20T17:00:00+05:30"),
        location=tender.location or "Maharashtra",
        overall_score=float(match_rec.overall_score),
        product_score=float(match_rec.product_score),
        eligibility_score=float(match_rec.eligibility_score),
        location_score=float(match_rec.location_score),
        turnover_score=float(match_rec.turnover_score),
        experience_score=float(match_rec.experience_score),
        eligibility_status=match_rec.eligibility_status,
        match_category=match_rec.match_category,
        risk_level=match_rec.risk_level,
        readiness_percentage=float(match_rec.readiness_percentage),
        reasons=reasons_list,
        missing_documents=gap_result["missing_documents"],
        available_documents=gap_result["available_documents"],
        days_remaining=gap_result["days_remaining"],
        urgency_status=gap_result["urgency_status"]
    )
