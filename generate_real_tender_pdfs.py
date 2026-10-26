import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

def create_tender_pdf(filename, title, tender_id, org, dept, budget_str, deadline_str, location, products, eligibility, req_docs, specs):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=15,
        leading=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0f2b5c'),
        spaceAfter=4,
        fontName='Helvetica-Bold'
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#334155'),
        spaceAfter=10,
        fontName='Helvetica'
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=10,
        spaceAfter=4,
        fontName='Helvetica-Bold'
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1e293b'),
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1e293b'),
        leftIndent=12,
        fontName='Helvetica'
    )
    tbl_header_style = ParagraphStyle(
        'TblHeader',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        fontName='Helvetica-Bold'
    )
    tbl_cell_style = ParagraphStyle(
        'TblCell',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1e293b'),
        fontName='Helvetica'
    )

    elements = []

    # 1. Header
    elements.append(Paragraph(org.upper(), title_style))
    elements.append(Paragraph(f"{dept} • Government of India Procurement Portal", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=10))

    # 2. Executive Summary Box
    summary_data = [
        [Paragraph("<b>Tender Title:</b>", tbl_cell_style), Paragraph(f"<b>{title}</b>", tbl_cell_style)],
        [Paragraph("<b>Tender ID / Ref No:</b>", tbl_cell_style), Paragraph(f"<font color='#0f2b5c'><b>{tender_id}</b></font>", tbl_cell_style)],
        [Paragraph("<b>Estimated Tender Value:</b>", tbl_cell_style), Paragraph(f"<b>{budget_str}</b>", tbl_cell_style)],
        [Paragraph("<b>Submission Deadline:</b>", tbl_cell_style), Paragraph(f"<font color='#b91c1c'><b>{deadline_str}</b></font>", tbl_cell_style)],
        [Paragraph("<b>Delivery Location:</b>", tbl_cell_style), Paragraph(location, tbl_cell_style)],
        [Paragraph("<b>Tender Fee & EMD:</b>", tbl_cell_style), Paragraph("Tender Fee: ₹2,000 | EMD: 2% of Tender Value (100% Exemption for registered MSME/Udyam enterprises under Rule 170 of GFR 2017)", tbl_cell_style)]
    ]
    summary_table = Table(summary_data, colWidths=[140, 390])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 12))

    # 3. Scope of Work / Procurement Items
    elements.append(Paragraph("1. Scope of Work and Schedule of Items", section_heading))
    elements.append(Paragraph("Bids are invited under Two-Cover Electronic Tender System from competent, eligible manufacturers and authorized suppliers for the supply, testing, delivery, and warranty maintenance of the following items:", body_style))
    elements.append(Spacer(1, 4))

    prod_rows = [[Paragraph("<b>S.No</b>", tbl_header_style), Paragraph("<b>Item Name & Description</b>", tbl_header_style), Paragraph("<b>Quantity / Scope</b>", tbl_header_style)]]
    for idx, p in enumerate(products, 1):
        prod_rows.append([
            Paragraph(str(idx), tbl_cell_style),
            Paragraph(f"<b>Supply of {p['name']}</b>: {p.get('desc', 'As per detailed technical specifications')}", tbl_cell_style),
            Paragraph(p.get('qty', 'As per BoQ'), tbl_cell_style)
        ])
    prod_table = Table(prod_rows, colWidths=[35, 395, 100])
    prod_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(prod_table)
    elements.append(Spacer(1, 12))

    # 4. Mandatory Eligibility Criteria
    elements.append(Paragraph("2. Mandatory Eligibility Criteria for Bidders", section_heading))
    elements.append(Paragraph("Bidders must strictly satisfy all the following technical and commercial qualifying conditions:", body_style))
    elements.append(Spacer(1, 4))

    for el in eligibility:
        elements.append(Paragraph(f"• <b>{el['title']}:</b> {el['text']}", bullet_style))
        elements.append(Spacer(1, 2))
    elements.append(Spacer(1, 8))

    # 5. Required Submission Documents Checklist
    elements.append(Paragraph("3. Technical Cover Checklist (Mandatory Submission Documents)", section_heading))
    elements.append(Paragraph("The bid submission must include the following verified documents scanned in PDF format:", body_style))
    elements.append(Spacer(1, 4))

    for doc_item in req_docs:
        elements.append(Paragraph(f"• <b>[DOC]</b> {doc_item}", bullet_style))
        elements.append(Spacer(1, 2))
    elements.append(Spacer(1, 8))

    # 6. Technical Specifications & Warranty
    elements.append(Paragraph("4. Technical Specifications & Quality Assurance", section_heading))
    for spec_k, spec_v in specs.items():
        elements.append(Paragraph(f"• <b>{spec_k}:</b> {spec_v}", bullet_style))
        elements.append(Spacer(1, 2))
    elements.append(Spacer(1, 10))

    # 7. Terms & Closing Notes
    elements.append(Paragraph("5. General Terms, Public Procurement Policy & Dispute Resolution", section_heading))
    elements.append(Paragraph(
        "Bidders registered as Micro and Small Enterprises (MSEs) under Udyam Registration are entitled to procurement preferences "
        "as per Public Procurement Policy for MSEs Order 2012, including exemption from payment of Earnest Money Deposit (EMD) and tender fee. "
        "Class-I Local Suppliers (having minimum 50% local content) shall receive purchase preference as per DPIIT Make in India Policy. "
        "Late submissions past the declared submission deadline will be automatically rejected by the electronic portal.",
        body_style
    ))
    elements.append(Spacer(1, 14))

    # Signature Block
    sig_data = [
        [Paragraph("Issued by:", tbl_cell_style), Paragraph("Authorized by:", tbl_cell_style)],
        [Paragraph(f"<b>Procurement Cell</b><br/>{org}", tbl_cell_style), Paragraph("<b>Superintending Procurement Officer</b><br/>Competent Authority, Govt of India", tbl_cell_style)]
    ]
    sig_table = Table(sig_data, colWidths=[265, 265])
    sig_table.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(sig_table)

    doc.build(elements)
    print(f"Generated: {filename}")

