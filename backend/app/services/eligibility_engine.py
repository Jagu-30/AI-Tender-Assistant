from typing import Dict, Any
from app.models.models import BusinessProfile

class EligibilityEngine:
    def evaluate(self, business: BusinessProfile, tender_eligibility: Dict[str, Any]) -> Dict[str, Any]:
        reasons = []
        is_eligible = True
        failed_count = 0

        # 1. Turnover Check
        min_turnover = float(tender_eligibility.get("minimum_turnover", 0.0))
        bus_turnover = float(business.annual_turnover or 0.0)
        
        if min_turnover > 0:
            if bus_turnover >= min_turnover:
                reasons.append({
                    "category": "MATCHED",
                    "reason": f"Turnover Requirement Satisfied: Business turnover (₹{bus_turnover/100000:.1f} Lakh) meets or exceeds minimum required (₹{min_turnover/100000:.1f} Lakh)."
                })
            else:
                is_eligible = False
                failed_count += 1
                reasons.append({
                    "category": "FAILED",
                    "reason": f"Turnover Failure: Business turnover (₹{bus_turnover/100000:.1f} Lakh) is below mandatory minimum required (₹{min_turnover/100000:.1f} Lakh)."
                })

        # 2. MSME Requirement Check
        msme_req = tender_eligibility.get("msme_required", False)
        if msme_req:
            if business.is_msme_registered:
                reasons.append({
                    "category": "MATCHED",
                    "reason": "MSME Status Verified: Valid MSME Udyam registration available."
                })
            else:
                is_eligible = False
                failed_count += 1
                reasons.append({
                    "category": "FAILED",
                    "reason": "MSME Failure: Tender specifies mandatory MSME registration, but profile indicates unregistered."
                })

        # 3. GST Requirement Check
        gst_req = tender_eligibility.get("gst_required", True)
        if gst_req:
            if business.has_gst_registration:
                reasons.append({
                    "category": "MATCHED",
                    "reason": "GST Registration Verified: Active GSTIN available."
                })
            else:
                is_eligible = False
                failed_count += 1
                reasons.append({
                    "category": "FAILED",
                    "reason": "GST Failure: Active GST registration is required."
                })

        # 4. Location Check
        allowed_locations = tender_eligibility.get("allowed_locations", [])
        if allowed_locations:
            bus_state = business.state_location or ""
            op_regions = business.operating_regions or []
            if "All India" in allowed_locations or bus_state in allowed_locations or any(r in allowed_locations for r in op_regions):
                reasons.append({
                    "category": "MATCHED",
                    "reason": f"Location Verified: Business operating location ({bus_state}) aligns with tender delivery region."
                })
            else:
                reasons.append({
                    "category": "WARNING",
                    "reason": f"Location Preference Warning: Tender prefers {allowed_locations}, business primary state is {bus_state}."
                })

        # 5. Experience Check
        min_exp = tender_eligibility.get("min_experience_years", 0)
        bus_exp = business.govt_experience_years or business.years_in_business or 0
        if min_exp > 0:
            if bus_exp >= min_exp:
                reasons.append({
                    "category": "MATCHED",
                    "reason": f"Experience Satisfied: {bus_exp} years experience satisfies minimum required ({min_exp} years)."
                })
            else:
                reasons.append({
                    "category": "WARNING",
                    "reason": f"Experience Gap: Tender asks for {min_exp} years prior supply experience; business profile lists {bus_exp} years. Documentary proof required."
                })

        status = "ELIGIBLE" if is_eligible else "NOT_ELIGIBLE"
        score = 100.0 if is_eligible else max(0.0, 100.0 - (failed_count * 50.0))

        return {
            "status": status,
            "score": score,
            "reasons": reasons
        }
