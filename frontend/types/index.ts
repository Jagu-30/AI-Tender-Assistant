export interface BusinessProfile {
  id: string;
  company_name: string;
  business_category: string;
  description: string;
  annual_turnover: number;
  is_msme_registered: boolean;
  msme_registration_number?: string;
  has_gst_registration: boolean;
  gstin?: string;
  state_location: string;
  operating_regions: string[];
  years_in_business: number;
  govt_experience_years: number;
  certifications: string[];
  manufacturing_capacity?: string;
  contact_email?: string;
  contact_phone?: string;
}

export interface BusinessProduct {
  id: string;
  business_id: string;
  name: string;
  category?: string;
  description?: string;
}

export interface BusinessDocument {
  id: string;
  business_id: string;
  document_name: string;
  document_type: "GST_CERTIFICATE" | "MSME_CERTIFICATE" | "FINANCIAL_STATEMENT" | "EXPERIENCE_CERTIFICATE" | "OTHER";
  verification_status: "AVAILABLE" | "MISSING" | "PENDING" | "UNKNOWN";
  issue_date?: string;
}

export interface TenderRequirement {
  id: string;
  requirement_type: string;
  is_mandatory: boolean;
  description: string;
  threshold_value?: number;
  source_page?: number;
  source_section?: string;
  source_text?: string;
}

export interface Tender {
  id: string;
  tender_id_code: string;
  title: string;
  organization: string;
  department?: string;
  tender_type?: string;
  estimated_value: number;
  tender_fee?: number;
  emd_amount?: number;
  issue_date?: string;
  closing_date?: string;
  location: string;
  processing_status: "UPLOADED" | "PROCESSING" | "EXTRACTING" | "ANALYZING" | "MATCHING" | "COMPLETED" | "FAILED";
  extracted_json?: any;
}

export interface MatchResult {
  id: string;
  business_id: string;
  tender_id: string;
  overall_score: number;
  product_score: number;
  eligibility_score: number;
  location_score: number;
  turnover_score: number;
  experience_score: number;
  eligibility_status: "ELIGIBLE" | "NOT_ELIGIBLE" | "PARTIALLY_ELIGIBLE" | "UNKNOWN";
  match_category: "STRONG_MATCH" | "GOOD_MATCH" | "PARTIAL_MATCH" | "LOW_MATCH";
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  readiness_percentage: number;
  reasons: {
    category: "MATCHED" | "FAILED" | "MISSING" | "WARNING";
    reason: string;
    source_citation?: { page?: number; section?: string };
  }[];
}

export interface ApplicationPackage {
  id: string;
  match_id: string;
  cover_letter: string;
  declaration: string;
  technical_response: string;
  checklist: { document_name: string; is_required: boolean; status: string }[];
}