if __name__ == "__main__":
    out_dir = r"d:\Download\Tender AI Assistant\Sample_Tender_Test_Documents"

    # Tender 1: School Furniture (Kendriya Vidyalaya Sangathan)
    create_tender_pdf(
        filename=os.path.join(out_dir, "Sample_School_Furniture_Tender.pdf"),
        title="Supply, Assembly and Placement of School Furniture, Classroom Dual Desks, and Library Fixtures",
        tender_id="KVS-FURN-2026-041",
        org="Kendriya Vidyalaya Sangathan",
        dept="Regional Procurement Cell, Western Region, Mumbai",
        budget_str="₹ 34,50,000 (Rupees Thirty Four Lakhs Fifty Thousand Only)",
        deadline_str="15 November 2026, 17:00 IST",
        location="Maharashtra",
        products=[
            {"name": "School Dual Desks & Benches", "desc": "Ergonomic dual desk-cum-benches with cold rolled steel frame, prelaminated particle board top with rounded safety edges, and built-in bookrack.", "qty": "650 Sets"},
            {"name": "Student & Office Chairs", "desc": "Heavy-duty ergonomic seating with cushioned seat, mesh back, and lumbar support.", "qty": "120 Units"},
            {"name": "Storage Lockers & Cabinets", "desc": "CRCA steel multi-compartment storage lockers with individual key lock systems for staff and library.", "qty": "45 Units"},
            {"name": "IT Peripheral Tables", "desc": "Modular computer lab workstation tables with integrated cable management raceways and CPU mounting brackets.", "qty": "80 Units"}
        ],
        eligibility=[
            {"title": "MSME Registration", "text": "Bidder must possess valid MSME Udyam Registration Certificate in furniture/manufacturing sector. MSME purchase preference applicable."},
            {"title": "GST Registration", "text": "Bidder must possess active GST Registration in Maharashtra (GSTIN prefix 27) with clean compliance record."},
            {"title": "Minimum Annual Turnover", "text": "Minimum average annual turnover of ₹ 12.0 Lakhs in the preceding three financial years certified by a Chartered Accountant with UDIN."},
            {"title": "Past Experience", "text": "Minimum 2 years prior experience in supplying institutional furniture or classroom equipment to educational institutions or government departments."},
            {"title": "Delivery Region", "text": "Bidders must be capable of direct delivery and installation across regional schools in Maharashtra."}
        ],
        req_docs=[
            "GST Registration Certificate",
            "MSME Udyam Registration Certificate",
            "Audited Financial Statements (Last 2 Years)",
            "Prior Experience / Work Order Execution Proof",
            "Copy of PAN Card",
            "Class-I Local Content (Make in India) Self-Declaration"
        ],
        specs={
            "Design & Durability": "Furniture manufactured conforming to BIS/IS standard specifications for institutional furniture.",
            "Warranty Period": "Comprehensive 36-month onsite replacement warranty on steel frames and 24-month on wooden/prelam components.",
            "Material Quality": "Pre-laminated boards of minimum 18mm thickness with 2mm PVC edge banding; CRCA pipes of 16-gauge thickness."
        }
    )

    # Tender 2: IT Hardware & Workstations (NIT Karnataka)
    create_tender_pdf(
        filename=os.path.join(out_dir, "01_IT_Hardware_Tender.pdf"),
        title="Procurement of Desktop Computers, Workstations, Interactive Flat Panels and UPS Peripherals",
        tender_id="HE-IT-2026-118",
        org="Department of Higher Education & Technical Learning",
        dept="National Institute of Technology Karnataka & State Colleges Cell",
        budget_str="₹ 48,50,000 (Rupees Forty Eight Lakhs Fifty Thousand Only)",
        deadline_str="18 November 2026, 17:00 IST",
        location="All India",
        products=[
            {"name": "IT Peripheral Tables & Workstations", "desc": "Heavy-duty lab computer workstation tables with cable managers, monitor mounts, and keyboard drawers.", "qty": "150 Units"},
            {"name": "Desktop Computers & Workstation Units", "desc": "Intel Core i7 14th Gen or equivalent desktop workstations, 32GB RAM, 1TB NVMe SSD with Windows 11 Pro.", "qty": "60 Units"},
            {"name": "Interactive Flat Panel Displays", "desc": "75-inch 4K UHD Interactive Flat Panels with multi-touch stylus support for smart lecture halls.", "qty": "15 Units"},
            {"name": "Online UPS Systems", "desc": "10 kVA 3-phase online UPS systems with 30-minute full load SMF battery backup bank.", "qty": "4 Units"}
        ],
        eligibility=[
            {"title": "MSME Registration", "text": "Valid MSME Udyam Registration under IT hardware or institutional supplies. MSE preference applies."},
            {"title": "GST Compliance", "text": "Bidder must possess active GST Registration with timely GSTR-3B filings."},
            {"title": "Minimum Annual Turnover", "text": "Minimum average annual turnover of ₹ 18.0 Lakhs during the last three financial years."},
            {"title": "Past Experience", "text": "Minimum 2 years experience in IT hardware, college labs, or institutional workstation deployments."},
            {"title": "OEM Authorization", "text": "Manufacturer Authorization Form (MAF) required for active electronic components."}
        ],
        req_docs=[
            "GST Registration Certificate",
            "MSME Udyam Registration Certificate",
            "Audited Financial Statements (Last 2 Years)",
            "Prior Experience / Work Order Execution Proof",
            "Copy of PAN Card",
            "OEM Manufacturer Authorization Form (MAF)"
        ],
        specs={
            "System Performance": "All desktop units must be Energy Star 8.0 compliant and RoHs certified.",
            "Warranty & Onsite Support": "3-Year comprehensive next business day (NBD) onsite warranty across all delivered hardware."
        }
    )

    # Tender 3: Rooftop Solar PV Systems (Renewable Energy Agency)
    create_tender_pdf(
        filename=os.path.join(out_dir, "02_Solar_Rooftop_Tender.pdf"),
        title="Design, Supply, Testing and Installation of Grid-Connected Rooftop Solar PV Power Systems",
        tender_id="REDA-SOLAR-2026-072",
        org="Government Renewable Energy Development Agency",
        dept="State Solar & Clean Energy Mission, Administrative Complex",
        budget_str="₹ 78,00,000 (Rupees Seventy Eight Lakhs Only)",
        deadline_str="30 October 2026, 17:00 IST",
        location="Maharashtra",
        products=[
            {"name": "Solar PV Modules", "desc": "Mono-crystalline PERC solar PV modules with minimum 540Wp capacity, ALMM approved.", "qty": "320 Panels"},
            {"name": "On-Grid Solar Inverters", "desc": "50 kVA three-phase string solar inverters with remote web telemetry and MPPT tracking.", "qty": "3 Units"},
            {"name": "Mounting Structures & Cable Trays", "desc": "Hot-dip galvanized mounting structures engineered to withstand 150 km/h wind loads.", "qty": "Complete Set"},
            {"name": "Electrical Protection & Balance of Plant", "desc": "ACDB/DCDB boxes, SPD surge protection, lightning arresters, and chemical earthing electrodes.", "qty": "Complete Set"}
        ],
        eligibility=[
            {"title": "MSME Registration", "text": "MSME Udyam registered enterprises are eligible for EMD exemption and tender fee waiver."},
            {"title": "GST Registration", "text": "Active GST registration mandatory."},
            {"title": "Minimum Annual Turnover", "text": "Mandatory average annual turnover of at least ₹ 30.0 Lakhs in the last 3 financial years."},
            {"title": "Solar Experience", "text": "Minimum 3 years past experience in execution and commissioning of grid-tied rooftop solar power projects."},
            {"title": "MNRE / Electrical License", "text": "Valid Electrical Contractor License from State Government and MNRE approved module list compliance."}
        ],
        req_docs=[
            "GST Registration Certificate",
            "MSME Udyam Registration Certificate",
            "Audited Financial Statements (Last 2 Years)",
            "Prior Experience / Work Order Execution Proof",
            "Copy of PAN Card",
            "Valid Electrical Contractor License"
        ],
        specs={
            "Module Warranty": "25-year linear power output performance warranty on solar PV modules.",
            "Inverter Warranty": "10-year comprehensive manufacturer replacement warranty on solar inverters."
        }
    )

    # Tender 4: Facility Cleaning & Housekeeping (District Collectorate)
    create_tender_pdf(
        filename=os.path.join(out_dir, "03_Office_Cleaning_Tender.pdf"),
        title="Annual Rate Contract for Comprehensive Facility Cleaning, Mechanized Housekeeping & Sanitization Services",
        tender_id="DC-HSK-2026-031",
        org="District Collectorate Administration",
        dept="General Administration & Estate Maintenance Cell",
        budget_str="₹ 22,50,000 (Rupees Twenty Two Lakhs Fifty Thousand Only)",
        deadline_str="25 November 2026, 16:00 IST",
        location="Maharashtra",
        products=[
            {"name": "Mechanized Floor Scrubbing & Deep Cleaning", "desc": "Daily mechanized wet scrubbing, sweeping, and buffing of administrative building floors.", "qty": "Annual Service"},
            {"name": "Eco-Friendly Cleaning Consumables", "desc": "Supply of biodegradable floor cleaners, disinfectant concentrates, microfiber mops, and trash liners.", "qty": "Monthly Supply"},
            {"name": "Waste Segregation & Sanitation Bins", "desc": "Color-coded heavy duty HDPE pedal dustbins for wet, dry, and sanitary waste segregation.", "qty": "120 Units"},
            {"name": "High-Pressure Facade & Washroom Cleaning", "desc": "Scheduled high-pressure steam cleaning of sanitization blocks and glass facades.", "qty": "Quarterly Service"}
        ],
        eligibility=[
            {"title": "MSME Registration", "text": "MSME registered service providers receive standard preference."},
            {"title": "GST Compliance", "text": "Active GSTIN registered in Maharashtra."},
            {"title": "Minimum Annual Turnover", "text": "Minimum average annual turnover of ₹ 9.0 Lakhs in the last three financial years."},
            {"title": "Past Experience", "text": "Minimum 2 years experience in providing facility management, commercial housekeeping or cleaning services."},
            {"title": "Labour & Statutory Compliance", "text": "Valid Labour License under Contract Labour Act, active EPF and ESIC registrations."}
        ],
        req_docs=[
            "GST Registration Certificate",
            "MSME Udyam Registration Certificate",
            "Audited Financial Statements (Last 2 Years)",
            "Prior Experience / Work Order Execution Proof",
            "Copy of PAN Card",
            "Labour Commissioner License & EPF/ESIC Registration Proof"
        ],
        specs={
            "Quality Compliance": "ISO 9001 certified housekeeping service protocol; usage of certified eco-friendly GreenSeal cleaning solutions.",
            "Manpower Standards": "All deployed personnel must be in uniform with photo identity badges and basic security clearance."
        }
    )

    # Tender 5: Medical Equipment & Hospital Beds (District Government Hospital)
    create_tender_pdf(
        filename=os.path.join(out_dir, "04_Medical_Supplies_Tender.pdf"),
        title="Procurement of Patient Examination Couches, Hospital Ward Beds, and Anti-Microbial Medical Furniture",
        tender_id="DGH-MED-2026-209",
        org="District Government Hospital Procurement Cell",
        dept="Civil Hospital & Medical College Administration",
        budget_str="₹ 58,00,000 (Rupees Fifty Eight Lakhs Only)",
        deadline_str="05 November 2026, 14:00 IST",
        location="Maharashtra",
        products=[
            {"name": "Hospital Patient Examination Beds", "desc": "Two-section hospital examination couches with hydraulic backrest elevation and washable rexine upholstery.", "qty": "110 Beds"},
            {"name": "Stainless Steel Medical Trolleys", "desc": "Grade 304 stainless steel two-shelf dressing and medicine distribution trolleys with anti-static swivel castors.", "qty": "75 Units"},
            {"name": "Storage Lockers & Cabinets", "desc": "Anti-microbial epoxy powder-coated medicine cabinets with dual glass doors and safety lock.", "qty": "40 Units"},
            {"name": "Student & Office Chairs", "desc": "Ergonomic doctor consultation chairs and heavy-duty visitor seating benches with anti-bacterial coating.", "qty": "160 Units"}
        ],
        eligibility=[
            {"title": "MSME Registration", "text": "MSME Udyam registered medical furniture manufacturers/suppliers eligible for EMD exemption."},
            {"title": "GST Registration", "text": "Mandatory active GSTIN registration in India."},
            {"title": "Minimum Annual Turnover", "text": "Minimum average annual turnover of ₹ 20.0 Lakhs in the preceding three financial years."},
            {"title": "Past Experience", "text": "Minimum 2 years experience in supplying hospital furniture or medical equipment to govt/private hospitals."},
            {"title": "Quality Certification", "text": "ISO 9001 or ISO 13485 (Medical Device QMS) certification required."}
        ],
        req_docs=[
            "GST Registration Certificate",
            "MSME Udyam Registration Certificate",
            "Audited Financial Statements (Last 2 Years)",
            "Prior Experience / Work Order Execution Proof",
            "Copy of PAN Card",
            "ISO 9001 or ISO 13485 Quality Certificate"
        ],
        specs={
            "Hygiene & Finish": "All medical contact surfaces must have anti-fungal and anti-bacterial epoxy coating resistant to medical disinfectants.",
            "Warranty": "3-Year comprehensive replacement warranty on mechanical mechanisms and frames."
        }
    )

    # Tender 6: Railway Station Modular Furniture & Waiting Chairs (Western Railway)
    create_tender_pdf(
        filename=os.path.join(out_dir, "05_Railway_Modular_Furniture_Tender.pdf"),
        title="Supply, Delivery and Placement of Heavy-Duty Perforated Steel Waiting Chairs and Station Consoles",
        tender_id="RAIL-WR-2026-INFRA-318",
        org="Western Railway Administration",
        dept="Office of Principal Chief Materials Manager, Western Railway HQ, Mumbai",
        budget_str="₹ 52,00,000 (Rupees Fifty Two Lakhs Only)",
        deadline_str="12 November 2026, 15:00 IST",
        location="Maharashtra",
        products=[
            {"name": "Heavy-Duty Perforated Steel Waiting Chairs", "desc": "Three-seater modular stainless steel perforated passenger waiting chairs with heavy-duty beam and armrests.", "qty": "350 Sets"},
            {"name": "Modular Station Master Consoles", "desc": "Heavy-duty ergonomic duty officer workstation consoles with dual display arms and rack mounts.", "qty": "40 Units"},
            {"name": "Storage Lockers & Cabinets", "desc": "Heavy gauge steel record filing cabinets and locker units with three-point locking mechanism.", "qty": "60 Units"},
            {"name": "IT Peripheral Tables", "desc": "Ticketing counter tables and computer workstations with cable grommets.", "qty": "50 Units"}
        ],
        eligibility=[
            {"title": "MSME Registration", "text": "MSME registered enterprises entitled to purchase preference and 100% EMD exemption as per Railway Board guidelines."},
            {"title": "GST Registration", "text": "Mandatory active GST registration in India."},
            {"title": "Minimum Annual Turnover", "text": "Minimum average annual turnover of ₹ 20.0 Lakhs during the preceding three financial years."},
            {"title": "Past Experience", "text": "Minimum 2 years experience in manufacturing or supplying steel furniture, transit seating or institutional consoles."},
            {"title": "Make in India Policy", "text": "Class-I Local Supplier (minimum 50% local content) mandatory under Public Procurement Policy."}
        ],
        req_docs=[
            "GST Registration Certificate",
            "MSME Udyam Registration Certificate",
            "Audited Financial Statements (Last 2 Years)",
            "Prior Experience / Work Order Execution Proof",
            "Copy of PAN Card",
            "Class-I Local Content (Make in India) Self-Declaration"
        ],
        specs={
            "Material Specifications": "Stainless steel grade 202/304 perforated sheet minimum 1.5mm thickness with anti-rust electrophoretic coating.",
            "Warranty": "Comprehensive 36-month onsite warranty for transit and high-traffic use."
        }
    )

    print("All 6 Authentic Tender Documents generated successfully!")

