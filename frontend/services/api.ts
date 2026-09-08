const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const headers: Record<string, string> = {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers as Record<string, string> || {}),
  };

  if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: "Request failed" }));
    throw new Error(errorData.detail || errorData.message || `API error ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Seed sample data
  seedSample: () => fetchApi<{ message: string }>("/seed/sample"),

  // Health
  getHealth: () => fetchApi<{ status: string; service: string }>("/health"),

  // Business Profile & Catalog
  getProfile: () => fetchApi<any>("/business/profile"),
  updateProfile: (data: any) => fetchApi<any>("/business/profile", { method: "PUT", body: JSON.stringify(data) }),
  getProducts: () => fetchApi<any[]>("/business/products"),
  addProduct: (product: { name: string; category?: string; description?: string }) =>
    fetchApi<any>("/business/products", { method: "POST", body: JSON.stringify(product) }),
  deleteProduct: (id: string) => fetchApi<any>(`/business/products/${id}`, { method: "DELETE" }),
  
  // Documents
  getDocuments: () => fetchApi<any[]>("/documents"),
  uploadDocument: (formData: FormData) => fetchApi<any>("/documents/upload", { method: "POST", body: formData }),

  // Tenders
  getTenders: () => fetchApi<any[]>("/tenders"),
  getTenderDetails: (id: string) => fetchApi<any>(`/tenders/${id}`),
  uploadTender: (formData: FormData) => fetchApi<any>("/tenders/upload", { method: "POST", body: formData }),
  getTenderStatus: (id: string) => fetchApi<any>(`/tenders/${id}/status`),
  
  // Analysis & Matching
  analyzeTender: (id: string) => fetchApi<any>(`/tenders/${id}/analyze`, { method: "POST" }),
  matchTender: (id: string) => fetchApi<any>(`/tenders/${id}/match`, { method: "POST" }),
  getTenderAnalysis: (id: string) => fetchApi<any>(`/tenders/${id}/analysis`),

  // Application Assistant
  generateCoverLetter: (data: { business_id: string; tender_id: string }) =>
    fetchApi<any>("/applications/cover-letter", { method: "POST", body: JSON.stringify(data) }),
  generateDeclaration: (data: { business_id: string; tender_id: string }) =>
    fetchApi<any>("/applications/declaration", { method: "POST", body: JSON.stringify(data) }),
  generateTechnicalResponse: (data: { business_id: string; tender_id: string }) =>
    fetchApi<any>("/applications/technical-response", { method: "POST", body: JSON.stringify(data) }),
  getApplication: (id: string) => fetchApi<any>(`/applications/${id}`),
  updateApplication: (id: string, data: any) => fetchApi<any>(`/applications/${id}`, { method: "PUT", body: JSON.stringify(data) }),
};
