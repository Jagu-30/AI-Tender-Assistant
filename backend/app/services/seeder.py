import os
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import User, BusinessProfile, BusinessProduct, BusinessDocument, Tender, Match, TenderRequirement
from app.core.security import get_password_hash
from app.services.sarvam_service import SarvamVisionProvider
from app.services.tender_extractor import TenderExtractionService
from app.services.scoring_engine import ScoringEngine
from app.services.gap_engine import RequirementGapEngine

logger = logging.getLogger("seeder")

async def seed_sample_data(db: AsyncSession, force_reset: bool = True):
    if force_reset:
        from sqlalchemy import text
        await db.execute(text("DELETE FROM matches"))
        await db.execute(text("DELETE FROM tender_requirements"))
        await db.execute(text("DELETE FROM tender_products"))
        await db.execute(text("DELETE FROM tenders"))
        await db.commit()
    else:
        res_t = await db.execute(select(Tender))
        tenders_count = len(res_t.scalars().all())
        if tenders_count >= 5:
            return {"message": "Sample data already seeded with 5 real tenders."}

    # 1. Create or retrieve User
    res = await db.execute(select(User).where(User.email == "demo@abcfurniture.com"))
    user = res.scalars().first()
    if not user:
        user = User(
            email="demo@abcfurniture.com",
            hashed_password=get_password_hash("password123"),
            full_name="Rajesh Sharma (Apex Enterprises)"
        )
        db.add(user)
        await db.flush()

    # 2. Create or retrieve Business Profile
    from sqlalchemy.orm import selectinload
    res_p = await db.execute(
        select(BusinessProfile)
        .where(BusinessProfile.user_id == user.id)
        .options(selectinload(BusinessProfile.products), selectinload(BusinessProfile.documents))
    )
    profile = res_p.scalars().first()
    if not profile:
        profile = BusinessProfile(
            user_id=user.id,
            company_name="Apex MSME Supplies Pvt. Ltd.",
            business_category="Institutional Furniture & General Contractor",
            description="Established MSME manufacturer and contractor supplying institutional furniture, office equipment, and infrastructure supplies.",
            annual_turnover=5000000.0,
            is_msme_registered=True,
            msme_registration_number="UDYAM-MH-12-0098765",
            has_gst_registration=True,
            gstin="27AABCA1234F1Z5",
            state_location="Maharashtra",
            operating_regions=["Maharashtra", "Goa", "Gujarat"],
            years_in_business=5,
            govt_experience_years=3,
            certifications=["ISO 9001:2015", "ISO 14001"],
            manufacturing_capacity="500 units per month",
            contact_email="contact@apexmsme.com",
            contact_phone="+91 98200 12345"
        )
        db.add(profile)
        await db.flush()

        products = [
            BusinessProduct(business_id=profile.id, name="Desks & Benches", category="Furniture", description="School dual desks, benches, and office tables"),
            BusinessProduct(business_id=profile.id, name="Student & Office Chairs", category="Furniture", description="Ergonomic chairs and seating"),
            BusinessProduct(business_id=profile.id, name="Storage Lockers & Cabinets", category="Furniture", description="Metal lockers and wooden storage cabinets"),
            BusinessProduct(business_id=profile.id, name="IT Peripheral Tables", category="Hardware", description="Computer tables and workstation desks")
        ]
        db.add_all(products)

        documents = [
            BusinessDocument(business_id=profile.id, document_name="GST Registration Certificate", document_type="GST_CERTIFICATE", verification_status="AVAILABLE"),
            BusinessDocument(business_id=profile.id, document_name="MSME Udyam Registration Certificate", document_type="MSME_CERTIFICATE", verification_status="AVAILABLE"),
            BusinessDocument(business_id=profile.id, document_name="Audited Financial Statements (Last 2 Years)", document_type="FINANCIAL_STATEMENT", verification_status="AVAILABLE")
        ]
        db.add_all(documents)
        await db.flush()

        res_p = await db.execute(
            select(BusinessProfile)
            .where(BusinessProfile.id == profile.id)
            .options(selectinload(BusinessProfile.products), selectinload(BusinessProfile.documents))
        )
        profile = res_p.scalars().first()

    # 3. Read and process all 5 PDFs from Sample_Tender_Test_Documents
    test_docs_folder = r"d:\Download\Tender AI Assistant\Sample_Tender_Test_Documents"
    if not os.path.exists(test_docs_folder):
        test_docs_folder = os.path.abspath("Sample_Tender_Test_Documents")

    pdf_files = [
        "01_IT_Hardware_Tender.pdf",
        "02_Solar_Rooftop_Tender.pdf",
        "03_Office_Cleaning_Tender.pdf",
        "04_Medical_Supplies_Tender.pdf",
        "Sample_School_Furniture_Tender.pdf"
    ]

    sarvam = SarvamVisionProvider()
    extractor = TenderExtractionService()
    scoring_engine = ScoringEngine()
    gap_engine = RequirementGapEngine()

    for pdf_name in pdf_files:
        fpath = os.path.join(test_docs_folder, pdf_name)
        if not os.path.exists(fpath):
            continue

        raw_ocr = await sarvam.process_document(fpath)
        extracted = await extractor.extract_structured_tender(fpath, raw_ocr)
        t_json = extracted.model_dump()

        # Check if tender already exists in DB
        res_ex = await db.execute(select(Tender).where(Tender.tender_id_code == extracted.tender_id))
        existing_t = res_ex.scalars().first()
        if existing_t:
            continue

        tender = Tender(
            tender_id_code=extracted.tender_id,
            title=extracted.title,
            organization=extracted.organization,
            department="Procurement Division",
            tender_type="Open E-Tender",
            estimated_value=extracted.budget,
            tender_fee=5000.0,
            emd_amount=extracted.budget * 0.02,
            location=extracted.location,
            processing_status="COMPLETED",
            extracted_json=t_json
        )
        db.add(tender)
        await db.flush()

        # Compute dynamic match score and risk matrix against profile
        score_res = scoring_engine.calculate_match(profile, t_json)
        gap_res = gap_engine.analyze_gap(profile, t_json)

        match_rec = Match(
            business_id=profile.id,
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

    await db.commit()
    return {"message": "Seeded 5 real tender PDFs from Sample_Tender_Test_Documents with real dynamic evaluation scores!"}
