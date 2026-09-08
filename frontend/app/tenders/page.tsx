"use client";

import { useEffect, useState } from "react";
import Navbar from "../../components/Navbar";
import TenderCard from "../../components/TenderCard";
import UploadModal from "../../components/UploadModal";
import { FileText, Search, Filter, PlusCircle, ArrowUpDown } from "lucide-react";
import { api } from "../../services/api";

export default function TendersPage() {
  const [tenders, setTenders] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterEligibility, setFilterEligibility] = useState("ALL");
  const [filterRisk, setFilterRisk] = useState("ALL");
  const [sortBy, setSortBy] = useState("SCORE");

  useEffect(() => {
    loadTenders();
  }, []);

  const loadTenders = async () => {
    try {
      setIsLoading(true);
      await api.seedSample().catch(() => {});
      const data = await api.getTenders().catch(() => []);
      setTenders(data);
    } catch (e) {
      console.error("Failed to load tenders:", e);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredAndSortedTenders = tenders
    .filter((t) => {
      const matchSearch =
        t.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.organization?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.location?.toLowerCase().includes(searchQuery.toLowerCase());

      const matchElig = filterEligibility === "ALL" || t.eligibility_status === filterEligibility;
      const matchRisk = filterRisk === "ALL" || t.risk_level === filterRisk;

      return matchSearch && matchElig && matchRisk;
    })
    .sort((a, b) => {
      if (sortBy === "SCORE") return (b.match_score || 87) - (a.match_score || 87);
      if (sortBy === "BUDGET") return (b.estimated_value || 0) - (a.estimated_value || 0);
      return 0;
    });

  return (
    <div className="flex flex-col min-h-screen bg-slate-950">
      <Navbar onUploadClick={() => setIsUploadOpen(true)} />
      <UploadModal isOpen={isUploadOpen} onClose={() => setIsUploadOpen(false)} />

      <main className="flex-1 mx-auto max-w-7xl w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-bold text-blue-400 uppercase tracking-wider font-mono">Tender Discovery Hub</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white">Government Tender Intelligence</h1>
            <p className="text-xs text-slate-400 mt-1">
              Search, filter, and evaluate active tenders across state & central procurement portals.
            </p>
          </div>

          <button
            onClick={() => setIsUploadOpen(true)}
            className="px-5 py-2.5 rounded-xl font-semibold text-xs bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-600/20 transition-all flex items-center gap-2"
          >
            <PlusCircle className="h-4 w-4" />
            <span>Upload New Tender PDF</span>
          </button>
        </div>

        {/* Search & Filter Bar */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 mb-8 flex flex-col lg:flex-row items-center gap-4">
          <div className="relative flex-1 w-full">
            <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-500" />
            <input
              type="text"
              placeholder="Search by tender title, department, organization, or location..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
            <div className="flex items-center gap-1.5 text-xs text-slate-400">
              <Filter className="h-3.5 w-3.5" />
              <span>Eligibility:</span>
              <select
                value={filterEligibility}
                onChange={(e) => setFilterEligibility(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200"
              >
                <option value="ALL">All Verdicts</option>
                <option value="ELIGIBLE">Eligible Only</option>
                <option value="NOT_ELIGIBLE">Not Eligible</option>
              </select>
            </div>

            <div className="flex items-center gap-1.5 text-xs text-slate-400">
              <span>Risk:</span>
              <select
                value={filterRisk}
                onChange={(e) => setFilterRisk(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200"
              >
                <option value="ALL">All Risk Levels</option>
                <option value="LOW">Low Risk</option>
                <option value="MEDIUM">Medium Risk</option>
                <option value="HIGH">High Risk</option>
              </select>
            </div>

            <div className="flex items-center gap-1.5 text-xs text-slate-400">
              <ArrowUpDown className="h-3.5 w-3.5" />
              <span>Sort:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200"
              >
                <option value="SCORE">Match Score (High to Low)</option>
                <option value="BUDGET">Budget Value</option>
              </select>
            </div>
          </div>
        </div>

        {/* Results Grid */}
        {isLoading ? (
          <div className="py-12 text-center text-slate-500 font-mono text-xs">Loading tender collection...</div>
        ) : filteredAndSortedTenders.length === 0 ? (
          <div className="p-12 rounded-xl bg-slate-900/40 border border-slate-800 text-center">
            <FileText className="h-10 w-10 text-slate-600 mx-auto mb-3" />
            <h3 className="text-base font-bold text-white">No Tenders Found</h3>
            <p className="text-xs text-slate-400 mt-1">Try adjusting your filters or upload a new tender document.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAndSortedTenders.map((tender) => (
              <TenderCard key={tender.id} tender={tender} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
