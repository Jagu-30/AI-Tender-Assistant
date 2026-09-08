import re
from typing import List, Tuple

class SemanticMatchingEngine:
    def compute_product_similarity(self, business_products: List[str], tender_products: List[str]) -> Tuple[float, List[str]]:
        if not business_products or not tender_products:
            return 50.0, ["No catalog products to match against tender items."]

        matches_found = []
        total_score = 0.0

        for t_item in tender_products:
            t_words = set(re.findall(r'\w+', t_item.lower()))
            best_sim = 0.0
            best_matched_b_item = ""

            for b_item in business_products:
                b_words = set(re.findall(r'\w+', b_item.lower()))
                if not t_words or not b_words:
                    continue
                
                intersection = t_words.intersection(b_words)
                union = t_words.union(b_words)
                jaccard = len(intersection) / len(union) if union else 0.0
                
                # Check stem & substring matches for domain-agnostic bonus
                stem_matches = 0
                for tw in t_words:
                    if len(tw) > 3 and any(tw[:4] in bw for bw in b_words):
                        stem_matches += 1
                stem_bonus = (stem_matches / len(t_words)) * 0.3 if t_words else 0.0

                sim = min(1.0, jaccard + stem_bonus)
                if sim > best_sim:
                    best_sim = sim
                    best_matched_b_item = b_item

            if best_sim > 0.25:
                total_score += best_sim
                matches_found.append(f"Matched '{t_item}' with business product catalog item '{best_matched_b_item}' ({int(best_sim*100)}% match).")
            else:
                matches_found.append(f"Partial match for '{t_item}'.")

        avg_score = (total_score / len(tender_products)) * 100.0 if tender_products else 0.0
        normalized_score = min(100.0, max(10.0, avg_score))

        return round(normalized_score, 1), matches_found
