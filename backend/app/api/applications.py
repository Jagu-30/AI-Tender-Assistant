from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.models import BusinessProfile, Match, Tender, GeneratedApplication
from app.schemas.schemas import ApplicationGenerateRequest, GeneratedApplicationResponse
from app.services.application_service import ApplicationAssistantService

router = APIRouter(prefix="/applications", tags=["Application Assistant"])

app_service = ApplicationAssistantService()

@router.post("/generate", response_model=GeneratedApplicationResponse)
@router.post("/cover-letter")
@router.post("/declaration")
@router.post("/technical-response")
async def generate_application(req: ApplicationGenerateRequest, db: AsyncSession = Depends(get_db)):
    res_m = await db.execute(select(Match).where(Match.id == req.match_id))
    match = res_m.scalars().first()
    if not match:
        # Fallback to search match by tender_id if match_id was tender_id
        res_m2 = await db.execute(select(Match).where(Match.tender_id == req.tender_id))
        match = res_m2.scalars().first()

    if not match:
        res_b = await db.execute(select(BusinessProfile).options(selectinload(BusinessProfile.products), selectinload(BusinessProfile.documents)))
        business = res_b.scalars().first()
        res_t = await db.execute(select(Tender).where(Tender.id == req.tender_id))
        tender = res_t.scalars().first()

        if business and tender:
            from app.services.scoring_engine import ScoringEngine
            from app.services.gap_engine import RequirementGapEngine
            sc_engine = ScoringEngine()
            g_engine = RequirementGapEngine()
            
            tender_data = tender.extracted_json or {"title": tender.title, "budget": float(tender.estimated_value or 0)}
            score_res = sc_engine.calculate_match(business, tender_data)
            gap_res = g_engine.analyze_gap(business, tender_data)

            match = Match(
                business_id=business.id,
                tender_id=req.tender_id,
                overall_score=score_res["overall_score"],
                product_score=score_res["product_score"],
                eligibility_score=score_res["eligibility_score"],
                location_score=score_res["location_score"],
                turnover_score=score_res["turnover_score"],
                experience_score=score_res["experience_score"],
                eligibility_status=score_res["eligibility_status"],
                match_category=score_res["match_category"],
                risk_level=gap_res["risk_level"],
                readiness_percentage=gap_res["readiness_percentage"]
            )
            db.add(match)
            await db.commit()
            await db.refresh(match)
        else:
            raise HTTPException(status_code=400, detail="Valid business profile and tender required")

    res_b = await db.execute(select(BusinessProfile).where(BusinessProfile.id == match.business_id))
    business = res_b.scalars().first()

    res_t = await db.execute(select(Tender).where(Tender.id == match.tender_id))
    tender = res_t.scalars().first()

    package = app_service.generate_application_package(business, tender, match)

    res_app = await db.execute(select(GeneratedApplication).where(GeneratedApplication.match_id == match.id))
    app_rec = res_app.scalars().first()
    if not app_rec:
        app_rec = GeneratedApplication(
            match_id=match.id,
            user_id=business.user_id if business else "demo-user"
        )
        db.add(app_rec)

    app_rec.cover_letter_content = package["cover_letter_content"]
    app_rec.declaration_content = package["declaration_content"]
    app_rec.technical_response_content = package["technical_response_content"]
    app_rec.document_checklist = package["document_checklist"]

    await db.commit()
    await db.refresh(app_rec)

    return GeneratedApplicationResponse(
        id=app_rec.id,
        match_id=app_rec.match_id,
        cover_letter_content=app_rec.cover_letter_content,
        declaration_content=app_rec.declaration_content,
        technical_response_content=app_rec.technical_response_content,
        document_checklist=app_rec.document_checklist,
        is_edited=app_rec.is_edited
    )

@router.get("/{app_id}", response_model=GeneratedApplicationResponse)
async def get_application(app_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(GeneratedApplication).where(GeneratedApplication.id == app_id))
    app_rec = res.scalars().first()
    if not app_rec:
        raise HTTPException(status_code=404, detail="Application not found")
    return GeneratedApplicationResponse.model_validate(app_rec)
