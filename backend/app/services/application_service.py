from typing import Dict, Any
from app.models.models import BusinessProfile, Match, Tender

class ApplicationAssistantService:
    def generate_application_package(self, business: BusinessProfile, tender: Tender, match: Match) -> Dict[str, Any]:
        company_name = business.company_name or "[REQUIRED INFORMATION]"
        gstin = business.gstin if business.has_gst_registration else "[REQUIRED INFORMATION - GSTIN]"
        msme_num = business.msme_registration_number if business.is_msme_registered else "[REQUIRED INFORMATION - MSME REGISTRATION]"
        turnover = f"₹{float(business.annual_turnover or 0)/100000:.1f} Lakh" if business.annual_turnover else "[REQUIRED INFORMATION - TURNOVER]"
        
        tender_title = tender.title
        tender_id = tender.tender_id_code
        org = tender.organization or "Purchasing Organization"

        cover_letter = f'''COVER LETTER FOR TENDER SUBMISSION

To,
The Tendering Authority,
{org}

Ref: Submission of Bid for {tender_title} (Tender ID: {tender_id})

Respected Sir/Madam,

We, {company_name}, hereby submit our technical and financial bid for the tender referenced above.
As an established enterprise operating in {business.state_location or 'India'}, we meet the required capabilities and specifications detailed in the tender notification.

Key Qualification Parameters:
- Entity Name: {company_name}
- MSME Status: {'Registered (' + msme_num + ')' if business.is_msme_registered else 'Not Registered'}
- GSTIN: {gstin}
- Certified Turnover: {turnover}

We confirm our full compliance with all technical requirements, supply timelines, and warranty terms.

Yours faithfully,
For {company_name}

Authorized Signatory
Name: [AUTHORIZED SIGNATORY NAME]
Designation: [DESIGNATION]
Contact: {business.contact_phone or '[PHONE]'} | Email: {business.contact_email or '[EMAIL]'}'''

        declaration = f'''FORMAL TENDER DECLARATION

I/We, the undersigned, authorized representative of M/s {company_name}, solemnly declare that:
1. All information, documents, and credentials submitted in this bid for Tender ID {tender_id} are true, genuine, and valid.
2. Our firm is not blacklisted, debarred, or banned by any Central/State Government department or Public Sector Undertaking.
3. We abide by all terms and conditions, legal covenants, and technical specifications prescribed in the Tender Document.
4. Active GSTIN: {gstin} | MSME Udyam Registration: {msme_num}

Date: [SUBMISSION DATE]
Place: {business.state_location or '[CITY/STATE]'}

(Signature & Company Seal)'''

        extracted_data = tender.extracted_json or {}
        tender_products = extracted_data.get("products", [])
        if not tender_products:
            tender_products = [tender.title]

        compliance_lines = []
        for idx, prod in enumerate(tender_products, 1):
            compliance_lines.append(f"- Item {idx}: {prod} -> Fully compliant with specified technical parameters and quality standards.")
        compliance_matrix_str = "\n".join(compliance_lines)

        tech_response = f'''TECHNICAL COMPLIANCE STATEMENT & MATRIX

Project: {tender_title}
Tender Ref: {tender_id}
Bidder: {company_name}

1. Business Overview:
{company_name} specializes in {business.business_category or 'Manufacturing & Supply Services'}. Description: {business.description or 'Certified supplier and solution provider'}.

2. Product Compliance Matrix:
{compliance_matrix_str}

3. Delivery & Warranty:
- Delivery Location: {tender.delivery_location or tender.location or 'As specified in tender'}
- Warranty & Support: Standard Onsite Warranty & Technical Support provided as per tender conditions.'''

        required_docs = extracted_data.get("required_documents", [
            "GST Registration Certificate",
            "MSME Udyam Certificate",
            "Audited Financial Statements",
            "Prior Experience Certificate"
        ])

        checklist = []
        for doc_name in required_docs:
            doc_lower = doc_name.lower()
            status = "AVAILABLE"
            if "gst" in doc_lower and not business.has_gst_registration:
                status = "MISSING"
            elif "msme" in doc_lower and not business.is_msme_registered:
                status = "MISSING"
            elif "financial" in doc_lower and not business.annual_turnover:
                status = "MISSING"
            
            checklist.append({"document": doc_name, "required": True, "status": status})

        return {
            "cover_letter_content": cover_letter,
            "declaration_content": declaration,
            "technical_response_content": tech_response,
            "document_checklist": checklist
        }
