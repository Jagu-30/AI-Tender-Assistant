from typing import Dict, Any
from app.services.eligibility_engine import EligibilityEngine
from app.services.embedding_service import SemanticMatchingEngine
from app.models.models import BusinessProfile

class ScoringEngine:
    def __init__(self):
        self.eligibility_engine = EligibilityEngine()
        self.matching_engine = SemanticMatchingEngine()

    def calculate_match(self, business: BusinessProfile, tender_data: Dict[str, Any]) -> Dict[str, Any]:
        eligibility_info = tender_data.get("eligibility", {})
        tender_products = tender_data.get("products", [])

        # 1. Product Score (30%)
        bus_product_names = [p.name for p in business.products] if business.products else ["Desks", "Chairs", "Tables", "Cabinets"]
        product_score, product_reasons = self.matching_engine.compute_product_similarity(bus_product_names, tender_products)

        # 2. Eligibility Evaluation (30%)
        el_result = self.eligibility_engine.evaluate(business, eligibility_info)
        eligibility_score = el_result["score"]
        eligibility_status = el_result["status"]

        # 3. Turnover Score (15%)
        min_turnover = float(eligibility_info.get("minimum_turnover", 0.0))
        bus_turnover = float(business.annual_turnover or 0.0)
        if min_turnover == 0 or bus_turnover >= min_turnover:
            turnover_score = 100.0
        else:
            turnover_score = round((bus_turnover / min_turnover) * 100.0, 1)

        # 4. Location Score (10%)
        bus_state = business.state_location or "Maharashtra"
        tender_loc = tender_data.get("location", "Maharashtra")
        location_score = 100.0 if (tender_loc in bus_state or bus_state in tender_loc or "All India" in tender_loc) else 75.0

        # 5. Experience Score (15%)
        min_exp = eligibility_info.get("min_experience_years", 0)
        bus_exp = business.govt_experience_years or business.years_in_business or 1
        experience_score = 100.0 if bus_exp >= min_exp else 50.0

        # Formula calculation
        final_score = (
            (product_score * 0.30) +
            (eligibility_score * 0.30) +
            (location_score * 0.10) +
            (turnover_score * 0.15) +
            (experience_score * 0.15)
        )
        final_score = round(final_score, 1)

        # Match Category Thresholds
        if final_score >= 90.0:
            match_category = "STRONG_MATCH"
        elif final_score >= 75.0:
            match_category = "GOOD_MATCH"
        elif final_score >= 60.0:
            match_category = "PARTIAL_MATCH"
        else:
            match_category = "LOW_MATCH"

        all_reasons = el_result["reasons"]
        for pr in product_reasons:
            all_reasons.append({"category": "MATCHED", "reason": pr})

        return {
            "overall_score": final_score,
            "product_score": product_score,
            "eligibility_score": eligibility_score,
            "location_score": location_score,
            "turnover_score": turnover_score,
            "experience_score": experience_score,
            "eligibility_status": eligibility_status,
            "match_category": match_category,
            "reasons": all_reasons
        }
