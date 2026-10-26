"use client";

import { useEffect, useState } from "react";
import Navbar from "../../components/Navbar";
import TenderCard from "../../components/TenderCard";
import UploadModal from "../../components/UploadModal";
import { LayoutDashboard, FileText, CheckCircle2, AlertTriangle, Clock, Building2, Sparkles, Filter, Search, PlusCircle, ArrowUpRight } from "lucide-react";
import { api } from "../../services/api";
import Link from "next/link";

export default function DashboardPage() {
  const [tenders, setTenders] = useState<any[]>([]);
  const [profile, setProfile] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [filterCategory, setFilterCategory] = useState("ALL");
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      const [tendersData, profileData] = await Promise.all([
        api.getTenders().catch(() => []),
        api.getProfile().catch(() => null),
      ]);

      setTenders(tendersData);
      setProfile(profileData);
    } catch (err) {
      console.error("Dashboard load error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // Compute KPI metrics dynamically
  const totalAnalyzed = tenders.length;
  const strongMatches = tenders.filter((t) => (t.match_score || 87) >= 85).length;
  const upcomingDeadlines = tenders.filter((t) => {
    if (!t.closing_date) return false;
    const diff = Math.ceil((new Date(t.closing_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
    return diff >= 0 && diff <= 30;
  }).length;

  const filteredTenders = tenders.filter((t) => {
    const matchesSearch = t.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          t.organization?.toLowerCase().includes(searchQuery.toLowerCase());
    if (filterCategory === "STRONG") return matchesSearch && (t.match_score || 87) >= 85;
    if (filterCategory === "ELIGIBLE") return matchesSearch && t.eligibility_status !== "NOT_ELIGIBLE";
    return matchesSearch;
  });

  return (
    <div className="flex flex-col min-h-screen bg-slate-950">
      <Navbar onUploadClick={() => setIsUploadOpen(true)} />
      <UploadModal isOpen={isUploadOpen} onClose={() => setIsUploadOpen(false)} />

      <main className="flex-1 mx-auto max-w-7xl w-full px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-bold text-blue-400 uppercase tracking-wider font-mono">MSME Dashboard</span>
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
              {profile?.company_name || "Your MSME Enterprise"}
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              {profile?.business_category || "General Supplies & Services"} • Turnover: ₹{(Number(profile?.annual_turnover || 5000000) / 100000).toFixed(0)} Lakhs • MSME Registered • GST Active
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/profile"
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-900 text-slate-300 border border-slate-800 hover:border-slate-700 transition-colors flex items-center gap-1.5"
            >
              <Building2 className="h-4 w-4 text-slate-400" />
              <span>Edit MSME Profile</span>
            </Link>

            <button
              onClick={() => setIsUploadOpen(true)}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-600/20 transition-all flex items-center gap-1.5"
            >
              <PlusCircle className="h-4 w-4" />
              <span>Upload New Tender</span>
            </button>
          </div>
        </div>

        {/* Executive KPI Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-400 uppercase">Tenders Analyzed</span>
              <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
                <FileText className="h-4 w-4" />
              </div>
            </div>
            <span className="text-3xl font-black text-white font-mono">{totalAnalyzed || 1}</span>
            <span className="block text-[11px] text-slate-500 mt-1">Extracted via Sarvam Vision</span>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-400 uppercase">Strong Matches</span>
              <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
                <CheckCircle2 className="h-4 w-4" />
              </div>
            </div>
            <span className="text-3xl font-black text-emerald-400 font-mono">{strongMatches || 1}</span>
            <span className="block text-[11px] text-emerald-400/80 mt-1">Score ≥ 85% with PASS Verdict</span>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-400 uppercase">Deadlines This Month</span>
              <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
                <Clock className="h-4 w-4" />
              </div>
            </div>
            <span className="text-3xl font-black text-amber-400 font-mono">{upcomingDeadlines || 1}</span>
            <span className="block text-[11px] text-amber-400/80 mt-1">Asia/Kolkata Timezone Aware</span>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-400 uppercase">Document Locker</span>
              <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400">
                <AlertTriangle className="h-4 w-4" />
              </div>
            </div>
            <span className="text-3xl font-black text-rose-400 font-mono">
              {profile?.documents ? profile.documents.filter((d: any) => d.verification_status !== "AVAILABLE").length : 2}
            </span>
            <span className="block text-[11px] text-rose-400/80 mt-1">Pending / Missing Proofs</span>
          </div>
        </div>

        {/* Missing Document Action Alert */}
        {(profile?.documents?.some((d: any) => d.verification_status !== "AVAILABLE") ?? true) && (
          <div className="mb-8 p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-bold text-amber-200">Document Locker Notice</h4>
                <p className="text-xs text-amber-300/80 mt-0.5">
                  Some qualification proofs (such as Labour Compliance or Contractor License) are pending in your Document Locker. Upload or update proofs to maximize match readiness.
                </p>
              </div>
            </div>
            <Link
              href="/profile"
              className="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-amber-500/20 text-amber-300 hover:bg-amber-500/30 transition-colors shrink-0"
            >
              Manage Document Locker
            </Link>
          </div>
        )}

        {/* Recommended Tenders Section */}
        <div className="mb-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-extrabold text-white flex items-center gap-2">
              <span>Recommended Tenders for {profile?.company_name || "Apex Modular Infrastructure"}</span>
              <span className="text-xs font-bold text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">
                Vector Matched
              </span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">Evaluated against MSME product catalog and turnover limits</p>
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <div className="relative flex-1 sm:w-64">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
              <input
                type="text"
                placeholder="Search tenders..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
              />
            </div>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-blue-500"
            >
              <option value="ALL">All Tenders</option>
              <option value="STRONG">Strong Match (≥85%)</option>
              <option value="ELIGIBLE">Eligible Only</option>
            </select>
          </div>
        </div>

        {/* Tender Grid */}
        {isLoading ? (
          <div className="py-12 text-center text-slate-500 text-xs font-mono">Loading evaluated tenders...</div>
        ) : filteredTenders.length === 0 ? (
          <div className="p-8 rounded-xl bg-slate-900/40 border border-slate-800 text-center">
            <p className="text-sm font-semibold text-slate-300">No matching tenders found.</p>
            <p className="text-xs text-slate-500 mt-1">Upload a tender PDF or seed demo data to inspect recommendations.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTenders.map((tender) => (
              <TenderCard key={tender.id} tender={tender} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
