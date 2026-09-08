"use client";

import { useState } from "react";
import { UploadCloud, X, FileText, CheckCircle2, Loader2, AlertCircle } from "lucide-react";
import { api } from "../services/api";

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (tenderId: string) => void;
}

export default function UploadModal({ isOpen, onClose, onSuccess }: UploadModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [statusStep, setStatusStep] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string>("");

  if (!isOpen) return null;

  const steps = [
    { key: "UPLOADED", label: "Uploaded PDF" },
    { key: "PROCESSING", label: "Sarvam Vision OCR" },
    { key: "EXTRACTING", label: "LLM Extraction" },
    { key: "ANALYZING", label: "Eligibility Check" },
    { key: "MATCHING", label: "Product Vectors" },
    { key: "COMPLETED", label: "Analysis Complete" },
  ];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      if (selected.size > 25 * 1024 * 1024) {
        setErrorMessage("File size exceeds 25MB limit.");
        return;
      }
      setFile(selected);
      setErrorMessage("");
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    try {
      setIsUploading(true);
      setErrorMessage("");
      setStatusStep("UPLOADED");

      const formData = new FormData();
      formData.append("file", file);

      // Trigger upload API
      const res = await api.uploadTender(formData);
      const tenderId = res.id || res.tender_id;

      // Simulate step-by-step progress visually
      const progressSteps = ["PROCESSING", "EXTRACTING", "ANALYZING", "MATCHING", "COMPLETED"];
      for (const step of progressSteps) {
        await new Promise((r) => setTimeout(r, 600));
        setStatusStep(step);
      }

      // Trigger analysis & match
      await api.analyzeTender(tenderId).catch(() => {});
      await api.matchTender(tenderId).catch(() => {});

      if (onSuccess) onSuccess(tenderId);
      setTimeout(() => {
        setIsUploading(false);
        onClose();
        window.location.href = `/tenders/${tenderId}`;
      }, 500);
    } catch (err: any) {
      console.error("Upload error:", err);
      setErrorMessage(err.message || "Failed to process tender document.");
      setIsUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl relative">
        <button
          onClick={onClose}
          disabled={isUploading}
          className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="flex items-center gap-3 mb-4">
          <div className="p-2.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400">
            <UploadCloud className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">Upload Government Tender PDF</h2>
            <p className="text-xs text-slate-400">PDF, PNG, JPG format (Max 25MB)</p>
          </div>
        </div>

        {errorMessage && (
          <div className="mb-4 flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-xs text-red-300">
            <AlertCircle className="h-4 w-4 shrink-0 text-red-400" />
            <span>{errorMessage}</span>
          </div>
        )}

        {!isUploading ? (
          <div>
            <div className="border-2 border-dashed border-slate-700 hover:border-blue-500/50 rounded-xl p-8 text-center bg-slate-950/40 transition-colors">
              <input
                type="file"
                accept=".pdf,.png,.jpg,.jpeg"
                onChange={handleFileChange}
                className="hidden"
                id="tender-file-input"
              />
              <label htmlFor="tender-file-input" className="cursor-pointer flex flex-col items-center">
                <FileText className="h-10 w-10 text-slate-500 mb-2" />
                <span className="text-sm font-semibold text-white">
                  {file ? file.name : "Click to browse or drag and drop tender document"}
                </span>
                <span className="text-xs text-slate-500 mt-1">
                  {file ? `${(file.size / (1024 * 1024)).toFixed(2)} MB` : "Supports multi-page RFPs, NITs, and tenders"}
                </span>
              </label>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={onClose}
                className="px-4 py-2 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-800 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleUpload}
                disabled={!file}
                className="px-5 py-2 rounded-lg text-sm font-semibold bg-blue-600 text-white hover:bg-blue-500 disabled:opacity-50 transition-colors"
              >
                Start AI Analysis
              </button>
            </div>
          </div>
        ) : (
          <div className="py-6">
            <div className="flex items-center justify-center gap-2 text-sm font-semibold text-blue-400 mb-6">
              <Loader2 className="h-5 w-5 animate-spin" />
              <span>Analyzing Document Intelligence...</span>
            </div>

            <div className="space-y-3">
              {steps.map((step, idx) => {
                const currentIdx = steps.findIndex((s) => s.key === statusStep);
                const isDone = currentIdx > idx;
                const isCurrent = currentIdx === idx;

                return (
                  <div
                    key={step.key}
                    className={`flex items-center justify-between p-3 rounded-lg text-xs border ${
                      isDone
                        ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-300"
                        : isCurrent
                        ? "bg-blue-500/10 border-blue-500/30 text-blue-300 font-bold"
                        : "bg-slate-950/40 border-slate-800 text-slate-500"
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      {isDone ? (
                        <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                      ) : isCurrent ? (
                        <Loader2 className="h-4 w-4 animate-spin text-blue-400" />
                      ) : (
                        <span className="h-4 w-4 rounded-full border border-slate-700 flex items-center justify-center text-[10px]">
                          {idx + 1}
                        </span>
                      )}
                      {step.label}
                    </span>
                    <span className="font-mono text-[10px] uppercase">
                      {isDone ? "Done" : isCurrent ? "Processing..." : "Pending"}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
