from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.models import BusinessProfile, BusinessDocument
from app.schemas.schemas import BusinessDocumentResponse
from app.services.storage_service import save_uploaded_file

router = APIRouter(prefix="/documents", tags=["Business Document Locker"])

@router.get("", response_model=list[BusinessDocumentResponse])
async def list_documents(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(BusinessDocument))
    docs = res.scalars().all()
    return [BusinessDocumentResponse.model_validate(d) for d in docs]

@router.post("/upload", response_model=BusinessDocumentResponse)
async def upload_document(
    document_name: str = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(BusinessProfile))
    profile = res.scalars().first()
    if not profile:
        raise HTTPException(status_code=400, detail="Create business profile before uploading documents")

    file_path, file_hash = await save_uploaded_file(file)

    new_doc = BusinessDocument(
        business_id=profile.id,
        document_name=document_name,
        document_type=document_type,
        file_path=file_path,
        verification_status="AVAILABLE"
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    return BusinessDocumentResponse.model_validate(new_doc)
