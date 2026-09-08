from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.seeder import seed_sample_data

router = APIRouter(tags=["Health & Seeder"])

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AI Tender Assistant API",
        "sarvam_vision": "configured",
        "version": "1.0.0"
    }

@router.get("/seed/sample")
@router.post("/seed/sample")
async def trigger_seed(reset: bool = True, db: AsyncSession = Depends(get_db)):
    result = await seed_sample_data(db, force_reset=reset)
    return result
