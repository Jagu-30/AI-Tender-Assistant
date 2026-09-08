import { AlertTriangle } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-slate-800 bg-slate-950 py-8 px-4 sm:px-6 lg:px-8 mt-auto text-xs text-slate-400">
      <div className="mx-auto max-w-7xl flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-start gap-2.5 max-w-2xl bg-amber-500/10 border border-amber-500/20 p-3 rounded-lg text-amber-200/90">
          <AlertTriangle className="h-4 w-4 shrink-0 text-amber-400 mt-0.5" />
          <p>
            <strong className="font-semibold text-amber-300">Legal & Verification Disclaimer:</strong> AI-generated tender analysis is provided for assistance and should be verified against the official tender document before submission.
          </p>
        </div>
        <div className="text-center md:text-right text-slate-500">
          <p>© 2026 AI Tender Assistant. Built for Indian MSMEs & Government Contractors.</p>
          <p className="mt-1 font-mono text-[11px] text-slate-600">Sarvam Vision + Multi-Factor Intelligence Engine v1.0.0</p>
        </div>
      </div>
    </footer>
  );
}
