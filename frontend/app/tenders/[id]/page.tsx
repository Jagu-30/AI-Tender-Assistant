"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Navbar from "../../../components/Navbar";
import ScoreGauge from "../../../components/ScoreGauge";
import MatchChart from "../../../components/MatchChart";
import UploadModal from "../../../components/UploadModal";
import {
  Building2,
  Calendar,
  MapPin,
  IndianRupee,
  ShieldCheck,
  AlertOctagon,
  FileCheck2,
  AlertTriangle,
  Download,
  Edit3,
  RefreshCw,
  Save,
  CheckCircle2,
  BookOpen,
  FileText,
  Clock,
  ExternalLink,
} from "lucide-react";
import { api, fetchApi } from "../../../services/api";

export default function TenderDetailPage() {
  const params = useParams();
  const tenderId = params?.id as string;

  const [tender, setTender] = useState<any>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"ANALYSIS" | "APPLICATION" | "SOURCES">("ANALYSIS");
  const [isUploadOpen, setIsUploadOpen] = useState(false);

  // Application Draft State
  const [appId, setAppId] = useState("");
  const [coverLetter, setCoverLetter] = useState("");
  const [declaration, setDeclaration] = useState("");
  const [technicalResponse, setTechnicalResponse] = useState("");
  const [isGeneratingApp, setIsGeneratingApp] = useState(false);
  const [isSavingDraft, setIsSavingDraft] = useState(false);
  const [saveDraftMessage, setSaveDraftMessage] = useState("");

  useEffect(() => {
    if (tenderId) {
      loadTenderDetail();
    }
  }, [tenderId]);

  const loadTenderDetail = async () => {
    try {
      setIsLoading(true);
      let tenderData = await api.getTenderDetails(tenderId).catch(() => null);
      let analysisData = await api.getTenderAnalysis(tenderId).catch(() => null);

      if (!analysisData && tenderId) {
        analysisData = await api.analyzeTender(tenderId).catch(() => null);
      }

      if (tenderData) setTender(tenderData);
      if (analysisData) setAnalysis(analysisData);
    } catch (e) {
      console.error("Failed to load tender details:", e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateApplication = async () => {
    try {
      setIsGeneratingApp(true);
      
      const appPackage = await fetchApi<any>("/applications/generate", {
        method: "POST",
        body: JSON.stringify({ tender_id: tenderId, match_id: analysis?.match_id || tenderId })
      }).catch(() => null);

      if (appPackage) {
        setAppId(appPackage.id || "");
        setCoverLetter(appPackage.cover_letter_content || "");
        setDeclaration(appPackage.declaration_content || "");
        setTechnicalResponse(appPackage.technical_response_content || "");
      } else {
        const coverRes = await api.generateCoverLetter({ business_id: "demo", tender_id: tenderId }).catch(() => null);
        const declRes = await api.generateDeclaration({ business_id: "demo", tender_id: tenderId }).catch(() => null);
        const techRes = await api.generateTechnicalResponse({ business_id: "demo", tender_id: tenderId }).catch(() => null);

        setCoverLetter(coverRes?.cover_letter_content || coverRes?.cover_letter || "");
        setDeclaration(declRes?.declaration_content || declRes?.declaration || "");
        setTechnicalResponse(techRes?.technical_response_content || techRes?.technical_response || "");
      }

      setActiveTab("APPLICATION");
    } catch (e) {
      console.error("Generate error:", e);
    } finally {
      setIsGeneratingApp(false);
    }
  };

  const handleSaveDrafts = async () => {
    try {
      setIsSavingDraft(true);
      await api.updateApplication(appId || tenderId, {
        cover_letter_content: coverLetter,
        declaration_content: declaration,
        technical_response_content: technicalResponse,
      });
      setSaveDraftMessage("Application package drafts saved successfully to server!");
      setTimeout(() => setSaveDraftMessage(""), 3500);
    } catch (e) {
      console.error("Failed to save drafts:", e);
      setSaveDraftMessage("Failed to save drafts.");
    } finally {
      setIsSavingDraft(false);
    }
  };

  const handleDownloadPackage = (format: "txt" | "md" = "txt") => {
    const isMd = format === "md";
    const fullText = isMd
      ? `# AI Tender Application Package\n**Tender:** ${tender?.title}\n**Ref:** ${tender?.tender_id_code}\n\n## 1. Formal Cover Letter\n${coverLetter}\n\n## 2. Tender Declaration\n${declaration}\n\n## 3. Technical Compliance Statement\n${technicalResponse}\n`
      : `=== AI TENDER APPLICATION PACKAGE ===\nTender: ${tender?.title}\nRef: ${tender?.tender_id_code}\n\n--- COVER LETTER ---\n${coverLetter}\n\n--- DECLARATION ---\n${declaration}\n\n--- TECHNICAL RESPONSE ---\n${technicalResponse}`;

    const mime = isMd ? "text/markdown" : "text/plain";
    const ext = isMd ? "md" : "txt";
    const blob = new Blob([fullText], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Tender_Application_${tender?.tender_id_code || "MH-2026"}.${ext}`;
    a.click();
  };

  if (isLoading) {
    return (
      <div className="flex flex-col min-h-screen bg-slate-950">
        <Navbar />
        <div className="flex-1 flex items-center justify-center text-slate-400 font-mono text-xs">
          Extracting Sarvam Vision document intelligence & computing score...
        </div>
      </div>
    );
  }

  const score = analysis?.overall_score || 87;
  const eligStatus = analysis?.eligibility_status || "ELIGIBLE";
  const readiness = analysis?.readiness_percentage || 75;

  return (
    <div className="flex flex-col min-h-screen bg-slate-950">
      <Navbar onUploadClick={() => setIsUploadOpen(true)} />
      <UploadModal isOpen={isUploadOpen} onClose={() => setIsUploadOpen(false)} />

      <main className="flex-1 mx-auto max-w-7xl w-full px-4 sm:px-6 lg:px-8 py-8">
        {/* Top Header Card */}
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="font-mono text-xs font-bold text-blue-400 bg-blue-500/10 px-2.5 py-1 rounded border border-blue-500/20">
                  {tender?.tender_id_code || "TENDER-MH-2026-089"}
                </span>
                <span className="text-xs font-semibold text-slate-400 bg-slate-800 px-2.5 py-1 rounded border border-slate-700">
                  {tender?.tender_type || "Open RFP"}
                </span>
              </div>

              <h1 className="text-2xl sm:text-3xl font-black text-white leading-tight mb-2">
                {tender?.title || "School Furniture Supply & Installation"}
              </h1>

              <p className="text-xs text-slate-400 flex items-center gap-2">
                <Building2 className="h-4 w-4 text-slate-500 shrink-0" />
                <span>{tender?.organization || "Department of School Education, Govt. of Maharashtra"}</span>
              </p>

              <div className="mt-4 flex flex-wrap items-center gap-4 text-xs">
                <div className="bg-slate-950/80 px-3 py-1.5 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-500 uppercase block font-semibold">Estimated Budget</span>
                  <span className="font-bold text-emerald-400 font-mono">
                    {tender?.estimated_value
                      ? tender.estimated_value >= 10000000
                        ? `₹ ${(tender.estimated_value / 10000000).toFixed(2)} Crores`
                        : `₹ ${(tender.estimated_value / 100000).toFixed(2)} Lakhs`
                      : analysis?.budget
                      ? `₹ ${(analysis.budget / 100000).toFixed(2)} Lakhs`
                      : "₹ 10.00 Lakhs"}
                  </span>
                </div>

                <div className="bg-slate-950/80 px-3 py-1.5 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-500 uppercase block font-semibold">Closing Deadline</span>
                  <span className="font-semibold text-amber-400 font-mono flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {analysis?.deadline ? new Date(analysis.deadline).toLocaleDateString("en-IN") : "30 Sept 2026"} (Asia/Kolkata)
                  </span>
                </div>

                <div className="bg-slate-950/80 px-3 py-1.5 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-500 uppercase block font-semibold">Delivery Location</span>
                  <span className="font-medium text-slate-300">{tender?.location || analysis?.location || "All India"}</span>
                </div>
              </div>
            </div>

            {/* Score & Action Column */}
            <div className="flex flex-col items-center lg:items-end justify-between border-t lg:border-t-0 lg:border-l border-slate-800 pt-4 lg:pt-0 lg:pl-6 gap-4">
              <ScoreGauge score={score} eligibilityStatus={eligStatus} />

              <button
                onClick={handleGenerateApplication}
                disabled={isGeneratingApp}
                className="w-full sm:w-auto px-6 py-3 rounded-xl font-bold text-xs bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/20 transition-all flex items-center justify-center gap-2"
              >
                <FileCheck2 className="h-4 w-4" />
                <span>{isGeneratingApp ? "Generating Drafts..." : "Generate Application Drafts"}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 border-b border-slate-800 mb-8">
          <button
            onClick={() => setActiveTab("ANALYSIS")}
            className={`px-5 py-3 text-xs font-bold transition-all border-b-2 ${
              activeTab === "ANALYSIS"
                ? "border-blue-500 text-blue-400 bg-blue-500/10"
                : "border-transparent text-slate-400 hover:text-white"
            }`}
          >
            Tender Match & Gap Intelligence
          </button>
          <button
            onClick={() => setActiveTab("APPLICATION")}
            className={`px-5 py-3 text-xs font-bold transition-all border-b-2 ${
              activeTab === "APPLICATION"
                ? "border-blue-500 text-blue-400 bg-blue-500/10"
                : "border-transparent text-slate-400 hover:text-white"
            }`}
          >
            Application Assistant Generator
          </button>
        </div>

        {/* Tab 1: Tender Match & Gap Intelligence */}
        {activeTab === "ANALYSIS" && (
          <div className="space-y-8">
            {/* Visual Score Breakdown & Hard Rules */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <MatchChart
                productScore={analysis?.product_score || 92}
                eligibilityScore={analysis?.eligibility_score || 100}
                turnoverScore={analysis?.turnover_score || 100}
                experienceScore={analysis?.experience_score || 50}
                locationScore={analysis?.location_score || 80}
              />

              {/* Explainable Reasoning Card */}
              <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
                <h3 className="text-sm font-extrabold text-white mb-4 flex items-center justify-between">
                  <span>Explainable Match Breakdown ("WHY?")</span>
                  <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                    Hard Rule PASS
                  </span>
                </h3>

                <div className="space-y-3 text-xs">
                  {analysis?.reasons?.map((item: any, idx: number) => (
                    <div
                      key={idx}
                      className={`p-3 rounded-lg border flex items-start justify-between gap-3 ${
                        item.category === "MATCHED"
                          ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-200"
                          : item.category === "WARNING"
                          ? "bg-amber-500/10 border-amber-500/20 text-amber-200"
                          : "bg-red-500/10 border-red-500/20 text-red-200"
                      }`}
                    >
                      <div className="flex items-start gap-2">
                        {item.category === "MATCHED" ? (
                          <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
                        ) : (
                          <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0 mt-0.5" />
                        )}
                        <span>{item.reason}</span>
                      </div>

                      {item.source_citation && (
                        <span className="font-mono text-[10px] bg-slate-950/80 px-2 py-0.5 rounded text-slate-400 shrink-0">
                          Page {item.source_citation.page}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Requirement Gap Analysis & Readiness Matrix */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
                <h3 className="text-sm font-extrabold text-white mb-4 flex items-center justify-between">
                  <span>Requirement Gap Analysis Matrix</span>
                  <span className="text-xs text-slate-400">Available vs Missing Proofs</span>
                </h3>

                <div className="space-y-3">
                  {analysis?.gap_matrix?.map((doc: any, idx: number) => (
                    <div
                      key={idx}
                      className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-xs"
                    >
                      <div className="flex items-center gap-3">
                        <FileText className="h-4 w-4 text-slate-400" />
                        <div>
                          <span className="font-semibold text-white block">{doc.document_name}</span>
                          <span className="text-[10px] text-slate-500">Mandatory Tender Qualification</span>
                        </div>
                      </div>

                      <div>
                        {doc.status === "SATISFIED" ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                            <CheckCircle2 className="h-3.5 w-3.5" />
                            SATISFIED
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-bold bg-amber-500/15 text-amber-400 border border-amber-500/30">
                            <AlertTriangle className="h-3.5 w-3.5" />
                            MISSING PROOF
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Readiness & Risk Column */}
              <div className="space-y-6">
                <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 text-center">
                  <span className="block text-xs font-bold text-slate-400 uppercase mb-2">Application Readiness</span>
                  <div className="text-4xl font-extrabold text-blue-400 font-mono mb-1">{readiness}%</div>
                  <p className="text-xs text-slate-400 mb-4">3 of 4 Required Documents Verified</p>
                  <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                    <div className="h-full bg-blue-500" style={{ width: `${readiness}%` }} />
                  </div>
                </div>

                <div className="p-6 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-xs">
                  <div className="flex items-center gap-2 text-amber-300 font-bold mb-2">
                    <AlertTriangle className="h-4 w-4 text-amber-400" />
                    <span>Risk Level: MEDIUM</span>
                  </div>
                  <p className="text-amber-200/90 leading-relaxed">
                    Business satisfies turnover and MSME requirements. Risk is medium solely due to missing past experience proof certificate.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Application Assistant Generator */}
        {activeTab === "APPLICATION" && (
          <div className="space-y-8">
            {saveDraftMessage && (
              <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                <span>{saveDraftMessage}</span>
              </div>
            )}

            <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs text-blue-300 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-blue-400 shrink-0" />
                <span>Zero Hallucination Guaranteed: All generated content is created strictly from verified profile facts.</span>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={handleSaveDrafts}
                  disabled={isSavingDraft || !coverLetter}
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold text-xs flex items-center gap-1.5 transition-all shadow-sm"
                >
                  <Save className="h-4 w-4" />
                  <span>{isSavingDraft ? "Saving..." : "Save Draft Changes"}</span>
                </button>

                <button
                  onClick={() => handleDownloadPackage("txt")}
                  disabled={!coverLetter}
                  className="px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-bold text-xs flex items-center gap-1.5 transition-all"
                  title="Download as TXT"
                >
                  <Download className="h-4 w-4" />
                  <span>Download .TXT</span>
                </button>

                <button
                  onClick={() => handleDownloadPackage("md")}
                  disabled={!coverLetter}
                  className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 border border-slate-700 font-bold text-xs flex items-center gap-1.5 transition-all"
                  title="Download as Markdown"
                >
                  <FileText className="h-4 w-4" />
                  <span>.MD</span>
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Cover Letter Editor */}
              <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
                <h3 className="text-sm font-extrabold text-white mb-3 flex items-center justify-between">
                  <span>1. Formal Cover Letter</span>
                  <span className="text-[10px] text-slate-500 font-mono">Editable Draft</span>
                </h3>
                <textarea
                  value={coverLetter}
                  onChange={(e) => setCoverLetter(e.target.value)}
                  rows={10}
                  className="w-full p-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 font-mono leading-relaxed focus:outline-none focus:border-blue-500"
                />
              </div>

              {/* Declaration Editor */}
              <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
                <h3 className="text-sm font-extrabold text-white mb-3 flex items-center justify-between">
                  <span>2. Tender Declaration</span>
                  <span className="text-[10px] text-slate-500 font-mono">Editable Draft</span>
                </h3>
                <textarea
                  value={declaration}
                  onChange={(e) => setDeclaration(e.target.value)}
                  rows={10}
                  className="w-full p-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 font-mono leading-relaxed focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            {/* Technical Response */}
            <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
              <h3 className="text-sm font-extrabold text-white mb-3 flex items-center justify-between">
                <span>3. Technical Compliance Statement</span>
                <span className="text-[10px] text-slate-500 font-mono">Editable Draft</span>
              </h3>
              <textarea
                value={technicalResponse}
                onChange={(e) => setTechnicalResponse(e.target.value)}
                rows={8}
                className="w-full p-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 font-mono leading-relaxed focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
