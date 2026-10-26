from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.models import Tender, ProcessingJob, TenderRequirement, TenderProduct
from app.services.storage_service import save_uploaded_file
from app.services.sarvam_service import SarvamVisionProvider
from app.services.tender_extractor import TenderExtractionService

from app.models.models import Tender, ProcessingJob, TenderRequirement, TenderProduct, BusinessProfile, Match

router = APIRouter(prefix="/tenders", tags=["Tenders & Extraction"])

sarvam_provider = SarvamVisionProvider()
extractor_service = TenderExtractionService()

@router.get("")
async def list_tenders(db: AsyncSession = Depends(get_db)):
    # Retrieve business profile to associate match scores
    res_b = await db.execute(select(BusinessProfile))
    business = res_b.scalars().first()

    res = await db.execute(select(Tender).order_by(Tender.created_at.desc()))
    tenders = res.scalars().all()

    # Also fetch all matches for this business
    matches_dict = {}
    if business:
        res_m = await db.execute(select(Match).where(Match.business_id == business.id))
        for m in res_m.scalars().all():
            matches_dict[m.tender_id] = m

    tender_list = []
    for t in tenders:
        m = matches_dict.get(t.id)
        # Parse closing date from closing_date or extracted_json
        closing_iso = None
        if t.closing_date:
            closing_iso = t.closing_date.isoformat()
        elif t.extracted_json and t.extracted_json.get("deadline"):
            closing_iso = t.extracted_json.get("deadline")

        t_dict = {
            "id": t.id,
            "tender_id_code": t.tender_id_code,
            "title": t.title,
            "organization": t.organization,
            "department": t.department,
            "tender_type": t.tender_type,
            "estimated_value": float(t.estimated_value or 0),
            "tender_fee": float(t.tender_fee or 0),
            "emd_amount": float(t.emd_amount or 0),
            "location": t.location,
            "delivery_location": t.delivery_location,
            "processing_status": t.processing_status,
            "closing_date": closing_iso,
            "match_score": float(m.overall_score) if m else None,
            "eligibility_status": m.eligibility_status if m else "UNKNOWN",
            "risk_level": m.risk_level if m else "UNKNOWN",
            "match_category": m.match_category if m else "UNKNOWN",
            "readiness_percentage": float(m.readiness_percentage) if m else 0.0,
            "extracted_json": t.extracted_json,
            "created_at": t.created_at.isoformat() if t.created_at else None
        }
        tender_list.append(t_dict)
    return tender_list

@router.get("/{tender_id}")
async def get_tender_details(tender_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(Tender)
        .where(Tender.id == tender_id)
        .options(selectinload(Tender.requirements), selectinload(Tender.products))
    )
    tender = res.scalars().first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    return tender

@router.get("/{tender_id}/status")
async def get_tender_status(tender_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Tender).where(Tender.id == tender_id))
    tender = res.scalars().first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    res_job = await db.execute(select(ProcessingJob).where(ProcessingJob.tender_id == tender_id).order_by(ProcessingJob.created_at.desc()))
    job = res_job.scalars().first()

    return {
        "tender_id": tender.id,
        "status": tender.processing_status,
        "job_status": job.status if job else tender.processing_status,
        "step_details": job.step_details if job else {"step": "Completed", "progress": 100}
    }

