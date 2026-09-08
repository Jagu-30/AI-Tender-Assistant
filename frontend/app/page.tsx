"use client";

import { useState } from "react";
import Link from "next/link";
import Navbar from "../components/Navbar";
import UploadModal from "../components/UploadModal";
import { ArrowRight, CheckCircle2, ShieldCheck, Sparkles, FileText, PieChart, AlertTriangle, FileCheck, Layers, Building2 } from "lucide-react";
import { api } from "../services/api";

export default function LandingPage() {
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isSeeding, setIsSeeding] = useState(false);

  const handleDemoWalkthrough = async () => {
    try {
      setIsSeeding(true);
      await api.seedSample();
      window.location.href = "/dashboard";
    } catch (e) {
      window.location.href = "/dashboard";
    } finally {
      setIsSeeding(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar onUploadClick={() => setIsUploadOpen(true)} />
      <UploadModal isOpen={isUploadOpen} onClose={() => setIsUploadOpen(false)} />

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-20 lg:pt-24 lg:pb-32 bg-gradient-to-b from-slate-900 via-slate-950 to-slate-950">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          <div className="inline-flex items-center gap-2 rounded-full bg-blue-500/10 border border-blue-500/20 px-3.5 py-1.5 text-xs font-semibold text-blue-400 mb-8 shadow-sm">
            <Sparkles className="h-3.5 w-3.5 text-blue-400" />
            AI-Powered Tender Intelligence for MSMEs
          </div>

          <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-6xl max-w-4xl mx-auto leading-tight">
            Find the right government tenders.{" "}
            <span className="bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
              Understand them.
            </span>{" "}
            Apply with confidence.
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Stop reading 100-page RFP PDFs manually. Instant Sarvam Vision extraction, hard rule eligibility engine, vector product matching, and gap analysis for small businesses.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={() => setIsUploadOpen(true)}
              className="w-full sm:w-auto px-8 py-4 rounded-xl font-bold text-base bg-blue-600 hover:bg-blue-500 text-white shadow-xl shadow-blue-600/25 transition-all flex items-center justify-center gap-2 group"
            >
              <span>Analyze a Tender</span>
              <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </button>

            <button
              onClick={handleDemoWalkthrough}
              disabled={isSeeding}
              className="w-full sm:w-auto px-8 py-4 rounded-xl font-semibold text-base bg-slate-800/80 hover:bg-slate-800 text-slate-200 border border-slate-700 transition-all flex items-center justify-center gap-2"
            >
              <Building2 className="h-5 w-5 text-emerald-400" />
              <span>{isSeeding ? "Loading ABC Furniture Demo..." : "Explore ABC Furniture Demo"}</span>
            </button>
          </div>

          {/* Key Value Stats */}
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto text-left">
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="block text-2xl font-extrabold text-white font-mono">100%</span>
              <span className="text-xs text-slate-400">Hard Rule Eligibility</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="block text-2xl font-extrabold text-blue-400 font-mono">5-Factor</span>
              <span className="text-xs text-slate-400">Weighted Match Model</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="block text-2xl font-extrabold text-emerald-400 font-mono">Zero</span>
              <span className="text-xs text-slate-400">LLM Hallucination</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="block text-2xl font-extrabold text-amber-400 font-mono">Asia/Kolkata</span>
              <span className="text-xs text-slate-400">Deadline Intelligence</span>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Showcase Grid */}
      <section className="py-16 bg-slate-950 border-t border-slate-900">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-2xl sm:text-3xl font-bold text-white">
              Built Specifically to Resolve MSME Tender Challenges
            </h2>
            <p className="text-sm text-slate-400 mt-2">
              From PDF ingestion to verified application drafts in under 3 minutes.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 hover:border-blue-500/30 transition-all">
              <div className="h-12 w-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 mb-5">
                <FileText className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Sarvam Vision PDF Extraction</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Native optical character recognition for complex tables, Indian government circular formatting, eligibility rules, and page-cited source references.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 hover:border-emerald-500/30 transition-all">
              <div className="h-12 w-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-5">
                <ShieldCheck className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Hard Rule Eligibility Engine</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Deterministic Python validation for MSME preferences, GST compliance, turnover limits, location criteria, and experience years.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 hover:border-amber-500/30 transition-all">
              <div className="h-12 w-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 mb-5">
                <FileCheck className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Verified Application Assistant</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Generates editable Cover Letters, Technical Response compliance statements, Tender Declarations, and document checklists with zero hallucination.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
