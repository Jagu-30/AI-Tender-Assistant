import Link from "next/link";
import { Building2, Calendar, MapPin, IndianRupee, ShieldAlert, ArrowRight, CheckCircle, AlertTriangle } from "lucide-react";

interface TenderCardProps {
  tender: {
    id: string;
    tender_id_code: string;
    title: string;
    organization: string;
    estimated_value: number;
    closing_date?: string;
    location: string;
    match_score?: number;
    eligibility_status?: string;
    risk_level?: string;
  };
}

export default function TenderCard({ tender }: TenderCardProps) {
  const formatCurrency = (val: number) => {
    if (!val) return "₹ Not Specified";
    if (val >= 10000000) return `₹ ${(val / 10000000).toFixed(2)} Crore`;
    if (val >= 100000) return `₹ ${(val / 100000).toFixed(2)} Lakh`;
    return `₹ ${val.toLocaleString("en-IN")}`;
  };

  const getDeadlineStatus = (dateStr?: string) => {
    if (!dateStr) return { text: "No Deadline", color: "text-slate-400 bg-slate-800" };
    const deadline = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.ceil((deadline.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays < 0) return { text: "TENDER CLOSED", color: "text-red-400 bg-red-500/10 border-red-500/30" };
    if (diffDays <= 2) return { text: `${diffDays} days remaining • URGENT`, color: "text-red-400 bg-red-500/10 border-red-500/30" };
    if (diffDays <= 7) return { text: `${diffDays} days remaining • ATTENTION`, color: "text-amber-400 bg-amber-500/10 border-amber-500/30" };
    return { text: `${diffDays} days remaining • SAFE`, color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30" };
  };

  const getRiskBadge = (risk?: string) => {
    switch (risk) {
      case "LOW":
        return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">RISK: LOW</span>;
      case "MEDIUM":
        return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">RISK: MEDIUM</span>;
      case "HIGH":
        return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-red-500/10 text-red-400 border border-red-500/20">RISK: HIGH</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-800 text-slate-400 border border-slate-700">RISK: UNKNOWN</span>;
    }
  };

  const deadlineInfo = getDeadlineStatus(tender.closing_date);

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 hover:border-slate-700 transition-all flex flex-col justify-between group shadow-sm hover:shadow-md">
      <div>
        <div className="flex items-start justify-between gap-3 mb-2">
          <span className="font-mono text-xs font-semibold text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">
            {tender.tender_id_code || "TENDER-REF"}
          </span>
          <div className="flex items-center gap-2">
            {tender.match_score !== undefined && (
              <span className="font-mono font-bold text-sm text-white bg-slate-800 px-2.5 py-1 rounded border border-slate-700">
                {Math.round(tender.match_score)}% Match
              </span>
            )}
            {getRiskBadge(tender.risk_level)}
          </div>
        </div>

        <h3 className="font-bold text-base text-white group-hover:text-blue-400 transition-colors line-clamp-2 mb-2">
          {tender.title}
        </h3>

        <p className="text-xs text-slate-400 flex items-center gap-1.5 mb-4">
          <Building2 className="h-3.5 w-3.5 shrink-0 text-slate-500" />
          <span className="truncate">{tender.organization}</span>
        </p>

        <div className="grid grid-cols-2 gap-2 text-xs mb-4">
          <div className="bg-slate-950/60 p-2 rounded border border-slate-800/80">
            <span className="block text-[10px] text-slate-500 uppercase font-semibold">Budget Value</span>
            <span className="font-bold text-emerald-400 font-mono flex items-center gap-1">
              <IndianRupee className="h-3 w-3" />
              {formatCurrency(tender.estimated_value)}
            </span>
          </div>

          <div className="bg-slate-950/60 p-2 rounded border border-slate-800/80">
            <span className="block text-[10px] text-slate-500 uppercase font-semibold">Location</span>
            <span className="font-medium text-slate-200 flex items-center gap-1 truncate">
              <MapPin className="h-3 w-3 text-slate-400 shrink-0" />
              {tender.location || "Pan India"}
            </span>
          </div>
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between border-t border-slate-800/80 pt-3 mb-3 text-xs">
          <div className="flex items-center gap-1.5">
            <Calendar className="h-3.5 w-3.5 text-slate-400" />
            <span className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${deadlineInfo.color}`}>
              {deadlineInfo.text}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Link
            href={`/tenders/${tender.id}`}
            className="flex-1 text-center py-2 px-3 rounded-lg text-xs font-semibold bg-blue-600/10 text-blue-400 border border-blue-500/20 hover:bg-blue-600 hover:text-white transition-all flex items-center justify-center gap-1"
          >
            <span>Analyze & Apply</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </div>
    </div>
  );
}
