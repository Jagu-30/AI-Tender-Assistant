"use client";

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

interface MatchChartProps {
  productScore: number;
  eligibilityScore: number;
  turnoverScore: number;
  experienceScore: number;
  locationScore: number;
}

export default function MatchChart({
  productScore,
  eligibilityScore,
  turnoverScore,
  experienceScore,
  locationScore,
}: MatchChartProps) {
  const data = [
    { name: "Product Match (30%)", score: productScore, color: "#3b82f6" },
    { name: "Eligibility (30%)", score: eligibilityScore, color: "#10b981" },
    { name: "Turnover (15%)", score: turnoverScore, color: "#8b5cf6" },
    { name: "Experience (15%)", score: experienceScore, color: "#f59e0b" },
    { name: "Location (10%)", score: locationScore, color: "#ec4899" },
  ];

  return (
    <div className="w-full bg-slate-900/60 p-4 rounded-xl border border-slate-800">
      <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center justify-between">
        <span>Weighted Score Component Breakdown</span>
        <span className="text-xs text-slate-500 font-mono">100% Total Formula</span>
      </h3>
      <div className="h-52 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
            <XAxis type="number" domain={[0, 100]} stroke="#64748b" fontSize={11} tickFormatter={(v) => `${v}%`} />
            <YAxis dataKey="name" type="category" stroke="#94a3b8" fontSize={12} width={130} />
            <Tooltip
              contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px", color: "#fff" }}
              formatter={(val: number) => [`${val}%`, "Score"]}
            />
            <Bar dataKey="score" radius={[0, 4, 4, 0]} barSize={16}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-3 grid grid-cols-5 gap-2 text-center text-xs">
        {data.map((item) => (
          <div key={item.name} className="p-1.5 rounded bg-slate-800/40 border border-slate-700/50">
            <span className="block text-[10px] text-slate-400 font-medium truncate">{item.name.split(" ")[0]}</span>
            <span className="font-bold text-white font-mono">{Math.round(item.score)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
