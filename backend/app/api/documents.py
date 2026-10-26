from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.models import BusinessProfile, BusinessDocument
from app.schemas.schemas import BusinessDocumentResponse, BusinessDocumentCreate, BusinessDocumentUpdate
from app.services.storage_service import save_uploaded_file

router = APIRouter(prefix="/documents", tags=["Business Document Locker"])

@router.get("", response_model=list[BusinessDocumentResponse])
async def list_documents(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(BusinessDocument).order_by(BusinessDocument.created_at.asc()))
    docs = res.scalars().all()
    return [BusinessDocumentResponse.model_validate(d) for d in docs]

@router.post("", response_model=BusinessDocumentResponse)
async def create_document(doc_in: BusinessDocumentCreate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(BusinessProfile))
    profile = res.scalars().first()
    if not profile:
        raise HTTPException(status_code=400, detail="Create business profile before adding documents")

    new_doc = BusinessDocument(
        business_id=profile.id,
        document_name=doc_in.document_name,
        document_type=doc_in.document_type,
        verification_status=doc_in.verification_status or "AVAILABLE",
        issue_date=doc_in.issue_date or ""
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    return BusinessDocumentResponse.model_validate(new_doc)

@router.post("/upload", response_model=BusinessDocumentResponse)
async def upload_document(
    document_name: str = Form(...),
    document_type: str = Form(...),
    issue_date: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(BusinessProfile))
    profile = res.scalars().first()
    if not profile:
        raise HTTPException(status_code=400, detail="Create business profile before uploading documents")

    file_path, file_hash = await save_uploaded_file(file)

    # Check if a document with same name/type exists to update or insert
    res_existing = await db.execute(
        select(BusinessDocument).where(
            BusinessDocument.business_id == profile.id,
            BusinessDocument.document_name == document_name
        )
    )
    existing_doc = res_existing.scalars().first()
    if existing_doc:
        existing_doc.file_path = file_path
        existing_doc.verification_status = "AVAILABLE"
        if issue_date:
            existing_doc.issue_date = issue_date
        await db.commit()
        await db.refresh(existing_doc)
        return BusinessDocumentResponse.model_validate(existing_doc)

    new_doc = BusinessDocument(
        business_id=profile.id,
        document_name=document_name,
        document_type=document_type,
        file_path=file_path,
        issue_date=issue_date or "",
        verification_status="AVAILABLE"
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    return BusinessDocumentResponse.model_validate(new_doc)

@router.put("/{document_id}", response_model=BusinessDocumentResponse)
async def update_document(
    document_id: str,
    doc_update: BusinessDocumentUpdate,
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(BusinessDocument).where(BusinessDocument.id == document_id))
    doc = res.scalars().first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    update_dict = doc_update.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        if val is not None:
            setattr(doc, field, val)

    await db.commit()
    await db.refresh(doc)
    return BusinessDocumentResponse.model_validate(doc)

@router.delete("/{document_id}")
async def delete_document(document_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(BusinessDocument).where(BusinessDocument.id == document_id))
    doc = res.scalars().first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    await db.delete(doc)
    await db.commit()
    return {"message": "Document removed from locker successfully"}
