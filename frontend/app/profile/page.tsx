"use client";

import { useEffect, useState } from "react";
import Navbar from "../../components/Navbar";
import UploadModal from "../../components/UploadModal";
import {
  Building2,
  Package,
  FileCheck2,
  CheckCircle2,
  AlertCircle,
  Plus,
  Trash2,
  ShieldCheck,
  Upload,
  Save,
  Clock,
  X,
  FileText,
  Phone,
  Mail,
  Award,
  Globe,
  Factory
} from "lucide-react";
import { api } from "../../services/api";

export default function ProfilePage() {
  const [profile, setProfile] = useState<any>({
    company_name: "Apex Modular Infrastructure Pvt. Ltd.",
    business_category: "Institutional Furniture, Modular Workstations & Educational Infrastructure",
    description: "Empanelled MSME manufacturer registered under Udyam and Make in India initiative.",
    annual_turnover: 6500000,
    is_msme_registered: true,
    msme_registration_number: "UDYAM-MH-12-0048291",
    has_gst_registration: true,
    gstin: "27AABCA4892F1Z4",
    state_location: "Maharashtra",
    operating_regions: ["Maharashtra", "Gujarat", "Goa", "Karnataka", "All India"],
    years_in_business: 6,
    govt_experience_years: 4,
    certifications: [
      "ISO 9001:2015 (QMS)",
      "ISO 14001:2015 (EMS)",
      "BIFMA Level-2 Compliant",
      "Class-1 Local Supplier (>50% MII)"
    ],
    manufacturing_capacity: "1,200 modular units / month from Pune facility",
    contact_email: "tenders@apexmodular.in",
    contact_phone: "+91 98220 84721"
  });

  const [products, setProducts] = useState<any[]>([]);
  const [documents, setDocuments] = useState<any[]>([]);

  // Product addition state
  const [newProductName, setNewProductName] = useState("");
  const [newProductCategory, setNewProductCategory] = useState("Furniture");
  const [newProductDesc, setNewProductDesc] = useState("");

  // Saving state
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");

  // Tender upload modal state
  const [isUploadOpen, setIsUploadOpen] = useState(false);

  // Document Locker Modal state
  const [isDocModalOpen, setIsDocModalOpen] = useState(false);
  const [docName, setDocName] = useState("");
  const [docType, setDocType] = useState("CERTIFICATE");
  const [docStatus, setDocStatus] = useState("AVAILABLE");
  const [docIssueDate, setDocIssueDate] = useState("");
  const [docFile, setDocFile] = useState<File | null>(null);
  const [isUploadingDoc, setIsUploadingDoc] = useState(false);

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
      const newProd = {
        name: newProductName,
        category: newProductCategory,
        description: newProductDesc || `Specification compliant ${newProductName}`
      };
      const saved = await api.addProduct(newProd).catch(() => ({ ...newProd, id: Date.now().toString() }));
      setProducts([...products, saved]);
      setNewProductName("");
      setNewProductDesc("");
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
      setTimeout(() => setSaveMessage(""), 3500);
    } catch (e) {
      setSaveMessage("Failed to update profile.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleUpdateDocStatus = async (id: string, newStatus: string) => {
    try {
      await api.updateDocument(id, { verification_status: newStatus }).catch(() => {});
      setDocuments(documents.map((d) => (d.id === id ? { ...d, verification_status: newStatus } : d)));
    } catch (e) {
      console.error("Failed to update doc status:", e);
    }
  };

  const handleDeleteDocument = async (id: string) => {
    try {
      await api.deleteDocument(id).catch(() => {});
      setDocuments(documents.filter((d) => d.id !== id));
    } catch (e) {
      console.error("Delete document error:", e);
    }
  };

  const handleAddDocumentToLocker = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!docName.trim()) return;

    try {
      setIsUploadingDoc(true);
      let savedDoc;

      if (docFile) {
        const formData = new FormData();
        formData.append("document_name", docName);
        formData.append("document_type", docType);
        if (docIssueDate) formData.append("issue_date", docIssueDate);
        formData.append("file", docFile);
        savedDoc = await api.uploadDocument(formData);
      } else {
        savedDoc = await api.createDocument({
          document_name: docName,
          document_type: docType,
          verification_status: docStatus,
          issue_date: docIssueDate
        });
      }

      setDocuments((prev) => {
        const exists = prev.find((d) => d.id === savedDoc.id || d.document_name === savedDoc.document_name);
        if (exists) {
          return prev.map((d) => (d.id === exists.id ? savedDoc : d));
        }
        return [...prev, savedDoc];
      });

      setIsDocModalOpen(false);
      setDocName("");
      setDocIssueDate("");
      setDocFile(null);
    } catch (err) {
      console.error("Document upload failed:", err);
    } finally {
      setIsUploadingDoc(false);
    }
  };

  // Dynamic Profile Completeness calculation
  const verifiedDocsCount = documents.filter((d) => d.verification_status === "AVAILABLE").length;
  const completeness = Math.min(
    100,
    Math.round(
      (profile.company_name ? 15 : 0) +
      (profile.gstin ? 15 : 0) +
      (profile.msme_registration_number ? 15 : 0) +
      (profile.annual_turnover > 0 ? 15 : 0) +
      (products.length >= 3 ? 15 : 10) +
      (verifiedDocsCount >= 5 ? 25 : verifiedDocsCount * 5)
    )
  );

  return (
    <div className="flex flex-col min-h-screen bg-slate-950">
      <Navbar onUploadClick={() => setIsUploadOpen(true)} />
      <UploadModal isOpen={isUploadOpen} onClose={() => setIsUploadOpen(false)} />

      {/* Document Upload/Add Modal */}
      {isDocModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl relative">
            <button
              onClick={() => setIsDocModalOpen(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              <X className="h-5 w-5" />
            </button>

            <div className="flex items-center gap-3 mb-4">
              <div className="p-2.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400">
                <FileCheck2 className="h-6 w-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Add Verification Document</h3>
                <p className="text-xs text-slate-400">Upload to Business Document Locker</p>
              </div>
            </div>

            <form onSubmit={handleAddDocumentToLocker} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Document Title / Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Valid Electrical Contractor License, ISO 9001, etc."
                  value={docName}
                  onChange={(e) => setDocName(e.target.value)}
                  className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Document Classification</label>
                  <select
                    value={docType}
                    onChange={(e) => setDocType(e.target.value)}
                    className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="MSME_CERTIFICATE">MSME Udyam Certificate</option>
                    <option value="GST_CERTIFICATE">GST Registration</option>
                    <option value="FINANCIAL_STATEMENT">Audited Financials</option>
                    <option value="EXPERIENCE_CERTIFICATE">Experience Proof</option>
                    <option value="PAN_CARD">PAN Card</option>
                    <option value="DECLARATION">Make in India Declaration</option>
                    <option value="CERTIFICATE">ISO / Quality Certificate</option>
                    <option value="AUTHORIZATION">OEM Authorization (MAF)</option>
                    <option value="LABOUR_COMPLIANCE">Labour / EPF License</option>
                    <option value="ELECTRICAL_LICENSE">Electrical License</option>
                    <option value="OTHER">Other Proof</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Initial Status</label>
                  <select
                    value={docStatus}
                    onChange={(e) => setDocStatus(e.target.value)}
                    className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="AVAILABLE">AVAILABLE (Verified)</option>
                    <option value="PENDING">PENDING (In Progress)</option>
                    <option value="MISSING">MISSING (Not Available)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Issue Date (Optional)</label>
                <input
                  type="date"
                  value={docIssueDate}
                  onChange={(e) => setDocIssueDate(e.target.value)}
                  className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Attach Scanned File (PDF/Image - Optional)</label>
                <input
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg"
                  onChange={(e) => setDocFile(e.target.files ? e.target.files[0] : null)}
                  className="w-full p-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-400 file:mr-3 file:py-1 file:px-3 file:rounded file:border-0 file:text-xs file:bg-blue-600 file:text-white hover:file:bg-blue-500 cursor-pointer"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsDocModalOpen(false)}
                  className="px-4 py-2 rounded-lg text-slate-300 hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isUploadingDoc}
                  className="px-5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold"
                >
                  {isUploadingDoc ? "Saving..." : "Save Document"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <main className="flex-1 mx-auto max-w-7xl w-full px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-bold text-blue-400 uppercase tracking-wider font-mono">
                Verified MSME Profile & Document Locker
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white">Business Intelligence Profile</h1>
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
              <span>{isSaving ? "Saving Changes..." : "Save Profile"}</span>
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
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-emerald-400 transition-all duration-500"
              style={{ width: `${completeness}%` }}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left 2 Columns: Core Profile Details & Products */}
          <div className="lg:col-span-2 space-y-6">
            {/* 1. Legal Entity & Registrations */}
            <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
              <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
                <Building2 className="h-5 w-5 text-blue-400" />
                <span>Enterprise Identity & Compliance Details</span>
              </h2>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Company Registered Name</label>
                  <input
                    type="text"
                    value={profile.company_name}
                    onChange={(e) => setProfile({ ...profile, company_name: e.target.value })}
                    className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-white font-medium focus:border-blue-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Primary Business Domain</label>
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
                  <span className="text-[10px] text-slate-500 mt-0.5 block">
                    Current: ₹{(Number(profile.annual_turnover || 0) / 100000).toFixed(1)} Lakhs
                  </span>
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Registered State (GST Principal Place)</label>
                  <input
                    type="text"
                    value={profile.state_location}
                    onChange={(e) => setProfile({ ...profile, state_location: e.target.value })}
                    className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-white font-medium focus:border-blue-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">MSME Udyam Registration No.</label>
                  <input
                    type="text"
                    value={profile.msme_registration_number || ""}
                    onChange={(e) => setProfile({ ...profile, msme_registration_number: e.target.value })}
                    className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-blue-400 font-mono font-semibold focus:border-blue-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Active GSTIN</label>
                  <input
                    type="text"
                    value={profile.gstin || ""}
                    onChange={(e) => setProfile({ ...profile, gstin: e.target.value })}
                    className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-amber-400 font-mono font-semibold focus:border-blue-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Years in Commercial Business</label>
                  <input
                    type="number"
                    value={profile.years_in_business}
                    onChange={(e) => setProfile({ ...profile, years_in_business: Number(e.target.value) })}
                    className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-white font-medium focus:border-blue-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Government Supply Experience (Years)</label>
                  <input
                    type="number"
                    value={profile.govt_experience_years}
                    onChange={(e) => setProfile({ ...profile, govt_experience_years: Number(e.target.value) })}
                    className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-white font-medium focus:border-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              {/* Manufacturing & Contact Info */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs mt-4 pt-4 border-t border-slate-800/80">
                <div>
                  <label className="block text-slate-400 mb-1 flex items-center gap-1.5">
                    <Factory className="h-3.5 w-3.5 text-slate-500" />
                    <span>Manufacturing Facility & Capacity</span>
                  </label>
                  <input
                    type="text"
                    value={profile.manufacturing_capacity || ""}
                    onChange={(e) => setProfile({ ...profile, manufacturing_capacity: e.target.value })}
                    className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-white font-medium focus:border-blue-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1 flex items-center gap-1.5">
                    <Mail className="h-3.5 w-3.5 text-slate-500" />
                    <span>Tender Desk Email</span>
                  </label>
                  <input
                    type="email"
                    value={profile.contact_email || ""}
                    onChange={(e) => setProfile({ ...profile, contact_email: e.target.value })}
                    className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-white font-medium focus:border-blue-500 focus:outline-none"
                  />
                </div>
              </div>
            </div>

            {/* 2. Product Catalog Section */}
            <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <Package className="h-5 w-5 text-emerald-400" />
                  <span>Business Product & Services Catalog ({products.length})</span>
                </h2>
                <span className="text-[10px] text-slate-500 font-mono">Vector Embedding Ready</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 mb-4">
                <input
                  type="text"
                  placeholder="Product name (e.g. Ergonomic Chairs)..."
                  value={newProductName}
                  onChange={(e) => setNewProductName(e.target.value)}
                  className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
                <select
                  value={newProductCategory}
                  onChange={(e) => setNewProductCategory(e.target.value)}
                  className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="Furniture">Furniture & Fixtures</option>
                  <option value="Hardware">IT Hardware & Networking</option>
                  <option value="Healthcare">Medical & Hospital Supplies</option>
                  <option value="Electrical">Electrical & Solar Systems</option>
                  <option value="Services">Facility & Housekeeping Services</option>
                </select>
                <button
                  onClick={handleAddProduct}
                  className="px-4 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-colors flex items-center justify-center gap-1.5"
                >
                  <Plus className="h-4 w-4" />
                  <span>Add Product</span>
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {products.map((p) => (
                  <div
                    key={p.id}
                    className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-start justify-between text-xs group hover:border-slate-700 transition-colors"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-white">{p.name}</span>
                        {p.category && (
                          <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-semibold">
                            {p.category}
                          </span>
                        )}
                      </div>
                      <span className="text-[10px] text-slate-400 line-clamp-1 mt-0.5">
                        {p.description || "Vector Embeddings Ready"}
                      </span>
                    </div>
                    <button
                      onClick={() => handleDeleteProduct(p.id)}
                      className="text-slate-600 group-hover:text-red-400 transition-colors p-1"
                      title="Remove product"
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
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <FileCheck2 className="h-5 w-5 text-blue-400" />
                  <span>Document Locker</span>
                </h2>
                <button
                  onClick={() => setIsDocModalOpen(true)}
                  className="px-2.5 py-1 rounded-lg bg-blue-600/10 text-blue-400 hover:bg-blue-600 hover:text-white border border-blue-500/20 text-xs font-semibold flex items-center gap-1 transition-all"
                >
                  <Plus className="h-3.5 w-3.5" />
                  <span>Add Doc</span>
                </button>
              </div>
              <p className="text-xs text-slate-400 mb-4">
                Verification status directly influences Requirement Gap Analysis & Readiness Index.
              </p>

              <div className="space-y-3">
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex flex-col gap-2 text-xs hover:border-slate-700 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <span className="font-semibold text-white block leading-tight">{doc.document_name}</span>
                        <span className="text-[10px] text-slate-500 uppercase font-mono">{doc.document_type}</span>
                      </div>

                      <button
                        onClick={() => handleDeleteDocument(doc.id)}
                        className="text-slate-600 hover:text-red-400 transition-colors p-0.5"
                        title="Remove Document"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>

                    <div className="flex items-center justify-between pt-1 border-t border-slate-900">
                      <span className="text-[10px] text-slate-500">
                        {doc.issue_date ? `Issued: ${doc.issue_date}` : "Digital Record"}
                      </span>

                      {/* Status Selector Dropdown */}
                      <select
                        value={doc.verification_status}
                        onChange={(e) => handleUpdateDocStatus(doc.id, e.target.value)}
                        className={`text-[10px] font-bold px-2 py-0.5 rounded border focus:outline-none cursor-pointer ${
                          doc.verification_status === "AVAILABLE"
                            ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
                            : doc.verification_status === "PENDING"
                            ? "bg-amber-500/15 text-amber-400 border-amber-500/30"
                            : "bg-rose-500/15 text-rose-400 border-rose-500/30"
                        }`}
                      >
                        <option value="AVAILABLE" className="bg-slate-900 text-emerald-400">AVAILABLE</option>
                        <option value="PENDING" className="bg-slate-900 text-amber-400">PENDING</option>
                        <option value="MISSING" className="bg-slate-900 text-rose-400">MISSING</option>
                      </select>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-5 border-t border-slate-800 pt-4">
                <button
                  onClick={() => setIsDocModalOpen(true)}
                  className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors flex items-center justify-center gap-2"
                >
                  <Upload className="h-4 w-4" />
                  <span>Upload / Add Verification Document</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
