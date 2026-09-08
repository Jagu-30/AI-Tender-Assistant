"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { FileText, Building2, LayoutDashboard, Sparkles, UploadCloud, CheckCircle2, ShieldCheck } from "lucide-react";
import { api } from "../services/api";

export default function Navbar({ onUploadClick }: { onUploadClick?: () => void }) {
  const pathname = usePathname();
  const [isSeeding, setIsSeeding] = useState(false);
  const [seedSuccess, setSeedSuccess] = useState(false);

  const handleSeed = async () => {
    try {
      setIsSeeding(true);
      await api.seedSample();
      setSeedSuccess(true);
      setTimeout(() => {
        setSeedSuccess(false);
        window.location.href = "/dashboard";
      }, 1200);
    } catch (err) {
      console.error("Failed to seed sample data:", err);
    } finally {
      setIsSeeding(false);
    }
  };

  const navLinks = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Tender Hub", href: "/tenders", icon: FileText },
    { name: "MSME Profile", href: "/profile", icon: Building2 },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-slate-900/90 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-blue-700 text-white shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg text-white tracking-tight">AI Tender Assistant</span>
                <span className="rounded bg-blue-500/10 px-2 py-0.5 text-xs font-semibold text-blue-400 border border-blue-500/20">
                  MSME Edition
                </span>
              </div>
              <p className="text-xs text-slate-400">Government Tender Intelligence Engine</p>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-1 ml-6">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-blue-600/15 text-blue-400 border border-blue-500/30"
                      : "text-slate-300 hover:text-white hover:bg-slate-800/60"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {link.name}
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleSeed}
            disabled={isSeeding}
            className="hidden sm:flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/20 transition-colors disabled:opacity-50"
            title="Load ABC Furniture Pvt. Ltd. sample business & tender"
          >
            {seedSuccess ? (
              <>
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                Sample Data Seeded!
              </>
            ) : (
              <>
                <Sparkles className="h-3.5 w-3.5 text-emerald-400" />
                {isSeeding ? "Seeding Demo Data..." : "Seed Demo Profile & Tender"}
              </>
            )}
          </button>

          <button
            onClick={onUploadClick}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold bg-blue-600 text-white shadow-md shadow-blue-600/20 hover:bg-blue-500 active:scale-95 transition-all"
          >
            <UploadCloud className="h-4 w-4" />
            <span>Upload Tender</span>
          </button>
        </div>
      </div>
    </header>
  );
}
