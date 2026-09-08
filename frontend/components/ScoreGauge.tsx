import { ShieldCheck, AlertOctagon, HelpCircle, CheckCircle2 } from "lucide-react";

interface ScoreGaugeProps {
  score: number;
  eligibilityStatus?: "ELIGIBLE" | "NOT_ELIGIBLE" | "PARTIALLY_ELIGIBLE" | "UNKNOWN";
  category?: string;
  size?: "sm" | "md" | "lg";
}

export default function ScoreGauge({ score, eligibilityStatus = "ELIGIBLE", category, size = "md" }: ScoreGaugeProps) {
  const getCategoryColor = (score: number, status: string) => {
    if (status === "NOT_ELIGIBLE") return "text-red-400 bg-red-500/10 border-red-500/30";
    if (score >= 90) return "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
    if (score >= 75) return "text-blue-400 bg-blue-500/10 border-blue-500/30";
    if (score >= 60) return "text-amber-400 bg-amber-500/10 border-amber-500/30";
    return "text-red-400 bg-red-500/10 border-red-500/30";
  };

  const getMatchCategoryLabel = (score: number) => {
    if (category) return category;
    if (score >= 90) return "STRONG MATCH";
    if (score >= 75) return "GOOD MATCH";
    if (score >= 60) return "PARTIAL MATCH";
    return "LOW MATCH";
  };

  const getEligibilityBadge = (status: string) => {
    switch (status) {
      case "ELIGIBLE":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="h-3.5 w-3.5" />
            ELIGIBLE
          </span>
        );
      case "NOT_ELIGIBLE":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/15 text-red-400 border border-red-500/30">
            <AlertOctagon className="h-3.5 w-3.5" />
            NOT ELIGIBLE
          </span>
        );
      case "PARTIALLY_ELIGIBLE":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/30">
            <AlertOctagon className="h-3.5 w-3.5" />
            PARTIALLY ELIGIBLE
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-700/50 text-slate-300 border border-slate-600">
            <HelpCircle className="h-3.5 w-3.5" />
            UNKNOWN
          </span>
        );
    }
  };

  return (
    <div className="flex flex-col items-center justify-center text-center">
      <div className="relative flex items-center justify-center">
        {/* Outer Circular Glow */}
        <div className={`rounded-full p-4 border-2 ${getCategoryColor(score, eligibilityStatus)}`}>
          <div className="flex flex-col items-center justify-center">
            <span className="text-4xl font-extrabold tracking-tight text-white font-mono">{Math.round(score)}%</span>
            <span className="text-[10px] font-bold tracking-wider text-slate-400 uppercase mt-0.5">Match Score</span>
          </div>
        </div>
      </div>

      <div className="mt-3 flex items-center gap-2">
        <span className={`px-2 py-0.5 text-xs font-bold rounded border ${getCategoryColor(score, eligibilityStatus)}`}>
          {getMatchCategoryLabel(score)}
        </span>
        {getEligibilityBadge(eligibilityStatus)}
      </div>
    </div>
  );
}
