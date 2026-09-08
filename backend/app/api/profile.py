from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.models import BusinessProfile, BusinessProduct, BusinessDocument, User
from app.schemas.schemas import BusinessProfileCreate, BusinessProfileResponse, BusinessProductCreate, BusinessProductResponse, BusinessDocumentCreate, BusinessDocumentResponse

router = APIRouter(prefix="/business", tags=["Business Profile"])

@router.get("/profile", response_model=BusinessProfileResponse)
async def get_profile(db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(BusinessProfile)
        .options(selectinload(BusinessProfile.products), selectinload(BusinessProfile.documents))
    )
    profile = res.scalars().first()
    if not profile:
        # Auto-create demo profile if none exists
        res_u = await db.execute(select(User))
        user = res_u.scalars().first()
        uid = user.id if user else "demo-user-id"
        
        profile = BusinessProfile(
            user_id=uid,
            company_name="ABC Furniture Pvt. Ltd.",
            business_category="Furniture Manufacturer",
            description="Manufacturer of high quality institutional furniture",
            annual_turnover=5000000.0,
            is_msme_registered=True,
            msme_registration_number="UDYAM-MH-12-0098765",
            has_gst_registration=True,
            gstin="27AABCA1234F1Z5",
            state_location="Maharashtra",
            operating_regions=["Maharashtra", "Goa"],
            years_in_business=5,
            govt_experience_years=3
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        
        # Load products & docs
        res = await db.execute(
            select(BusinessProfile)
            .where(BusinessProfile.id == profile.id)
            .options(selectinload(BusinessProfile.products), selectinload(BusinessProfile.documents))
        )
        profile = res.scalars().first()

    return BusinessProfileResponse.model_validate(profile)

@router.post("/profile", response_model=BusinessProfileResponse)
@router.put("/profile", response_model=BusinessProfileResponse)
async def save_profile(profile_in: BusinessProfileCreate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(BusinessProfile))
    profile = res.scalars().first()
    
    if not profile:
        profile = BusinessProfile(user_id="demo-user-id", **profile_in.model_dump())
        db.add(profile)
    else:
        for k, v in profile_in.model_dump().items():
            setattr(profile, k, v)

    await db.commit()
    await db.refresh(profile)
    
    res_full = await db.execute(
        select(BusinessProfile)
        .where(BusinessProfile.id == profile.id)
        .options(selectinload(BusinessProfile.products), selectinload(BusinessProfile.documents))
    )
    return BusinessProfileResponse.model_validate(res_full.scalars().first())

@router.get("/products", response_model=list[BusinessProductResponse])
async def list_products(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(BusinessProduct))
    prods = res.scalars().all()
    return [BusinessProductResponse.model_validate(p) for p in prods]

@router.post("/products", response_model=BusinessProductResponse)
async def add_product(prod_in: BusinessProductCreate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(BusinessProfile))
    profile = res.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Business Profile not found")

    new_prod = BusinessProduct(business_id=profile.id, **prod_in.model_dump())
    db.add(new_prod)
    await db.commit()
    await db.refresh(new_prod)
    return BusinessProductResponse.model_validate(new_prod)

@router.delete("/products/{product_id}")
async def delete_product(product_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(BusinessProduct).where(BusinessProduct.id == product_id))
    prod = res.scalars().first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    await db.delete(prod)
    await db.commit()
    return {"message": "Product removed successfully"}
