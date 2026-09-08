from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.models import Tender, ProcessingJob, TenderRequirement, TenderProduct
from app.services.storage_service import save_uploaded_file
from app.services.sarvam_service import SarvamVisionProvider
from app.services.tender_extractor import TenderExtractionService

router = APIRouter(prefix="/tenders", tags=["Tenders & Extraction"])

sarvam_provider = SarvamVisionProvider()
extractor_service = TenderExtractionService()

@router.get("")
async def list_tenders(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Tender).order_by(Tender.created_at.desc()))
    tenders = res.scalars().all()
    return tenders

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

@router.post("/upload")
async def upload_tender(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    file_path, file_hash = await save_uploaded_file(file)

    # Hash duplicate check
    res = await db.execute(select(Tender).where(Tender.file_hash == file_hash))
    existing_tender = res.scalars().first()
    if existing_tender:
        return {
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

    tender.title = extracted.title
    tender.tender_id_code = extracted.tender_id
    tender.organization = extracted.organization
    tender.estimated_value = extracted.budget
    tender.location = extracted.location
    tender.extracted_json = extracted.model_dump()
    tender.processing_status = "COMPLETED"
    
    job.status = "COMPLETED"
    job.step_details = {"step": "Intelligence Extraction & Analysis", "progress": 100}

    await db.commit()

    return {
        "tender_id": tender.id,
        "job_id": job.id,
        "status": "COMPLETED",
        "extracted_data": extracted.model_dump()
    }