@router.post("/upload")
async def upload_tender(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    from datetime import datetime
    from app.models.models import Match, MatchReason
    from app.services.scoring_engine import ScoringEngine
    from app.services.gap_engine import RequirementGapEngine

    file_path, file_hash = await save_uploaded_file(file)

    # Hash duplicate check
    res = await db.execute(select(Tender).where(Tender.file_hash == file_hash))
    existing_tender = res.scalars().first()
    if existing_tender:
        return {
            "id": existing_tender.id,
            "tender_id": existing_tender.id,
            "status": "COMPLETED",
            "message": "Duplicate document detected via hash. Previous analysis loaded."
        }

    tender = Tender(
        tender_id_code="TENDER-UPLOADED",
        title=file.filename or "Uploaded Tender Document",
        raw_document_path=file_path,
        file_hash=file_hash,
        processing_status="PROCESSING"
    )
    db.add(tender)
    await db.flush()

    job = ProcessingJob(
        tender_id=tender.id,
        status="PROCESSING",
        step_details={"step": "Sarvam Vision OCR Ingestion", "progress": 25}
    )
    db.add(job)
    await db.commit()

    # Trigger Extraction Process
    raw_ocr = await sarvam_provider.process_document(file_path)
    extracted = await extractor_service.extract_structured_tender(file_path, raw_ocr)
    t_json = extracted.model_dump()

    tender.title = extracted.title
    tender.tender_id_code = extracted.tender_id
    tender.organization = extracted.organization
    tender.estimated_value = extracted.budget
    tender.location = extracted.location
    tender.extracted_json = t_json
    tender.processing_status = "COMPLETED"

    if extracted.deadline:
        try:
            tender.closing_date = datetime.fromisoformat(extracted.deadline.replace("Z", "+00:00").split("+")[0])
        except Exception:
            pass
    
    job.status = "COMPLETED"
    job.step_details = {"step": "Intelligence Extraction & Analysis", "progress": 100}

    # Populate Tender Products
    for p_name in extracted.products:
        db.add(TenderProduct(
            tender_id=tender.id,
            name=p_name,
            description=f"Specification compliant {p_name}"
        ))

    # Populate Tender Requirements
    t_reqs = [
        TenderRequirement(
            tender_id=tender.id,
            requirement_type="TURNOVER",
            is_mandatory=True,
            description=f"Minimum Average Annual Turnover of ₹{extracted.eligibility.minimum_turnover/100000:.1f} Lakhs",
            threshold_value=extracted.eligibility.minimum_turnover,
            source_section="Mandatory Eligibility Criteria"
        ),
        TenderRequirement(
            tender_id=tender.id,
            requirement_type="MSME",
            is_mandatory=extracted.eligibility.msme_required,
            description="Valid MSME Udyam Registration Certificate under Public Procurement Policy",
            source_section="MSME Policy & EMD Exemption"
        ),
        TenderRequirement(
            tender_id=tender.id,
            requirement_type="GST",
            is_mandatory=extracted.eligibility.gst_required,
            description="Active GSTIN Registration Certificate with regular filing record",
            source_section="Tax & Statutory Compliance"
        ),
        TenderRequirement(
            tender_id=tender.id,
            requirement_type="EXPERIENCE",
            is_mandatory=True,
            description=f"Minimum {extracted.eligibility.min_experience_years} years past supply experience to Government / PSUs",
            threshold_value=extracted.eligibility.min_experience_years,
            source_section="Technical Qualification"
        )
    ]
    db.add_all(t_reqs)

    # Perform instant matching against business profile
    res_b = await db.execute(
        select(BusinessProfile)
        .options(selectinload(BusinessProfile.products), selectinload(BusinessProfile.documents))
    )
    business = res_b.scalars().first()
    if business:
        sc_engine = ScoringEngine()
        g_engine = RequirementGapEngine()
        score_res = sc_engine.calculate_match(business, t_json)
        gap_res = g_engine.analyze_gap(business, t_json)

        match_rec = Match(
            business_id=business.id,
            tender_id=tender.id,
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
        db.add(match_rec)
        await db.flush()

        for r_item in score_res.get("reasons", []):
            db.add(MatchReason(
                match_id=match_rec.id,
                category=r_item["category"],
                reason=r_item["reason"]
            ))

    await db.commit()

    return {
        "id": tender.id,
        "tender_id": tender.id,
        "job_id": job.id,
        "status": "COMPLETED",
        "extracted_data": t_json
    }
