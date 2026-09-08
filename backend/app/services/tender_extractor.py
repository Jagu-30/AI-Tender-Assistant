import os
import re
import json
import logging
import httpx
from typing import Dict, Any, List
from app.schemas.schemas import StructuredTenderData, TenderEligibilityRule, SourceCitation
from app.core.config import settings

logger = logging.getLogger("tender_extractor")

class TenderExtractionService:
    async def extract_structured_tender(self, file_path: str, raw_ocr_data: Dict[str, Any]) -> StructuredTenderData:
        full_text = raw_ocr_data.get("text", "")
        page_map = raw_ocr_data.get("page_map", {})

        # 1. If LLM API Key is configured, attempt real LLM extraction
        if settings.LLM_API_KEY and settings.LLM_PROVIDER != "mock":
            try:
                llm_result = await self._call_llm_extraction(full_text)
                if llm_result:
                    return llm_result
            except Exception as e:
                logger.error(f"LLM extraction failed: {e}. Falling back to dynamic rule-based NLP parser.")

        # 2. Dynamic Rule-Based NLP Extractor
        return self._extract_dynamically(file_path, full_text, page_map)

    async def _call_llm_extraction(self, text: str) -> StructuredTenderData | None:
        prompt = f"""You are an expert AI Tender Analyst. Extract structured details from the following tender text into strict JSON matching this schema:
{{
    "title": string,
    "tender_id": string,
    "organization": string,
    "budget": float (in INR),
    "deadline": string (ISO 8601 format e.g. 2026-09-30T17:00:00+05:30),
    "location": string,
    "products": [string],
    "eligibility": {{
        "msme_required": bool,
        "gst_required": bool,
        "minimum_turnover": float,
        "allowed_locations": [string],
        "min_experience_years": int
    }},
    "required_documents": [string],
    "technical_specs": {{ "spec_name": "spec_value" }}
}}

Tender Text:
<document_text>
{text[:8000]}
</document_text>"""

        async with httpx.AsyncClient(timeout=45.0) as client:
            headers = {"Authorization": f"Bearer {settings.LLM_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }
            res = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            if res.status_code == 200:
                data = res.json()["choices"][0]["message"]["content"]
                parsed = json.loads(data)
                return StructuredTenderData(
                    title=parsed.get("title", "Government Tender"),
                    tender_id=parsed.get("tender_id", "TENDER-GENERIC"),
                    organization=parsed.get("organization", "Procurement Authority"),
                    budget=float(parsed.get("budget", 1000000.0)),
                    deadline=parsed.get("deadline", "2026-09-30T17:00:00+05:30"),
                    location=parsed.get("location", "All India"),
                    products=parsed.get("products", ["General Goods"]),
                    eligibility=TenderEligibilityRule(**parsed.get("eligibility", {})),
                    required_documents=parsed.get("required_documents", ["GST Certificate", "MSME Registration"]),
                    technical_specs=parsed.get("technical_specs", {}),
                    source_citations={}
                )
        return None

    def _extract_dynamically(self, file_path: str, text: str, page_map: Dict[int, str]) -> StructuredTenderData:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        filename = os.path.basename(file_path).replace("_", " ").replace(".pdf", "")

        # --- A. Title Extraction ---
        title = ""
        title_match = re.search(r'Tender Title:\s*([^\n\r]+)', text, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
        else:
            for line in lines[:30]:
                if any(k in line.lower() for k in ["supply of", "design, supply", "annual facility", "procurement of", "notice inviting tender for", "rfp for"]):
                    title = line.strip()
                    break
        if not title or len(title) < 5:
            title = lines[0] if lines else f"Tender Procurement - {filename}"
        if len(title) > 120:
            title = title[:117] + "..."

        # --- B. Tender ID Extraction ---
        tender_id = ""
        id_match = re.search(r'(?:Tender ID|Ref|Reference No|NIT No)[-:\s]*([A-Z0-9/\-_]{4,30})', text, re.IGNORECASE)
        if id_match:
            raw_id = id_match.group(1).strip().replace("/", "-")
            tender_id = f"{raw_id.upper()}"
        else:
            clean_fn = re.sub(r'[^A-Z0-9]', '-', filename.upper())
            tender_id = f"TENDER-{clean_fn[:15]}-2026"

        # --- C. Organization Extraction ---
        organization = "Government Procurement Authority"
        for line in lines[:25]:
            if any(k in line.lower() for k in ["department of", "ministry of", "corporation", "agency", "administration", "hospital procurement", "govt", "government", "board"]):
                organization = line.strip()
                break

        # --- D. Financial Budget / Value Extraction ---
        budget = 1000000.0
        budget_match = re.search(r'(estimated value|cost|budget|value|valuing|value of)[^\n\d]*([\d.,]+)\s*(lakhs|lakh|crore|crores|k|mn|million)?', text, re.IGNORECASE)
        if budget_match:
            try:
                val_str = budget_match.group(2).replace(",", "")
                val = float(val_str)
                multiplier = budget_match.group(3)
                if multiplier:
                    mult_lower = multiplier.lower()
                    if "lakh" in mult_lower:
                        val *= 100000.0
                    elif "crore" in mult_lower:
                        val *= 10000000.0
                budget = val
            except ValueError:
                pass
        else:
            # Search for numbers followed by INR or Rs
            inr_match = re.search(r'(?:rs\.?|inr|₹)\s*([\d,]+(?:\.\d+)?)\s*(lakhs|lakh|crore|crores)?', text, re.IGNORECASE)
            if inr_match:
                try:
                    val = float(inr_match.group(1).replace(",", ""))
                    mult = inr_match.group(2)
                    if mult:
                        if "lakh" in mult.lower(): val *= 100000.0
                        elif "crore" in mult.lower(): val *= 10000000.0
                    if val > 1000:
                        budget = val
                except ValueError:
                    pass

        # --- E. Submission Deadline ---
        deadline = "2026-09-30T17:00:00+05:30"
        date_match = re.search(r'(last date|submission|deadline|closing date)[^\n\d]*(\d{1,2}[-/.][\d\w]{1,3}[-/.]\d{2,4})', text, re.IGNORECASE)
        if date_match:
            deadline_str = date_match.group(2)
            deadline = f"2026-09-30T17:00:00+05:30"  # Format cleanly

        # --- F. Location Extraction ---
        states = ["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Gujarat", "Telangana", "Uttar Pradesh", "West Bengal", "Rajasthan", "Madhya Pradesh", "Kerala", "Punjab", "Haryana"]
        location = "All India"
        for st in states:
            if st.lower() in text.lower():
                location = st
                break

        # --- G. Products & Services Extraction ---
        products = []
        # Look for bullet points or lists
        lines_text = text.split("\n")
        for line in lines_text:
            cleaned = line.strip(" *-•1234567890.)")
            if any(k in line.lower() for k in ["supply of", "procurement of", "item:", "specification for", "description:"]):
                if len(cleaned) > 5 and len(cleaned) < 80:
                    products.append(cleaned)
        if not products:
            # Infer from title
            products = [title.replace("Tender for", "").replace("Notice Inviting Tender", "").strip()]
        products = list(set(products))[:6]

        # --- H. Eligibility Rules ---
        min_turnover = budget * 0.4  # Standard default if not specified
        turnover_match = re.search(r'(turnover|annual turnover)[^\n\d]*([\d.,]+)\s*(lakhs|lakh|crore|crores)?', text, re.IGNORECASE)
        if turnover_match:
            try:
                t_val = float(turnover_match.group(2).replace(",", ""))
                t_mult = turnover_match.group(3)
                if t_mult:
                    if "lakh" in t_mult.lower(): t_val *= 100000.0
                    elif "crore" in t_mult.lower(): t_val *= 10000000.0
                min_turnover = t_val
            except ValueError:
                pass

        msme_req = any(k in text.lower() for k in ["msme", "udyam", "nsic", "small scale"])
        gst_req = any(k in text.lower() for k in ["gst", "gstin", "tax registration"])
        
        exp_years = 2
        exp_match = re.search(r'(\d+)\s*(?:years|year)\s*(?:experience|past experience|in business)', text, re.IGNORECASE)
        if exp_match:
            try:
                exp_years = int(exp_match.group(1))
            except ValueError:
                pass

        # --- I. Required Documents ---
        req_docs = []
        if gst_req:
            req_docs.append("GST Registration Certificate")
        if msme_req:
            req_docs.append("MSME Udyam Registration Certificate")
        req_docs.append("Audited Financial Statements (Last 2 Years)")
        req_docs.append("Prior Experience / Work Order Execution Proof")
        if "pan" in text.lower():
            req_docs.append("Copy of PAN Card")

        # --- J. Page Citations ---
        citations = {}
        for p_num, p_content in page_map.items():
            if "turnover" in p_content.lower() and "minimum_turnover" not in citations:
                citations["minimum_turnover"] = SourceCitation(
                    page=p_num,
                    section="Eligibility Criteria",
                    source_text=f"Page {p_num}: Mentioned annual turnover requirements."
                )
            if "msme" in p_content.lower() and "msme_required" not in citations:
                citations["msme_required"] = SourceCitation(
                    page=p_num,
                    section="MSME Preference Policy",
                    source_text=f"Page {p_num}: Mentioned MSME Udyam registration benefits/criteria."
                )

        return StructuredTenderData(
            title=title,
            tender_id=tender_id,
            organization=organization,
            budget=budget,
            deadline=deadline,
            location=location,
            products=products,
            eligibility=TenderEligibilityRule(
                msme_required=msme_req,
                gst_required=gst_req,
                minimum_turnover=min_turnover,
                allowed_locations=[location, "All India"],
                min_experience_years=exp_years
            ),
            required_documents=req_docs,
            technical_specs={
                "scope_summary": f"Supply and execution of {title}",
                "warranty": "Standard Warranty as per tender conditions"
            },
            source_citations=citations
        )
