from datetime import datetime
import pytz
from typing import Dict, Any
from app.models.models import BusinessProfile

class RequirementGapEngine:
    def analyze_gap(self, business: BusinessProfile, tender_data: Dict[str, Any]) -> Dict[str, Any]:
        required_docs = tender_data.get("required_documents", [])
        
        uploaded_doc_types = set()
        if business.documents:
            uploaded_doc_types = {d.document_type for d in business.documents if d.verification_status == "AVAILABLE"}

        available_docs = []
        missing_docs = []

        doc_type_keywords = {
            "gst": "GST_CERTIFICATE",
            "msme": "MSME_CERTIFICATE",
            "turnover": "FINANCIAL_STATEMENT",
            "financial": "FINANCIAL_STATEMENT",
            "experience": "EXPERIENCE_CERTIFICATE"
        }

        for req in required_docs:
            req_lower = req.lower()
            matched = False
            for kw, dtype in doc_type_keywords.items():
                if kw in req_lower and dtype in uploaded_doc_types:
                    available_docs.append(req)
                    matched = True
                    break
            if not matched:
                if "gst" in req_lower and business.has_gst_registration:
                    available_docs.append(req)
                elif "msme" in req_lower and business.is_msme_registered:
                    available_docs.append(req)
                else:
                    missing_docs.append(req)

        total_req_count = len(required_docs) if required_docs else 1
        readiness_pct = round((len(available_docs) / total_req_count) * 100.0, 1)

        risk_level = "LOW"
        risk_reasons = []

        if missing_docs:
            risk_level = "MEDIUM"
            risk_reasons.append(f"Missing {len(missing_docs)} required submission document(s): {', '.join(missing_docs[:2])}")
        
        if float(business.annual_turnover or 0) < float(tender_data.get("eligibility", {}).get("minimum_turnover", 0)):
            risk_level = "HIGH"
            risk_reasons.append("Mandatory minimum turnover criteria is not satisfied.")

        kolkata_tz = pytz.timezone("Asia/Kolkata")
        now_kolkata = datetime.now(kolkata_tz)
        
        days_remaining = 18
        urgency_status = "SAFE"

        deadline_str = tender_data.get("deadline")
        if deadline_str:
            try:
                deadline_dt = datetime.fromisoformat(deadline_str.replace("Z", "+00:00"))
                if deadline_dt.tzinfo is None:
                    deadline_dt = kolkata_tz.localize(deadline_dt)
                else:
                    deadline_dt = deadline_dt.astimezone(kolkata_tz)
                
                diff = (deadline_dt - now_kolkata).days
                days_remaining = max(0, diff)
            except Exception:
                pass

        if days_remaining <= 2:
            urgency_status = "URGENT"
        elif days_remaining <= 7:
            urgency_status = "ATTENTION"
        else:
            urgency_status = "SAFE"

        return {
            "readiness_percentage": readiness_pct,
            "available_documents": available_docs,
            "missing_documents": missing_docs,
            "risk_level": risk_level,
            "risk_reasons": risk_reasons,
            "days_remaining": days_remaining,
            "urgency_status": urgency_status
        }
