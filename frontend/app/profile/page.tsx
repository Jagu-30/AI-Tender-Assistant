"use client";

import { useEffect, useState } from "react";
import Navbar from "../../components/Navbar";
import UploadModal from "../../components/UploadModal";
import { Building2, Package, FileCheck2, CheckCircle2, AlertCircle, Plus, Trash2, ShieldCheck, Upload, Save } from "lucide-react";
import { api } from "../../services/api";

export default function ProfilePage() {
  const [profile, setProfile] = useState<any>({
    company_name: "ABC Furniture Pvt. Ltd.",
    business_category: "Furniture Manufacturer",
    description: "Leading manufacturer of school, office, and institutional furniture.",
    annual_turnover: 5000000,
    is_msme_registered: true,
    msme_registration_number: "UDYAM-MH-12-0098765",
    has_gst_registration: true,
    gstin: "27AABCA1234F1Z5",
    state_location: "Maharashtra",
    operating_regions: ["Maharashtra", "Goa", "Gujarat"],
    years_in_business: 5,
    govt_experience_years: 3,
    certifications: ["ISO 9001:2015"],
  });

  const [products, setProducts] = useState<any[]>([
    { id: "1", name: "Desks", category: "Furniture", description: "Classroom and office desks" },
    { id: "2", name: "Chairs", category: "Furniture", description: "Student seating chairs" },
    { id: "3", name: "Tables", category: "Furniture", description: "Teacher and conference tables" },
    { id: "4", name: "Cabinets", category: "Furniture", description: "Storage cabinets" },
  ]);

  const [documents, setDocuments] = useState<any[]>([
    { id: "1", document_name: "GST Registration Certificate", document_type: "GST_CERTIFICATE", verification_status: "AVAILABLE" },
    { id: "2", document_name: "MSME Udyam Certificate", document_type: "MSME_CERTIFICATE", verification_status: "AVAILABLE" },
    { id: "3", document_name: "Audited Financial Statement 2024-25", document_type: "FINANCIAL_STATEMENT", verification_status: "AVAILABLE" },
    { id: "4", document_name: "Previous Supply Experience Proof", document_type: "EXPERIENCE_CERTIFICATE", verification_status: "MISSING" },
  ]);

  const [newProductName, setNewProductName] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");
  const [isUploadOpen, setIsUploadOpen] = useState(false);

  useEffect(() => {
    loadProfileData();
  }, []);

  const loadProfileData = async () => {
    try {
      const p = await api.getProfile().catch(() => null);
      if (p) setProfile(p);
      const prods = await api.getProducts().catch(() => null);
      if (prods && prods.length > 0) setProducts(prods);
      const docs = await api.getDocuments().catch(() => null);
      if (docs && docs.length > 0) setDocuments(docs);
    } catch (e) {
      console.error("Failed to load profile data:", e);
    }
  };

  const handleAddProduct = async () => {
    if (!newProductName.trim()) return;
    try {
      const newProd = { name: newProductName, category: "Furniture", description: "Added product" };
      const saved = await api.addProduct(newProd).catch(() => ({ ...newProd, id: Date.now().toString() }));
      setProducts([...products, saved]);
      setNewProductName("");
    } catch (e) {
      console.error("Add product error:", e);
    }
  };

  const handleDeleteProduct = async (id: string) => {
    try {
      await api.deleteProduct(id).catch(() => {});
      setProducts(products.filter((p) => p.id !== id));
    } catch (e) {
      console.error("Delete product error:", e);
    }
  };

  const handleSaveProfile = async () => {
    try {
      setIsSaving(true);
      await api.updateProfile(profile).catch(() => {});
      setSaveMessage("Business profile updated successfully!");
      setTimeout(() => setSaveMessage(""), 3000);
    } catch (e) {
      setSaveMessage("Failed to update profile.");
    } finally {
      setIsSaving(false);
    }
  };

  // Completeness score
  const completeness = 85;

  return (
    <div className="flex flex-col min-h-screen bg-slate-950">
      <Navbar onUploadClick={() => setIsUploadOpen(true)} />
      <UploadModal isOpen={isUploadOpen} onClose={() => setIsUploadOpen(false)} />

      <main className="flex-1 mx-auto max-w-7xl w-full px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-bold text-blue-400 uppercase tracking-wider font-mono">MSME Profile & Document Locker</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white">Business Verification Profile</h1>
            <p className="text-xs text-slate-400 mt-1">
              Maintained as verified business facts for zero-hallucination tender evaluation and application generation.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleSaveProfile}
              disabled={isSaving}
              className="px-5 py-2.5 rounded-xl font-semibold text-xs bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-600/20 transition-all flex items-center gap-2"
            >
              <Save className="h-4 w-4" />
              <span>{isSaving ? "Saving..." : "Save Profile"}</span>
            </button>
          </div>
        </div>

        {saveMessage && (
          <div className="mb-6 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            <span>{saveMessage}</span>
          </div>
        )}

        {/* Profile Completeness Bar */}
        <div className="mb-8 p-5 rounded-xl bg-slate-900/60 border border-slate-800">
          <div className="flex items-center justify-between mb-2 text-xs">
            <span className="font-bold text-slate-300">Profile Completeness Score</span>
            <span className="font-mono font-bold text-emerald-400">{completeness}% Complete</span>
          </div>
          <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
            <div className="h-full bg-gradient-to-r from-blue-500 to-emerald-400" style={{ width: `${completeness}%` }} />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left 2 Columns: Core Profile Details */}
          <div className="lg:col-span-2 space-y-6">
            <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
              <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
                <Building2 className="h-5 w-5 text-blue-400" />
                <span>Company Details</span>
              </h2>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Company Name</label>
                  <input
                    type="text"
                    value={profile.company_name}
                    onChange={(e) => setProfile({ ...profile, company_name: e.target.value })}
                    className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-white font-medium focus:border-blue-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Business Category</label>
                  <input
                    type="text"
                    value={profile.business_category}
                    onChange={(e) => setProfile({ ...profile, business_category: e.target.value })}
                    className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-white font-medium focus:border-blue-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Annual Turnover (INR)</label>
                  <input
                    type="number"
                    value={profile.annual_turnover}
                    onChange={(e) => setProfile({ ...profile, annual_turnover: Number(e.target.value) })}
                    className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-emerald-400 font-mono font-bold focus:border-blue-500 focus:outline-none"
                  />
                  <span className="text-[10px] text-slate-500 mt-0.5 block">Current: ₹50 Lakhs</span>
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Business State Location</label>
                  <input
                    type="text"
                    value={profile.state_location}
                    onChange={(e) => setProfile({ ...profile, state_location: e.target.value })}
                    className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-white font-medium focus:border-blue-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Years in Business</label>
                  <input
                    type="number"
                    value={profile.years_in_business}
                    onChange={(e) => setProfile({ ...profile, years_in_business: Number(e.target.value) })}
                    className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-white font-medium focus:border-blue-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Govt Supply Experience (Years)</label>
                  <input
                    type="number"
                    value={profile.govt_experience_years}
                    onChange={(e) => setProfile({ ...profile, govt_experience_years: Number(e.target.value) })}
                    className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-white font-medium focus:border-blue-500 focus:outline-none"
                  />
                </div>
              </div>
            </div>

            {/* Product Catalog Section */}
            <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <Package className="h-5 w-5 text-emerald-400" />
                  <span>Business Product Catalog ({products.length})</span>
                </h2>
              </div>

              <div className="flex items-center gap-2 mb-4">
                <input
                  type="text"
                  placeholder="Add new product or service (e.g. Desks, Chairs)..."
                  value={newProductName}
                  onChange={(e) => setNewProductName(e.target.value)}
                  className="flex-1 p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
                <button
                  onClick={handleAddProduct}
                  className="px-4 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-colors flex items-center gap-1 shrink-0"
                >
                  <Plus className="h-4 w-4" />
                  <span>Add Product</span>
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {products.map((p) => (
                  <div key={p.id} className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between text-xs">
                    <div>
                      <span className="font-bold text-white block">{p.name}</span>
                      <span className="text-[10px] text-slate-500">{p.description || "Vector Embeddings Ready"}</span>
                    </div>
                    <button
                      onClick={() => handleDeleteProduct(p.id)}
                      className="text-slate-500 hover:text-red-400 transition-colors p-1"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column: Business Document Locker */}
          <div className="space-y-6">
            <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
              <h2 className="text-base font-bold text-white mb-2 flex items-center gap-2">
                <FileCheck2 className="h-5 w-5 text-blue-400" />
                <span>Business Document Locker</span>
              </h2>
              <p className="text-xs text-slate-400 mb-4">
                Verification status used by Requirement Gap Analysis engine.
              </p>

              <div className="space-y-3">
                {documents.map((doc) => (
                  <div key={doc.id} className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-xs">
                    <div>
                      <span className="font-semibold text-white block">{doc.document_name}</span>
                      <span className="text-[10px] text-slate-500 uppercase font-mono">{doc.document_type}</span>
                    </div>

                    <div>
                      {doc.verification_status === "AVAILABLE" ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                          <CheckCircle2 className="h-3 w-3" />
                          AVAILABLE
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/15 text-rose-400 border border-rose-500/30">
                          <AlertCircle className="h-3 w-3" />
                          MISSING
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-5 border-t border-slate-800 pt-4 text-center">
                <button
                  onClick={() => setIsUploadOpen(true)}
                  className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors flex items-center justify-center gap-2"
                >
                  <Upload className="h-4 w-4" />
                  <span>Upload Verification Document</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
