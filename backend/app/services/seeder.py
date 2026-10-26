import os
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.models import (
    User, BusinessProfile, BusinessProduct, BusinessDocument,
    Tender, Match, MatchReason, TenderRequirement, TenderProduct
)
from app.core.security import get_password_hash
from app.services.sarvam_service import SarvamVisionProvider
from app.services.tender_extractor import TenderExtractionService
from app.services.scoring_engine import ScoringEngine
from app.services.gap_engine import RequirementGapEngine

logger = logging.getLogger("seeder")

async def seed_sample_data(db: AsyncSession, force_reset: bool = True):
    if force_reset:
        from sqlalchemy import text
        await db.execute(text("DELETE FROM match_reasons"))
        await db.execute(text("DELETE FROM matches"))
        await db.execute(text("DELETE FROM tender_requirements"))
        await db.execute(text("DELETE FROM tender_products"))
        await db.execute(text("DELETE FROM tenders"))
        await db.execute(text("DELETE FROM business_documents"))
        await db.execute(text("DELETE FROM business_products"))
        await db.execute(text("DELETE FROM business_profiles"))
        await db.commit()

    # 1. Create or retrieve User
    res = await db.execute(select(User).where(User.email == "tenders@apexmodular.in"))
    user = res.scalars().first()
    if not user:
        user = User(
            email="tenders@apexmodular.in",
            hashed_password=get_password_hash("password123"),
            full_name="Rajesh Sharma (Director, Apex Modular Infrastructure)"
        )
        db.add(user)
        await db.flush()

    res_demo = await db.execute(select(User).where(User.email == "demo@abcfurniture.com"))
    if not res_demo.scalars().first():
        db.add(User(
            email="demo@abcfurniture.com",
            hashed_password=get_password_hash("password123"),
            full_name="Rajesh Sharma (Apex Modular / ABC Furniture)"
        ))
        await db.flush()

    # 2. Create or update Business Profile
    res_p = await db.execute(
        select(BusinessProfile)
        .where(BusinessProfile.user_id == user.id)
        .options(selectinload(BusinessProfile.products), selectinload(BusinessProfile.documents))
    )
    profile = res_p.scalars().first()

    if force_reset and profile:
        # Clear old products and documents to ensure updated real data
        from sqlalchemy import text
        await db.execute(text(f"DELETE FROM business_products WHERE business_id = '{profile.id}'"))
        await db.execute(text(f"DELETE FROM business_documents WHERE business_id = '{profile.id}'"))
        await db.commit()
        # Reload profile
        res_p = await db.execute(
            select(BusinessProfile)
            .where(BusinessProfile.id == profile.id)
            .options(selectinload(BusinessProfile.products), selectinload(BusinessProfile.documents))
        )
        profile = res_p.scalars().first()

    if not profile:
        profile = BusinessProfile(
            user_id=user.id,
            company_name="Apex Modular Infrastructure Pvt. Ltd.",
            business_category="Institutional Furniture, Modular Workstations & Educational Infrastructure",
            description="Empanelled MSME manufacturer registered under Udyam and Make in India initiative, specializing in high-durability school dual desks, modular IT workstations, anti-microbial healthcare couches, and precision steel storage solutions.",
            annual_turnover=6500000.0,
            is_msme_registered=True,
            msme_registration_number="UDYAM-MH-12-0048291",
            has_gst_registration=True,
            gstin="27AABCA4892F1Z4",
            state_location="Maharashtra",
            operating_regions=["Maharashtra", "Gujarat", "Goa", "Karnataka", "All India"],
            years_in_business=6,
            govt_experience_years=4,
            certifications=[
                "ISO 9001:2015 (QMS)",
                "ISO 14001:2015 (EMS)",
                "BIFMA Level-2 Compliant",
                "ZED Bronze MSME Certified",
                "Class-1 Local Supplier (>50% MII)"
            ],
            manufacturing_capacity="1,200 modular units / month from Pune industrial facility",
            contact_email="tenders@apexmodular.in",
            contact_phone="+91 98220 84721"
        )
        db.add(profile)
        await db.flush()
    else:
        # Update existing profile fields with authentic Indian MSME details
        profile.company_name = "Apex Modular Infrastructure Pvt. Ltd."
        profile.business_category = "Institutional Furniture, Modular Workstations & Educational Infrastructure"
        profile.description = "Empanelled MSME manufacturer registered under Udyam and Make in India initiative, specializing in high-durability school dual desks, modular IT workstations, anti-microbial healthcare couches, and precision steel storage solutions."
        profile.annual_turnover = 6500000.0
        profile.is_msme_registered = True
        profile.msme_registration_number = "UDYAM-MH-12-0048291"
        profile.has_gst_registration = True
        profile.gstin = "27AABCA4892F1Z4"
        profile.state_location = "Maharashtra"
        profile.operating_regions = ["Maharashtra", "Gujarat", "Goa", "Karnataka", "All India"]
        profile.years_in_business = 6
        profile.govt_experience_years = 4
        profile.certifications = [
            "ISO 9001:2015 (QMS)",
            "ISO 14001:2015 (EMS)",
            "BIFMA Level-2 Compliant",
            "ZED Bronze MSME Certified",
            "Class-1 Local Supplier (>50% MII)"
        ]
        profile.manufacturing_capacity = "1,200 modular units / month from Pune industrial facility"
        profile.contact_email = "tenders@apexmodular.in"
        profile.contact_phone = "+91 98220 84721"
        await db.flush()

    # Populate authentic Products if empty
    res_prod = await db.execute(select(BusinessProduct).where(BusinessProduct.business_id == profile.id))
    if not res_prod.scalars().all():
        products = [
            BusinessProduct(
                business_id=profile.id,
                name="School Dual Desks & Benches",
                category="Furniture",
                description="Ergonomic dual desk-cum-benches with cold rolled steel frame, prelaminated board with rounded edges, and built-in bookrack."
            ),
            BusinessProduct(
                business_id=profile.id,
                name="Student & Office Chairs",
                category="Furniture",
                description="Heavy-duty ergonomic seating with cushioned seat, mesh back, and lumbar support."
            ),
            BusinessProduct(
                business_id=profile.id,
                name="Storage Lockers & Cabinets",
                category="Furniture",
                description="CRCA steel multi-compartment storage lockers with individual key lock systems for staff and library."
            ),
            BusinessProduct(
                business_id=profile.id,
                name="IT Peripheral Tables & Workstations",
                category="Hardware",
                description="Modular computer lab workstation tables with integrated cable management raceways and CPU mounting brackets."
            ),
            BusinessProduct(
                business_id=profile.id,
                name="Heavy-Duty Perforated Steel Waiting Chairs",
                category="Furniture",
                description="Three-seater modular stainless steel perforated passenger waiting chairs with heavy-duty beam and armrests."
            ),
            BusinessProduct(
                business_id=profile.id,
                name="Modular Station Master Consoles",
                category="Furniture",
                description="Heavy-duty ergonomic duty officer workstation consoles with dual display arms and rack mounts."
            ),
            BusinessProduct(
                business_id=profile.id,
                name="Hospital Patient Examination Beds",
                category="Healthcare",
                description="Two-section hospital examination couches with hydraulic backrest elevation and washable rexine upholstery."
            ),
        ]
        db.add_all(products)
        await db.flush()

    # Populate authentic Document Locker if empty
    res_docs = await db.execute(select(BusinessDocument).where(BusinessDocument.business_id == profile.id))
    if not res_docs.scalars().all():
        documents = [
            BusinessDocument(business_id=profile.id, document_name="MSME Udyam Registration Certificate", document_type="MSME_CERTIFICATE", verification_status="AVAILABLE", issue_date="2021-04-12"),
            BusinessDocument(business_id=profile.id, document_name="GST Registration Certificate", document_type="GST_CERTIFICATE", verification_status="AVAILABLE", issue_date="2018-07-01"),
            BusinessDocument(business_id=profile.id, document_name="Audited Financial Statements (Last 2 Years)", document_type="FINANCIAL_STATEMENT", verification_status="AVAILABLE", issue_date="2025-09-30"),
            BusinessDocument(business_id=profile.id, document_name="Prior Experience / Work Order Execution Proof", document_type="EXPERIENCE_CERTIFICATE", verification_status="AVAILABLE", issue_date="2024-11-15"),
            BusinessDocument(business_id=profile.id, document_name="Copy of PAN Card", document_type="PAN_CARD", verification_status="AVAILABLE", issue_date="2018-05-10"),
            BusinessDocument(business_id=profile.id, document_name="Class-I Local Content (Make in India) Self-Declaration", document_type="DECLARATION", verification_status="AVAILABLE", issue_date="2026-01-10"),
            BusinessDocument(business_id=profile.id, document_name="ISO 9001:2015 Quality Management Certificate", document_type="CERTIFICATE", verification_status="AVAILABLE", issue_date="2023-08-20"),
            BusinessDocument(business_id=profile.id, document_name="OEM Manufacturer Authorization Form (MAF)", document_type="AUTHORIZATION", verification_status="AVAILABLE", issue_date="2026-03-01"),
            BusinessDocument(business_id=profile.id, document_name="Labour Commissioner License & EPF/ESIC Registration Proof", document_type="LABOUR_COMPLIANCE", verification_status="PENDING", issue_date=""),
            BusinessDocument(business_id=profile.id, document_name="Valid Electrical Contractor License", document_type="ELECTRICAL_LICENSE", verification_status="MISSING", issue_date=""),
        ]
        db.add_all(documents)
        await db.flush()

    # Reload profile with products and documents attached
    res_p = await db.execute(
        select(BusinessProfile)
        .where(BusinessProfile.id == profile.id)
        .options(selectinload(BusinessProfile.products), selectinload(BusinessProfile.documents))
    )
    profile = res_p.scalars().first()

    # 3. Read and process all 6 PDFs from Sample_Tender_Test_Documents
    test_docs_folder = r"d:\Download\Tender AI Assistant\Sample_Tender_Test_Documents"
    if not os.path.exists(test_docs_folder):
        test_docs_folder = os.path.abspath("Sample_Tender_Test_Documents")

    pdf_files = [
        "Sample_School_Furniture_Tender.pdf",
        "05_Railway_Modular_Furniture_Tender.pdf",
        "04_Medical_Supplies_Tender.pdf",
        "01_IT_Hardware_Tender.pdf",
        "03_Office_Cleaning_Tender.pdf",
        "02_Solar_Rooftop_Tender.pdf"
    ]

    sarvam = SarvamVisionProvider()
    extractor = TenderExtractionService()
    scoring_engine = ScoringEngine()
    gap_engine = RequirementGapEngine()

    seeded_tenders = []

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

        closing_dt = None
        if extracted.deadline:
            try:
                closing_dt = datetime.fromisoformat(extracted.deadline.replace("Z", "+00:00").split("+")[0])
            except Exception:
                pass

        tender = Tender(
            tender_id_code=extracted.tender_id,
            title=extracted.title,
            organization=extracted.organization,
            department="Procurement Division",
            tender_type="Open E-Tender (Two-Cover)",
            estimated_value=extracted.budget,
            tender_fee=2000.0,
            emd_amount=extracted.budget * 0.02,
            closing_date=closing_dt,
            location=extracted.location,
            delivery_location=extracted.location,
            raw_document_path=fpath,
            processing_status="COMPLETED",
            extracted_json=t_json
        )
        db.add(tender)
        await db.flush()

        # Add Tender Products to relational table
        for p_name in extracted.products:
            t_prod = TenderProduct(
                tender_id=tender.id,
                name=p_name,
                description=f"Specification compliant {p_name}"
            )
            db.add(t_prod)

        # Add Tender Requirements to relational table
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
        await db.flush()

        # Persist explainable AI reasons
        for r_item in score_res["reasons"]:
            db.add(MatchReason(
                match_id=match_rec.id,
                category=r_item["category"],
                reason=r_item["reason"]
            ))

        seeded_tenders.append(tender.title)

    await db.commit()
    logger.info(f"Seeded {len(seeded_tenders)} authentic tenders.")
    return {
        "message": f"Successfully seeded {len(seeded_tenders)} authentic government tenders with active deadlines, complete Indian MSME profile, and dynamic match scores!",
        "tenders": seeded_tenders
    }
